import argparse, os, sys, re


def collect_input_args(parser):
    parser.add_argument("-u", "--url", type=str, required=True)
    parser.add_argument("-d", "--data_scheme", type=str, required=True)
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


def unpack_variables_from_json(json_value, variable):
    if type(json_value) == str:
        json_value = os.path.expandvars(os.getenv(json_value, variable))
    elif type(json_value) == list:
        json_value[0] = os.path.expandvars(os.getenv(json_value[0], variable))
    return json_value


def do_sth(data_scheme, credentials_file):
    variables_to_injection = re.findall("\$\{[a-zA-Z]+}", data_scheme)
    credentials = []
    for line in credentials_file:
        fields_cnt = line.count(":") + 1
        print(
            f"Fields in credentials file: {fields_cnt}, Variables in your data to injection file: {len(variables_to_injection)}"
        )
        if fields_cnt > 0:
            if fields_cnt == len(variables_to_injection):
                credentials.append(
                    tuple(line.split(":")[i].rstrip() for i in range(fields_cnt))
                )
            elif fields_cnt > len(variables_to_injection):
                # warinng
                print(f"Biorę {len(variables_to_injection)} pierwsze z brzegu")
                credentials.append(
                    tuple(line.split(":")[i].rstrip() for i in range(fields_cnt))
                )
        else:
            print("Dopasuj liczbę danych wejściowych do liczby zmiennych w pliku txt")
            sys.exit(-1)
    return variables_to_injection, credentials
