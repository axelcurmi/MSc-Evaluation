import json
import os

from datetime import datetime
from time import time

import commands
import files
import util
import rv

from pysecube import Wrapper

experiments_table = {
    "commands": commands.run,
    "files": files.run
}

def main():
    import argparse

    # Parse CLI arguments
    argparser = argparse.ArgumentParser("MSc-Evaluation experiment runner")
    argparser.add_argument("config", type=argparse.FileType('r'),
        help="Configuration file")
    argparser.add_argument("instruction", type=argparse.FileType('r'),
        help="Test instruction file")
    argparser.add_argument("--with-instrumentation", default=False,
        action="store_true",
        help="Runs the Paramiko experiments with RV instrumentation")
    argparser.add_argument("--with-secube", default=False, action="store_true",
        help="Runs the Paramiko experiments using the SEcube HSM")
    argparser.add_argument("--profiling-memory", default=False,
        action="store_true",
        help="Determines whether the memory is being profiled or not")

    args = argparser.parse_args()

    # Load config and instruction files
    config = json.load(args.config)
    instruction = json.load(args.instruction)

    runner = experiments_table[instruction["type"]]

    # Create the destination directory "out/<TIMESTAMP>_<TYPE>_<INSTRUMENTATION>"
    #   Examples:
    #       - out/20210713_commands_T
    #       - out/20210713_shell_F
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    out_dir = os.path.join(
        config["out_dir"],
        "{}_{}_{}_{}".format(timestamp,
                          instruction["type"],
                          str(args.with_instrumentation)[0],
                          str(args.with_secube)[0]))

    # Weave aspects if we want to add instrumentation
    if args.with_instrumentation:
        rv.weave()

    # Create PySEcube wrapper instance
    pysecube = None
    if args.with_secube:
        pysecube = Wrapper(b"test")
        pysecube.crypto_set_time_now()

    for experiment in instruction["experiments"]:
        dest_dir = os.path.join(out_dir, experiment["name"])

        print("Running experiment with {} repetitions".format(
            experiment["repetitions"]))
        for i in range(experiment["repetitions"]):
            print("Starting repetition {}".format(i + 1))
            runner(
                config=config,
                experiment=experiment,
                pysecube=pysecube,
                save_timing= None if args.profiling_memory \
                    else util.save_timing(dest_dir) 
            )

            if args.with_instrumentation and not args.profiling_memory:
                util.save_trace(dest_dir, i)
        
        if not args.profiling_memory:
            util.add_stats(dest_dir)

    # Logout and free library handles
    if pysecube:
        pysecube.destroy()

if __name__ == "__main__":
    main()
