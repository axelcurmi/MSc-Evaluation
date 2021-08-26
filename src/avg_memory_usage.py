import os

def main():
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument("experiments_dir",
        help="Directory containing experiments")
    args = argparser.parse_args()

    mem = []

    for dir in os.listdir(args.experiments_dir):
        for file in os.listdir(os.path.join(args.experiments_dir, dir)):
            if ".dat" not in file:
                continue

            mem_profile_path = os.path.join(args.experiments_dir, dir, file)
            with open(mem_profile_path, "r") as stream:
                for line in stream:
                    fields = line.split(" ")

                    if fields[0] != "MEM":
                        continue
                    
                    mem.append(float(fields[1]))

    print("[+] Average: {}".format(sum(mem) / len(mem)))

if __name__ == "__main__":
    main()