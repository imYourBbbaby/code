# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import json
from scrapy_project.spider_web_settings import conf
from scrapy_project.utils import write_log

class ScrapyProjectPipeline:
    def __init__(self):
        self.file = open(f'datas/{conf["spider_target"]}-{conf["spider_index_type"]}.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        item_data = dict(item)
        if spider.name == 'anhui_hefei':
            item_data['project'] = dict(item.project)
            item_data['procurement_notice'] = dict(item.notice)
            try:
                item_data['procurement_notice']['attachments'] = [json.loads(attachment_str) for attachment_str in
                                                                  json.loads(item.notice['attachments'])]
            except Exception:
                item_data['procurement_notice']['attachments'] = []

            bid_results = []
            for bid_result in item.bid_results:
                bid_result_dic = dict(bid_result)
                bid_result_dic['attachments'] = [json.loads(attachment_str) for attachment_str in
                                                 json.loads(bid_result['attachments'])]
                bid_results.append(bid_result_dic)

            item_data['bid_results'] = bid_results
            item_data['notifications'] = [dict(notification) for notification in item.notifications]
            str_data = json.dumps(item_data, ensure_ascii=False) + ',\n'
            if self.file.write(str_data):
                try:
                    data_info = f"OK: {item.project['project_id']} : {item['title']}"
                    write_log(json.dumps(data_info, ensure_ascii=False))
                except Exception as e:
                    print(e)

        return item

    def __del__(self):
        self.file.close()
