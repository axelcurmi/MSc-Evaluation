def main():
    import argparse
    import json

    argparser = argparse.ArgumentParser()
    argparser.add_argument("file", type=argparse.FileType('r'),
        help="SEcube metrics file")

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

    print(json.dumps(summary, indent=4))

if __name__ == "__main__":
    main()
