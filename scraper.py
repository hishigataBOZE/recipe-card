import requests
from bs4 import BeautifulSoup
import re
import csv


load_url = "https://mariegohan.com/6841"
csv_list = []

html = requests.get(load_url)
soup = BeautifulSoup(html.content, "html.parser")

# レシピ名
title_recipe = soup.find(class_="entry-title")
csv_list.append(title_recipe.string)

# 準備
title_ingredients = soup.find(class_="ingredients")

# 人数
num_people_content = title_ingredients.previous_sibling.previous_sibling
num_people = re.search(r'(人数：.+)$', num_people_content.string)
csv_list.append(num_people.group())

# 材料取得
contents_ingredients = title_ingredients.next_sibling.next_sibling.contents

tmp_ingredient = ''
for ingredient in contents_ingredients:
    if ingredient != '\n':
        tmp_ingredient += ingredient.string + '\n'

csv_list.append(tmp_ingredient.rstrip())

# CSV出力
# print(csv)
with open('./output/recipe_scraped.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(csv_list)