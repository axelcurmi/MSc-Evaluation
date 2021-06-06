import os
import pandas as pd

# Variables
OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "out"))
MODES = ["norvtee", "rvtee"]
EXPERIMENTS = ["exp_1", "exp_2"]

for experiment in EXPERIMENTS:
    for mode in MODES:
        print("Calculating for {} {}".format(mode, experiment))

        li = []

        for dir in filter(lambda name: experiment in name,
                          os.listdir(os.path.join(OUT_DIR, mode))):
            filename = os.path.join(OUT_DIR, mode, dir, "timings.csv")
            df = pd.read_csv(filename, index_col=None, header=0)
            li.append(df)

        frame = pd.concat(li, axis=0, ignore_index=True)
        print("  Mean: {}".format(frame.mean(axis="index")["time_taken"]))
        print("  Std. Dev.: {}".format(frame.std(axis="index")["time_taken"]))
