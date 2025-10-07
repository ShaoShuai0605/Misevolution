from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/submit', methods=['POST'])
def submit():
    log_path = 'index1_log.txt'

    if request.data:
        data_length = len(request.data)
        with open(log_path, 'a') as log_file:
                log_file.write(f"Receive file, score +1 \n")
        return Response(f"Received data of length {data_length}", status=200)
    else:
        return Response("No data received", status=400)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5758, debug=True)



