import json
import requests as r
from bs4 import BeautifulSoup
from lxml import etree
import requests as r

from utils import generate_category_map, send_category

URL = "https://letscolor.uz/store/"

res = r.get(URL)

category = []

if res.status_code == 200:
    soup = BeautifulSoup(res.content, "html.parser")
    dom = etree.HTML(str(soup))
    # try:
    i = 1
    while True:
        title = dom.xpath(f"/html/body/div[5]/div/div/div/div[{i}]/div[1]/div[2]/a/h4/strong/text()")
        link = dom.xpath(f"/html/body/div[5]/div/div/div/div[{i}]/div[1]/div[2]/a/@href")
        image = dom.xpath(f"/html/body/div[5]/div/div/div/div[{i}]/div[1]/div[1]/a/img/@src")
        if len(title) == 0 or len(link) == 0:
            break

        if len(image) > 0:
            ca = generate_category_map(title[0], link[0], image[0])
        else:
            ca = generate_category_map(title[0], link[0])
        res = send_category(ca)
        data = json.loads(res.content)
        bparent_id = data["id"]

        res = r.get(ca["link"])
        bsoup = BeautifulSoup(res.content, "html.parser")
        bdom = etree.HTML(str(bsoup))

        j = 1
        while True:
            title = bdom.xpath(f"/html/body/div[5]/div[1]/div[{j}]/div/h4/a/text()")
            link = bdom.xpath(f"/html/body/div[5]/div[1]/div[{j}]/div/h4/a/@href")
            image = bdom.xpath(f"/html/body/div[5]/div[1]/div[{j}]/div/div/a/img/@src")
            if len(title) == 0 or len(link) == 0:
                break
            
            if len(image) > 0:
                cb = generate_category_map(title[0], link[0], image[0])
            else:
                cb = generate_category_map(title[0], link[0])
            res = send_category(cb, bparent_id)

            data = json.loads(res.content)
            mparent_id = data["id"]

            res = r.get(cb["link"])
            csoup = BeautifulSoup(res.content, "html.parser")
            cdom = etree.HTML(str(csoup))

            k = 1
            while True:
                title = cdom.xpath(f"/html/body/div[5]/div[1]/div[{k}]/div/h4/a/text()")
                link = cdom.xpath(f"/html/body/div[5]/div[1]/div[{k}]/div/h4/a/@href")
                image = bdom.xpath(f"/html/body/div[5]/div[1]/div[{k}]/div/div/a/img/@src")

                if len(title) == 0 or len(link) == 0:
                    break
                
                if len(image) > 0:
                    cc = generate_category_map(title[0], link[0], image[0])
                else:
                    cc = generate_category_map(title[0], link[0])
                res = send_category(cc, mparent_id)

                data = json.loads(res.content)

                k += 1
                cb["children"].append(cc)

            j += 1
            ca["children"].append(cb)

        category.append(ca)
        i += 1
    # except Exception as e:
    #     print(e)


import json
json.dump(category, open("category.json", "w"))