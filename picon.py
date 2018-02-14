#!/usr/bin/env python3
"""
Searches local network for a Raspberry Pi and connects to it over SSH
"""

import sys
import time
import argparse
import subprocess

__author__ = "Nick Everett"
__version__ = "0.1.0"
__license__ = "GNU GPLv3"


def ip_range(start_ip, end_ip):
    start = list(map(int, start_ip.split(".")))
    end = list(map(int, end_ip.split(".")))
    temp = start
    ip_range = [start_ip]
    while temp != end:
        start[3] += 1
        for i in (3, 2, 1):
            if temp[i] == 256:
                temp[i] = 0
                temp[i - 1] += 1
        ip_range.append(".".join(map(str, temp)))
    return ip_range


def test_connection(ip_list):
    is_up=[]
    for ip in ip_list:
        p = subprocess.Popen(
            ["ping", ip, "-c 1"], stdout=subprocess.PIPE)
        print("testing connection to {}".format(ip))
        #while p.poll() is None:
            #print('.', end='', flush=True)
            #time.sleep(1)
        # TODO add in machine names to output
        try:
            p.wait(timeout=2)
            if p.poll() == 0:
                is_up.append([ip, True])
                sys.stdout.write("\033[F")  # cursor up one line
                print("\n" + ip + " is up")
            elif p.poll() >= 1:
                is_up.append([ip, False])
                sys.stdout.write("\033[F")  # cursor up one line
                print("\n" + ip + " is down")
            else:
                print("Fail")
        except subprocess.TimeoutExpired:
            print("connection timed out")
            pass
        # TODO except if IP is self
    return is_up


def ssh_connection(target_ip, command=""):
    ssh_cmd = subprocess.Popen(
        ["ssh", "pi@" + target_ip, command])
    ssh_cmd.wait()
    return ssh_cmd.poll()


# TODO - Set up sending authentication keys if first time connection.
# 1. Check if key exists in folder /Users/Nick/.ssh/id_rsa.pub
# 2. If not, execute 'ssh-keygen -t rsa -b 2048'
# 3. Then run 'ssh-copy-id pi@192.168.0.10'


def main():
    args = parse_args()
    if args.ip is not None:
        ip_list = [args.ip]
    elif args.range is not None:
        ip_list = ip_range(args.range[0], args.range[1])
    else:
        ip_list = ['127.0.0.1']
    try:
        test = test_connection(ip_list)
        #print(test)
        for ip_test in test:
            #print(ip_test)
            if ip_test[1] is True:
                ssh_connection(ip_test[0], args.cmd)
                #sys.exit("pi_connect quiting. goodbye")
                # successful_ping_tests = [x for x in test_connection if x[1] is True]  # Finds all True
    except KeyboardInterrupt:
        sys.exit("Keyboard Interrupt. Exiting...")


def parse_args():       # Command line arguments
    description = (
        'Command line interface for sending commands to Raspberry Pi over SSH\n'
        '------------------------------------------------------------'
        '--------------\n'
        'https://github.com/nickever/')

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-i", type=str, dest="ip", action="store", default=None,
                        help="ip address")
    parser.add_argument("-r", type=str, dest="range", action="store", default=None,
                        nargs=2, help="start and end ip address")
    parser.add_argument("-c", type=str, dest="cmd", action="store", default="",
                        help="commands to send over ssh")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="verbosity (-v, -vv, etc)")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))
    parser.add_argument("-b", "--bytes", dest="bytes", action="store_true", default=False,
                        help="readout in MBps "
                        "(default is Mbps)")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
