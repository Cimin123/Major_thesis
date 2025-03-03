import os
import time
import argparse
import threading
import queue
import requests as re

active_threads = os.cpu_count()
q = queue.Queue()
valid_proxies = []
URL = "https://ipinfo.io/json"

with open("Proxies/proxies_list.txt", "r") as f:
    proxies = f.read().split("\n")
    for p in proxies:
        q.put(p)


def check_proxies():
    global q
    while not q.empty():
        proxy = q.get()
        try:
            res = re.get(URL, proxies={"http": proxy, "https:": proxy}, headers={'User-agent': 'your bot 0.1'})
        except:
            continue

        print(f'Proxy {proxy} {res}')

        if res.status_code == 429:
            #time.sleep(int(res.headers["Retry-After"]))
            print(res.headers)

        elif res.status_code == 200:
            valid_proxies.append(proxy)
            #valid_proxies.append(proxy)
        # else:
        #     print(f'Proxy {proxy} is not working')


for _ in range(active_threads):
    threading.Thread(target=check_proxies).start()


print(valid_proxies)