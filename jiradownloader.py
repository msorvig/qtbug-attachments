import json
from urllib.request import urlopen, urlretrieve
import codecs
import os
import urllib
import concurrent.futures
import sys

# http://stackoverflow.com/questions/21028979/
# recursive-iteration-through-nested-json-for-specific-key-in-python
def key_generator(obj, key):
      for k, v in obj.items():
            if k == key:
                 yield v
            elif isinstance(v, dict):
                 for id_val in key_generator(v, key):
                       yield id_val

def attachment_generator(bug):
    for attachments in key_generator(bug, "attachment"):
        for attachment in attachments:
            for content in key_generator(attachment, "content"):
                yield content


def download_qtbug(i):
    QTBUG = "QTBUG-" + str(i)
    if os.path.exists(QTBUG):
        return
    print("Getting " + QTBUG)

    try:
        response = urlopen("https://bugreports.qt.io/rest/api/2/issue/" + QTBUG)
    except urllib.error.HTTPError as err:
        print("Error: " + str(err.code))
        return

    reader = codecs.getreader("utf-8")
    bug = json.load(reader(response))
    os.makedirs(QTBUG)
    for attachment in attachment_generator(bug):
        print(QTBUG + " " + attachment)
        filename = attachment.split("/")[-1]
        urlretrieve(attachment, QTBUG + "/" + filename)

# get bug ID range: begin, end
if len(sys.argv) == 2:
    # expect "QTBUG-XXXXX"
    begin = int(sys.argv[1][6:])
    end = begin + 1
else:
    # expect "begin length"
    begin = int(sys.argv[1])
    end = begin + int(sys.argv[2])

with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    { executor.submit(download_qtbug, i) : i for i in range(begin, end) }
