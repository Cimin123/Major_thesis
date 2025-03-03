import requests
from requests.exceptions import ProxyError, ReadTimeout, ConnectTimeout

scheme_proxy_map = {
    'http': PROXY1,
    'https': PROXY2,
    'https://example.org': PROXY3,
}

URL = "https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=medical+research&btnG=&oq=med"
try:
    response = requests.get(URL, proxies=scheme_proxy_map, timeout=TIMEOUT_IN_SECONDS)
except (ProxyError, ReadTimeout, ConnectTimeout) as error:
        print('Unable to connect to the proxy: ', error)
else:
    print(response.text)
