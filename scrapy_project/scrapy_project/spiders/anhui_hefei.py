import scrapy
import json
import random
from scrapy_project.spider_web_settings import conf
from scrapy_project.items import IndexItem, BidResult, NotificationOfAward
from scrapy_project.utils import write_errs_log

spider_domain = conf['spider_domain']
spider_sub_url = conf['spider_sub_url']
spider_sub_url_first_page = conf.get('spider_sub_url_page_first', '')
spider_url_page = f'https://{spider_domain}/{spider_sub_url}/{spider_sub_url_first_page}.html'
spider_index_type = conf['spider_index_type']
spider_name = conf['spider_name']


class AnhuiHefeiSpider(scrapy.Spider):
    name = "anhui_hefei"
    if spider_name == name:
        allowed_domains = [spider_domain]
        start_urls = [spider_url_page]

    def start_requests(self):
        if spider_name != AnhuiHefeiSpider.name:
            return
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                headers={
                    'User-Agent': random.choice([
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6; rv:54.0) Gecko/20100101 Firefox/54.0",
                    ]),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, sdch, br",
                    "Accept-Language": "en-US,en;q=0.8",
                    "Cache-Control": "max-age=0",
                    "Connection": "keep-alive",
                    # "Host": IndexSpider.allowed_domains,  # 替换为你要爬取的网站域名
                    "Upgrade-Insecure-Requests": "1",
                },
                callback=self.parse,
            )

    def parse(self, response):
        node_list = response.xpath('/html/body/ul/li')
        for node in node_list:
            item = IndexItem()
            if spider_index_type == '其他交易':
                item['title'] = node.xpath('./a/@title').extract_first()
                item['date'] = node.xpath('./span/text()').extract_first()
                item['city'] = node.xpath('./a/span[@class="ewb-label1 l"]/text()').extract_first().translate(
                    {ord(i): None for i in '【】'})
                if len(node.xpath('./a/span[@class="ewb-label2 l hidden"]/text()')) > 0:
                    item['method'] = node.xpath(
                        './a/span[@class="ewb-label2 l hidden"]/text()').extract_first().translate(
                        {ord(i): None for i in '【】'})
                item['text'] = node.xpath('./a/span[@class="ewb-context l"]/text()').extract_first()
                item['details_link'] = response.urljoin(node.xpath('./a/@href').extract_first())
            elif spider_index_type == '工程建设':
                item['title'] = node.xpath('./a/@title').extract_first()
                item['date'] = node.xpath('./span/text()').extract_first()
                item['city'] = node.xpath('./a/span[@class="ewb-label1 l"]/text()').extract_first().translate(
                    {ord(i): None for i in '【】'})
                if len(node.xpath('./a/span[@class="ewb-label2 l hidden"]/text()')) > 0:
                    item['method'] = node.xpath(
                        './a/span[@class="ewb-label2 l hidden"]/text()').extract_first().translate(
                        {ord(i): None for i in '【】'})
                item['text'] = node.xpath('./a/span[@class="ewb-context l"]/text()').extract_first()
                item['details_link'] = response.urljoin(node.xpath('./a/@href').extract_first())
            elif spider_index_type == '政府采购':
                item['title'] = node.xpath('./a/@title').extract_first()
                item['date'] = node.xpath('./span/text()').extract_first()
                item['city'] = node.xpath('./a/span[@class="ewb-label1 l"]/text()').extract_first().translate(
                    {ord(i): None for i in '【】'})
                # item['status'] = node.xpath('./a/span[@class="ewb-label2 l"]/text()').extract_first()
                item['method'] = node.xpath('./a/span[@class="ewb-label3 l"]/text()').extract_first().translate(
                    {ord(i): None for i in '【】'})
                item['text'] = node.xpath('./a/span[@class="ewb-context l"]/text()').extract_first()
                item['details_link'] = response.urljoin(node.xpath('./a/@href').extract_first())
            # yield item
            yield scrapy.Request(
                url=item['details_link'],
                callback=self.parse_details,
                meta={'item': item}
            )

        # 下一页
        next_page_url = response.urljoin(response.xpath(
            '/html/body/div/ul/li[9]/a/@href').extract_first())
        if next_page_url is not None:
            print(next_page_url)
            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse,
            )
        else:
            print('Stop')

    def parse_details(self, response):
        item = response.meta['item']
        print('*' * 100)
        print(item['title'])
        self.parse_details_types(response, item, type_str=spider_index_type)

        yield item

    def parse_details_types(self, response, item, type_str=''):
        if type_str == '其他交易':
            base_node = response.xpath('/html/body/div/div[3]/div[2]/div[2]')
            node = base_node.xpath('./div[2]')
            list_nodes = base_node.xpath('./div[1]//a//text()').extract()
            if len(list_nodes) == 6:  # 招标公告/(澄清/变更公告)/中标候选人公示/中标结果公示/进场交易见证书/合同及履约
                if not self.parse_detals_procurement(response, node, item, project_blank=True, type_str=type_str,
                                                     list_nodes_cnt=len(list_nodes)):
                    data_info = {'err_msg': '爬取数据异常',
                                 'datas': json.dumps(dict(item), ensure_ascii=False)}
                    write_errs_log(json.dumps(data_info, ensure_ascii=False))
                else:
                    try:
                        self.parse_detals_bid_results(node, item, response, type_str=type_str)
                        self.parse_notifications(node, item, type_str=type_str)
                    except Exception as e:
                        data_info = {'err_msg': e,
                                     'datas': json.dumps(dict(item), ensure_ascii=False)}
                        write_errs_log(json.dumps(data_info, ensure_ascii=False))
            else:
                print(f'页面格式不符合要求: {item["title"]}\n {item["details_link"]}')
        elif type_str == '工程建设':
            base_node = response.xpath('/html/body/div/div[3]/div[2]/div[2]')
            node = base_node.xpath('./div[2]')
            list_nodes = base_node.xpath('./div[1]//a//text()').extract()
            if len(list_nodes) == 10:  # 招标计划/项目登记/招标公告/澄清/变更公告/中标候选人公示/保证金退款/中标结果公示/进场交易见证书/中标通知书/合同及履约
                try:
                    if base_node.xpath('./div[1]/a[2]//text()').extract_first() == '项目登记':
                        if self.parse_detals_project(node, item, type_str=type_str):
                            page_style = 1
                        else:
                            page_style = 0
                    else:
                        page_style = 0
                except Exception as e:
                    page_style = 0
                finally:
                    if not self.parse_detals_procurement(response, node, item, project_blank=page_style == 0,
                                                         type_str=type_str):
                        data_info = {'err_msg': '爬取数据异常',
                                     'datas': json.dumps(dict(item), ensure_ascii=False)}
                        write_errs_log(json.dumps(data_info, ensure_ascii=False))
                    else:
                        try:
                            self.parse_detals_bid_results(node, item, response, type_str=type_str)
                            self.parse_notifications(node, item, type_str=type_str)
                        except Exception as e:
                            data_info = {'err_msg': e,
                                         'datas': json.dumps(dict(item), ensure_ascii=False)}
                            write_errs_log(json.dumps(data_info, ensure_ascii=False))
            elif len(list_nodes) == 7:  # 招标计划/招标公告/(澄清/变更公告)/中标候选人公示/中标结果公示/进场交易见证书/合同及履约
                if not self.parse_detals_procurement(response, node, item, project_blank=True, type_str=type_str,
                                                     list_nodes_cnt=len(list_nodes)):
                    data_info = {'err_msg': '爬取数据异常',
                                 'datas': json.dumps(dict(item), ensure_ascii=False)}
                    write_errs_log(json.dumps(data_info, ensure_ascii=False))
                else:
                    try:
                        self.parse_detals_bid_results(node, item, response, type_str=type_str)
                        self.parse_notifications(node, item, type_str=type_str)
                    except Exception as e:
                        data_info = {'err_msg': e,
                                     'datas': json.dumps(dict(item), ensure_ascii=False)}
                        write_errs_log(json.dumps(data_info, ensure_ascii=False))
            elif len(list_nodes) == 6:  # 招标公告/(澄清/变更公告)/中标候选人公示/中标结果公示/进场交易见证书/合同及履约
                if not self.parse_detals_procurement(response, node, item, project_blank=True, type_str=type_str,
                                                     list_nodes_cnt=len(list_nodes)):
                    data_info = {'err_msg': '爬取数据异常',
                                 'datas': json.dumps(dict(item), ensure_ascii=False)}
                    write_errs_log(json.dumps(data_info, ensure_ascii=False))
                else:
                    try:
                        self.parse_detals_bid_results(node, item, response, type_str=type_str)
                        self.parse_notifications(node, item, type_str=type_str)
                    except Exception as e:
                        data_info = {'err_msg': e,
                                     'datas': json.dumps(dict(item), ensure_ascii=False)}
                        write_errs_log(json.dumps(data_info, ensure_ascii=False))
            else:
                print(f'页面格式不符合要求: {item["title"]}\n {item["details_link"]}')
        else:
            base_node = response.xpath('/html/body/div/div[3]/div[2]/div[2]')
            node = base_node.xpath('./div[2]')
            list_nodes = base_node.xpath('./div[1]//a//text()').extract()
            # print(len(list_nodes), item['details_link'])
            if len(list_nodes) == 7:  # 项目登记/采购公告/答疑变更/中标结果/进场交易见证书/中标通知书/合同及履约
                try:
                    if base_node.xpath('./div[1]/a[1]//text()').extract_first() == '项目登记':
                        if self.parse_detals_project(node, item):
                            page_style = 1
                        else:
                            page_style = 0
                    else:
                        page_style = 0
                except Exception:
                    page_style = 0
                finally:
                    if not self.parse_detals_procurement(response, node, item, project_blank=page_style == 0):
                        data_info = {'err_msg': '爬取数据异常',
                                     'datas': json.dumps(dict(item), ensure_ascii=False)}
                        write_errs_log(json.dumps(data_info, ensure_ascii=False))
                    else:
                        try:
                            self.parse_detals_bid_results(node, item, response)
                            self.parse_notifications(node, item)
                        except Exception as e:
                            data_info = {'err_msg': e,
                                         'datas': json.dumps(dict(item), ensure_ascii=False)}
                            write_errs_log(json.dumps(data_info, ensure_ascii=False))

            elif len(list_nodes) == 5:  # 采购公告/答疑变更/中标结果/进场交易见证书/合同及履约
                if not self.parse_detals_procurement(response, node, item, project_blank=True):
                    print('爬取数据异常')
                    data_info = {'err_msg': '爬取数据异常',
                                 'datas': json.dumps(dict(item), ensure_ascii=False)}
                    write_errs_log(json.dumps(data_info, ensure_ascii=False))
                else:
                    try:
                        self.parse_detals_bid_results(node, item, response)
                    except Exception as e:
                        data_info = {'err_msg': e,
                                     'datas': json.dumps(dict(item), ensure_ascii=False)}
                        write_errs_log(json.dumps(data_info, ensure_ascii=False))

    # 项目登记
    def parse_detals_project(self, node, item, type_str=''):
        try:
            if type_str == '工程建设':
                _, name, _, _id, _, approval_name, _, approval_department, _, platform, amount_title, amount, _, method, _, project_type, _, department_num, _, department_name, _, agency, _, project_date = node.xpath(
                    './div[8]//table//tr/td/text()').extract()
                item.project['project_name'] = name
                item.project['project_id'] = _id
                item.project['approval_name'] = approval_name
                item.project['approval_department'] = approval_department
                item.project['platform'] = platform
                item.project['budget_amount_unit'] = '万' if '（万元）' in amount_title else ''
                item.project['budget_amount'] = amount
                item.project['method'] = method
                item.project['project_type'] = project_type
                item.project['department_num'] = department_num
                item.project['department_name'] = department_name
                item.project['agency'] = agency
                item.project['project_date'] = project_date
                is_ok = True
            else:
                _, name, _, _id, _, purchaser, _, commission_num, _, platform, amount_title, amount, _, method, _, is_ppp, _, department_num, _, department_name, _, agency, _, project_date = node.xpath(
                    './div[6]//table//tr/td/text()').extract()
                item.project['project_name'] = name
                item.project['project_id'] = _id
                item.project['purchaser'] = purchaser
                item.project['financial_commission_num'] = commission_num
                item.project['platform'] = platform
                item.project['budget_amount_unit'] = '万' if '（万元）' in amount_title else ''
                item.project['budget_amount'] = amount
                item.project['method'] = method
                item.project['is_ppp'] = is_ppp
                item.project['department_num'] = department_num
                item.project['department_name'] = department_name
                item.project['agency'] = agency
                item.project['project_date'] = project_date
                is_ok = True

        except Exception as e:
            is_ok = False
        return is_ok

    # 采购公告 nodes_cnt   7:正常    5: 23年以前的旧版
    def parse_detals_procurement(self, response, node, item, project_blank=False, type_str='', list_nodes_cnt=0):
        try:
            if type_str == '其他交易':
                _, name, _, purchaser, _, address, _, approval_name, _, approval_department, _, department_name, _, agency, _, platform, _, procurement_date = node.xpath(
                    './div[1]/div[2]//table//tr/td/text()').extract()
                item.notice['address'] = address
                item.notice['purchaser'] = purchaser
                item.notice['procurement_date'] = procurement_date
                item.notice['title'] = None
                if list_nodes_cnt == 6:
                    item.notice['title'] = ''.join(node.xpath(
                        './div[1]/div[2]/p[1]//text()').extract())
                    if item.notice['title'] is None or item.notice['title'] == '':
                        item.notice['title'] = ''.join(node.xpath(
                            './div[1]/div[2]/div[4]/div//text()').extract())
                    if item.notice['title'] is None or item.notice['title'].strip() == '':
                        item.notice['title'] = ''.join(node.xpath(
                            './div[1]/div[2]/p[2]//text()').extract())
                    if item.notice['title'] is None:
                        item.notice['title'] = node.xpath(
                            './div[1]/div[2]/div[2]/div[1]/div[2]/div/p[1]/b[1]/span//text()').extract_first()
                        if item.notice['title'] is None:
                            item.notice['title'] = node.xpath(
                                './div[1]/div[2]/div[2]/div[1]/div[2]/div/h3//text()').extract_first()
                        if item.notice['title'] is None:
                            texts = node.xpath('./div[1]/div[2]/div[2]/div[1]/div[2]/p[1]//text()').extract()
                            if len(texts) > 0:
                                item.notice['title'] = ''.join(texts)
                        if item.notice['title'] is None or item.notice['title'] == '':
                            texts = node.xpath('./div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/p[1]//text()').extract()
                            if len(texts) > 0:
                                item.notice['title'] = ''.join(texts)
                        if item.notice['title'] is None or item.notice['title'] == '':
                            item.notice['title'] = node.xpath(
                                './div[1]/div[2]/div[4]/h3//text()').extract_first()
                        if item.notice['title'] is None or item.notice['title'] == '':
                            item.notice['title'] = node.xpath(
                                './div[1]/div[2]/p[1]//text()').extract_first()
                        if item.notice['title'] is None or item.notice['title'] == '':
                            texts = node.xpath(
                                './div[1]/div[2]/div[4]/div//text()').extract()
                            if len(texts) > 0:
                                item.notice['title'] = ''.join(texts)
                    if item.notice['title'] is None:
                        print('#####没有采购标题#####')
                    #
                    notice_contents = node.xpath(
                        './div[1]/div[2]/div[2]/div[1]/div[2]/p//text()').extract()
                    if len(notice_contents) == 0:
                        notice_contents = node.xpath(
                            './div[1]/div[2]/p//text()').extract()
                    if len(notice_contents) == 0:
                        notice_contents = node.xpath(
                            './div[1]/div[2]/div[4]//text()').extract()
                    if len(notice_contents) == 0:
                        notice_contents = node.xpath(
                            './div[1]/div[2]/div[2]/div[1]/div[2]/div/p//text()').extract()
                    if len(notice_contents) == 0:
                        notice_contents = node.xpath(
                            './div[1]/div[2]/div[4]/p[2]//text()').extract()
                    if len(notice_contents) == 0:
                        notice_contents = node.xpath(
                            './div[1]/div[2]/p//text()').extract()
                    if len(notice_contents) == 0:
                        text_nodes = node.xpath('./div[1]/div[2]/div[4]')
                        if '繁华轩' in item['title']:
                            print(text_nodes)

                    notice_content = ''
                    for content in notice_contents:
                        notice_content += content.strip() + '\n'
                    item.notice['content'] = notice_content
                    if notice_content == '':
                        print('#####没有采购内容#####')
                    # 附件
                    attachments_nodes = node.xpath(f'./div[1]/div[3]/div//a')
                    attachments = []
                    # print(item['title'], len(attachments_nodes))
                    for idx, node1 in enumerate(attachments_nodes):
                        attachment_name = node1.xpath('./@title').extract_first()
                        attachment_href = response.urljoin(node1.xpath(f'./@href').extract_first())
                        attachment = {'file_name': attachment_name, 'file_link': attachment_href}
                        attachments.append(json.dumps(attachment, ensure_ascii=False))
                    item.notice['attachments'] = json.dumps(attachments, ensure_ascii=False)
                    # print(item.notice['attachments'])

                    if project_blank:
                        item.project['project_name'] = name
                        item.project['project_id'] = ''
                        item.project['purchaser'] = purchaser
                        item.project['platform'] = platform
                        item.project['approval_name'] = approval_name
                        item.project['approval_department'] = approval_department
                        item.project['budget_amount_unit'] = ''
                        item.project['budget_amount'] = ''
                        item.project['method'] = ''
                        item.project['is_ppp'] = ''
                        item.project['department_num'] = ''
                        item.project['department_name'] = department_name
                        item.project['agency'] = agency
                        item.project['project_date'] = ''

                    is_ok = True
            elif type_str == '工程建设':
                _, name, _, purchaser, _, address, _, approval_name, _, approval_department, _, department_name, _, agency, _, platform, _, procurement_date = node.xpath(
                    './div[1]/div[2]//table//tr/td/text()').extract()
                item.notice['address'] = address
                item.notice['purchaser'] = purchaser
                item.notice['procurement_date'] = procurement_date
                item.notice['title'] = None
                if list_nodes_cnt == 6:
                    item.notice['title'] = ''.join(node.xpath(
                        './div[1]/div[2]/p[1]//text()').extract())
                    if item.notice['title'] is None or item.notice['title'] == '':
                        item.notice['title'] = ''.join(node.xpath(
                            './div[1]/div[2]/div[4]/div//text()').extract())
                    if item.notice['title'] is None or item.notice['title'].strip() == '':
                        item.notice['title'] = ''.join(node.xpath(
                            './div[1]/div[2]/p[2]//text()').extract())

                    # print('xxxxxxxx', item.notice['title'], item['details_link'])
                elif list_nodes_cnt == 7:
                    item.notice['title'] = ''.join(node.xpath(
                        './div[1]/div[2]/div[4]/h3//text()').extract())
                    if item.notice['title'] is None or item.notice['title'] == '':
                        item.notice['title'] = ''.join(node.xpath(
                            './div[1]/div[2]/p[1]//text()').extract())
                    if item.notice['title'] == '':
                        item.notice['title'] = None

                if item.notice['title'] is None:
                    item.notice['title'] = node.xpath(
                        './div[1]/div[2]/div[2]/div[1]/div[2]/div/p[1]/b[1]/span//text()').extract_first()
                    if item.notice['title'] is None:
                        item.notice['title'] = node.xpath(
                            './div[1]/div[2]/div[2]/div[1]/div[2]/div/h3//text()').extract_first()
                    if item.notice['title'] is None:
                        texts = node.xpath('./div[1]/div[2]/div[2]/div[1]/div[2]/p[1]//text()').extract()
                        if len(texts) > 0:
                            item.notice['title'] = ''.join(texts)
                    if item.notice['title'] is None or item.notice['title'] == '':
                        texts = node.xpath('./div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/p[1]//text()').extract()
                        if len(texts) > 0:
                            item.notice['title'] = ''.join(texts)
                    if item.notice['title'] is None or item.notice['title'] == '':
                        item.notice['title'] = node.xpath(
                            './div[1]/div[2]/div[4]/h3//text()').extract_first()
                    if item.notice['title'] is None or item.notice['title'] == '':
                        item.notice['title'] = node.xpath(
                            './div[1]/div[2]/p[1]//text()').extract_first()
                    if item.notice['title'] is None or item.notice['title'] == '':
                        texts = node.xpath(
                            './div[1]/div[2]/div[4]/div//text()').extract()
                        if len(texts) > 0:
                            item.notice['title'] = ''.join(texts)
                if item.notice['title'] is None:
                    print('#####没有采购标题#####')
                #
                notice_contents = node.xpath(
                    './div[1]/div[2]/div[2]/div[1]/div[2]/p//text()').extract()
                if len(notice_contents) == 0:
                    notice_contents = node.xpath(
                        './div[1]/div[2]/p//text()').extract()
                if len(notice_contents) == 0:
                    notice_contents = node.xpath(
                        './div[1]/div[2]/div[4]//text()').extract()
                if len(notice_contents) == 0:
                    notice_contents = node.xpath(
                        './div[1]/div[2]/div[2]/div[1]/div[2]/div/p//text()').extract()
                if len(notice_contents) == 0:
                    notice_contents = node.xpath(
                        './div[1]/div[2]/div[4]/p[2]//text()').extract()
                if len(notice_contents) == 0:
                    notice_contents = node.xpath(
                        './div[1]/div[2]/p//text()').extract()
                if len(notice_contents) == 0:
                    text_nodes = node.xpath('./div[1]/div[2]/div[4]')
                    if '繁华轩' in item['title']:
                        print(text_nodes)

                notice_content = ''
                for content in notice_contents:
                    notice_content += content.strip() + '\n'
                item.notice['content'] = notice_content
                if notice_content == '':
                    print('#####没有采购内容#####')
                # 附件
                attachments_nodes = node.xpath(f'./div[1]/div[3]/div//a')
                attachments = []
                # print(item['title'], len(attachments_nodes))
                for idx, node1 in enumerate(attachments_nodes):
                    attachment_name = node1.xpath('./@title').extract_first()
                    attachment_href = response.urljoin(node1.xpath(f'./@href').extract_first())
                    attachment = {'file_name': attachment_name, 'file_link': attachment_href}
                    attachments.append(json.dumps(attachment, ensure_ascii=False))
                item.notice['attachments'] = json.dumps(attachments, ensure_ascii=False)
                # print(item.notice['attachments'])

                if project_blank:
                    item.project['project_name'] = name
                    item.project['project_id'] = ''
                    item.project['purchaser'] = purchaser
                    item.project['platform'] = platform
                    item.project['approval_name'] = approval_name
                    item.project['approval_department'] = approval_department
                    item.project['budget_amount_unit'] = ''
                    item.project['budget_amount'] = ''
                    item.project['method'] = ''
                    item.project['is_ppp'] = ''
                    item.project['department_num'] = ''
                    item.project['department_name'] = department_name
                    item.project['agency'] = agency
                    item.project['project_date'] = ''

                is_ok = True
            else:
                _, name, _, purchaser, _, address, _, commission_num, _, platform, _, department_name, _, agency, _, procurement_date = node.xpath(
                    './div[1]//table//tr/td/text()').extract()
                item.notice['purchaser'] = purchaser
                item.notice['address'] = address
                item.notice['procurement_date'] = procurement_date
                item.notice['title'] = node.xpath(
                    './div[1]/div[2]/div[2]/div[1]/div[2]/div/h3/span/text()').extract_first()

                if item.notice['title'] is None:
                    item.notice['title'] = node.xpath(
                        './div[1]/div[2]/p[1]/span[1]//text()').extract_first()
                    if item.notice['title'] is None:
                        './div[1]/div[2]/p[1]/b/span'
                        texts = node.xpath(
                            './div[1]/div[2]/p[1]/b/span//text()').extract()
                        if len(texts) > 0:
                            item.notice['title'] = ''.join(texts)
                        if item.notice['title'] is None:
                            item.notice['title'] = node.xpath(
                                './div[1]/div[2]/div[4]/h3/span//text()').extract_first()
                notice_contents = node.xpath(
                    './div[1]/div[2]/div[2]/div[1]/div[2]/div/p/span/text()').extract()
                if len(notice_contents) == 0:
                    notice_contents = node.xpath(
                        './div[1]/div[2]/div[4]/p//text()').extract()
                    if len(notice_contents) == 0:
                        notice_contents = node.xpath(
                            './div[1]/div[2]/p//text()').extract()
                notice_content = ''
                for content in notice_contents:
                    notice_content += content.strip() + '\n'
                item.notice['content'] = notice_content
                # 附件
                attachments_nodes = node.xpath(f'./div[1]/div[3]/div//a')
                attachments = []

                # print(item['title'], len(attachments_nodes))
                for idx, node1 in enumerate(attachments_nodes):
                    attachment_name = node1.xpath('./@title').extract_first()
                    attachment_href = response.urljoin(node1.xpath(f'./@href').extract_first())
                    attachment = {'file_name': attachment_name, 'file_link': attachment_href}
                    attachments.append(json.dumps(attachment, ensure_ascii=False))
                item.notice['attachments'] = json.dumps(attachments, ensure_ascii=False)

                if project_blank:
                    item.project['project_name'] = name
                    item.project['project_id'] = ''
                    item.project['purchaser'] = purchaser
                    item.project['financial_commission_num'] = commission_num
                    item.project['platform'] = platform
                    item.project['budget_amount_unit'] = ''
                    item.project['budget_amount'] = ''
                    item.project['method'] = ''
                    item.project['is_ppp'] = ''
                    item.project['department_num'] = ''
                    item.project['department_name'] = department_name
                    item.project['agency'] = agency
                    item.project['project_date'] = ''
                is_ok = True
        except Exception as e:  # 采购公告出错
            # print(e)
            is_ok = False
        return is_ok

    # 中标信息
    def parse_detals_bid_results(self, node, item, response, type_str=''):
        # 清空临时记录
        if len(item.bid_results) > 0:
            item.bid_results.clear()
        # print('中标结果数量', len(node.xpath('./div[4]/div')))

        # 获取中标的结果节点列表
        for i in range(1, len(node.xpath(
                f'./div[4]/div' if type_str == '工程建设' or type_str == '其他交易' else f'./div[3]/div')) + 1):
            if i % 3 == 2:
                bid_result_node = node.xpath(
                    f'./div[4]/div[{i}]' if type_str == '工程建设' or type_str == '其他交易' else f'./div[3]/div[{i}]')
                bid_result = BidResult()
                # 标题
                bid_result_title = bid_result_node.xpath(
                    './div/div[1]/div/div/h3/span/text()').extract_first()
                if type_str == '其他交易':
                    if bid_result_title is None:
                        bid_result_title = ''.join(bid_result_node.xpath(
                            './p[1]//text()').extract())
                    if bid_result_title == '':
                        bid_result_title = None
                if bid_result_title is None:
                    bid_result_title = bid_result_node.xpath('./div/h3/span//text()').extract_first()
                    if bid_result_title is None:
                        bid_result_title = bid_result_node.xpath(
                            './div/div/div/div/p/b/span//font/text()').extract_first()
                        if bid_result_title is None:
                            bid_result_title = ''.join(bid_result_node.xpath(
                                './h1//text()').extract())
                            if bid_result_title is None or bid_result_title == '':
                                bid_result_title = ''.join(bid_result_node.xpath('./p[1]/b/span//text()').extract())
                                if bid_result_title is None:
                                    bid_result_title = ''.join(bid_result_node.xpath(
                                        './div/div[1]/div/h1/span/font/text()').extract())
                                    if bid_result_title is None or bid_result_title == '':
                                        bid_result_title = ''.join(bid_result_node.xpath(
                                            './h1/b[1]/span//text()').extract())

                if bid_result_title is None or bid_result_title == '':
                    bid_result_title = bid_result_node.xpath(
                        './div/p[1]/span//text()').extract_first()
                if bid_result_title is None or bid_result_title == '':
                    bid_result_title = bid_result_node.xpath(
                        './p/span//text()').extract_first()
                if bid_result_title is None or bid_result_title == '':
                    bid_result_title = bid_result_node.xpath(
                        './p/span//text()').extract_first()
                if bid_result_title is None or bid_result_title == '':
                    bid_result_title = bid_result_node.xpath(
                        './p[1]//text()').extract_first()
                if bid_result_title is None or bid_result_title == '':
                    bid_result_title = bid_result_node.xpath(
                        './div/div//text()').extract_first()
                if bid_result_title is None or bid_result_title == '':
                    bid_result_title = bid_result_node.xpath(
                        './div/p//text()').extract_first()

                if bid_result_title is None or bid_result_title == '':
                    bid_result_title = ''.join(bid_result_node.xpath(
                        './div/div[1]/div/p[1]//text()').extract())
                if type_str == '其他交易':
                    if bid_result_title is not None:
                        bid_result_title = bid_result_title.strip()

                if bid_result_title is None or bid_result_title == '':
                    print('没有中标结果标题', )

                # print(f'第{i // 3 + 1}分结果正文')
                # 内容
                bid_result_contents = bid_result_node.xpath(
                    './div/div[1]/div/div/p//span/text()').extract()
                bid_result_contents = [content.strip() for content in bid_result_contents]
                if len(bid_result_contents) == 0:
                    bid_result_contents = bid_result_node.xpath(
                        './div/div[1]/div/p/span//text()').extract()
                if len(''.join(bid_result_contents)) == 0:
                    bid_result_contents = bid_result_node.xpath(
                        './div/div/div/div//text()').extract()
                if len(''.join(bid_result_contents)) == 0:
                    bid_result_contents = bid_result_node.xpath(
                        './div/p//text()').extract()
                if len(''.join(bid_result_contents)) == 0:
                    bid_result_contents = bid_result_node.xpath(
                        './p//text()').extract()
                if len(''.join(bid_result_contents)) == 0:
                    bid_result_contents = bid_result_node.xpath('./div/font//text()').extract()
                if len(''.join(bid_result_contents)) == 0:
                    bid_result_contents = bid_result_node.xpath('./div//strong//font/text()').extract()

                if len(bid_result_contents) == 0:
                    print('!!!!没有中标内容')
                bid_result_content = ''
                bid_info = None
                for content in bid_result_contents:
                    if '主要标的信息' in content:  # MsoTableGrid
                        # 表格形式 class=MsoNormalTable/15 MsoTableGrid
                        table_node = bid_result_node.xpath('./div/div[1]/div//table[@class="MsoTableGrid"]')
                        if len(table_node) > 0:
                            bid_nodes_cols = table_node.xpath('./tbody/tr[1]/td')
                            bid_nodes_rows = table_node.xpath('./tbody/tr')
                            if len(bid_nodes_cols) > 2:
                                tb_dict = {(i + 1): [] for i, _ in enumerate(bid_nodes_cols)}
                                tb_dict['table_style'] = 2
                                for tr_idx in range(1, len(bid_nodes_rows) + 1):
                                    td_nodes = table_node.xpath(f'./tbody/tr[{tr_idx}]/td')
                                    for idx, td in enumerate(td_nodes):
                                        text = ''.join(td.xpath('.//text()').extract()).strip()
                                        tb_dict[idx + 1].append(text)
                                bid_info = json.dumps(tb_dict, ensure_ascii=False)
                                # print(tb_dict)
                        else:
                            table_node = bid_result_node.xpath('./div/div[1]/div/div//table')
                            if table_node is None or len(table_node) == 0:
                                table_node = bid_result_node.xpath(
                                    './/table')
                            if len(table_node) > 0:
                                bid_nodes_cols = table_node.xpath('./tbody/tr[1]/td')
                                bid_nodes_rows = table_node.xpath('./tbody/tr')
                                if len(bid_nodes_cols) > 2:
                                    tb_dict = {(i + 1): [] for i, _ in enumerate(bid_nodes_cols)}
                                    tb_dict['table_style'] = 2
                                    for tr_idx in range(1, len(bid_nodes_rows) + 1):
                                        td_nodes = table_node.xpath(f'./tbody/tr[{tr_idx}]/td')
                                        for idx, td in enumerate(td_nodes):
                                            text = ''.join(td.xpath('.//text()').extract()).strip()
                                            tb_dict[idx + 1].append(text)
                                    bid_info = json.dumps(tb_dict, ensure_ascii=False)
                                    # print(tb_dict)
                                else:
                                    # print('默认格式的表格')
                                    bid_nodes = table_node.xpath('./tbody/tr/td')
                                    tb_dict = {}
                                    if len(bid_nodes) > 0:
                                        tb_key = ''
                                        tb_value = ''
                                        for idx, bid_node in enumerate(bid_nodes):
                                            bid_infos = bid_node.xpath('.//text()').extract()
                                            bid_info = ''.join([info_str.strip() for info_str in bid_infos])
                                            if idx % 2 == 0:
                                                tb_key = bid_info
                                            else:
                                                tb_value = bid_info
                                            tb_dict[tb_key] = tb_value
                                        tb_dict = {'table_style': 1}
                                        bid_info = json.dumps(tb_dict, ensure_ascii=False)
                            else:
                                print('！！没有表格')

                    bid_result_content += content.strip() + '\n'
                    if bid_info is not None:
                        bid_result_content += bid_info + '\n'
                        bid_info = None
                bid_result['title'] = bid_result_title
                bid_result['content'] = bid_result_content

            elif i % 3 == 0:
                # print(f'第{i // 3}分结果附件')
                bid_attachments_nodes = node.xpath(
                    f'./div[4]/div[{i}]/div//a' if type_str == '工程建设' or type_str == '其他交易' else f'./div[3]/div[{i}]/div//a')
                attachments = []
                for idx, node1 in enumerate(bid_attachments_nodes):
                    attachment_name = node1.xpath('./@title').extract_first()
                    attachment_href = response.urljoin(node1.xpath(f'./@href').extract_first())
                    attachment = {'file_name': attachment_name, 'file_link': attachment_href}
                    attachments.append(json.dumps(attachment, ensure_ascii=False))
                bid_result['attachments'] = json.dumps(attachments, ensure_ascii=False)
                item.bid_results.append(bid_result)

                # print('-' * 10)

    def parse_notifications(self, node, item, type_str=''):
        # 中标通知书
        if len(item.notifications) > 0:  # 清空临时记录
            item.notifications.clear()
        try:
            # 获取中标的结果节点列表
            for i in range(1, len(node.xpath(
                    './div[10]/div' if type_str == '工程建设' or type_str == '其他交易' else './div[7]/div')) + 1):
                if i % 3 == 2:
                    notification_node = node.xpath(
                        f'./div[10]/div[{i}]' if type_str == '工程建设' or type_str == '其他交易' else f'./div[7]/div[{i}]')
                    notification = NotificationOfAward()
                    notification['title'] = notification_node.xpath('./div[1]/h3/text()').extract_first()
                    tb_node = notification_node.xpath(f'./div[1]/div[2]/table')
                    tr_nodes = tb_node.xpath('.//tr')
                    if len(tr_nodes) > 5:
                        for tr_node in tr_nodes:
                            texts = tr_node.xpath('./td//text()').extract()
                            if '标段编号' in texts[0]:
                                notification['section_num'] = texts[1] if len(texts) > 1 else ''
                            elif '标段名称' in texts[0]:
                                notification['section_name'] = texts[1] if len(texts) > 1 else ''
                            elif '建设单位' in texts[0]:
                                notification['tenderer'] = texts[1] if len(texts) > 1 else ''
                            elif '代理机构' in texts[0]:
                                notification['agency'] = texts[1] if len(texts) > 1 else ''
                            elif '中标（成交）单位' in texts[0]:
                                notification['tenderer'] = texts[1] if len(texts) > 1 else ''
                            elif '中标（成交）价' in texts[0]:
                                notification['bid_amount'] = texts[1] if len(texts) > 1 else ''
                                if '万元' in notification['bid_amount']:
                                    notification['bid_amount_unit'] = '万'
                                    notification['bid_amount'] = notification['bid_amount'].replace('万元', '')
                                elif '（万元）' in texts[0]:
                                    notification['bid_amount_unit'] = '万'
                                else:
                                    notification['bid_amount_unit'] = ''
                            elif '发放日期' in texts[0]:
                                notification['issuance_date'] = texts[1] if len(texts) > 1 else ''
                            # print(dict(notification))
                        item.notifications.append(notification)
            # if len(item.notifications) == 0:
            #     print('#### 没有中标通知书')
        except Exception as e:
            print(e)





