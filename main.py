import sys

import bs4

from scrapper import Scrapper

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("You need to specify single path argument")
        exit(1)

    url = sys.argv[1]
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    scrapper = Scrapper(url)
    scrapper.get_destinations()
    scrapper.get_offers()
    scrapper.get_trips()




