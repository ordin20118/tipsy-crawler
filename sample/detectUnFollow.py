import time
import random
import infiniteScroll

FOLLOWER_LIMIT = 3000
FIND_NICK_NAME = "lux.una"

## 언팔로우 체크
def detect(driver):
    # https://www.instagram.com/lux.una/ 페이지로 이동
    driver.get('https://www.instagram.com/lux.una/')

    # 팔로우 버튼 클릭 - 3번째 '_81NM2' 클래스(좁은 화면 일 때), 'g47SY' 클래스(화면 넉넉)
    tabs = driver.find_elements_by_class_name("g47SY")
    i = 0
    for tab in tabs:
        i += 1
        if i == 3:
            myFollowers = int(tab.text)
            print("My All Followers Count:%d" % (myFollowers))
            tab.click()

    # 팔로워 한명 클릭 - 'Jv7Aj.MqpiF' 클래스 리스트를 받고 클릭
    # 먼저 사이즈가 어떻게 되는지 확인 -> 스크롤 필요함
    # 1. 무한 스크롤링으로 현재 나의 모든 팔로워 리스트 로드
    followerDiv = driver.find_element_by_xpath('//div[@class="isgrP"]')

    infiniteScroll.elScroll(driver, myFollowers, followerDiv)

    loadedFollowers = driver.find_elements_by_class_name("FPmhX.notranslate._0imsa")
    followerCnt = len(loadedFollowers)
    print("Loaded My Follower Count:%d" % (followerCnt))

    if followerCnt != myFollowers:
        return

    # 2. 각 팔로워들의 페이지를 들어가서 팔로우 확인
    k = 0
    for follower in loadedFollowers:
        time.sleep(random.randrange(1, 3))
        loadedFollowers = driver.find_elements_by_class_name("FPmhX.notranslate._0imsa")
        userId = loadedFollowers[k].text
        print("#### %s ####"%(userId))
        loadedFollowers[k].click()
        k += 1

        # 그 사람의 팔로우 클릭
        # 팔로우 숫자가 3000 이하일 경우 모든 리스트 로드
        # 3000이상이면 중지 - 창 닫고 뒤로가기
        isCrawlThisUser = True
        tabs = driver.find_elements_by_class_name("g47SY")
        i = 0
        userFollowers = 0
        for tab in tabs:
            i += 1
            if i == 3:
                userFollowers = int(tab.text.replace(',', ""))
                print("User's All Followers Count:%d" % (userFollowers))
                if(userFollowers > FOLLOWER_LIMIT):
                    isCrawlThisUser = False
                tab.click()

        if isCrawlThisUser:
            isFind = False
            # 팔로우 리스트에서 루스우나 존재 체크
            # 1. 팔로워 리스트 모두 로드
            userFollowerDiv = driver.find_element_by_xpath('//div[@class="isgrP"]')

            try:
                infiniteScroll.elScroll(driver, userFollowers, userFollowerDiv)
            except:
                continue;


            userLoadedFollowers = driver.find_elements_by_class_name("FPmhX.notranslate._0imsa")
            # 2. 반복문으로 lux.una 확인
            for follower in userLoadedFollowers:
                if follower.text == FIND_NICK_NAME:
                    #print("[Find Lux.Una!!]")
                    isFind = True

            # FPmhX notranslate  _0imsa
            if isFind:
                print("%s follow lux.una" % (userId))
                time.sleep(1)
                driver.back()
                time.sleep(random.randrange(1, 3))
                driver.back()
            else:
                print("%s not follow lux.una !!!" % (userId))
                time.sleep(1)
                driver.back()
                time.sleep(2)
                # 언팔로우하기
                #driver.find_element_by_class_name("_5f5mN.-fzfL._6VtSN.yZn4P").click() # 3번째 버튼
                # buttons = driver.find_elements_by_tag_name("button")
                # b = 0
                # for button in buttons:
                #     b += 1
                #     if b == 2:
                #         button.click()

                isFollow = driver.find_element_by_xpath('//div[@id="react-root"]//section//main//div//header//section//div//button').text
                if isFollow == "메시지 보내기":
                    #driver.find_element_by_xpath('//div[@id = "react-root"]//section//main//div//header//section//div//div[2]//div//span//span//button').click()
                    driver.find_element_by_xpath('//div[@id = "react-root"]//section//main//div//header//section//div//div[2]').click()
                    time.sleep(random.randrange(1, 3))
                    # driver.find_element_by_class_name("aOOlW.-Cab_").click()
                    driver.find_element_by_xpath('//button[text()="팔로우 취소"]').click()
                    print("Unfollow %s success ~,~" % (userId))
                    time.sleep(random.randrange(1, 3))
                    driver.back()
                # 팔로우 li, 숫자부분 li
                #// div[ @ id = "react-root"] // section // main // div // header // section // ul // li[3]
                #//div[@id="react-root"]//section//main//div//header//section//ul//li[3]/a/span
                # 팔로우 취소 버튼
                #//div[@id="react-root"]//section//main//div//header//section//div//button
                # 위의 버튼의 text가 "메시지 보내기"이면 팔로우상태, "팔로우"이면 언팔 상태이다.
                #//div[@id = "react-root"]//section//main//div//header//section//div//div[2]//div//span//span//button
        else:
            time.sleep(random.randrange(2, 4))
            driver.back()
            time.sleep(random.randrange(2, 4))
            driver.back()

        # 팔로워창 닫기
        # driver.find_element_by_class_name("_8-yf5").click()
        # time.sleep(2)
        # buttons = driver.find_elements_by_class_name("QBdPU")  # 2번째 아이템임 xpath로 가능한가
        # b = 0
        # for button in buttons:
        #     b += 1
        #     if b == 2:
        #         button.click()
        #driver.execute_script("arguments[0].click();", cancelBtn)
        # 뒤로가기











