import requests
import math
import sys
import os
import json
from bs4 import BeautifulSoup as soup

def printHelp():
    print("vyturys-dumper")
    print(" https://github.com/SSStormy/vyturys-dumper")
    print(" usage: python vydump.py BEARER ID_START ID_END")
    print(" example: python vydump.py abcd_my_bearer 0 1200")
    print("          will dump all books accessible in the range [0;1200)")

if len(sys.argv) < 4:
    printHelp()
    sys.exit(0)

bearer = str.format("Bearer {0}", sys.argv[1])
idStart = int(sys.argv[2])
idEnd = int(sys.argv[3])

def getContent(id):

    url = str.format("http://skaitykle.vyturys.lt/api/books/{0}/chapters.json", id)
    r = requests.get(url, headers= {"Authorization" : bearer})

    return r.json()

def getMetadata(id):
    url = str.format("http://skaitykle.vyturys.lt/api/books/{0}/metadata.json", id)
    r = requests.get(url, headers= {"Authorization" : bearer})

    return r.json()

def progressBar(current, maxVal, width, status):
    eqInterval = math.ceil(maxVal/width)
    numEq = int(math.ceil(current/eqInterval))
    numSpace = width-numEq
    percentage = int(math.ceil((current*100)/maxVal))

    sys.stdout.write('\r')

    sys.stdout.write("[")
    sys.stdout.write("=" * numEq)
    sys.stdout.write(" " * numSpace)
    sys.stdout.write("] ")

    sys.stdout.write(str.format("{0}% {1}/{2} {3}", percentage, current+1, maxVal, status))

    sys.stdout.flush()

def serialize(id, metadata, content):
    if metadata is None or content is None:
        return

    if "books" not in content or "author" not in metadata or "title" not in metadata or metadata["author"] is None or "full_name" not in metadata["author"]:
        return

    author = metadata["author"]["full_name"]
    title = metadata["title"]

    os.makedirs(author, exist_ok=True)

    with open(str.format("{0}/{1}", author, title), "w") as f:
        f.write(str.format("{0} - {1} (id={2})\n\n", author, title,id))

        for chapter in content["books"]:
            if chapter is None: continue

            raw = soup(chapter, "lxml")
            f.write(raw.get_text())
            f.write("\n\n\n\n")

def isNotFound(metadata):
    if "status" in metadata:
        return metadata["status"] == "404"
    return False

def isBadAuth(metadata):
    return "errors" in metadata

def processId(id):
    metadata = getMetadata(id)

    if isBadAuth(metadata):
        return False

    if isNotFound(metadata):
        return True

    serialize(id, metadata, getContent(id))
    return True

for i in range(idStart, idEnd):
    progressBar(i - idStart, idEnd - idStart, 50, str.format("dumpin' id {0}", i))

    status = processId(i)
    if not status:
        print("Bad auth.")
        break
