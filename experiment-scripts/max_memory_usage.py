
def main():
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("mprofile_file", type=argparse.FileType('r'),
        help="Python memory profiler data file")

    args = argparser.parse_args()

    mem_max = 0
    for line in args.mprofile_file:
        fields = line.split(" ")

        if fields[0] != "MEM":
            continue
        
        mem = float(fields[1])

        if mem > mem_max:
            mem_max = mem
    print("MAX MiB: {}".format(mem_max))

if __name__ == "__main__":
    main()
