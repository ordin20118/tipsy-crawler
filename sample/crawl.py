import time
import random
from selenium import webdriver
import followAndLike
import detectUnFollow
import sys
from urllib import parse

BOT_TYPE = sys.argv[1]

## Chrome의 경우 | 아까 받은 chromedriver의 위치를 지정해준다.
#driver = webdriver.Chrome('C:\Users\GwangA\Desktop\dev\web_crawling\chromedriver_win32\chromedriver')
driver = webdriver.Chrome('C:\\Users\\GwangA\\Desktop\\dev\\web_crawling\\chromedriver_win32\\chromedriver96')

## 암묵적으로 웹 자원 로드를 위해 3초까지 기다려 준다.
driver.implicitly_wait(3)

## url에 접근한다.
driver.get('https://www.instagram.com/')



## 인스타그램 로그인
## ex) driver.find_element_by_name('_2hvTZ pexuQ zyHYP').send_keys('ddd')
inputs = driver.find_elements_by_class_name("_2hvTZ")
i = 0
for input in inputs:
    if i==0:
        i = i + 1
        input.send_keys('id 입력하세요')
    else:
        input.send_keys('패스워드 입력하세요')
## 로그인 버튼 클릭
driver.find_element_by_class_name('sqdOP.L3NKy.y3zKF').click()
## 잠시 쉬어줌
time.sleep(3)


## 댓글에 사용될 메시지
comments = ['안녕하세요!', '맞팔해요~', '피드가 너무 이뻐요', '소통해요!!']
random.shuffle(comments)
print(random.choice(comments))


if BOT_TYPE == "like":
    ## '맞팔'로 검색된 페이지 이동
    encodedTag = parse.quote(sys.argv[2])
    driver.get('https://www.instagram.com/explore/tags/' + encodedTag + '/')
    ## 팔로우 및 좋아요 클릭 반복
    driver.find_element_by_xpath('//body//section//main//article//div/div/div/div/div[3]').click()
    time.sleep(1)
    followAndLike.followLike(driver, 1)
elif BOT_TYPE == "follow":
    ## '맞팔'로 검색된 페이지 이동
    encodedTag = parse.quote(sys.argv[2])
    driver.get('https://www.instagram.com/explore/tags/' + encodedTag + '/')
    ## 팔로우 및 좋아요 클릭 반복
    driver.find_element_by_xpath('//body//section//main//article//div/div/div/div/div[3]').click()
    time.sleep(1)
    followAndLike.followLike(driver, 2)
elif BOT_TYPE == "likefollow":
    ## '맞팔'로 검색된 페이지 이동
    encodedTag = parse.quote(sys.argv[2])
    driver.get('https://www.instagram.com/explore/tags/' + encodedTag + '/')
    ## 팔로우 및 좋아요 클릭 반복
    driver.find_element_by_xpath('//body//section//main//article//div/div/div/div/div[3]').click()
    time.sleep(1)
    followAndLike.followLike(driver, 3)
else:
    ## 언팔로우 체크
    detectUnFollow.detect(driver)









