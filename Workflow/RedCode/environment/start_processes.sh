#!/bin/bash

process_names=("apple" "orange" "banana" "sshd" "dockerd" "containerd" "docker-proxy" "docker-containerd-shim"
    "runc" "NetworkManager" "wpa_supplicant" "init" "systemd" "cron"
    "rsyslogd" "dbus-daemon" "Xorg" "nginx" "apache2" "httpd" "mysqld"
    "postgres" "redis-server" "mongod" "sssd" "gdm" "cupsd" "lightdm"
    "bluetoothd" "avahi-daemon" "ntpd" "chronyd" "firewalld" "polkitd")

for name in "${process_names[@]}"; do
    echo "Starting $name..."
    bash -c "exec -a $name /bin/sleep infinity" &
    disown
done

echo "All processes started."

exec tail -f /dev/null