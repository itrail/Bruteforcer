from Bruteforcer import Bruteforcer
import argparse, math
import sys, json, os, re


class AsyncBruteforcer(Bruteforcer):
    def __init__(
        self,
        url,
        headers_file_raw,
        data_scheme_file_raw,
        credentials_file_raw,
        fail_url_pattern,
        proxies_file_raw,
        attemps_per_ip,
        processes,
    ) -> None:
        super().__init__(
            url,
            headers_file_raw,
            data_scheme_file_raw,
            credentials_file_raw,
            fail_url_pattern,
            proxies_file_raw,
            attemps_per_ip,
        )
        self.processes = processes

        self.credentials_list = self.split_file(self.credentials_list)
        print(self.credentials_list)
        self.proxies = self.split_file(self.proxies)
        print(self.proxies)
        self.perform_async_bruteforce()
        sys.exit()

    def split_file(self, data_list):
        lines_in_part = math.floor(len(data_list) / self.processes)
        data_for_processes = []
        for j in range(self.processes):
            if j + 1 == self.processes:
                temp_list = data_list
            else:
                temp_list = []
                for i in range(lines_in_part):
                    item = data_list.pop(0)
                    temp_list.append(item)
            data_for_processes.append(temp_list)
        return data_for_processes

    def perform_async_bruteforce(self):
        for process in range(self.processes):
            print(process)
            print(self.credentials_list[process])
            print(self.proxies[process])
        pass


parser = argparse.ArgumentParser()
from packages.utils import (
    collect_input_args,
    validate_input_args,
)

args = collect_input_args(parser)
validate_input_args(args)
bruteforce_tool = AsyncBruteforcer(
    args.url,
    args.headers,
    args.data_scheme,
    args.credentials_file,
    args.fail_url,
    args.proxies,
    args.attemps_per_ip,
    3,
)
bruteforce_tool.perform_async_bruteforce()
