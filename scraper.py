#!/usr/bin/env python3

# Scraper to download all exercises, solutions and slides from the courses of
# the 2nd semester in comp-sci, written in Python using BeautifulSoup.

# MIT license applies. See LICENSE file.
# Author: Patrick Wicki <patrick.wicki96@member.fsf.org>

import urllib.request
import urllib.parse
import os
import sys
import getpass
from urllib.request import Request
try:
    import requests
except:
    print('Missing requests library.')
    sys.exit(1)
try:
    from bs4 import BeautifulSoup
except:
    print('Missing BeautifulSoup library.')
    sys.exit(1)


user_agent = 'python-requests/2.7.0 CPython/3.5.1+ Linux/4.4.0-22-generic'
headers = {'User-Agent': user_agent}


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Generate directories if nonexistent
dirs = ["exercises/analysis", "exercises/dc",
        "exercises/pprog", "exercises/algowar"]

for i in dirs:
    if not os.path.isdir(i):
        print("Creating directory: ", i)
        os.makedirs(i)
print()

# Enter your defaults here. Else, user will be asked by getLoginInfo method
login = {'name': '', 'password': ''}


def getLoginInfo():
    global login
    if login['name'] == "":
        login['name'] = input("Enter your ETHZ-login: ")
    if login['password'] == "":
        login['password'] = getpass.getpass(
            "Enter the password for " + login['name'] + ": (hidden)")


def download(url, link, path):
    filename = os.path.basename(path)
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    if not os.path.isfile(path):
        with open(path, 'wb') as f:
            response = requests.get(
                url + link, stream=True, headers=headers, auth=(login['name'], login['password']))
            total_length = response.headers.get('content-length')
            if total_length is None:  # no content length header
                f.write(response.content)
                sys.stdout.write("\r -> Downloading: %-20s" % (filename))
                sys.stdout.flush()
            else:  # fancy progress bar, because why not
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    width = 40
                    done = int(width * dl / total_length)
                    progress = '=' * done + '>' + ' ' * (width-done)
                    if width - done == 0:
                        sys.stdout.write(
                            "\r   [%s%s%s] %s" % (bcolors.OKGREEN, progress, bcolors.ENDC, filename))
                    else:
                        sys.stdout.write(
                            "\r   [%s%s%s] %s" % (bcolors.OKBLUE, progress, bcolors.ENDC, filename))
                    sys.stdout.flush()
                print()


def ana():
    print('[1/4] Analysis')
    url = 'https://metaphor.ethz.ch/x/2018/fs/401-0212-16L/'
    request = Request(url, headers=headers)
    try:
        soup = BeautifulSoup(urllib.request.urlopen(request), 'html.parser')
    except urllib.error.URLError:
        input("No internet connection - connect to internet and try again.")
        sys.exit(0)

    lpart = '<table class="table table-bordered table-condensed table-striped">'
    rpart = 'Übungsgruppen'
    soup = str(soup).partition(lpart)[-1]
    soup = soup.rpartition(rpart)[0]
    soup = BeautifulSoup(soup, 'html.parser')

    links = []
    for link in soup.find_all('a'):
        link = link['href']
        links.append(link)

    basedir = dirs[0]
    for link in links:
        path = basedir + '/' + link.split('/', 1)[1]
        download(url, link, path)
    print('\n')


def aw():
    print('[2/4] Algorithmen und Wahrscheinlichkeiten')
    url = 'https://www.cadmo.ethz.ch/education/lectures/FS18/AW/'

    request = Request(url + 'index.html', headers=headers)
    try:
        soup = BeautifulSoup(urllib.request.urlopen(request), 'html.parser')
    except urllib.error.URLError:
        input("No internet connection - connect to internet and try again.")
        sys.exit(0)

    lpart = '<table cellpadding="3" cellspacing="0" style="width:100%">'
    rpart = 'Einschreibung in die Übungsstunden'
    soup = str(soup).partition(lpart)[-1]
    soup = soup.rpartition(rpart)[0]
    soup = BeautifulSoup(soup, 'html.parser')

    links = []
    for link in soup.find_all('a'):
        link = link['href']
        if not 'http' in link:
            links.append(link)

    getLoginInfo()

    basedir = dirs[3]
    for link in links:
        path = basedir + '/' + link.split('/', 2)[2]
        download(url, link, path)
    print('\n')


def pp():
    print('[3/4] Parallel Programming')
    url = 'https://www.srl.inf.ethz.ch/'

    request = Request(url + 'pp2018.php', headers=headers)
    try:
        soup = BeautifulSoup(urllib.request.urlopen(request), 'html.parser')
    except urllib.error.URLError:
        input("No internet connection - connect to internet and try again.")
        sys.exit(0)
    print('\n')

    lpart = 'Presentation Schedule'
    rpart = 'Exams and Grading'
    soup = str(soup).partition(lpart)[-1]
    soup = soup.rpartition(rpart)[0]
    soup = BeautifulSoup(soup, 'html.parser')

    links = []
    for link in soup.find_all('a'):
        link = link['href']
        links.append(link)

    getLoginInfo()
    basedir = dirs[2]
    for link in links:
        path = basedir + '/' + link.split('/', 2)[-1]
        download(url, link, path)
    print('\n')


def dc():
    print('[4/4] Design of Digital Circuits')
    url = 'https://safari.ethz.ch/'
    basedir = dirs[1]

    request = Request(
        url + 'digitaltechnik/spring2018/doku.php?id=labs', headers=headers)
    try:
        soup = BeautifulSoup(urllib.request.urlopen(request), 'html.parser')
    except urllib.error.URLError:
        input("No internet connection - connect to internet and try again.")
        sys.exit(0)

    lpart = '<div class="table sectionedit2">'
    rpart = 'Working with the FPGA Board'
    soup = str(soup).partition(lpart)[-1]
    soup = soup.rpartition(rpart)[0]
    soup = BeautifulSoup(soup, 'html.parser')

    links = []
    for link in soup.find_all('a'):
        link = link['href']
        links.append(link)

    getLoginInfo()
    basedir = dirs[1]
    for link in links:
        path = basedir + '/' + link.split('media=')[-1]
        download(url, link, path)

    print('\n')


ana()
aw()
pp()
dc()


print("All done. :)\n")
