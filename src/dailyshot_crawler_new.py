import time
import random
import sys
import json
import urllib.request
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from utils import slack

#API_SAVE_URL = 'http://tipsy.co.kr/svcmgr/api/crawled/liquor.tipsy'
#API_SAVE_URL = 'http://localhost:8080/svcmgr/api/crawled/liquor.tipsy'
HOST = 'tipsy.co.kr'
#HOST = 'localhost:8080'
API_SAVE_URL = 'https://'+HOST+'/svcmgr/api/crawled/liquor.tipsy'
CRAWL_SITE_CODE = 1
MIN_WAIT_TIME = 1      # 최소 대기 시간 - 5초
MAX_WAIT_TIME = 4      # 최대 대기 시간 - 15초
IS_TEST = False

def set_chrome_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument('--headless')
    #chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')  # 공유 메모리 대신 디스크를 사용하도록 하여 메모리 부족 문제를 해결
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")    # 브라우저가 자동화 도구임을 감지하지 못하도록 방지
    chrome_options.add_argument('--lang=ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7')
    chrome_options.add_argument("--user-data-dir=/home/ubuntu/tipsy-crawler/logs")
    
    #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver = webdriver.Chrome(options=chrome_options)

    return driver

def get_crawl_info_file_path():
    now_path = os.path.abspath(__file__)
    parent_path = os.path.dirname(now_path)
    pparent_path = os.path.dirname(parent_path)
    path = "%s/logs/dailyshot_crawl_info.txt"%pparent_path
    return path

def get_black_list_file_path():
    now_path = os.path.abspath(__file__)
    parent_path = os.path.dirname(now_path)
    pparent_path = os.path.dirname(parent_path)
    path = "%s/logs/dailyshot_black_list.txt"%pparent_path
    return path

def get_err_log_file_path():
    now_path = os.path.abspath(__file__)
    parent_path = os.path.dirname(now_path)
    pparent_path = os.path.dirname(parent_path)
    path = "%s/logs/error.log"%pparent_path
    return path

def get_err_list_file_path():
    now_path = os.path.abspath(__file__)
    parent_path = os.path.dirname(now_path)
    pparent_path = os.path.dirname(parent_path)
    path = "%s/logs/dailyshot_error_list.log"%pparent_path
    return path

def get_fail_list_file_path():
    now_path = os.path.abspath(__file__)
    parent_path = os.path.dirname(now_path)
    pparent_path = os.path.dirname(parent_path)
    path = "%s/logs/dailyshot_fail_list.log"%pparent_path
    return path

black_list = {}
def set_black_list():
    with open(get_black_list_file_path(), "r", encoding="utf-8") as file:
        for blacklist_id in file:
            black_list[int(blacklist_id)] = True

# TODO: 고도화 필요
next_crawl_liquor_id = None
def set_crawl_info():
    global next_crawl_liquor_id
    with open(get_crawl_info_file_path(), "r", encoding="utf-8") as file:
        for line in file:
            crawl_info = parse_crawl_info(line)
            if crawl_info[0] == 'next_crawl_liquor_id':
                next_crawl_liquor_id = int(crawl_info[1])
                print("[SET_CRAWL_INFO] next_crawl_liquor_id:%s" % (next_crawl_liquor_id))

def parse_crawl_info(info):
    info_arr = info.split(":")
    return (info_arr[0], info_arr[1])

def set_next_crawl_liquor_id(id):
    with open(get_crawl_info_file_path(), "w", encoding="utf-8") as file:
        sentence = 'next_crawl_liquor_id:%s' % (id)
        file.write(sentence)

def is_url_duplicated(url):
    API_URL_DUP_CHCK_URL = 'http://'+HOST+'/svcmgr/api/crawled/url.tipsy'
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
    API_URL_DUP_CHCK_URL = 'http://'+HOST+'/svcmgr/api/liquor/duplication.tipsy'
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

def parse_abv(value):
    abv = value.replace("%", "")
    if '~' in abv:
        abv_arr = abv.split("~")
        abv = abv_arr[1]
    return abv

set_crawl_info()
#set_black_list()


print('[START DAILY_SHOT CRAWLING] start_crawl_liquor_id:%s' % next_crawl_liquor_id)

slack.send_message('데일리샷 술 데이터 수집 시작', '[데일리샷] 주류 번호 %s 부터 수집 시작됨.' % next_crawl_liquor_id)

driver_error_cnt = 0
crawled_cnt = 0
crawled_success = 0
crawled_fail = 0
duplicated_cnt = 0
unknown_cnt = 0
while True:

    data = {}

    liquor_id = next_crawl_liquor_id
    next_crawl_liquor_id = next_crawl_liquor_id + 1
    set_next_crawl_liquor_id(next_crawl_liquor_id)
    
    # ID 범위 1 ~ 4999
    #liquor_id = random.randrange(MIN_LIQUOR_ID, MAX_LIQUOR_ID)

    crawl_url = 'https://dailyshot.co/m/item/%d' % liquor_id

    # for test - 지정된 URL로 테스트 하고 싶은 경우 사용 
    if IS_TEST:
        crawl_url = 'https://dailyshot.co/m/item/17255'     # wine
        #crawl_url = 'https://dailyshot.co/m/item/5188'     # wine - have description
        #crawl_url = 'https://dailyshot.co/m/item/3254'     # 짐빔
        #crawl_url = 'https://dailyshot.co/m/item/2981'     # 가쿠빈

    
    if (crawled_cnt + 1) >= 101:
            content = '''
            [데일리샷 데이터 수집 집계]
            - 총 수집 시도: %s
            - 수집 성공: %s
            - 수집 실패: %s
            - 중복 수집: %s
            - 알수 없음: %s
            - 마지막 술 ID: %s
            ''' % (crawled_cnt, crawled_success, crawled_fail, duplicated_cnt, unknown_cnt, liquor_id)
            slack.send_message('데일리샷 술 데이터 집계', content)

            # 초기화
            crawled_cnt = 0
            crawled_success = 0
            crawled_fail = 0
            duplicated_cnt = 0
            unknown_cnt = 0
            driver_error_cnt = 0

    crawled_cnt = crawled_cnt + 1

    # URL 중복 확인
    if is_url_duplicated(crawl_url) == True and IS_TEST is False:
        duplicated_cnt = duplicated_cnt + 1
        driver.quit()
        continue
       
    driver = set_chrome_driver()
    driver.implicitly_wait(20) 
    try:
        try:
            driver.get(crawl_url)
        except Exception as err:
            print("[Driver Error Exception !!!]")
            print(err)
            driver_error_cnt = driver_error_cnt + 1
            with open(get_err_log_file_path(), "a", encoding="utf-8") as file:
                sentence = '[DailyShot Crawl Error] url:%s / msg:%s\n' % (crawl_url, err)
                file.write(sentence)
            next_crawl_liquor_id = next_crawl_liquor_id - 1
            set_next_crawl_liquor_id(next_crawl_liquor_id)
            time.sleep(2)
            driver = set_chrome_driver()
            driver.implicitly_wait(20)
            continue

        if driver_error_cnt >= 1000:
            print('[END DAILY_SHOT CRAWLING]')
            driver.quit()
            break

        current_url = driver.current_url
        crawl_url = current_url

        data['url'] = crawl_url
        data['site'] = CRAWL_SITE_CODE

        print("[CRAWL_URL]:%s"%crawl_url)

        # 블랙리스트 확인
        # if liquor_id in black_list:
        #     continue

        # 페이지 로드 여부 확인 => TODO: 사용되지 않는 경우 삭제 
        if len(driver.find_elements(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-k9szl2"]')) > 0:
            message = driver.find_element(by=By.XPATH, value='//*[@class="dailyshot-Text-root dailyshot-k9szl2"]')
            print("[message]:%s"%message.text)
            if message.text == '존재하지 않는 상품입니다.' or message.text == '상세 페이지가 없는 상품입니다':
                unknown_cnt = unknown_cnt + 1
                with open(get_black_list_file_path(), "a", encoding="utf-8") as file:
                    sentence = '%d\n' % liquor_id
                    file.write(sentence)
                black_list[liquor_id] = True
                driver.quit()
                continue
        elif len(driver.find_elements(by=By.XPATH, value='//*[@class="next-error-h1"]')) > 0:
            unknown_cnt = unknown_cnt + 1
            print("존재하지 않는 술 번호")
            with open(get_black_list_file_path(), "a", encoding="utf-8") as file:
                sentence = '%d\n' % liquor_id
                file.write(sentence)
            black_list[liquor_id] = True
            driver.quit()
            continue;

        # 술 이름 가져오기 
        #name_en_xpath = '//*[@id="__next"]/div[1]/div/main/div/div/div[1]/div[1]/div[3]/div/div[2]/div'
        name_en_selector = '#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(1) > div.dailyshot-Stack-root.dailyshot-1178y6y > div > div.dailyshot-Stack-root.dailyshot-16cncgc > div'
        if len(driver.find_elements(by=By.CSS_SELECTOR, value=name_en_selector)) > 0:
            name_en = driver.find_element(by=By.CSS_SELECTOR, value=name_en_selector)
            data['name_en'] = name_en.text

            if is_name_duplicated(name_en.text) == True and IS_TEST is False:
                duplicated_cnt = duplicated_cnt + 1
                driver.quit()
                continue

            print("[name_en]:%s"%name_en.text)
        else:
            print("[name_en]:None")

        # 영어 이름을 알 수 없는 경우 error 리스트에 추가 - 집계에는 unknown으로
        isNE = 'name_en' in data
        if isNE is False:
            unknown_cnt = unknown_cnt + 1
            with open(get_black_list_file_path(), "a", encoding="utf-8") as file:
                sentence = '%d\n' % liquor_id
                file.write(sentence)
            driver.quit()
            continue

        #name_kr_xpath = '//*[@id="__next"]/div[1]/div/main/div/div/div[1]/div[1]/div[3]/div/div[2]/h1'
        name_kr_selector = '#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(1) > div.dailyshot-Stack-root.dailyshot-1178y6y > div > div.dailyshot-Stack-root.dailyshot-16cncgc > h1'
        if len(driver.find_elements(by=By.CSS_SELECTOR, value=name_kr_selector)) > 0:
            name_kr = driver.find_element(by=By.CSS_SELECTOR, value=name_kr_selector)
            data['name_kr'] = name_kr.text
            print("[name_kr]:%s"%name_kr.text)
        else:
            print("[name_kr]:None")

    
        # abv, category, country, tasting notes ...
        tasting_notes = {}
        print("scrape tasting note, nation, region, abv, category, country ...")
        info_xpath = '//*[@class="dailyshot-Group-root dailyshot-1lweaqt"]'
        if len(driver.find_elements(by=By.XPATH, value=info_xpath)) > 0:
            info_rows = driver.find_elements(by=By.XPATH, value=info_xpath)
            
            for row in info_rows:
                # h3 존재 여부확인
                h3_chck = row.find_elements(by=By.XPATH, value='./div/h3')
                if len(h3_chck) > 0:
                    # 타이틀에 따른 데이터 파싱
                    h3 = row.find_element(by=By.XPATH, value='./div/h3')
                    title = h3.text
                    value = row.find_element(by=By.XPATH, value='./div[2]').text
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

        if tasting_notes is not None:
            data['tasting_notes'] = tasting_notes

        # rating_avg => //*[@class="review-rate"]/p
        print("scrape rating info ...")
        if '와인' in data['category_name'] or '샴페인' in data['category_name']:
            # rate_avg
            rating_avg_selector = "#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(7) > div.dailyshot-Stack-root.dailyshot-1bixg60 > div > div > div.dailyshot-Text-root.dailyshot-1t1nzgw"
            if len(driver.find_elements(by=By.CSS_SELECTOR, value=rating_avg_selector)) > 0:
                rating_avg_info = driver.find_elements(by=By.CSS_SELECTOR, value=rating_avg_selector)
                rating_avg = rating_avg_info[0].text
                data['rating_avg'] = rating_avg
                print("[rating_avg]:%s"%rating_avg)

            # rating count
            rating_count_selector = "#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(7) > div.dailyshot-Stack-root.dailyshot-1bixg60 > div > div > div.dailyshot-Stack-root.css-82a6rk.dailyshot-1kzvwqj > div:nth-child(2) > div:nth-child(1)"
            if len(driver.find_elements(by=By.CSS_SELECTOR, value=rating_count_selector)) > 0:
                rating_count_info = driver.find_elements(by=By.CSS_SELECTOR, value=rating_count_selector)
                rating_count_txt = rating_count_info[0].text
                end_idx = rating_count_txt.find("개")
                rating_count = rating_count_txt[0:end_idx].replace(",", "")
                data['rating_count'] = rating_count
                print("[rating_count]:%s"%rating_count)

            # pairing
            print("scrape pairing info ...")
            pairing_selector = "#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(7) > div:nth-child(8) > div"
            if len(driver.find_elements(by=By.CSS_SELECTOR, value=pairing_selector)) > 0:
                pairing_info = driver.find_elements(by=By.CSS_SELECTOR, value=pairing_selector)
                pairing = pairing_info[0].text
                data['pairing'] = pairing
                print("[pairing]:%s"%pairing)

        else:
            # 리뷰 평점
            rating_avg_selector = "#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(1) > div.dailyshot-Stack-root.dailyshot-1178y6y > div > div.dailyshot-Group-root.dailyshot-k87rjc > div.dailyshot-Text-root.dailyshot-15bwq65"
            if len(driver.find_elements(by=By.CSS_SELECTOR, value=rating_avg_selector)) > 0:
                rating_info = driver.find_elements(by=By.CSS_SELECTOR, value=rating_avg_selector)
                rating_avg = rating_info[0].text
                data['rating_avg'] = rating_avg
                print("[rating_avg]:%s"%rating_avg)

            # 리뷰 개수
            rating_count_selector = "#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(1) > div.dailyshot-Stack-root.dailyshot-1178y6y > div > div.dailyshot-Group-root.dailyshot-k87rjc > a > span"
            if len(driver.find_elements(by=By.CSS_SELECTOR, value=rating_count_selector)) > 0:
                rate_info = driver.find_elements(by=By.CSS_SELECTOR, value=rating_count_selector)
                rating_count_txt = rate_info[0].text
                end_idx = rating_count_txt.find("개")
                rating_count = rating_count_txt[0:end_idx].replace(",", "")
                data['rating_count'] = rating_count
                print("[rating_count]:%s"%rating_count)


        # 가격
        print("scrape price ...")
        price_selector = "#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(1) > div.dailyshot-Stack-root.dailyshot-1178y6y > div > div.dailyshot-Stack-root.dailyshot-uet3or > div > div > div > span.dailyshot-Text-root.dailyshot-15bwq65"
        if len(driver.find_elements(by=By.CSS_SELECTOR, value=price_selector)) > 0:
            price_info = driver.find_elements(by=By.CSS_SELECTOR, value=price_selector)
            price = price_info[0].text
            data['price'] = price.replace(',', '')
            print("[price]:%s"%price)


        # 썸네일 이미지
        print("scrape thumbnail ...")
        sumbnail_selector = '#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(1) > div.dailyshot-Stack-root.dailyshot-iuqr8 > div > div.dailyshot-AspectRatio-root.dailyshot-8ma7di > img'
        if len(driver.find_elements(by=By.CSS_SELECTOR, value=sumbnail_selector)) > 0:
            thumb = driver.find_element(by=By.CSS_SELECTOR, value=sumbnail_selector)
            data['image_url'] = thumb.get_attribute('src')
            print("[image_url]:%s"%thumb.get_attribute('src'))
        else:
            print("[image_url]:None")


        # description
        print("scrape deescription ...")
        desc_selector = '#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(9) > div.dailyshot-Stack-root.dailyshot-e90c5m'
        if len(driver.find_elements(by=By.CSS_SELECTOR, value=desc_selector)) > 0:
            desc_test = driver.find_elements(by=By.CSS_SELECTOR, value=desc_selector)
            desc_test_text = desc_test[0].text
            data['description'] = desc_test_text
            print("[description]:%s"%desc_test_text)
        else:
            print("[description]:None")


        print("[data]")
        print(data)

        data_json = json.dumps(data, ensure_ascii=False).encode('utf8')
        # print("[DATA JSON]")
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
            #print(json.loads(res.text))
            print(res.text)

            if res.status_code == 200:
                crawled_success = crawled_success + 1
            else:
                crawled_fail = crawled_fail + 1
                with open(get_fail_list_file_path(), "a", encoding="utf-8") as file:
                    sentence = '%s\n' % (liquor_id)
                    file.write(sentence)

        print("[CRAWLED_RESULT] - [TOTAL]:%s/[SUCCESS]:%s/[FAIL]:%s" % (crawled_cnt, crawled_success, crawled_fail))

        driver.quit()

        # set delay
        random_time = random.randrange(MIN_WAIT_TIME, MAX_WAIT_TIME)
        print("[WAITING FOR]: %ds ... "% random_time)
        time.sleep(random_time)

    except Exception as err:
        print("[Error Exception !!!]")
        print(err)
        crawled_fail = crawled_fail + 1
        with open(get_err_log_file_path(), "a", encoding="utf-8") as file:
            sentence = '[DailyShot Crawl Error] url:%s / msg:%s\n' % (crawl_url, err)
            file.write(sentence)
        with open(get_err_list_file_path(), "a", encoding="utf-8") as file:
            sentence = '%s\n' % (liquor_id)
            file.write(sentence)

        if 'chromedriver' in str(err) or 'invalid session id' in str(err) or 'page crash' in str(err) or 'session' in str(err):
            next_crawl_liquor_id = next_crawl_liquor_id - 1
            set_next_crawl_liquor_id(next_crawl_liquor_id)
            time.sleep(2)
            driver.quit()
            driver = set_chrome_driver()
            driver.implicitly_wait(20)
            continue

#slack.send_message('데일리샷 신규 데이터 수집기', '데일리샷 신규 데이터 수집기 종료')
print('[END DAILY_SHOT CRAWLING]')
driver.quit()

