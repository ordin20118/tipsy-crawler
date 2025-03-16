import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from dailyshot_liquor_crawler.items import DailyshotLiquorCrawlerItem
from dailyshot_liquor_crawler.items import TastingNotesItem

# import sys
# # items.py에 대한 path 추가
# sys.path.insert(0, '../project/chat_bot_project/section01_2/section01_2')
# from items import SiteRankItems

class DailyshotSpider(scrapy.Spider):
    name = "dailyshot"
    allowed_domains = ["dailyshot.co"]
    start_urls = ["https://dailyshot.co/m/item/15061"]

    # 링크 크롤링 규칙
    # 해당 규칙을 따라서 계속 크롤링
    # rules = [
    #     Rule(LinkExtractor(allow=r'/m/item/\d+'), callback='parse', follow=True),
    # ]

    def parse_abv(self, value):
        abv = value.replace("%", "")
        if '~' in abv:
            abv_arr = abv.split("~")
            abv = abv_arr[1]
        return abv

    def start_requests(self):
        # start_id = 1    # 시작 ID
        # end_id = 30000  # 원하는 마지막 ID
        start_id = 3254  # 시작 ID
        end_id = 30000  # 원하는 마지막 ID

        for item_id in range(start_id, end_id + 1):
            url = f"https://dailyshot.co/m/item/{item_id}"
            yield scrapy.Request(url, callback=self.parse)


    def parse(self, response):

        self.logger.info(f"Processing: {response.url}")

        item = DailyshotLiquorCrawlerItem()
        tasting_notes = TastingNotesItem()
        item['url'] = response.url
        item['name_en'] = response.css('#__next > div > div.dailyshot-dgr89h > div > main > div > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(1) > div.dailyshot-Stack-root.dailyshot-1178y6y > div > div.dailyshot-Stack-root.dailyshot-16cncgc > div::text').get()
        item['name_kr'] = response.css('#__next > div > div.dailyshot-dgr89h > div > main > div > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(1) > div.dailyshot-Stack-root.dailyshot-1178y6y > div > div.dailyshot-Stack-root.dailyshot-16cncgc > h1::text').get()
        
       
        self.logger.info(f"name_en: {item['name_en']}")
        self.logger.info(f"name_kr: {item['name_kr']}")

        if item['name_en'] == None:
            return

        # abv
        # category
        # country
        # tasting notes
        elements = response.xpath('//*[@class="dailyshot-Group-root dailyshot-1lweaqt"]')
        for element in elements:
            title = element.xpath('./div/h3/text()').get()
            value = element.xpath('./div[2]/text()').get()
            self.logger.info(f"{title}:{value}")
            if title == '종류':
                item['category_name'] = value
            elif title == '용량':
                pass
            elif title == '도수':
                item['abv'] = self.parse_abv(value)
            elif title == '국가':
                item['country_name'] = value
            elif title == '지역':
                item['region_name'] = value
            elif title == '품종':
                item['variety'] = value
            elif title == 'Aroma':
                tasting_notes['nosing'] = value
            elif title == 'Taste':
                tasting_notes['tasting'] = value
            elif title == 'Finish':
                tasting_notes['finish'] = value
            elif title == '바디':
                div = div.xpath('./div')
                input = div.xpath('./input').get()
                self.logger.info(f"[input]:{input}")
                tasting_notes['body'] = int(input)
            elif title == '타닌':
                div = div.xpath('./div')
                input = div.xpath('./input').get()
                self.logger.info(f"[input]:{input}")
                tasting_notes['tannin'] = int(input)
            elif title == '당도':
                div = div.xpath('./div')
                input = div.xpath('./input').get()
                self.logger.info(f"[input]:{input}")
                tasting_notes['sweetness'] = int(input)
            elif title == '산미':
                div = div.xpath('./div')
                input = div.xpath('./input').get()
                self.logger.info(f"[input]:{input}")
                tasting_notes['acidity'] = int(input)
        
            item['tasting_notes'] = tasting_notes

        # rating_avg, rating_count, pairing
        # 와인, 샴페인인 경우
        if '와인' in item['category_name'] or '샴페인' in item['category_name']:
            # rate_avg
            rating_avg_selector = "#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(7) > div.dailyshot-Stack-root.dailyshot-1bixg60 > div > div > div.dailyshot-Text-root.dailyshot-1t1nzgw"
            rating_avg_selector_2 = "#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(9) > div.dailyshot-Stack-root.dailyshot-1bixg60 > div > div > div.dailyshot-Text-root.dailyshot-1t1nzgw"
            
            rating_avg = 0
            rating_avg_info = response.css(rating_avg_selector)
            self.logger.info(f"[rating_avg_info_1] len:{len(rating_avg_info)} / {type(rating_avg_info)}")
            if len(rating_avg_info) == 0:
                rating_avg_info = response.css(rating_avg_selector_2)
                self.logger.info(f"[rating_avg_info_2] len:{len(rating_avg_info)} / {type(rating_avg_info)}")
                if len(rating_avg_info) != 0:
                    rating_avg = rating_avg_info[0].xpath("text()").get()
                    self.logger.info(f"[rating_avg]: type:{type(rating_avg)}")
                    item['rating_avg'] = rating_avg
            else:
                rating_avg = rating_avg_info[0].xpath("text()").get()
                self.logger.info(f"[rating_avg]: type:{type(rating_avg)}")
                item['rating_avg'] = rating_avg
            self.logger.info("[rating_avg]:%s"%rating_avg)

            # rating count
            rating_count_selector = "#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(7) > div.dailyshot-Stack-root.dailyshot-1bixg60 > div > div > div.dailyshot-Stack-root.css-82a6rk.dailyshot-1kzvwqj > div:nth-child(2) > div:nth-child(1)"
            rating_count_info = response.css(rating_count_selector)
            if len(rating_count_info) > 0:
                rating_count_txt = rating_count_info[0].xpath("text()").get()
                end_idx = rating_count_txt.find("개")
                rating_count = rating_count_txt[0:end_idx].replace(",", "")
                item['rating_count'] = rating_count
                self.logger.info("[rating_count]:%s"%rating_count)
                
            # pairing
            self.logger.info("scrape pairing info ...")
            pairing_selector = "#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(7) > div:nth-child(8) > div"
            pairing_info = response.css(pairing_selector)
            if len(pairing_info) > 0:
                pairing = pairing_info[0].xpath("text()").get()
                item['pairing'] = pairing
                self.logger.info("[pairing]:%s"%pairing)
        else:
            # 리뷰 평점
            rating_avg_selector = "#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(1) > div.dailyshot-Stack-root.dailyshot-1178y6y > div > div.dailyshot-Group-root.dailyshot-k87rjc > div.dailyshot-Text-root.dailyshot-15bwq65"
            rating_info = response.css(rating_avg_selector)
            if len(rating_info) > 0:
                rating_avg = rating_info[0].xpath("text()").get()
                item['rating_avg'] = rating_avg
                self.logger.info("[rating_avg]:%s"%rating_avg)

            # 리뷰 개수
            rating_count_selector = "#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(1) > div.dailyshot-Stack-root.dailyshot-1178y6y > div > div.dailyshot-Group-root.dailyshot-k87rjc > a > span"
            rating_count_info = response.css(rating_count_selector)
            if len(rating_count_info) > 0:
                rating_count_txt = rating_count_info[0].xpath("text()").get()
                end_idx = rating_count_txt.find("개")
                rating_count = rating_count_txt[0:end_idx].replace(",", "")
                item['rating_count'] = rating_count
                self.logger.info("[rating_count]:%s"%rating_count)

        # price
        self.logger.info("scrape price ...")
        price_selector = "#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(1) > div.dailyshot-Stack-root.dailyshot-1178y6y > div > div.dailyshot-Stack-root.dailyshot-uet3or > div > div > div > span.dailyshot-Text-root.dailyshot-15bwq65"
        price_info = response.css(price_selector)
        if len(price_info) > 0:
            price = price_info[0].xpath("text()").get()
            item['price'] = price.replace(',', '')
            self.logger.info("[price]:%s"%price)

        # sumbnail
        self.logger.info("scrape thumbnail ...")
        sumbnail_selector = '#gentoo-sc > div > div > div.dailyshot-Stack-root.dailyshot-1178y6y > div:nth-child(1) > div.dailyshot-Stack-root.dailyshot-iuqr8 > div > div.dailyshot-AspectRatio-root.dailyshot-8ma7di > img'
        thumb = response.css(sumbnail_selector)
        if len(thumb) > 0:
            item['image_url'] = thumb[0].xpath("@src").get()
            self.logger.info("[image_url]:%s"%item['image_url'])
        else:
            self.logger.info("[image_url]:None")

        # description
        self.logger.info("scrape deescription ...")
        desc_selector = 'div.dailyshot-Stack-root.dailyshot-e90c5m > div.dailyshot-Stack-root.dailyshot-2ufkj3'
        desc_info = response.css(desc_selector)
        if len(desc_info) > 0:
            texts = response.xpath('//div[@class="dailyshot-Stack-root dailyshot-2ufkj3"]//p//text()').getall()
            cleaned_texts = [text.strip() for text in texts if text.strip()]
            full_text = '\n'.join(cleaned_texts)
            item['description'] = full_text
            self.logger.info("[description]:%s"%full_text)
        else:
            self.logger.info("[description]:None")

        return item
