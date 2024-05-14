import requests
from bs4 import BeautifulSoup
from check_proxies import *


class Athlete:
    def __init__(self):
        self.athlete_categories = ["agegroup=0"]
        self.gender_list = ["gender=1", "gender=2"]
        self.pool_length = ["course=LCM", "course=SCM"]
        self.url_prefix = "https://www.swimrankings.net/index.php"
        self.posnania_url = ("https://www.swimrankings.net/index.php?page=rankingDetail&clubId=65773"
                             "&gender=1&season=2024&course=LCM&stroke=0&agegroup=0")

    def get_url(self):
        with open("valid_proxies.txt", "r") as f:
            proxies = f.read().split("\n")
        my_dict = {}
        counter = 0
        posnania_club = self.posnania_url
        for i in self.gender_list:
            posnania_club = posnania_club.replace("gender=1", i)
            for j in self.pool_length:
                posnania_club = posnania_club.replace("course=LCM", j)
                links = Athlete.loader(posnania_club).select("td.swimstyle a")
                for link in links:
                    distance_link = self.url_prefix + link.get("href")
                    distance_text = link.text
                    if " x " not in distance_text and "Lap" not in distance_text:
                        print(distance_text)
                        print(distance_link)
                        my_dict.update(self.process_distance(distance_link, counter, proxies))
                        counter += 1

    def process_distance(self, distance_link, counter, proxies):
        print(f"using the proxy: {proxies[counter]}")
        my_dict = {}
        scraping_system = Athlete.proxy_loader(distance_link, counter, proxies)
        number = self.get_places(scraping_system)
        times = (number // 25) + 1
        xd = number
        tab = [min(xd, 25)] * (xd // 25)
        remainder = xd % 25
        xd -= min(xd, 25) * (xd // 25)
        print(times)
        if remainder:
            tab.append(remainder)
        for i in range(times):
            print(i)
            if i == 0:
                print(distance_link)
                my_dict.update(self.get_fullnames(distance_link))
            else:
                distance_link = distance_link.replace(f"firstPlace=1", f"firstPlace={(25 * times) + 1}")
                print(distance_link)
                my_dict.update(self.get_fullnames(distance_link))
        return my_dict

    def get_places(self, scraping_system):
        places = scraping_system.find_all("td", class_="navigation")
        place_text = places[9].text if len(places) > 9 else ""
        place_number = int(place_text.split()[-1]) if place_text else 0
        print(place_number)
        return place_number

    def get_fullnames(self, distance_link):
        my_dict = {}
        td_fullname = Athlete.loader(distance_link).find_all("td", class_="fullname")
        for i in td_fullname:
            if i:
                a_tags = i.find_all("a")
                for a_tag in a_tags:
                    href = a_tag.get('href')
                    inner_text = a_tag.text
                    if inner_text not in my_dict:
                        my_dict[inner_text] = self.url_prefix + href

        return my_dict





    @staticmethod
    def loader(url):
        response = requests.get(url)
        html = response.text
        html_document = BeautifulSoup(html, 'html.parser')
        return html_document

    @staticmethod
    def proxy_loader(url, counter, proxies):
        res = requests.get(url, proxies={"http": proxies[counter],
                                         "https": proxies[counter]})
        print(res.status_code)
        html = res.text
        html_document = BeautifulSoup(html, 'html.parser')
        return html_document


athlete = Athlete()
athlete.get_url()


