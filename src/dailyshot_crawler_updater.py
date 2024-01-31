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

HOST = 'tipsy.co.kr'
#HOST = 'localhost:8080'
#HOST = '192.168.219.104:8080'
API_SAVE_URL = 'http://'+HOST+'/svcmgr/api/crawled/liquor.tipsy'
CRAWL_SITE_CODE = 1
MAX_CRAWL_COUNT = 5000    # 최대 크롤링 데이터 개수  
MIN_LIQUOR_ID = 1       # 최소 주류 ID
MAX_LIQUOR_ID = 96000    # 최대 주류 ID
MIN_WAIT_TIME = 1      # 최소 대기 시간 - 5초
MAX_WAIT_TIME = 4      # 최대 대기 시간 - 15초
IS_TEST = False

def set_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('headless')
    #chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument("disable-gpu")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager(version="114.0.5735.90").install()), options=chrome_options)

    #/Users/gwanga/Downloads/chromedriver_mac_arm64/chromedriver
    #driver = webdriver.Chrome('/Users/gwanga/git/tipsy-crawler/chromedriver', options=chrome_options)
    
    return driver

def get_err_log_file_path():
    now_path = os.path.abspath(__file__)
    parent_path = os.path.dirname(now_path)
    pparent_path = os.path.dirname(parent_path)
    path = "%s/error.log"%pparent_path
    return path

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

def get_retry_queue():
    API_RETRY_QUEUE_URL = 'http://' + HOST + '/svcmgr/api/crawled/retryQueue.tipsy'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': 'Bearer AUTOmKFxUkmakDV9w8z/yLOxrbm0WwxgbNpsOS6HhoUAGNY='
    }
    URL = API_RETRY_QUEUE_URL
    res = requests.get(URL, headers=headers)
    resJson = res.json()

    if res.status_code == 200:
        if resJson['data'] != None:
            return resJson['data']
        else:
            return None
    else:
        return None

def parse_abv(value):
    abv = value.replace("%", "")
    if '~' in abv:
        abv_arr = abv.split("~")
        abv = abv_arr[1]
    return abv




driver = set_chrome_driver()
driver.implicitly_wait(3)

print('[START DAILY_SHOT CRAWLING UPDATER]')

# 한 번의 실행에 100개의 데이터 조회
crawled_cnt = 0
crawled_success = 0
crawled_fail = 0
while crawled_cnt < MAX_CRAWL_COUNT:

    data = {}

    # retry queue가 존재한다면 우선 처리 
    liquor_id = 0
    crawl_url = ''
    prev_data = get_retry_queue()
    
    if(prev_data != None):
        retry_url = prev_data['url']
        data['id'] = prev_data['id']
        crawl_url = retry_url
    else:
        time.sleep(5)
        continue

    try:        
        driver.get(crawl_url)

        current_url = driver.current_url
        if crawl_url != current_url:
            data['new_url'] = current_url

        data['url'] = crawl_url
        data['site'] = CRAWL_SITE_CODE

        print("[CRAWL_URL]:%s"%crawl_url)

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
            print("[name_en]:%s"%name_en.text)
        else:
            print("[name_en]:None")

        name_kr_xpath = '//*[@id="__next"]/div[1]/div/main/div/div/div[1]/div[1]/div[3]/div/div[2]/h1'
        if len(driver.find_elements(by=By.XPATH, value='//*[@id="__next"]/div[1]/div/main/div/div/div[1]/div[1]/div[3]/div/div[2]/h1')) > 0:
            name_kr = driver.find_element(by=By.XPATH, value='//*[@id="__next"]/div[1]/div/main/div/div/div[1]/div[1]/div[3]/div/div[2]/h1')
            data['name_kr'] = name_kr.text
            print("[name_kr]:%s"%name_kr.text)
        else:
            print("[name_kr]:None")


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
                        abv = parse_abv(els[1].text)
                        data['abv'] = abv
                        print("[abv]:%s"%abv)
                    elif el.text == '국가':
                        data['country_name'] = els[1].text
                        print("[country_name]:%s"%els[1].text)
                    elif el.text == '지역':
                        data['region_name'] = els[1].text
                        print("[region_name]:%s"%els[1].text)
        
        tasting_notes = {}
        print("scrape tasting note, nation, region, abv, category, country ...")
        if len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Group-root dailyshot-8k3bl3"]')) > 0:
            info_rows = driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Group-root dailyshot-8k3bl3"]')
            
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
                        data['abv'] = parse_abv(value)
                    elif title == '국가':
                        data['country_name'] = value
                    elif title == '지역':
                        data['region_name'] = value
                    elif title == '품종':
                        data['variety'] = value
                    elif title == 'Aroma':
                        tasting_notes['nosing'] = value
                    elif title == 'Taste':
                        tasting_notes['tasting'] = value
                    elif title == 'Finish':
                        tasting_notes['finish'] = value
                    elif title == '바디':
                        div = row.find_element(by=By.XPATH, value='./div')
                        input = div.find_element(by=By.XPATH, value='./input')
                        tasting_notes['body'] = int(input.get_attribute("value"))
                    elif title == '타닌':
                        div = row.find_element(by=By.XPATH, value='./div')
                        input = div.find_element(by=By.XPATH, value='./input')
                        tasting_notes['tannin'] = int(input.get_attribute("value"))
                    elif title == '당도':
                        div = row.find_element(by=By.XPATH, value='./div')
                        input = div.find_element(by=By.XPATH, value='./input')
                        tasting_notes['sweetness'] = int(input.get_attribute("value"))
                    elif title == '산미':
                        div = row.find_element(by=By.XPATH, value='./div')
                        input = div.find_element(by=By.XPATH, value='./input')
                        tasting_notes['acidity'] = int(input.get_attribute("value"))
        else:            
            if len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Group-root dailyshot-1lweaqt"]')) > 0:
                info_rows = driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Group-root dailyshot-1lweaqt"]')
                
                for row in info_rows:
                    # h3 존재 여부확인
                    row_text = row.text
                    value_div = row.find_element(by=By.XPATH, value='./div[@class="dailyshot-Text-root dailyshot-1kszlmz"]')
                    value = value_div.text

                    if '종류' in row_text:
                        print("[value]:%s" % value)
                        data['category_name'] = value
                    elif '용량' in row_text:
                        print("[value]:%s" % value)
                        data['volume'] = value
                    elif '도수' in row_text:
                        abv = parse_abv(value)
                        print("[value]:%s" % abv)
                        data['abv'] = abv
                    elif '국가' in row_text:
                        print("[value]:%s" % value)
                        data['country_name'] = value
                    elif '지역' in row_text:
                        print("[value]:%s" % value)
                        data['region_name'] = value
                    elif '품종' in row_text:
                        data['variety'] = value
                    elif 'Aroma' in row_text:
                        print("[value]:%s" % value)
                        tasting_notes['nosing'] = value
                    elif 'Taste' in row_text:
                        print("[value]:%s" % value)
                        tasting_notes['tasting'] = value
                    elif 'Finish' in row_text:
                        print("[value]:%s" % value)
                        tasting_notes['finish'] = value

        if tasting_notes is not None:
            data['tasting_notes'] = tasting_notes

        # rating_avg => //*[@class="review-rate"]/p
        print("scrape rating info ...")
        if '와인' in data['category_name'] or '샴페인' in data['category_name']:
            # rate_avg
            if len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-6fh1wo"]')) > 0: # 2024.01.29
                rating_avg_info = driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-6fh1wo"]')
                rating_avg = rating_avg_info[0].text
                data['rating_avg'] = rating_avg
                print("[rating_avg]:%s"%rating_avg)

            # rating count
            if len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-r40kji"]')) > 0: # 2024.01.29
                rating_count_info = driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-r40kji"]')
                rating_count_txt = rating_count_info[0].text
                end_idx = rating_count_txt.find("개")
                rating_count = rating_count_txt[0:end_idx].replace(",", "")
                data['rating_count'] = rating_count
                print("[rating_count]:%s"%rating_count)

            # price and pairing
            if len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-3j9rdk"]')) > 0:
                rate_info = driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-3j9rdk"]')
                
                # 가격
                price = rate_info[0].text
                data['price'] = price.replace(',', '')
                print("[price]:%s"%price)

                # 페어링
                if len(rate_info) >= 2:
                    pairing = rate_info[1].text
                    data['pairing'] = pairing
                    print("[pairing]:%s"%pairing)
        else:
            if len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-d2e2oa"]')) > 0:
                rate_info = driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-d2e2oa"]')
                
                # 리뷰 평점
                rating_avg = rate_info[0].text
                data['rating_avg'] = rating_avg
                print("[rating_avg]:%s"%rating_avg)

                # 리뷰 개수
                if len(rate_info) >= 2:
                    rating_count_txt = rate_info[1].text
                    end_idx = rating_count_txt.find("개")
                    rating_count = rating_count_txt[0:end_idx].replace(",", "")
                    data['rating_count'] = rating_count
                    print("[rating_count]:%s"%rating_count)

            elif len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-3j9rdk"]')) > 0:
                rate_info = driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-3j9rdk"]')
                
                # 가격
                price = rate_info[0].text
                data['price'] = price.replace(',', '')
                print("[price]:%s"%price)

                # 리뷰 평점
                if len(rate_info) >= 2:
                    rating_avg = rate_info[1].text
                    data['rating_avg'] = rating_avg
                    print("[rating_avg]:%s"%rating_avg)

                # 리뷰 개수
                if len(rate_info) >= 3:
                    rating_count_txt = rate_info[2].text
                    end_idx = rating_count_txt.find("개")
                    rating_count = rating_count_txt[0:end_idx].replace(",", "")
                    data['rating_count'] = rating_count
                    print("[rating_count]:%s"%rating_count)



        # 썸네일 이미지
        print("scrape thumbnail ...")
        if len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Stack-root dailyshot-iuqr8"]')) > 0:
            thumb_div = driver.find_element(by=By.XPATH, value='//*[@class="dailyshot-Stack-root dailyshot-iuqr8"]')
            thumb = thumb_div.find_element(by=By.XPATH, value='./img')
            data['image_url'] = thumb.get_attribute('src')
            print("[image_url]:%s"%thumb.get_attribute('src'))
        else:
            print("[image_url]:None")



        # description
        print("scrape deescription ...")
        if len(driver.find_elements(by=By.XPATH, value='//div[@class="dailyshot-Text-root dailyshot-eqknkd"]')) > 0:
            description = ""
            comments = driver.find_elements(by=By.XPATH, value='//div[@class="dailyshot-Text-root dailyshot-eqknkd"]')
            for comment in comments:
                comment_txt = comment.text
                description = description + "\n" + comment_txt
            data['description'] = description
            print("[description]:%s"%description)
        else:
            print("[description]:None")


        print("[data]")
        print(data)

        data_json = json.dumps(data, ensure_ascii=False).encode('utf8')
        # print("[data_json]")
        # print(data_json)
        

        # send data
        if IS_TEST is not True:
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
            sentence = '[DailyShot Crawl Updater Error] url:%s / msg:%s\n' % (crawl_url, err)
            file.write(sentence)


print('[END DAILY_SHOT CRAWLING]')
driver.quit()

