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


# Enter your defaults here. Else, user will be asked by getLoginInfo method
login = {'name': '', 'password': ''}


# function to print str in bold format
def printb(str):
    print(bcolors.BOLD + str + bcolors.ENDC)

def getLoginInfo():
    global login
    if login['name'] == "":
        login['name'] = input("Enter your ETHZ-login: ")
    if login['password'] == "":
        login['password'] = getpass.getpass(
            "Enter the password for " + login['name'] + ": (hidden)\n")


# Function to download a file
def download(url, link, path):
    filename = os.path.basename(path)
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    if not os.path.isfile(path) or (len(sys.argv) > 1 and sys.argv[1] == '-r'):
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

# Downloads all files in a filtered part of a website, e.g. in a table
def downloadAll(name, basedir, url, url_ext, lpart, rpart):
    printb(name)
    request = Request(url + url_ext, headers=headers)
    try:
        soup = BeautifulSoup(urllib.request.urlopen(request), 'html.parser')
    except urllib.error.URLError:
        input("No internet connection - connect to internet and try again.")
        sys.exit(0)

    soup = str(soup).partition(lpart)[-1]
    soup = soup.rpartition(rpart)[0]
    soup = BeautifulSoup(soup, 'html.parser')

    links = []
    for link in soup.find_all('a'):
        print(link)
        if "href" not in str(link):
            continue
        print(link)
        link = link['href']
        links.append(link)

    print(links)

    for link in links:
        path = basedir + '/' + link.split('/', 1)[-1]
        download(url, link, path)
    print('\n')


# TODO: systems programming


def numcse():
    name = 'NumCSE'
    url = 'https://metaphor.ethz.ch/x/2018/hs/401-0663-00L/'
    lpart = '<div class="page-header" id="exercises">'
    rpart = 'Exercises are'
    basedir = 'numCSE'
    downloadAll(name, basedir, url, '', lpart, rpart)

def ti():
    name = 'Theoretische Informatik'
    url = 'http://www.ita.inf.ethz.ch/theoInf18/'
    lpart = '<table class="exercises">'
    rpart = 'Kontakt'
    basedir = 'ti'
    downloadAll(name, basedir, url, '', lpart, rpart)

def ana1():
    basedir = "analysis-1"
    url = 'https://metaphor.ethz.ch/x/2018/fs/401-0212-16L/'
    lpart = '<table class="table table-bordered table-condensed table-striped">'
    rpart = 'Übungsgruppen'
    downloadAll("Analysis I", basedir, url, '', lpart, rpart)

def ana2():
    basedir = "analysis-2"
    url = 'https://metaphor.ethz.ch/x/2018/hs/401-0213-16L/'
    lpart = '<h1>Übungsserien</h1>'
    rpart = '<h1>Übungsstunden</h1>'
    downloadAll("Analysis II", basedir, url, '', lpart, rpart)

def dc():
    name = 'Design of Digital Circuits'
    url = 'https://safari.ethz.ch/'
    url_ext = 'digitaltechnik/spring2018/doku.php?id=labs'
    basedir = "design_of_digital_circuits"
    lpart = '<div class="table sectionedit2">'
    rpart = 'Working with the FPGA Board'
    downloadAll(name, basedir, url, url_ext, lpart, rpart)

def aw():
    getLoginInfo()
    basedir = 'aw'
    name = 'Algorithmen und Wahrscheinlichkeiten'
    url = 'https://www.cadmo.ethz.ch/education/lectures/FS18/AW/'
    url_ext = 'index.html'
    lpart = '<table cellpadding="3" cellspacing="0" style="width:100%">'
    rpart = 'Einschreibung in die Übungsstunden'
    downloadAll(name, basedir, url, url_ext, lpart, rpart)

def pp():
    getLoginInfo()
    url = 'https://www.sri.inf.ethz.ch/'
    url_ext = 'pp2018.php'
    lpart = 'Presentation Schedule'
    rpart = 'Exams and Grading'
    basedir = 'pprog'
    name = "Parallel Computing"
    downloadAll(name, basedir, url, url_ext, lpart, rpart)


ana2()
numcse()
ti()


print("All done. ;)\n")
