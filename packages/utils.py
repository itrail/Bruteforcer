import argparse


def collect_input_args(parser):
    parser.add_argument(
        "-M", "--mode", type=str, required=True
    )  # bruteforce (one account many passwords)/password_spraying (one password many logins)/credentials_stuffing (one account one password)
    parser.add_argument("-U", "--url", type=str, required=True)
    parser.add_argument(
        "-l",
        "--logins_list",
        type=str,
    )
    parser.add_argument(
        "-L",
        "--Login",
        type=str,
    )
    parser.add_argument("-p", "--passwords_list", type=str)
    parser.add_argument("-P", "--Password", type=str)
    parser.add_argument("--proxies", type=str)
    parser.add_argument("--attemps_per_ip", type=str)
    return parser.parse_args()


def validate_input_args(args):
    if args.mode not in (["BRUTEFORCE", "PASSWORD_SPRAYING", "CREDENTIAL_STUFFING"]):
        print("Uknown mode")
        sys.exit(-1)
    if not (args.Login or args.logins_list):
        print("Login input is empty")
        sys.exit(-1)
    if not (args.Password or args.passwords_list):
        print("Login input is empty")
        sys.exit(-1)
    if not args.proxies:
        print("Bruteforce will be perfomed with your IP")
    if not args.attemps_per_ip:
        print("Bruteforce will be perfomed in default mode 1 password per 1 one IP")
    for arg in vars(args):
        if getattr(args, arg):
            print(f"{arg}: {getattr(args, arg)}")
