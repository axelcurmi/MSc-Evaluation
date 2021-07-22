import os

files_table = {
    "128B": pow(2, 7),
    "256B": pow(2, 8),
    "512B": pow(2, 9),
    "1KB":  pow(2, 10),
    "1MB":  pow(2, 20),
    "1GB":  pow(2, 30)
}

def generate_files():
    if not os.path.exists("resources"):
        os.mkdir("resources")

    for filename, filesize in files_table.items():
        filename = "{}.txt".format(filename)
        with open(os.path.join("resources", filename), "w") as stream:
            print("[+] Generating {}".format(filename))
            stream.write((b"A" * filesize).decode())

def transfer_and_execute_script(config):
    import paramiko
    import scp

    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(
        config["host"],
        config["port"],
        config["username"],
        config["password"]
    )

    sftp = scp.SCPClient(ssh.get_transport())

    # Upload Python script to server
    print("[+] Transferring script to remote server")
    sftp.put(os.path.basename(__file__), os.path.basename(__file__))
    sftp.close()

    # Execute script
    print("[+] Executing script on remote server")
    ssh.exec_command("python3 {}".format(os.path.basename(__file__)))

    ssh.close()

def main():
    import argparse

    argparser = argparse.ArgumentParser("Experimentation file generator")
    argparser.add_argument("--config", "-c",
                           type=argparse.FileType('r'),
                           help="SSH server configuration file")
    args = argparser.parse_args()

    generate_files()

    if args.config:
        import json
        config = json.load(args.config)
        transfer_and_execute_script(config["ssh"])

if __name__ == "__main__":
    main()
