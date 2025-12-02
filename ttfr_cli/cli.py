import argparse
from .main import do_start, do_stop, do_status, do_flush, do_replay

def run_cli():
    p = argparse.ArgumentParser(prog="ttfr", description="Time Travel Forensics Recorder")
    sub = p.add_subparsers(dest="command")

    sub.add_parser("start")
    sub.add_parser("stop")
    sub.add_parser("status")

    f = sub.add_parser("flush")
    f.add_argument("--reason", required=True)

    r = sub.add_parser("replay")
    r.add_argument("path")

    args = p.parse_args()

    if args.command == "start": do_start()
    elif args.command == "stop": do_stop()
    elif args.command == "status": do_status()
    elif args.command == "flush": do_flush(args.reason)
    elif args.command == "replay": do_replay(args.path)
    else:
        p.print_help()

