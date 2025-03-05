import time
import random
import followAndLike
import detectUnFollow
import sys
import db_config
import urllib.request
import pymysql
from selenium import webdriver



raw_data_db = pymysql.connect(
    user = db_config.DB_USER_RAW_DATA,
    passwd = db_config.DB_PW,
    host = db_config.DB_HOST,
    db = db_config.DB_SCHEMA_RAW_DATA,
    charset = 'utf8'
)

cursor = raw_data_db.cursor(pymysql.cursors.DictCursor)

## Chrome의 경우 | 아까 받은 chromedriver의 위치를 지정해준다.
driver = webdriver.Chrome('C:\\Users\\GwangA\\Desktop\\dev\\web_crawling\\chromedriver_win32\\chromedriver84')

## 암묵적으로 웹 자원 로드를 위해 3초까지 기다려 준다.
driver.implicitly_wait(3)

## url에 접근한다.
driver.get('https://ko.wikipedia.org/wiki/%EA%B5%AD%EA%B0%80%EB%B3%84_%EA%B5%AD%EA%B0%80_%EC%BD%94%EB%93%9C_%EB%AA%A9%EB%A1%9D')

country_rows = driver.find_elements_by_xpath("//body//table/tbody/tr")

country_count = len(country_rows)
print("country count:%d"%(country_count))

cid = 0
for country in country_rows:

    tds = country.find_elements_by_tag_name('td')

    cid += 1
    country_name = ''
    country_2_alpha = ''
    country_3_alpha = ''
    image = ''

    i = 0
    for td in tds:
        i += 1
        if i == 1:
            country_name = td.text
            print(country_name)
            imgTag = '//body//table/tbody/tr//td/span/a/img['+str(cid)+']'
            image = td.find_element_by_xpath('.//span/a/img').get_attribute('src')
            splits = image.split('.')
            splits_size = len(splits)
            extention = splits[splits_size-1]
            print("확장자:%s"%(extention))
            print("image src:%s"%(image))
        elif i == 2:
            country_2_alpha = td.text
            print(country_2_alpha)
        elif i == 3:
            country_3_alpha = td.text
            print(country_3_alpha)

    urllib.request.urlretrieve(image, "C:\\Users\\GwangA\\Desktop\\all_alcohol\\country\\" + country_2_alpha + "." + extention)

    # inser DB
    sql = "INSERT INTO country (country_id, name, type, alpha2, alpha3, image, reg_date) VALUES (%s,%s,%s,%s,%s,%s,NOW())"
    param = (int(cid), country_name, int(1), country_2_alpha, country_3_alpha, image)
    cursor.execute(sql, param)
    raw_data_db.commit()






# ## 인스타그램 로그인
# ## ex) driver.find_element_by_name('_2hvTZ pexuQ zyHYP').send_keys('ddd')
# inputs = driver.find_elements_by_class_name("_2hvTZ")
# i = 0
# for input in inputs:
#     if i==0:
#         i = i + 1
#         input.send_keys('ordin20118@gmail.com')
#     else:
#         input.send_keys('rmfltm134%')
# ## 로그인 버튼 클릭
# driver.find_element_by_class_name('sqdOP.L3NKy.y3zKF').click()
# ## 잠시 쉬어줌
# time.sleep(3)













