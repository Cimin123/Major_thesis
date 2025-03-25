import requests

def load_proxies(file_path, low_thresh=None, high_thresh=None):
    with open(file_path, "r") as f:
        proxies = f.read().splitlines()

    # Filter
    if low_thresh is not None or high_thresh is not None:
        proxies = proxies[low_thresh or 0:high_thresh or len(proxies)]

    return proxies

BASE_URL = "https://scholar.google.com/scholar"

max_pages = 10
val_proxies = "valid_proxies.txt"

proxy_list = load_proxies(val_proxies)

header = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
header_agent = {"User-Agent": header}
query = "Radiologia"

page = 2
articles_per_page = 10
start = page * articles_per_page  # Each Scholar page contains 10 results
params = {"as_vs": 1, "hl": "pl", "q": query, "as_sdt": "0%2C5", "start": start}
full_url = requests.Request("GET", BASE_URL, params=params).prepare().url
print(f'{full_url}')

for proxy_address in proxy_list:
    proxy = {"http": proxy_address, "https": proxy_address}

    # Send the request
    try:
        response = requests.get(BASE_URL,
                                headers=header_agent,
                                params=params,
                                proxies=proxy,
                                timeout=10)

        print(f"Response Status Code: {response.status_code}")
    except Exception as e:
        print(f'Proxy {proxy} failed with error {e}')
        continue


# Desired output
"https://scholar.google.com/scholar?hl=pl&as_sdt=0%2C5&q=Radiologia&btnG="
"https://scholar.google.com/scholar?q=Radiologia&start=0"