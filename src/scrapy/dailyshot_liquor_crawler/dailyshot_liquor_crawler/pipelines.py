# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import requests
import json

class DailyshotLiquorCrawlerPipeline:

    API_URL = "https://tipsy.co.kr/svcmgr/api/crawled/liquor.tipsy"
    API_URL_DEV = "http://localhost:8080/svcmgr/api/crawled/liquor.tipsy"
    # 초기화 메소드
    # def __init__(self):
    #     # DB 설정(자동 커밋)
    #     # isolation_level=None => Auto Commit
    #     self.conn = 

    # 최초 1회 실행
    def open_spider(self, spider):
        spider.logger.info("LiquorSpider Pipeline Started.")
        

    # Item 별 실행
    def process_item(self, item, spider):
        if not item.get('name_en') is None:
            # 데이터가 있다면
            item['site'] = 1
        
            # 데이터 저장 API 호출
            spider.logger.info("[ ### ITEM ### ]")
            spider.logger.info(item)

            #data_json = json.dumps(dict(item), ensure_ascii=False).encode('utf8')
            data_json = json.dumps(dict(item), ensure_ascii=False, indent=4, default=lambda o: dict(o)).encode('utf-8')


            try:
                headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                    'Authorization': 'Bearer AUTOmKFxUkmakDV9w8z/yLOxrbm0WwxgbNpsOS6HhoUAGNY='
                }
                res = requests.post(self.API_URL, headers=headers, data=data_json)
            except requests.exceptions.RequestException as e:
                spider.logger.error(f"API request failed: {e}")
        else:
            raise DropItem('Dropped Item. Because This Contents is Empty')

        return item

    def close_spider(self, spider):
        spider.logger.info('LiquorSpider Pipline Stopped.')
