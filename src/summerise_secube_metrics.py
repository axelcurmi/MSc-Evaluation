def main():
    import argparse
    import json
    import math

    argparser = argparse.ArgumentParser()
    argparser.add_argument("file", type=argparse.FileType('r'),
        help="SEcube metrics file")
    argparser.add_argument("--json", default=False, action="store_true",
        help="Return a JSON object instead of CSV")

    args = argparser.parse_args()

    data = args.file.read()
    data = json.loads(data)

    summary = {}

    # Summerise
    for i in data:
        for key, value in i.items():
            
            if key not in summary:
                summary[key] = value
            else:
                summary[key] += value

    # Average
    for key, value in summary.items():
        summary[key] = value / len(data)

    if args.json:
        print(json.dumps(summary, indent=4))
    else:
        print("{},{},{},{}".format(
            math.floor(summary["crypto_init_count"]),
            round(summary["crypto_init_time"], 5),
            math.floor(summary["crypto_update_count"]),
            round(summary["crypto_update_time"], 5)))

if __name__ == "__main__":
    main()
