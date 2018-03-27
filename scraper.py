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

def printb(str):
	print(bcolors.BOLD + str + bcolors.ENDC)

def getLoginInfo():
    global login
    if login['name'] == "":
        login['name'] = input("Enter your ETHZ-login: ")
    if login['password'] == "":
        login['password'] = getpass.getpass(
            "Enter the password for " + login['name'] + ": (hidden)\n")


def download(url, link, path):
    filename = os.path.basename(path)
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    if not os.path.isfile(path):
        with open(path, 'wb') as f:
            response = requests.get(
                url + link, stream=True, headers=headers, auth=(login['name'], login['password']))
            if not response.ok:
                if response.status_code == 401:
                    print(bcolors.FAIL + 'Authorization error' + bcolors.ENDC)
                    sys.exit(1)
                else:
                    print(bcolors.FAIL + 'Download error' + bcolors.ENDC)
                    sys.exit(1)

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
                            "\r %-40.40s [%s%s%s]" % (filename, bcolors.OKGREEN, progress, bcolors.ENDC))
                    else:
                        sys.stdout.write(
                            "\r %-40.40s [%s%s%s]" % (filename, bcolors.OKBLUE, progress, bcolors.ENDC))
                    sys.stdout.flush()
                print()
    else:
        if len(sys.argv) > 1 and sys.argv[1] == '-v':
            sys.stdout.write(
                " %-40.40s [%-22s%s%21s]\n" % (filename, bcolors.WARNING, 'Skipped', bcolors.ENDC))



def ana():
    printb('[1/4] Analysis')
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


def dc():
    printb('[2/4] Design of Digital Circuits')
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

    basedir = dirs[1]
    for link in links:
        path = basedir + '/' + link.split('media=')[-1]
        download(url, link, path)

    print('\n')


def aw():
    getLoginInfo()
    printb('[3/4] Algorithmen und Wahrscheinlichkeiten')
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


    basedir = dirs[3]
    for link in links:
        path = basedir + '/' + link.split('/', 2)[2]
        download(url, link, path)
    print('\n')


def pp():
    getLoginInfo()
    printb('[4/4] Parallel Programming')
    url = 'https://www.srl.inf.ethz.ch/'

    request = Request(url + 'pp2018.php', headers=headers)
    try:
        soup = BeautifulSoup(urllib.request.urlopen(request), 'html.parser')
    except urllib.error.URLError:
        input("No internet connection - connect to internet and try again.")
        sys.exit(0)

    lpart = 'Presentation Schedule'
    rpart = 'Exams and Grading'
    soup = str(soup).partition(lpart)[-1]
    soup = soup.rpartition(rpart)[0]
    soup = BeautifulSoup(soup, 'html.parser')

    links = []
    for link in soup.find_all('a'):
        link = link['href']
        links.append(link)

    basedir = dirs[2]
    for link in links:
        path = basedir + '/' + link.split('/', 2)[-1]
        download(url, link, path)
    print('\n')


ana()
dc()
aw()
pp()


print("All done. :)\n")
