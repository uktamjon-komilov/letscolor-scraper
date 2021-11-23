import json
import os

import requests
from lxml import etree
from bs4 import BeautifulSoup

from utils import download, get_content, get_product_detail, localize_photo, send_product

file = open("category.json", "r")
categories = json.load(file)

pages = []

for category in categories:
    for mid_category in category["children"]:
        if len(mid_category["children"]) == 0:
            pages.append(mid_category["link"])
        else:
            for small_category in mid_category["children"]:
                pages.append(small_category["link"])

start = 59
end = 60

print(pages)
print(len(pages))

pages = pages[start:end]

products = []

for page in pages:
    content = get_content(page)
    soup = BeautifulSoup(content, "html.parser")
    dom = etree.HTML(str(soup))

    i = 1
    error_try = 0
    while True:
        link = dom.xpath(f"/html/body/div[5]/div[1]/div/div[3]/div[{i}]/div/div[2]/p/a/@href")
        if len(link) == 0 and error_try < 6:
            error_try += 1
            i += 1
            continue
        elif error_try == 6:
            break
        else:
            link = "https://letscolor.uz{}".format(link[0])
        
        print(link)
        
        product = get_product_detail(link)
        product = localize_photo(product)
        send_product(product)

        print(product)
        products.append(product)
        i += 1


json.dump(products, open(f"products{start}{end}.json", "w"))