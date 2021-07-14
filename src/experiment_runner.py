import json
import os

from datetime import datetime
from time import time

import commands
import util
import rv

experiments_table = {
    "commands": commands.run
} 

def main():
    import argparse

    # Parse CLI arguments
    argparser = argparse.ArgumentParser("MSc-Evaluation experiment runner")
    argparser.add_argument("config", type=argparse.FileType('r'),
        help="Configuration file")
    argparser.add_argument("instruction", type=argparse.FileType('r'),
        help="Test instruction file")

    args = argparser.parse_args()

    # Load config and instruction files
    config = json.load(args.config)
    instruction = json.load(args.instruction)

    runner = experiments_table[instruction["type"]]

    # Should add instrumentation?
    instrumentation = "instrumentation" in instruction and \
        instruction["instrumentation"]

    # Create the destination directory "out/<TIMESTAMP>_<TYPE>_<INSTRUMENTATION>"
    #   Examples:
    #       - out/20210713_commands_T
    #       - out/20210713_shell_F
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    dest_dir = os.path.join(
        config["out_dir"],
        "{}_{}_{}".format(timestamp,
                          instruction["type"],
                          str(instrumentation)[0]))
    os.mkdir(dest_dir)

    # Weave aspects if we want to add instrumentation
    if instrumentation:
        rv.weave

    for experiment in instruction["experiments"]:
        dest_dir = os.path.join(dest_dir, experiment["name"])

        print("Running experiment with {} repetitions".format(
            experiment["repetitions"]))
        for i in range(experiment["repetitions"]):
            print("Starting repetition {}".format(i + 1))
            runner(
                config=config,
                experiment=experiment,
                save_timing=util.save_timing(dest_dir)
            )

            if instrumentation:
                util.save_trace(dest_dir, i)
        
        util.add_stats(dest_dir)

if __name__ == "__main__":
    main()
