import os
import re
import urllib
import urllib.error
import urllib.parse
from pprint import pprint

import unicodedata
from bs4 import BeautifulSoup
import requests
import datetime
from database import *
from time import time


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
def get_fleet_carrier(identifier: str, collection):
    flag = False
    # Check if the identifier is in the database
    db_name = find_value(collection, "id_lower", identifier.lower())
    if db_name:
        db_name = db_name[0]
        if time() - db_name["last_updated"] < 86400:  # Time passed < 24h
            # TODO: Add logging of from DB/from API, as well as name requested
            return f"Carrier {db_name['name']}.\n\
Owned by: {db_name['owner']}\n\
{f'Part of {db_name['owner_squadron']}\n' if db_name['owner_squadron'] is not None else 'Not in Squadron\n'}\
Last recorded location: {db_name['star_system']}\n\
Station Distance: {db_name['station_distance']}\n\
Docking Access: {db_name['docking_access']}\n\
Allow Notorious: {db_name['notorious']}\n\
Allegiance: {db_name['allegiance']}\n\
Carrier URL: {db_name['url']}"
        else:  # Time passed > 24h
            flag = True
    url = "https://inara.cz/elite/station/?search=" + identifier
    soup = get_soup(url)
    if not soup.title.string.startswith(identifier):
        return "No fleet carrier found with that identifier."
    else:
        name = [i.text for i in soup.find("div", class_="headercontent").find_all("a") if "/elite/station/" in i.get("href")][0]
        url_station = "https://inara.cz"+[i.get("href") for i in soup.find("div", class_="headercontent").find_all("a") if "/elite/station/" in i.get("href")][0]
        info = soup.find_all("div", class_="itempaircontainer")
        try:
            star_system = [i.find("a").text for i in info if "Star system" in i.text][0]
        except IndexError:
            star_system = "Unknown"
        try:
            station_distance = \
            [i.find("div", class_="itempairvalue").text for i in info if "Station distance" in i.text][0]
        except IndexError:
            station_distance = "Unknown"
        try:
            docking_access = [i.find("div", class_="itempairvalue").text for i in info if "Docking access" in i.text][0]
        except IndexError:
            docking_access = "Unknown"
        try:
            notorious = [i.find("div", class_="itempairvalue").text for i in info if "Allow notorious" in i.text][0]
        except IndexError:
            notorious = "Unknown"
        try:
            allegiance = [i.find("div", class_="itempairvalue").text for i in info if "Allegiance" in i.text][0]
        except IndexError:
            allegiance = "Unknown"
        try:
            owner = [i.text for i in [i for i in info if "Owner" in i.text][0].find_all("a") if
                     "/elite/cmdr/" in i.get("href")][0]
        except IndexError:
            owner = "Unknown"
        try:
            owner_squadron = [i.text for i in [i for i in info if "Owner" in i.text][0].find_all("a") if
                              "/elite/squadron/" in i.get("href")][0]
        except IndexError:
            owner_squadron = None
        info = {
            "name": name,
            "star_system": star_system,
            "station_distance": station_distance,
            "docking_access": docking_access,
            "notorious": notorious,
            "allegiance": allegiance,
            "owner": owner,
            "owner_squadron": owner_squadron,
            "url": url_station,
            "last_updated": time(),
            "id_lower": identifier.lower()
        }
        if not flag:
            insert_new_value(collection, info)
        else:
            update_value(collection, "id_lower", identifier.lower(), info)
        # TODO: Add logging of from DB/from API, as well as name requested
        output = f"Carrier {name}.\n\
Owned by: {owner}\n\
{f'Part of {owner_squadron}\n' if owner_squadron is not None else 'Not in Squadron\n'}\
Last recorded location: {star_system}\n\
Station Distance: {station_distance}\n\
Docking Access: {docking_access}\n\
Allow Notorious: {notorious}\n\
Allegiance: {allegiance}\n\
Carrier URL: {url_station}"
        return output


def short_fleet_carrier(identifier: str, collection):
    flag = False
    # Check if the identifier is in the database
    db_name = find_value(collection, "id_lower", identifier.lower())
    if db_name:
        db_name = db_name[0]
        if time() - db_name["last_updated"] < 86400:  # Time passed < 24h
            # TODO: Add logging of from DB/from API, as well as name requested
            return f"{db_name['name']}. Owned by: {db_name['owner']}"
        else:  # Time passed > 24h
            flag = True

    url = "https://inara.cz/elite/station/?search=" + identifier
    soup = get_soup(url)
    if not soup.title.string.startswith(identifier):
        return "No fleet carrier found with that identifier."
    else:
        name = [i.text for i in soup.find("div", class_="headercontent").find_all("a") if "/elite/station/" in i.get("href")][0]
        url_station = "https://inara.cz" + \
                      [i.get("href") for i in soup.find("div", class_="headercontent").find_all("a") if
                       "/elite/station/" in i.get("href")][0]
        info = soup.find_all("div", class_="itempaircontainer")
        print(identifier)
        pprint(info)
        try:
            star_system = [i.find("a").text for i in info if "Star system" in i.text][0]
        except IndexError:
            star_system = "Unknown"
        try:
            station_distance = [i.find("div", class_="itempairvalue").text for i in info if "Station distance" in i.text][0]
        except IndexError:
            station_distance = "Unknown"
        try:
            docking_access = [i.find("div", class_="itempairvalue").text for i in info if "Docking access" in i.text][0]
        except IndexError:
            docking_access = "Unknown"
        try:
            notorious = [i.find("div", class_="itempairvalue").text for i in info if "Allow notorious" in i.text][0]
        except IndexError:
            notorious = "Unknown"
        try:
            allegiance = [i.find("div", class_="itempairvalue").text for i in info if "Allegiance" in i.text][0]
        except IndexError:
            allegiance = "Unknown"
        try:
            owner = [i.text for i in [i for i in info if "Owner" in i.text][0].find_all("a") if "/elite/cmdr/" in i.get("href")][0]
        except IndexError:
            owner = "Unknown"
        try:
            owner_squadron = [i.text for i in [i for i in info if "Owner" in i.text][0].find_all("a") if
                              "/elite/squadron/" in i.get("href")][0]
        except IndexError:
            owner_squadron = None
        info = {
            "name": name,
            "star_system": star_system,
            "station_distance": station_distance,
            "docking_access": docking_access,
            "notorious": notorious,
            "allegiance": allegiance,
            "owner": owner,
            "owner_squadron": owner_squadron,
            "url": url_station,
            "last_updated": time(),
            "id_lower": identifier.lower()
        }
        if not flag:
            insert_new_value(collection, info)
        else:
            update_value(collection, "id_lower", identifier.lower(), info)
        # TODO: Add logging of from DB/from API, as well as name requested
        output = f"{name}. Owned by: {owner}"
        return output


# Get Fleet Carrier by name (ex. N.S.C. Chicky Nuggies)
# Example URL: https://inara.cz/elite/station/?search=N.S.C.%20Chicky%20Nuggies
def find_carrier_by_name(name: str, collection):
    url = "https://inara.cz/elite/station/?search=" + url_quote(name)
    soup = get_soup(url)
    try:
        if soup.find("div", class_="block1").find("div", class_="notice0").text == "No stations were found.":
            return "No fleet carrier found with that name."
    except:
        urls = soup.find("div", class_="mainblock").find_all("a")
        ids = []
        flag = soup.find("div", class_="mainblock").find("div", class_="listitem") is not None
        for i in urls:
            ids.append(i.find("span", class_="minor").text[1:-1])
        if len(ids) == 1:
            return f"Found fleet carrier with ID: {ids[0]}"
        else:
            fc_list = [short_fleet_carrier(i, collection) for i in ids]
            print(len(fc_list))
            if len(fc_list) > 30:
                fc_list = fc_list[:30]
                flag = True
            fc_list_str = "\n".join(fc_list)
            if flag:
                return f"Found multiple fleet carriers:\n{fc_list_str}\nAnd more..."
            else:
                return f"Found multiple fleet carriers:\n{fc_list_str}"


# Get Commander by Name using API or DB
def get_cmdr(name: str, app_name, api_key, cmdr_name, cmdr_id, collection):
    flag = False
    # Check if the name is in the database
    db_name = find_value(collection, "name_lower", name.lower())
    if db_name:
        db_name = db_name[0]
        if time() - db_name["last_updated"] < 86400:  # Time passed < 24h
            # TODO: Add logging of from DB/from API, as well as name requested
            return f"CMDR {name}.\n{f'Squadron {db_name['squadron']}\n' if db_name['squadron'] is not None else 'Not in Squadron\n'}Profile URL: {db_name['url']}"
        else:  # Time passed > 24h
            flag = True
    ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    send_json = {
        "header": {
            "appName": app_name,
            "appVersion": "0.0.1",
            "isBeingDeveloped": True,
            "APIkey": api_key,
            "commanderName": cmdr_name,
            "commanderFrontierID": cmdr_id
        },
        "events": [
            {
                "eventName": "getCommanderProfile",
                "eventTimestamp": ts,
                "eventData": {
                    "searchName": name
                }
            }
        ]
    }
    url = "https://inara.cz/inapi/v1/"
    r = requests.post(url, json=send_json)
    full_json = r.json()["events"][0]
    if full_json["eventStatus"] != 200:
        if full_json["eventStatus"] == 204:
            return f"Inara Doesn't have a profile for {name}."
        elif full_json["eventStatus"] == 202:
            pass
        else:
            return f"ERR {full_json['eventStatus']}: {full_json['eventStatusText']}"
    full_json = full_json["eventData"]
    url = full_json["inaraURL"]
    username = full_json["userName"]
    try:
        squadron = full_json["commanderSquadron"]["squadronName"]
    except KeyError:
        squadron = None
    try:
        other_names = full_json["otherNamesFound"]
    except KeyError:
        other_names = None
    data_json = {
        "username": username,
        "squadron": squadron,
        "url": url,
        "last_updated": time(),
        "name_lower": username.lower()
    }
    if not flag:
        insert_new_value(collection, data_json)
    else:
        if username == name:
            update_value(collection, "username", name, data_json)
        else:
            if find_value(collection, "username", username) is None:
                insert_new_value(collection, data_json)
            else:
                update_value(collection, "username", username, data_json)
    # TODO: Add logging of from DB/from API, as well as name requested
    output = f"CMDR {username}.\n{f'Squadron {squadron}\n' if squadron is not None else 'Not in Squadron\n'}{f'Other possible names: {' '.join(other_names)}\n' if other_names is not None else ''}Profile URL: {url}"
    return output
