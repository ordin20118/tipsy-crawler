import time
import random
from selenium import webdriver
import sys
import urllib.request
import pymysql

options = webdriver.ChromeOptions()
options.add_argument('headless')
#options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
# 혹은 options.add_argument("--disable-gpu")


## Chrome의 경우 | 아까 받은 chromedriver의 위치를 지정해준다.
driver = webdriver.Chrome('/Users/gwanga/git/tipsy-crawler/chromedriver', options=options)

## 암묵적으로 웹 자원 로드를 위해 3초까지 기다려 준다.
driver.implicitly_wait(3)

## url에 접근한다.
driver.get('http://www.kajawine.kr/shop/item.php?it_id=1219550509')


# 술 이름 가져오기 
names = driver.find_elements_by_class_name("good_tit1")

for name in names:
    print(name.text)

driver.quit()

# country_rows = driver.find_elements_by_xpath("//body//table/tbody/tr")

# country_count = len(country_rows)
# print("country count:%d"%(country_count))

# cid = 0
# for country in country_rows:

#     tds = country.find_elements_by_tag_name('td')

#     cid += 1
#     country_name = ''
#     country_2_alpha = ''
#     country_3_alpha = ''
#     image = ''

#     i = 0
#     for td in tds:
#         i += 1
#         if i == 1:
#             country_name = td.text
#             print(country_name)
#             imgTag = '//body//table/tbody/tr//td/span/a/img['+str(cid)+']'
#             image = td.find_element_by_xpath('.//span/a/img').get_attribute('src')
#             splits = image.split('.')
#             splits_size = len(splits)
#             extention = splits[splits_size-1]
#             print("확장자:%s"%(extention))
#             print("image src:%s"%(image))
#         elif i == 2:
#             country_2_alpha = td.text
#             print(country_2_alpha)
#         elif i == 3:
#             country_3_alpha = td.text
#             print(country_3_alpha)

#     urllib.request.urlretrieve(image, "C:\\Users\\GwangA\\Desktop\\all_alcohol\\country\\" + country_2_alpha + "." + extention)














