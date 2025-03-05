import time
import random
import json

def elScroll(driver, allfoll, el):
    #print("[scrolling]")
    prevHeight = 0
    for i in range(int(allfoll / 3)):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", el)

        # 스크롤 후 약간의 딜레이
        time.sleep(random.randint(1900, 2200)/1000)

        # 스크롤 element의 높이 변화가 없다면 중지
        scrollEl = driver.find_element_by_xpath('//body/div[@role="presentation"]/div/div/div[2]//ul')
        size = scrollEl.size
        height = size['height']

        #print(prevHeight, height)
        if(prevHeight != height):
            prevHeight = height
        else:
            break


def scroll(driver):

    print("scrolling")

    SCROLL_PAUSE_TIME = 2

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight-50);")
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height