import argparse, os, sys, re


def collect_input_args(parser):
    parser.add_argument("-U", "--url", type=str, required=True)
    parser.add_argument("-H", "--headers", type=str)
    parser.add_argument("-D", "--data_scheme", type=str, required=True)
    parser.add_argument("-C", "--credentials_file", type=str, required=True)
    parser.add_argument("-F", "--fail_url", type=str)
    parser.add_argument("--proxies", type=str)
    parser.add_argument("--attemps_per_ip", type=int)
    return parser.parse_args()


def validate_input_args(args):
    # if not (args.url):
    #     print("Empty target url of attack!")
    #     sys.exit(-1)
    # if not (args.credentials_file):
    #     print("Login input is empty!")
    #     sys.exit(-1)
    # if not args.data_scheme:
    #     print("Credentials data to POST form is empty!")
    #     sys.exit(-1)
    if not args.headers:
        args.headers = ""
    if not args.fail_url:
        args.fail_url = ""
    if not args.proxies:
        args.proxies = ""
        print("Bruteforce will be perfomed with your IP")
    if not args.attemps_per_ip or args.attemps_per_ip < 1:
        args.attemps_per_ip = 1
        print("Bruteforce will be perfomed in default mode 1 password per 1 one IP")
    for arg in vars(args):
        if getattr(args, arg):
            print(f"{str(arg).upper()}: {getattr(args, arg)}")
