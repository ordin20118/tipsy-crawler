import time
import random
import sys
import urllib.request
import pymysql
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys



#####################a#####################################################################
#
# target site: www.whisky.com
# ex: https://www.whisky.com/whisky-database/bottle-search/whisky.html(whisky list)
# ex: https://www.whisky.com/whisky-database/bottle-search/gin.html(gin list)
#
##########################################################################################

def set_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('headless')
    #chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument("disable-gpu")
    # 혹은 options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver



## Chrome의 경우 chromedriver의 위치를 지정해준다.
## => 셀리니움 4버전 부터는 시스템에 설치된 크롬드라이버를 사용해야함.
driver = set_chrome_driver()

## 암묵적으로 웹 자원 로드를 위해 3초까지 기다려 준다.
driver.implicitly_wait(3)

## url에 접근한다.
driver.get('https://www.whisky.com/whisky-database/bottle-search/whisky.html')


# 해당 카테고리의 페이지 리스트를 조회하여 몇페이지까지 데이터가 있는지 확인
# Full Xpath: /html/body/ul[1]
# page_list_ul = driver.find_elements(by=By.CLASS_NAME, value="datamints-infinite-scroll-pagination")
# print(page_list_ul)

page_list_ul = driver.find_elements(by=By.XPATH, value="/html/body/ul[1]")
page_list = driver.find_elements(by=By.XPATH, value="/html/body/ul[1]/li")
print(len(page_list))

cookie_accept_btn = driver.find_elements(by=By.XPATH, value='//*[@id="cookiebanner"]/div/div[2]/div/div/div/div/div[1]/div[1]/a')
cookie_accept_btn[0].click()

i = 0
for li in page_list:

    if i == 0:
        i += 1
        continue

    # 랜덤 시간 보내기
    # driver.implicitly_wait(3)
    time.sleep(3)

    #page_list_ul.style.visibility = 'visible'
    # 아주 살짝 스크롤
    print('[ %d 페이지 ]' % i)


    # 현재 스크롤 위치에서 검색 결과 요소의 끝까지 이동
    # 
    driver.execute_script('window.scrollTo(0,2)')
    
    # 활성 상태로 class 변경
    driver.execute_script("arguments[0].setAttribute('class',arguments[1])",li, "page show")

    # 페이지 클릭
    li.click()
    #li.send_keys(Keys.ENTER)
    
    time.sleep(2)
    
    i += 1
    













# # 술 이름 가져오기 
# names = driver.find_elements_by_class_name("good_tit1")

# for name in names:
#     print(name.text)

# driver.quit()

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














