import time
import random
import sys
import json
import urllib.request
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

#API_SAVE_URL = 'http://tipsy.co.kr/svcmgr/api/crawled/liquor.tipsy'
API_SAVE_URL = 'http://localhost:8080/svcmgr/api/crawled/liquor.tipsy'
CRAWL_SITE_CODE = 1
MAX_CRAWL_COUNT = 1000    # 최대 크롤링 데이터 개수
MIN_LIQUOR_ID = 1       # 최소 주류 ID
MAX_LIQUOR_ID = 96000    # 최대 주류 ID
MIN_WAIT_TIME = 1      # 최소 대기 시간 - 5초
MAX_WAIT_TIME = 4      # 최대 대기 시간 - 15초

def set_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.add_argument('headless')
    #chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument("disable-gpu")
    # 혹은 options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager(version="114.0.5735.90").install()), options=chrome_options)

    #/Users/gwanga/Downloads/chromedriver_mac_arm64/chromedriver
    #driver = webdriver.Chrome('/Users/gwanga/git/tipsy-crawler/chromedriver', options=chrome_options)
    
    return driver

def get_black_list_file_path():
    now_path = os.path.abspath(__file__)
    parent_path = os.path.dirname(now_path)
    pparent_path = os.path.dirname(parent_path)
    path = "%s/dailyshot_new_blacklist.txt"%pparent_path
    return path

def get_err_log_file_path():
    now_path = os.path.abspath(__file__)
    parent_path = os.path.dirname(now_path)
    pparent_path = os.path.dirname(parent_path)
    path = "%s/error.log"%pparent_path
    return path

black_list = {}
def set_black_list():
    with open(get_black_list_file_path(), "r", encoding="utf-8") as file:
        for blacklist_id in file:
            black_list[int(blacklist_id)] = True

def is_url_duplicated(url):
    API_URL_DUP_CHCK_URL = 'http://tipsy.co.kr/svcmgr/api/crawled/url.tipsy'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'Bearer AUTOmKFxUkmakDV9w8z/yLOxrbm0WwxgbNpsOS6HhoUAGNY='
    }
    URL = '%s?url=%s' % (API_URL_DUP_CHCK_URL, url)
    res = requests.get(URL, headers=headers)
    resJson = res.json()

    if res.status_code == 200:
        if resJson['state'] == 0:
            return False
        elif resJson['state'] == 10:
            print("[중복 URL]:%s" % url)
            return True
    else:
        return True

def is_name_duplicated(nameEn):
    API_URL_DUP_CHCK_URL = 'http://tipsy.co.kr/svcmgr/api/liquor/duplication.tipsy'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'Bearer AUTOmKFxUkmakDV9w8z/yLOxrbm0WwxgbNpsOS6HhoUAGNY='
    }
    URL = '%s?nameEn=%s' % (API_URL_DUP_CHCK_URL, nameEn)
    res = requests.get(URL, headers=headers)
    resJson = res.json()

    if res.status_code == 200:
        if resJson['state'] == 0:
            return False
        elif resJson['state'] == 10:
            print("[중복 영문명]:%s" % nameEn)
            return True
    else:
        return True



driver = set_chrome_driver()
driver.implicitly_wait(3)

set_black_list()

print('[START DAILY_SHOT CRAWLING]')

# 한 번의 실행에 100개의 데이터 조회
crawled_cnt = 0
crawled_success = 0
crawled_fail = 0
while crawled_cnt < MAX_CRAWL_COUNT:

    data = {}

    # ID 범위 1 ~ 4999
    liquor_id = random.randrange(MIN_LIQUOR_ID, MAX_LIQUOR_ID)

    crawl_url = 'https://dailyshot.co/m/items/%d' % liquor_id

    # URL 중복 확인
    if is_url_duplicated(crawl_url) == True:
        continue

    try:        
        driver.get(crawl_url)

        # TODO: 없는 제품 번호의 경우 블랙리스트로 등록 - file

        data['url'] = crawl_url
        data['site'] = CRAWL_SITE_CODE

        print("[CRAWL_URL]:%s"%crawl_url)

        # 블랙리스트 확인
        if liquor_id in black_list:
            continue

        # TODO: 기존에 크롤링한 데이터인지 확인 (to server)

        # 페이지 로드 여부 확인
        if len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-k9szl2"]')) > 0:
            message = driver.find_element(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-k9szl2"]')
            print("[message]:%s"%message.text)
            if message.text == '존재하지 않는 상품입니다.' or message.text == '상세 페이지가 없는 상품입니다':
                with open(get_black_list_file_path(), "a", encoding="utf-8") as file:
                    sentence = '%d\n' % liquor_id
                    file.write(sentence)
                black_list[liquor_id] = True
                continue

        # 술 이름 가져오기 
        #names = driver.find_elements_by_class_name("good_tit1")
        name_en_xpath = '//*[@id="__next"]/div[1]/div/main/div/div/div[1]/div[1]/div[3]/div/div[2]/div'
        if len(driver.find_elements(by=By.XPATH, value=name_en_xpath)) > 0:
            name_en = driver.find_element(by=By.XPATH, value=name_en_xpath)
            data['name_en'] = name_en.text

            if is_name_duplicated(name_en.text) == True:
                continue

            print("[name_en]:%s"%name_en.text)
        

        name_kr_xpath = '//*[@id="__next"]/div[1]/div/main/div/div/div[1]/div[1]/div[3]/div/div[2]/h1'
        if len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-Title-root dailyshot-2eov7z"]')) > 0:
            name_kr = driver.find_element(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-Title-root dailyshot-2eov7z"]')
            data['name_kr'] = name_kr.text
            print("[name_kr]:%s"%name_kr.text)


        # abv, category, country
        print("scrape abv, category, country ...")
        if len(driver.find_elements(by=By.XPATH, value='//*[@class="product-info-row"]')) > 0:
            info_rows = driver.find_elements(by=By.XPATH, value='//*[@class="product-info-row"]')
            for row in info_rows:
                els = row.find_elements(by=By.XPATH, value='./p')
                for el in els:
                    if el.text == '종류':
                        data['category_name'] = els[1].text
                        print("[category_name]:%s"%els[1].text)
                    elif el.text == '도수':
                        # TODO: replace 이후 숫자가 아니라면 데이터 설정x
                        data['abv'] = els[1].text.replace("%", "")
                        print("[abv]:%s"%els[1].text)
                    elif el.text == '국가':
                        data['country_name'] = els[1].text
                        print("[country_name]:%s"%els[1].text)
                    elif el.text == '지역':
                        data['region_name'] = els[1].text
                        print("[region_name]:%s"%els[1].text)
        
        print("scrape tasting note, nation, region, abv, category, country ...")
        if len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Group-root dailyshot-8k3bl3"]')) > 0:
            info_rows = driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Group-root dailyshot-8k3bl3"]')
            tasting_notes = {}
            for row in info_rows:
                # h3 존재 여부확인
                h3_chck = row.find_elements(by=By.XPATH, value='./h3')
                if len(h3_chck) > 0:
                    # 타이틀에 따른 데이터 파싱

                    h3 = row.find_element(by=By.XPATH, value='./h3')
                    title = h3.text
                    value = row.find_element(by=By.XPATH, value='./div').text
                    print("[%s]:%s" % (h3.text, value))

                    if title == '종류':
                        data['category_name'] = value
                    elif title == '용량':
                        pass
                    elif title == '도수':
                        data['abv'] = value.replace("%", "")
                    elif title == '국가':
                        data['country_name'] = value
                    elif title == '지역':
                        data['region_name'] = value
                    elif title == '품종':
                        pass
                    elif title == 'Aroma':
                        tasting_notes['nosing'] = value
                    elif title == 'Taste':
                        tasting_notes['tasting'] = value
                    elif title == 'Finish':
                        tasting_notes['finish'] = value

            data['tasting_notes'] = tasting_notes


        # rating_avg => //*[@class="review-rate"]/p
        print("scrape rating info ...")
        if data['category_name'] in '와인':
            if len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-8uh6vn"]')) > 0:
                rating_avg_info = driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-8uh6vn"]')
                
                # 리뷰 평점
                rating_avg = rating_avg_info[0].text
                data['rating_avg'] = rating_avg
                print("[rating_avg]:%s"%rating_avg)

                # 리뷰 개수
                rating_count_info = driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Group-root dailyshot-1unsgds"]')
                rating_count_txt = rating_count_info[1].text
                end_idx = rating_count_txt.find("개")
                rating_count = rating_count_txt[0:end_idx]
                data['rating_count'] = rating_count
                print("[rating_count]:%s"%rating_count)
        else:
            if len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-d2e2oa"]')) > 0:
                rate_info = driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-d2e2oa"]')
                
                # 리뷰 평점
                rating_avg = rate_info[0].text
                data['rating_avg'] = rating_avg
                print("[rating_avg]:%s"%rating_avg)

                # 리뷰 개수
                rating_count_txt = rate_info[1].text
                end_idx = rating_count_txt.find("개")
                rating_count = rating_count_txt[0:end_idx]
                data['rating_count'] = rating_count
                print("[rating_count]:%s"%rating_count)



        # 썸네일 이미지
        print("scrape thumbnail ...")
        if len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Stack-root dailyshot-iuqr8"]')) > 0:
            thumb_div = driver.find_element(by=By.XPATH, value='//*[@class="dailyshot-Stack-root dailyshot-iuqr8"]')
            thumb = thumb_div.find_element(by=By.XPATH, value='./img')
            data['image_url'] = thumb.get_attribute('src')
            print("[image_url]:%s"%thumb.get_attribute('src'))



        # description
        print("scrape deescription ...")
        if len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-1gwjnlq"]')) > 0:
            description = ""
            comments = driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-1gwjnlq"]')
            for comment in comments:
                comment_txt = comment.find_element(by=By.XPATH, value='./div/p').text
                description = description + "\n" + comment_txt
            data['description'] = description
            # print("[description]")
            # print(description)


        data_json = json.dumps(data, ensure_ascii=False).encode('utf8')
        # print("[data_json]")
        # print(data_json)
        




        # send data
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': 'Bearer AUTOmKFxUkmakDV9w8z/yLOxrbm0WwxgbNpsOS6HhoUAGNY='
        }
        res = requests.post(API_SAVE_URL, headers=headers, data=data_json)

        print("[SAVE REQUEST RESULT]")
        print("[STATUS_CODE]:%s" % res.status_code)
        print(json.loads(res.text))
        #print(res.json)

        if res.status_code == 200:
            crawled_success = crawled_success + 1
        else:
            crawled_fail = crawled_fail + 1
        
        crawled_cnt = crawled_cnt + 1

        print("[CRAWLED_RESULT] - [TOTAL]:%s/[SUCCESS]:%s/[FAIL]:%s" % (crawled_cnt, crawled_success, crawled_fail))

        # set delay
        random_time = random.randrange(MIN_WAIT_TIME, MAX_WAIT_TIME)
        print("[WAITING FOR]: %ds ... "% random_time)
        time.sleep(random_time)
    except Exception as err:
        print("[Error Exception !!!]")
        print(err)
        with open(get_err_log_file_path(), "a", encoding="utf-8") as file:
            sentence = '[DailyShot Crawl Error] url:%s / msg:%s\n' % (crawl_url, err)
            file.write(sentence)


print('[END DAILY_SHOT CRAWLING]')
driver.quit()

