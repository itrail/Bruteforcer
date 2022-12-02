import argparse, os, sys


def collect_input_args(parser):
    parser.add_argument("-u", "--url", type=str, required=True)
    parser.add_argument("-f", "--format", type=str, required=True)
    parser.add_argument("-s", "--form_scheme", type=str, required=True)
    parser.add_argument("-c", "--credentials_file", type=str)
    parser.add_argument("--proxies", type=str)
    parser.add_argument("--attemps_per_ip", type=int)
    return parser.parse_args()


def validate_input_args(args):
    if not (args.credentials_file):
        print("Login input is empty")
        sys.exit(-1)
    if not args.proxies:
        print("Bruteforce will be perfomed with your IP")
    if not args.attemps_per_ip:
        print("Bruteforce will be perfomed in default mode 1 password per 1 one IP")
    for arg in vars(args):
        if getattr(args, arg):
            print(f"{arg}: {getattr(args, arg)}")
    if args.format == "json":
        return 1


def unpack_variables_from_json(json_value, variable):
    if type(json_value) == str:
        json_value = os.path.expandvars(os.getenv(json_value, variable))
    elif type(json_value) == list:
        json_value[0] = os.path.expandvars(os.getenv(json_value[0], variable))
    return json_value
