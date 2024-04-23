import os
import re
import urllib
import urllib.error
import urllib.parse

import unicodedata
from bs4 import BeautifulSoup
import requests


# Prep functions
def find_all(needle: str, haystack: str):
    return [m.start() for m in re.finditer(needle, haystack)]


def url_quote(url):
    return urllib.parse.quote(url).replace("%3A", ":").replace("%3F", "?")


def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0] != "C").replace(' ', '-')


def empty_lines(text):
    text = os.linesep.join([a for a in text.splitlines() if a])
    text = text.replace('  ', '')
    return os.linesep.join([s for s in text.splitlines() if s])


def get_soup(url):
    r = requests.get(url)
    r.encoding = 'utf8'
    soup = BeautifulSoup(r.content, 'lxml')
    return soup


# Scraper funcs

# Get Fleet Carrier by identifier (ex. T9X-LQV)
# URL: https://inara.cz/elite/station/?search=T9X-LQV
def get_fleet_carrier(identifier: str):
    url = "https://inara.cz/elite/station/?search=" + identifier
    soup = get_soup(url)
    if not soup.title.string.startswith(identifier):
        return "No fleet carrier found with that identifier."
    else:
        name = [i.text for i in soup.find("div", class_="headercontent").find_all("a") if "/elite/station/" in i.get("href")][0]
        info = soup.find_all("div", class_="itempaircontainer")

        star_system = [i.find("a").text for i in info if "Star system" in i.text][0]
        station_distance = [i.find("div", class_="itempairvalue").text for i in info if "Station distance" in i.text][0]
        docking_access = [i.find("div", class_="itempairvalue").text for i in info if "Docking access" in i.text][0]
        notorious = [i.find("div", class_="itempairvalue").text for i in info if "Allow notorious" in i.text][0]
        allegiance = [i.find("div", class_="itempairvalue").text for i in info if "Allegiance" in i.text][0]
        owner = [i.text for i in [i for i in info if "Owner" in i.text][0].find_all("a") if "/elite/cmdr/" in i.get("href")][0]
        try:
            owner_squadron = [i.text for i in [i for i in info if "Owner" in i.text][0].find_all("a") if "/elite/squadron/" in i.get("href")][0]
        except IndexError:
            owner_squadron = "None"
        info = {
            "name": name,
            "star_system": star_system,
            "station_distance": station_distance,
            "docking_access": docking_access,
            "notorious": notorious,
            "allegiance": allegiance,
            "owner": owner,
            "owner_squadron": owner_squadron
        }
        return info
