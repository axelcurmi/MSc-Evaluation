START_HTML_TAG = b"<html>"
END_HTML_TAG = b"</html>"

size_table = {
    "128B": pow(2, 7),
    "256B": pow(2, 8),
    "512B": pow(2, 9),
    "1KB":  pow(2, 10),
    "10KB": pow(2, 10) * 10,
    "100KB": pow(2, 10) * 100,
    "500KB": pow(2, 10) * 500,
    "1MB":  pow(2, 20),
    "1GB":  pow(2, 30)
}

def main():
    import argparse

    argparser = argparse.ArgumentParser("HTML file generator")
    argparser.add_argument("size",
                           type=str,
                           help="Size of the HTML file to generate")
    args = argparser.parse_args()

    size_in_bytes = size_table[args.size]
    bytes_to_generate = size_in_bytes - len(START_HTML_TAG) - len(END_HTML_TAG)

    with open(f"{args.size}.html", "wb+") as stream:
        stream.write(START_HTML_TAG)
        stream.write(b"A" * bytes_to_generate)
        stream.write(END_HTML_TAG)

if __name__ == "__main__":
    main()
