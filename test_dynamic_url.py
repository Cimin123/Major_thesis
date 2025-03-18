import requests

BASE_URL = "https://scholar.google.com/scholar"

max_pages = 10

proxy_list = [
"socks4://174.64.199.82:4145",
    "http://130.36.36.29:443",
    "socks4://198.8.94.174:39078",
    "http://45.22.209.157:8888",
    "socks4://51.75.202.177:8493",
    "socks4://179.1.110.87:5678",
    "socks4://152.53.36.109:45894",
    "socks4://68.71.254.6:4145",
    "http://102.176.228.219:8080",
    "socks4://199.229.254.129:4145",
    "socks4://192.111.139.165:4145",
    "http://130.36.36.29:443",
    "socks4://174.64.199.82:4145",
    "socks4://51.75.202.177:8493",
    "socks4://68.71.254.6:4145",
    "socks4://199.229.254.129:4145",
    "socks4://192.111.139.165:4145",
    "http://47.252.11.233:8080",
    "http://124.217.107.60:8082",
    "http://8.219.229.53:13",
    "http://45.140.143.77:18080",
    "http://188.132.150.162:8080",
    "http://115.74.6.170:10004",
    "http://115.74.3.99:10001",
    "http://103.156.248.173:3128",
    "http://103.46.11.190:3000",
    "http://47.250.159.65:8002",
    "http://54.37.214.253:8080",
    "http://88.99.171.90:7003",
    "socks4://41.223.234.116:37259",
    "socks4://98.178.72.21:10919",
    "socks4://39.104.23.154:8443",
    "socks4://184.178.172.11:4145",
    "socks4://8.213.134.213:8080",
    "socks4://181.115.75.102:5678",
    "socks4://47.91.89.3:9080",
    "socks4://82.223.151.8:53347",
    "socks4://47.122.31.59:8080",
    "socks4://39.102.208.23:9080",
    "socks4://192.252.220.89:4145",
    "socks4://142.54.231.38:4145",
    "socks4://192.111.135.18:18301",
    "socks4://192.111.137.37:18762",
    "socks4://142.54.232.6:4145",
    "socks4://8.211.42.167:3128",
    "socks4://177.136.124.36:3629",
    "socks4://170.78.211.161:1080",
    "socks4://106.14.91.83:8443",
    "socks4://8.212.165.164:3128",
    "socks4://104.37.135.145:4145",
    "socks4://8.130.39.117:8090",
    "socks4://106.14.104.220:8081",
    "socks4://192.252.220.92:17328",
    "socks4://104.238.100.115:45314",
    "socks4://185.43.249.148:39316",
    "socks4://174.77.111.198:49547",
    "socks4://72.195.34.58:4145",
    "socks4://199.58.185.9:4145",
    "socks4://107.181.168.145:4145",
    "socks4://142.54.235.9:4145"
]

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