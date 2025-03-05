import time
import random

def followLike(driver, type):
    j = 0
    while j < 200:
        try:
            ## 팔로우 클릭 - 약간의 딜레이(5~10분)
            if type == 2 or type == 3:
                time.sleep(random.randrange(10000, 40000)/1000)
                #driver.find_element_by_class_name('sqdOP.yWX7d.y3zKF').click()
                followBtn = driver.find_element_by_xpath("//body//div[@role='dialog']/div[2]/div/article/header/div[2]/div/div[2]/button")

                if followBtn.text == "팔로우":
                    followBtn.click()


            if type == 1 or type == 3:
                ## 약간의 딜레이를 준다. (1~3분 랜덤값)
                time.sleep(random.randrange(6000, 18000)/1000)

                ## 좋아요 클릭
                driver.find_element_by_xpath("//body//div[@role='dialog']/div[2]/div/article/div[3]/section/span[1]").click()
                time.sleep(random.randrange(6000, 18000)/1000)

            ## 다음 게시물 이동 클릭
            #driver.find_element_by_class_name('_65Bje.coreSpriteRightPaginationArrow').click()
            driver.find_element_by_xpath("//body//div[@role='dialog']/div/div/div/a[2]").click()
            time.sleep(random.randrange(15000, 30000)/1000)
            j += 1
        except:
            print("[Error occurred]")
            driver.find_element_by_xpath("//body//div[@role='dialog']/div/div/div/a[2]").click()
            time.sleep(random.randrange(1000, 1800) / 1000)