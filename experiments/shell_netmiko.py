from netmiko import ConnectHandler

linux_ssh = {
    "device_type": "linux_ssh",
    "host": "192.168.1.90",
    "port": 22,
    "username": "user",
    "password": "password"
}

shell = ConnectHandler(**linux_ssh)
for i in range(100):
    print(i)
    shell.send_command("cat resources/1MB.txt")
shell.disconnect()
