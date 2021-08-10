def get_max_memory_usage(file_stream):
    max_mem = 0
    for line in file_stream:
        fields = line.split(" ")

        if fields[0] != "MEM":
            continue
        
        mem = float(fields[1])

        if mem > max_mem:
            max_mem = mem
    return max_mem


def main():
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("mprofile_file", type=argparse.FileType('r'),
        help="Python memory profiler data file")

    args = argparser.parse_args()
    print("[+] Max memory: {} MiB".format(
        get_max_memory_usage(args.mprofile_file)))

if __name__ == "__main__":
    main()