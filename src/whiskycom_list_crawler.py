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


###########################################################################################
#                                                                                         #
# target site: www.whisky.com                                                             #
# https://www.whisky.com/whisky-database/bottle-search/whisky.html(whisky list)           #
# https://www.whisky.com/whisky-database/bottle-search/gin.html(gin list)                 #
#                                                                                         #
###########################################################################################

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
#driver.get('https://www.whisky.com/whisky-database/bottle-search/whisky.html')
driver.get('https://www.whisky.com/whisky-database/bottle-search/gin.html')


# 해당 카테고리의 페이지 리스트를 조회하여 몇페이지까지 데이터가 있는지 확인
# Full Xpath: /html/body/ul[1]
# page_list_ul = driver.find_elements(by=By.CLASS_NAME, value="datamints-infinite-scroll-pagination")
# print(page_list_ul)

page_list_ul = driver.find_elements(by=By.XPATH, value="/html/body/ul[1]")
page_list = driver.find_elements(by=By.XPATH, value="/html/body/ul[1]/li")

print("총 페이지 li 개수: %d" % len(page_list))

total_page_li = len(page_list)

cookie_accept_btn = driver.find_elements(by=By.XPATH, value='//*[@id="cookiebanner"]/div/div[2]/div/div/div/div/div[1]/div[1]/a')
cookie_accept_btn[0].click()

loaded_page = 0
for li in page_list:

    if loaded_page == 0:
        loaded_page += 1
        continue

    # 랜덤 시간 보내기
    # driver.implicitly_wait(3)
    rand_num = random.randrange(1,4)
    time.sleep(rand_num)

    #page_list_ul.style.visibility = 'visible'
    # 아주 살짝 스크롤
    print('[ %d 페이지 로드 ]' % loaded_page)


    # 현재 스크롤 위치에서 검색 결과 요소의 끝까지 이동
    
    now_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script('window.scrollTo(0,'+str(now_height)+')')
    
    # 활성 상태로 class 변경
    driver.execute_script("arguments[0].setAttribute('class',arguments[1])",li, "page show")

    # 페이지 클릭
    li.click()
    #li.send_keys(Keys.ENTER)

    # 마지막 페이지 확인
    if loaded_page == (total_page_li-2):
        print("모든 페이지를 로드 했습니다.")
        break
 
    loaded_page += 1

    rand_num = random.randrange(1,3)
    time.sleep(rand_num)   
    

# 로드된 리스트를 읽어들여서 20개씩 저장
# //*[@id="flaschendb_flaschen_search_result"]/div[4]/div[1]

liquor_page_list = driver.find_elements(by=By.XPATH, value='//*[@id="flaschendb_flaschen_search_result"]/div[4]/div')

print("[ 로드된 페이지 개수 ]: %d" % len(liquor_page_list))

now_page_num = 0
for page in liquor_page_list:
    now_page_num += 1
    liquor_list = page.find_elements(by=By.CLASS_NAME, value='flaschenIdentifier')

    for item in liquor_list:
        # 부모 요소(a태그) href 값 가져오기
        a_tag = item.find_element(by=By.XPATH, value='..')
        url = a_tag.get_attribute('href')
        
        # 자식 요소들(span태그) 중에서 class가 marke, namenszusatz인 녀석들의 값 가져오기
        span_marke = item.find_element(by=By.CLASS_NAME, value='marke')
        marke = span_marke.text

        span_namenszusatz = item.find_element(by=By.CLASS_NAME, value='namenszusatz')
        namenszusatz = span_namenszusatz.text

        name = marke + namenszusatz
    

    print("[ %d 페이지의 술 데이터 개수 ]: %d" % (now_page_num, len(liquor_list)))
    

# liquor_list = driver.find_elements(by=By.XPATH, value='//*[@id="flaschendb_flaschen_search_result"]/div[4]/div[1]/div')

# print("[ 로드된 술 개수 ]: %d" % len(liquor_list))

