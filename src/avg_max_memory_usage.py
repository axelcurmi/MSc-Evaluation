from max_memory_usage import get_max_memory_usage

import os

def main():
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("mprofile_dir",
        help="Directory containing Python memory profiler data")
    args = argparser.parse_args()

    files = os.listdir(args.mprofile_dir)

    mem_max_total = 0
    count = 0

    for file in files:
        if file.endswith(".dat"):
            file_stream = open(os.path.join(args.mprofile_dir, file), "r")
            mem_max = get_max_memory_usage(file_stream)
            print("[+] {} :: {}".format(file, mem_max))
            mem_max_total += mem_max
            count += 1
            file_stream.close()
    
    print("[+] Average: {} / {} = {}".format(
        mem_max_total, count, mem_max_total / count))

if __name__ == "__main__":
    main()