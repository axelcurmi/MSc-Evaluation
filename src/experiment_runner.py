import json
import os

from datetime import datetime
from time import time

import commands
import util

experiments_table = {
    "commands": commands.run
}

def save_trace(out_dir):
    def inner(trace_id):
        import rv

        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        with open(os.path.join(out_dir, f"{trace_id}.json"), "w") as stream:
            json.dump(rv.trace, stream, indent=4)

        rv.trace = []
    return inner   

def main():
    import argparse

    argparser = argparse.ArgumentParser("MSc-Evaluation experiment runner")
    argparser.add_argument("config", type=argparse.FileType('r'),
        help="Configuration file")
    argparser.add_argument("instruction", type=argparse.FileType('r'),
        help="Test instruction file")

    args = argparser.parse_args()

    config = json.load(args.config)
    instruction = json.load(args.instruction)

    runner = experiments_table[instruction["type"]]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    out_dir = os.path.join(config["out_dir"], timestamp) # TODO: Better name?

    save_trace_callback = None
    if "instrumentation" in instruction and instruction["instrumentation"]:
        import rv
        rv.weave()

        save_trace_callback = save_trace(out_dir)
    save_timing = util.save_timing(out_dir)

    for experiment in instruction["experiments"]:
        # Fix experiment name in out file names:
        #   out/20210713/command_instrumentation/uname/timings.csv
        #   out/20210713/command_instrumentation/uname/0.json
        print("Running commands experiment with {} repetitions".format(
            experiment["repetitions"]))
        for i in range(experiment["repetitions"]):
            print("Starting repetition {}".format(i + 1))
            runner(
                config=config,
                experiment=experiment,
                save_trace_callback=save_trace_callback,
                save_timing=save_timing
            )
    
    util.write_average(out_dir)

if __name__ == "__main__":
    main()
