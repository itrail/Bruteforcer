import json, sys, math, os
import logging
from packages.logger import Logger
import urllib.parse, urllib.request

logger = logging.getLogger("utils")  # config


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


def create_logger(level):
    LOGFILE = "log/app.log"
    LOGFILE_COUNT = 7
    LOGGING_FILE = (
        True if os.getenv("LOGGING_FILE", "false").lower() == "true" else False
    )
    LOGGING_STD = True if os.getenv("LOGGING_STD", "true").lower() == "true" else False
    LOGGING_LEVEL = logging.DEBUG if level > 0 else logging.INFO
    logger = (
        Logger()
        .Init(
            loggerType="std",
            loggerInit=LOGGING_STD,
            level=LOGGING_LEVEL,
            formatterName="formater",
        )
        .Init(
            loggerType="file",
            loggerInit=LOGGING_FILE,
            logFile=LOGFILE,
            logFileCount=LOGFILE_COUNT,
        )
        .Get()
    )
    return logger


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
    keyboard_input = input(
        "Would You like to continue bruteforce without proxy? Y or N?"
    )
    if keyboard_input.lower() in ["y", "yes", "yeah", ""]:
        logger.warn("I'll continue with your IP")
        return True
    return False


def parse_url(url):
    parse_url = urllib.parse.urlparse(url)
    host = "{uri.scheme}://{uri.netloc}/".format(uri=parse_url)
    logger.debug(f"Host `{host}` availability check started")
    with urllib.request.urlopen(host) as response:
        if response.code in [200, 201]:
            logger.debug(f"Host `{host}` availability check finished correctly")
            return host
        else:
            logger.error(f"Host `{host}` availability check failed")


def split_file_for_processes(input_file_raw, processes):
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
        keyboard_input = input(
            "Would you like to attack with POST data without your headers? Y or N?"
        )
        if keyboard_input.lower() in ["y", "yes", "yeah", ""]:
            return True
        return False

    headers = {}
    try:
        with open(headers_file_raw) as headers_file:
            if ".json" in headers_file_raw:
                headers = json.load(headers_file)
                return headers
            else:
                headers_list_raw = list(headers_file.readlines())
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
    else:
        headers_list_raw_len = len(headers_list_raw)
        current_separator = None
        for separator in [": ", ",", ";", "; "]:  # to config
            if (
                len([header for header in headers_list_raw if separator in header])
                == headers_list_raw_len
            ):
                current_separator = separator
                break
        if not current_separator or headers_list_raw_len == 0:
            logger.warning(
                f"Unknown separator in `{headers_file_raw}` or file is empty! Please give me correct headers file"
            )
            if not ask_for_continue():
                logger.info("Bye!")
                sys.exit(-1)
            return
        for header in headers_list_raw:
            header = str(header).replace('"', "").replace("'", "")
            headers[header.split(current_separator)[0]] = header.split(
                current_separator
            )[1].strip()
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


def set_proxies(proxies_file_raw, attemps_per_ip, len_credentials_list):
    try:
        with open(proxies_file_raw) as proxies_file:
            proxies = [line.rstrip() for line in proxies_file if line.strip()]
            if not proxies:
                raise ValueError(f"{proxies_file_raw} is empty")
    except FileNotFoundError as e:
        logger.warning(f"Exception in proxies file `{proxies_file_raw}`: `{e}`")
        if not ask_for_continue_without_proxy():
            logger.info("Bye!")
            sys.exit(0)
        return
    except ValueError as e:
        logger.warning(f"Exception: `{e}`")
    else:
        if attemps_per_ip * len(proxies) < len_credentials_list:
            logger.warning(
                f"There is too much credentials to check for (`{len_credentials_list}`) for `{attemps_per_ip}` trials per `{len(proxies)}` IP addresses. Rest of the attemps will be performed with last IP in list: `{proxies[len(proxies)-1]}`"
            )
            while attemps_per_ip * len(proxies) < len_credentials_list:
                proxies.insert(len(proxies), proxies[len(proxies) - 1])
