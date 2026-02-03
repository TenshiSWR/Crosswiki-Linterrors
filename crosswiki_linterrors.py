from datetime import datetime
from dotenv import load_dotenv
from json import dumps, JSONDecodeError, loads
from os import getenv
import regex
import requests

load_dotenv()
USER_AGENT = loads(getenv("USER-AGENT"))
families_list = ["wikibooks", "wikipedia", "wikinews", "wikiquote", "wikisource", "wikiversity", "wikivoyage", "wiktionary"] + ["specials"]
lint_errors = {family:{} for family in families_list}
projects = {family:[] for family in families_list}
api_string = "/w/api.php?action=query&format=json&meta=linterstats"
timing = [datetime.utcnow()]

sitematrix = loads(requests.get("https://meta.wikimedia.org/w/api.php?action=sitematrix&format=json&formatversion=2", headers=USER_AGENT).text)["sitematrix"]
del sitematrix["count"]

for sites in sitematrix:
    if sites == "specials":
        sites = sitematrix[sites]
        for site in sites:
            if "private" in site.keys():
                continue
            else:
                projects["specials"].append([site["url"], "closed" in site.keys(), "fishbowl" in site.keys()])
    else:
        sites = sitematrix[sites]["site"]
        for site in sites:
            if site["code"] == "wiki":
                site["code"] = "wikipedia"
            projects[site["code"]].append([site["url"], "closed" in site.keys(), "fishbowl" in site.keys()])

print("Sitematrix:", datetime.utcnow()-timing[-1], datetime.utcnow())
timing.append(datetime.utcnow())

for name, family in projects.items():
    for project in family:
        if regex.search("(?:beta|test)", project[0]):
            continue
        try:
            r = requests.get(project[0]+api_string, headers=USER_AGENT, allow_redirects=False)
            if "warnings" in loads(r.text).keys():
                continue
            lint_errors[name][regex.search(r"https://([^\.]*).", project[0].replace("www.", "")).group(1)] = [loads(r.text), project[1], project[2]]
        except JSONDecodeError as exception:
            print(project, exception)
        except Exception as exception:
            print(project, exception)
    print(name + ":", datetime.utcnow() - timing[-1], datetime.utcnow())
    timing.append(datetime.utcnow())

print("Done.", datetime.utcnow())
file = None
try:
    file = open("data.json", "w+")
except FileNotFoundError:
    open("data.json", "x")
    file = open("data.json", "w+")
finally:
    file.write(dumps(lint_errors))
