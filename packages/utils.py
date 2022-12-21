import json
import sys
import math
import logging
from urllib import parse, request
from packages.config import separators

logger = logging.getLogger("utils")


def collect_input_args(parser):
    parser.add_argument("-v", "--verbose", action="count", dest="verbose", default=0)
    parser.add_argument("-U", "--url", type=str, required=True)
    parser.add_argument("-H", "--headers", type=str)
    parser.add_argument("-D", "--data_scheme", type=str, required=True)
    parser.add_argument("-C", "--credentials_file", type=str, required=True)
    parser.add_argument("-F", "--fail_url", type=str)
    parser.add_argument("--proxies", type=str)
    parser.add_argument("--attemps_per_ip", type=int)
    parser.add_argument("-P", "--processes", type=int, default=1)
    return parser.parse_args()


def validate_input_args(args):
    # if not (args.url):
    #     logger.error("Empty target url of attack!")
    #     sys.exit(-1)
    # if not (args.credentials_file):
    #     logger.error("Login input is empty!")
    #     sys.exit(-1)
    # if not args.data_scheme:
    #     logger.error("Credentials data to POST form is empty!")
    #     sys.exit(-1)
    if args.processes <= 0:
        args.processes = 1
    if not args.headers:
        args.headers = ""
    if not args.fail_url:
        args.fail_url = ""
    if not args.proxies:
        args.proxies = ""
        logger.warning("Bruteforce will be perfomed with your IP")
    if not args.attemps_per_ip or args.attemps_per_ip < 1:
        args.attemps_per_ip = 1
        logger.warning(
            "Bruteforce will be perfomed in default mode 1 password per 1 one IP"
        )
    for arg in vars(args):
        if getattr(args, arg):
            logger.info(f"{str(arg).upper()}: {getattr(args, arg)}")


def __is_file_empty__(input_file, file_name):
    if not input_file:
        logger.info(f"File: `{file_name}` is empty! Adios!")
        return True
    return False


def ask_for_continue_without_proxy():
    logger.warning("Would You like to continue bruteforce without proxy? Y or N?")
    keyboard_input = input()
    if keyboard_input.lower() in ["y", "yes", "yeah", ""]:
        logger.warn("I'll continue with your IP")
        return True
    return False


def parse_url(url):
    parse_url = parse.urlparse(url)
    host = "{uri.scheme}://{uri.netloc}/".format(uri=parse_url)
    logger.debug(f"Host `{host}` availability check started")
    with request.urlopen(host) as response:
        if response.code in [200, 201]:
            logger.debug(f"Host `{host}` availability check finished correctly")
            return host
        else:
            logger.error(f"Host `{host}` availability check failed")
            return None


def open_file_as_list(input_file_raw):
    with open(input_file_raw) as input_file:
        logger.debug(f"File `{input_file_raw}` opened")
        input_as_a_list = input_file.readlines()
        if __is_file_empty__(input_as_a_list, input_file_raw):
            sys.exit(-1)
        return input_as_a_list


def find_separator(input_list, input_file_raw):
    current_separator = ""
    len_input_list = len(input_list)
    for separator in separators:
        if len([item for item in input_list if separator in item]) == len_input_list:
            current_separator = separator
            break
    if current_separator:
        logger.debug(
            f"Separator `{current_separator}` found in `{input_file_raw}` file"
        )
    return current_separator
    # if not input_file_raw:
    #     sys.exit(-1)
    # TU JEST KALSA
    # input_list = __open_file_as_list(input_file_raw)
    # current_separator = __find_separator(input_list, input_file_raw)


def split_file_for_processes(input_list, processes):
    if processes > 1:
        if len(input_list) < processes:
            data_for_processes = [input_list] * processes
            logger.warning(
                f"You have selected more workers (`{processes}`) than data to attack `{len(input_list)}`! Each process will get all the data to check"
            )
        else:
            lines_in_part = math.floor(len(input_list) / processes)
            data_for_processes = []
            for j in range(processes):
                # reszta dla ostatniego procesu
                if j + 1 == processes:
                    temp_list = input_list
                else:
                    temp_list = []
                    for _ in range(lines_in_part):
                        item = input_list.pop(0)
                        temp_list.append(item)
                data_for_processes.append(temp_list)
        return data_for_processes
    else:
        return [input_list]


def split_file_for_processes2(input_file_raw, processes):
    # if not input_file_raw:
    #     sys.exit(-1)
    with open(input_file_raw) as input_file:
        input_list = input_file.readlines()
        if __is_file_empty__(input_list, input_file_raw):
            sys.exit(-1)
    if processes > 1:
        if len(input_list) <= processes:
            data_for_processes = [input_list] * processes
            logger.warning(
                f"You have selected more workers (`{processes}`) than data to attack `{len(input_list)}`! Each process will get all the data to check"
            )
        else:
            lines_in_part = math.floor(len(input_list) / processes)
            data_for_processes = []
            for j in range(processes):
                # reszta dla ostatniego procesu
                if j + 1 == processes:
                    temp_list = input_list
                else:
                    temp_list = []
                    for i in range(lines_in_part):
                        item = input_list.pop(0)
                        temp_list.append(item)
                data_for_processes.append(temp_list)
        return data_for_processes
    else:
        return [input_list]


def parse_headers(headers_file_raw):
    def ask_for_continue():
        logger.warning(
            "Would you like to attack with POST data without your headers? Y or N?"
        )
        keyboard_input = input()
        if keyboard_input.lower() in ["y", "yes", "yeah", ""]:
            return True
        return False

    def parse_text_headers(headers_list_raw, headers_file_raw):
        headers = {}
        current_separator = find_separator(headers_list_raw, headers_file_raw)
        if not current_separator and not ask_for_continue():
            logger.warning(
                f"Unknown separator in `{headers_file_raw}`! Please give me correct credentials file"
            )
            logger.info("Bye!")
            sys.exit(-1)
        for header in headers_list_raw:
            header = str(header).replace('"', "").replace("'", "")
            headers[header.split(current_separator)[0]] = header.split(
                current_separator
            )[1].strip()
        return headers

    headers = {}
    try:
        with open(headers_file_raw) as headers_file:
            if ".json" in headers_file_raw:
                headers = json.load(headers_file)
            else:
                headers_list_raw = list(headers_file.readlines())
                headers = parse_text_headers(headers_list_raw, headers_file_raw)
    except json.decoder.JSONDecodeError as e:
        logger.error(f"Error in headers file `{headers_file_raw}`: `{e}`")
        if not ask_for_continue():
            logger.info("Bye!")
            sys.exit(-1)
    except FileNotFoundError as e:
        logger.error(f"Exception in headers file `{headers_file_raw}`: `{e}`")
        if not ask_for_continue():
            logger.info("Bye!")
            sys.exit(-1)
    return headers


def parse_data_scheme(data_scheme_file_raw):
    data_scheme = None
    with open(data_scheme_file_raw, "r") as data_scheme_file:
        data_scheme = data_scheme_file.read().rstrip()
        if __is_file_empty__(data_scheme, data_scheme_file_raw):
            sys.exit(-1)
    return data_scheme


def open_credentials_file(credentials_file_raw):
    credentials_list = []
    with open(credentials_file_raw) as credentials_file:
        credentials_list = credentials_file.readlines()
        if __is_file_empty__(credentials_list, credentials_file_raw):
            sys.exit(-1)
    return credentials_list
