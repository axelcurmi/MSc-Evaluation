import argparse

argparser = argparse.ArgumentParser(
    description="Calculates average time taken for M.Sc. evaluation")
argparser.add_argument("file", metavar="FILE",
                       type=argparse.FileType("r"),
                       help="The CSV file to load")
args = argparser.parse_args()

total_time_taken = 0
n = 0

for result in args.file:
    time_taken = result.split(",")[2]

    total_time_taken += float(time_taken)
    n += 1

print(f"{total_time_taken} / {n} = {total_time_taken / n}")
