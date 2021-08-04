import json
import os

from datetime import datetime

# Experiments
import commands
import files
import shell
import dockercontainers
import web

import util
import rv

experiments_table = {
    "commands": commands.run,
    "files": files.run,
    "shell": shell.run,
    "docker": dockercontainers.run,
    "web": web.run,
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
    argparser.add_argument("--out", help="Specify an output directory")
    argparser.add_argument("--no-calc-stats", default=False,
        action="store_true",
        help="Determines whether the AVG and STDEV stats are auto-calculated")
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
    if args.out:
        out_dir = os.path.join(args.out,
            "{}_{}".format(str(args.with_instrumentation)[0],
                              str(args.with_secube)[0]))
    else:
        out_dir = os.path.join(config["out_dir"],
            "{}_{}_{}_{}".format(timestamp,
                            instruction["type"],
                            str(args.with_instrumentation)[0],
                            str(args.with_secube)[0]))

    # Weave aspects if we want to add instrumentation
    if args.with_instrumentation:
        rv.weave()

    for experiment in instruction["experiments"]:
        dest_dir = os.path.join(out_dir, experiment["name"])
        
        offset = 0
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        else:
            while True:
                if os.path.exists(os.path.join(dest_dir, f"{offset}.json")):
                    offset += 1
                else:
                    break

        print("Running experiment with {} repetitions".format(
            experiment["repetitions"]))
        for i in range(experiment["repetitions"]):
            if args.with_instrumentation:
                trace_stream = open(
                    os.path.join(dest_dir, f"{i + offset}.json"), "w+b")
                if not args.unbuffered:
                    trace_stream.write(b"[]")
                    rv.set_buffered_stream(trace_stream)

            print("Starting repetition {}".format(i + 1))
            runner(
                config=config,
                experiment=experiment,
                with_secube=args.with_secube,
                save_timing=util.save_timing(dest_dir),
                add_secube_metrics=util.add_secube_metrics(dest_dir)
            )

            if args.with_instrumentation:
                if args.unbuffered:
                    # Save trace in one go
                    json_dump = json.dumps(rv.trace)
                    trace_stream.write(json_dump.encode())
                    # Reset
                    rv.trace = []
                rv.event_id = 0
                trace_stream.close()

        if not args.no_calc_stats:
            util.add_stats(dest_dir)

if __name__ == "__main__":
    main()
