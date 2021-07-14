import csv
import json
import os
import pandas

import rv

def save_timing(dest_dir):
    def inner(timing):
        if not os.path.exists(dest_dir):
            os.mkdir(dest_dir)

        add_header = False
        flag = "a"

        timings_file_path = os.path.join(dest_dir, "timings.csv")
        if not os.path.exists(timings_file_path):
            add_header = True
            flag = "w"

        with open(timings_file_path, flag, newline="") as stream:
            csv_out=csv.writer(stream)
            
            if add_header:
                csv_out.writerow(["start_time", "end_time", "time_taken"])

            csv_out.writerow(timing)
    return inner

def save_trace(dest_dir, trace_id):
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    with open(os.path.join(dest_dir, f"{trace_id}.json"), "w") as stream:
        json.dump(rv.trace, stream, indent=4)

    rv.trace = []

def add_stats(dest_dir):
    timings_file_path = os.path.join(dest_dir, "timings.csv")
    df = pandas.read_csv(timings_file_path, index_col=None, header=0)

    with open(timings_file_path, "a", newline="") as stream:
        csv_out=csv.writer(stream)
        
        csv_out.writerow([]) # Add blank row
        csv_out.writerow(["", "Avg.", df.mean(axis="index")["time_taken"]])
        csv_out.writerow(["", "Std. Dev.", df.std(axis="index")["time_taken"]])
