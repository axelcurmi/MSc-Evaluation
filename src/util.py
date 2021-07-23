import csv
import json
import os
import pandas
import threading

save_event_lock = threading.RLock()

def save_event(stream, event):
    save_event_lock.acquire()
    try:
        stream.seek(0)
        data = json.loads(stream.read().decode())

        data.append(event)
        stream.seek(0)
        stream.write(json.dumps(data).encode())
    finally:
        save_event_lock.release()

def save_timing(dest_dir):
    def inner(timing):
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

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

def add_stats(dest_dir):
    timings_file_path = os.path.join(dest_dir, "timings.csv")
    df = pandas.read_csv(timings_file_path, index_col=None, header=0)

    with open(timings_file_path, "a", newline="") as stream:
        csv_out=csv.writer(stream)
        
        csv_out.writerow([]) # Add blank row
        csv_out.writerow(["", "Avg.", df.mean(axis="index")["time_taken"]])
        csv_out.writerow(["", "Std. Dev.", df.std(axis="index")["time_taken"]])
