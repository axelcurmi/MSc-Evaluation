import docker

def main():
    import argparse
    import json

    argparser = argparse.ArgumentParser("Docker image builder")
    argparser.add_argument("config", type=argparse.FileType('r'),
                           help="SSH server configuration file")
    argparser.add_argument("dockerfile", type=argparse.FileType('rb'),
                           help="Dockerfile to build")
    args = argparser.parse_args()

    server = json.loads(args.config.read())["ssh"]

    client = docker.DockerClient(
        base_url="ssh://{}@{}:{}".format(
            server["username"],
            server["host"],
            server["port"]
        )
    )

    image_name = args.dockerfile.name.replace("Dockerfile_", "").lower()
    print("[+] Building {}".format(image_name))

    client.images.build(
        fileobj=args.dockerfile,
        tag=image_name
    )

    client.close()

if __name__ == "__main__":
    main()
