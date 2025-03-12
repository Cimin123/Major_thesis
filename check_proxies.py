import os
import time
import argparse
import threading
import queue
import random
import requests


def load_proxies(file_path, low_thresh=None, high_thresh=None):
    with open(file_path, "r") as f:
        proxies = f.read().splitlines()

    # Filter
    if low_thresh is not None or high_thresh is not None:
        proxies = proxies[low_thresh or 0:high_thresh or len(proxies)]

    return proxies


def save_list(valid_proxies_list, file="valid_proxies.txt"):
    with open(file, 'a') as f:
        for line in valid_proxies_list:
            f.write(f"{line}\n")


def random_delay(min_delay=3, max_delay=15):
    delay = random.uniform(min_delay, max_delay)  # Generate random float between min and max
    time.sleep(delay)


def check_proxies():
    global q
    while not q.empty():
        proxy = q.get()

        header_agent = {"User-Agent": random.choice(user_agents)}
        proxy_dict = {"http": proxy, "https": proxy, "socks4": proxy}

        try:
            res = requests.get(URL, proxies=proxy_dict, headers=header_agent, timeout=10, verify=False)

        except Exception as e:
            #print(f" {e}\n")
            continue

        # if res.status_code == 429:
        #     print(res.headers)

        if res.status_code == 200:
            print(proxy)
            valid_proxies.append(proxy)

        q.task_done()
        random_delay()

proxies_file = "Proxies/proxies_list_2.txt"
URL = "https://scholar.google.com/"

active_threads = os.cpu_count()
active_threads = 10

q = queue.Queue()
valid_proxies = []
threads = []
proxy_start = 0
proxy_limit = 150
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.2420.81",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0"
]

proxies = load_proxies(proxies_file, proxy_start, proxy_limit)
for p in proxies:
    q.put(p)

for _ in range(active_threads):
    #t = threading.Thread(target=check_proxies).start()
    t = threading.Thread(target=check_proxies)
    threads.append(t)
    t.start()

# Wait for threads to finish
[t.join() for t in threads]

# Save valid proxies
print("Saving the file with valid proxies")
save_list(valid_proxies)


