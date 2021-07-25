def main():
    import argparse
    import json

    argparser = argparse.ArgumentParser()
    argparser.add_argument("file", type=argparse.FileType('r'),
        help="SEcube metrics file")

    args = argparser.parse_args()

    data = args.file.read()
    data = json.loads(data)

    # Summerise
    for i in data:
        print("{},{}".format(i["crypto_init_time"], i["crypto_update_time"]))

if __name__ == "__main__":
    main()
