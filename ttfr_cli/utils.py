import datetime
import sys

def now():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def green(x): return f"\033[92m{x}\033[0m"
def yellow(x): return f"\033[93m{x}\033[0m"
def red(x): return f"\033[91m{x}\033[0m"
def blue(x): return f"\033[94m{x}\033[0m"

def info(msg):
    print(blue("[INFO]"), msg)

def success(msg):
    print(green("[OK]"), msg)

def warn(msg):
    print(yellow("[WARN]"), msg)

def error(msg):
    print(red("[ERROR]"), msg)

