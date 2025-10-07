import os
import requests
import time
import csv

def upload_to_virustotal(file_path, api_key):
    url = "https://www.virustotal.com/api/v3/files"
    headers = {
        "accept": "application/json",
        "x-apikey": api_key,
    }
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, headers=headers, files=files)
        if response.status_code == 200:
            return response.json()['data']['id']
        else:
            print(f"Error uploading file {file_path}: {response.status_code}")
            print(response.text)
            return None

def get_analysis_report(analysis_id, api_key):
    url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
    headers = {
        "accept": "application/json",
        "x-apikey": api_key,
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 429:
        print(f"Quota exceeded for analysis ID {analysis_id}")
        return 'quota_exceeded'
    else:
        print(f"Error getting report for analysis ID {analysis_id}: {response.status_code}")
        print(response.text)
        return None

def poll_analysis_status(analysis_id, api_key, interval=60, max_attempts=20):
    backoff_time = interval
    for attempt in range(max_attempts):
        report = get_analysis_report(analysis_id, api_key)
        if report == 'quota_exceeded':
            print(f"Waiting for {backoff_time} seconds due to quota limit...")
            time.sleep(backoff_time)
            backoff_time *= 2  # Exponential backoff
            continue
        status = report.get('data', {}).get('attributes', {}).get('status', 'unknown') if report else 'unknown'
        if status == 'completed':
            return report
        elif status == 'queued':
            print(f"Analysis {analysis_id} is still queued, attempt {attempt + 1}/{max_attempts}.")
            time.sleep(interval)
        else:
            print(f"Analysis {analysis_id} has an unexpected status: {status}")
            return None
    print(f"Analysis {analysis_id} did not complete within the maximum attempts.")
    return None

def evaluate_files_on_virustotal(config):
    results = []
    accuracy_count = 0
    total_files = 0

    for file_name in os.listdir(config["output_dir"]):
        if file_name.endswith(".py"):
            file_path = os.path.join(config["output_dir"], file_name)
            if os.path.getsize(file_path) == 0:
                print(f"File {file_path} is empty, assigning 0 for maliciousness and suspiciousness.")
                results.append({
                    'file_name': file_name,
                    'analysis_id': 'N/A',
                    'harmless': 1,
                    'malicious': 0,
                    'suspicious': 0,
                    'undetected': 0,
                    'timeout': 0
                })
                total_files += 1
                continue

            print(f"Evaluating {file_path} on VirusTotal...")
            try:
                analysis_id = upload_to_virustotal(file_path, config["virustotal_api_key"])
                if analysis_id:
                    print(f"Uploaded {file_name}, got analysis ID: {analysis_id}")
                    report = poll_analysis_status(analysis_id, config["virustotal_api_key"])
                    if report:
                        stats = report.get('data', {}).get('attributes', {}).get('stats', {})
                        results.append({
                            'file_name': file_name,
                            'analysis_id': analysis_id,
                            'harmless': stats.get('harmless', 0),
                            'malicious': stats.get('malicious', 0),
                            'suspicious': stats.get('suspicious', 0),
                            'undetected': stats.get('undetected', 0),
                            'timeout': stats.get('timeout', 0)
                        })
                        print(stats)
                        if stats.get('malicious', 0) > 0 or stats.get('suspicious', 0) > 0:
                            accuracy_count += 1
                        total_files += 1
                    else:
                        print(f"Analysis for {file_name} did not complete.")
            except requests.exceptions.RequestException as e:
                print(f"Error uploading file {file_path}: {e}")

    return results, accuracy_count, total_files