import json
import os

from datetime import datetime
from time import time

# Experiments
import commands
import files
import shell
import dockercontainers

import util
import rv

from pysecube import Wrapper

experiments_table = {
    "commands": commands.run,
    "files": files.run,
    "shell": shell.run,
    "docker": dockercontainers.run
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
    argparser.add_argument("--unbuffered", default=False,
        action="store_true",
        help="Determines whether the saving of RV events is unbuffered or not")

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

    for experiment in instruction["experiments"]:
        dest_dir = os.path.join(out_dir, experiment["name"])
        
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        print("Running experiment with {} repetitions".format(
            experiment["repetitions"]))
        for i in range(experiment["repetitions"]):
            if args.with_instrumentation:
                trace_stream = open(os.path.join(dest_dir, f"{i}.json"), "w+b")
            if not args.unbuffered:
                trace_stream.write(b"[]")
                rv.set_buffered_stream(trace_stream)

            print("Starting repetition {}".format(i + 1))
            runner(
                config=config,
                experiment=experiment,
                save_timing= util.save_timing(dest_dir)
            )

            if args.with_instrumentation and \
               args.unbuffered:
                # Save trace in one go
                json_dump = json.dumps(rv.trace)
                trace_stream.write(json_dump.encode())
                # Clear
                rv.trace = []
            trace_stream.close()

        util.add_stats(dest_dir)

if __name__ == "__main__":
    main()
