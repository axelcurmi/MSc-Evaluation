import csv
import os

def save_timing(out_dir):
    def inner(timing):
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        add_header = False
        flag = "a"

        timings_file_path = os.path.join(out_dir, "timings.csv")
        if not os.path.exists(timings_file_path):
            add_header = True
            flag = "w"

        with open(timings_file_path, flag, newline="") as stream:
            csv_out=csv.writer(stream)
            
            if add_header:
                csv_out.writerow(["start_time", "end_time", "time_taken"])

            csv_out.writerow(timing)
    return inner

def write_average(out_dir):
    import pandas as pd

    with open(os.path.join(out_dir, "timings.csv")) as stream:
        csv_in = csv.reader(stream)
        for row in csv_in:
            print(row)
