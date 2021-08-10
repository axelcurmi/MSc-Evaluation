START_HTML_TAG = b"<html>"
END_HTML_TAG = b"</html>"

size_table = {
    "KB":  pow(2, 10),
    "MB":  pow(2, 20),
    "GB":  pow(2, 30)
}

def main():
    import argparse

    argparser = argparse.ArgumentParser("HTML file generator")
    argparser.add_argument("size", nargs=2, type=str,
                           help="Size of the HTML file to generate")
    args = argparser.parse_args()

    size_in_bytes = int(args.size[0]) * size_table[args.size[1]]
    bytes_to_generate = size_in_bytes - len(START_HTML_TAG) - len(END_HTML_TAG)

    with open(f"{args.size[0]}{args.size[1]}.html", "wb+") as stream:
        stream.write(START_HTML_TAG)
        stream.write(b"A" * bytes_to_generate)
        stream.write(END_HTML_TAG)

if __name__ == "__main__":
    main()
