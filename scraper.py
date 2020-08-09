import requests
from bs4 import BeautifulSoup
import re
import csv


# url_list = ["https://mariegohan.com/6841","https://mariegohan.com/5328"]
url_list = "https://mariegohan.com/6841"

csv_list = []
header = ['#タイトル', '画像URL', '人数', '材料']
csv_list.append(header)

html = requests.get(url_list)
soup = BeautifulSoup(html.content, "html.parser")
title_ingredients = soup.find(class_="ingredients")
body = []

# レシピ名
title_recipe = soup.find(class_="entry-title")
body.append(title_recipe.string)

# 画像
img = soup.section.img.get('data-src')
body.append(img)

# 人数
num_people_content = title_ingredients.previous_sibling.previous_sibling
num_people = re.search(r'(人数：.+)$', num_people_content.string)
body.append(num_people.group())

# 材料取得
contents_ingredients = title_ingredients.next_sibling.next_sibling.contents

tmp_ingredient = ''
for ingredient in contents_ingredients:
    if ingredient != '\n':
        tmp_ingredient += ingredient.string + '\n'

body.append(tmp_ingredient.rstrip())
csv_list.append(body)

# CSV出力
# print(csv_list)
with open('./output/recipe_scraped.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(csv_list)
