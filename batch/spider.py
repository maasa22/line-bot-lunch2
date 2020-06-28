import json
import pandas as pd
import requests
import json
import config
import time

hit_per_page = 100

GURUNAVI_ACCESS_KEY = config.GURUNAVI_ACCESS_KEY
api = "https://api.gnavi.co.jp/RestSearchAPI/v3/?keyid={keyid}&latitude={latitude}&longitude={longitude}&range={range}&offset={offset}&hit_per_page={hit_per_page}"

# 例 https://api.gnavi.co.jp/RestSearchAPI/v3/?keyid=[keyid}]&latitude=35.688494&longitude=139.702167&range=1&offset=11
# data = json.load(open('test.json'))
# print(data)

url = api.format( \
    keyid=GURUNAVI_ACCESS_KEY, \
    latitude=35.688494, \
    longitude=139.702167, \
    range=1, \
    offset=1, \
    hit_per_page=hit_per_page, \
)
print("will get", str(hit_per_page), "restaurants info from num:", 1)
r = requests.get(url)
data = json.loads(r.text)
total_hit_count = data["total_hit_count"]
df = pd.DataFrame(data["rest"])

for i in range(1, int(total_hit_count/hit_per_page)+1):
    url = api.format( \
    keyid=GURUNAVI_ACCESS_KEY, \
    latitude=35.688494, \
    longitude=139.702167, \
    range=1, \
    offset=1+hit_per_page*i, \
    hit_per_page=hit_per_page
    )
    time.sleep(3)
    print("will get", str(hit_per_page), "restaurants info from num:", 1+hit_per_page*i)
    r = requests.get(url)
    data = json.loads(r.text)
    if not "error" in data:
        df2 = pd.DataFrame(data["rest"])
        df = pd.concat([df, df2])
df.to_csv("restaurants_neighboring.csv")
