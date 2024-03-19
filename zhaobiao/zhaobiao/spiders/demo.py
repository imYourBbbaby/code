import scrapy
import random
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class DemoSpider(scrapy.Spider):
    name = "demo"
    allowed_domains = ["ggzy.hefei.gov.cn"]
    start_urls = ["https://ggzy.hefei.gov.cn/jyxx/002001/engineer2.html", ]
    # def start_requests(self):
    #
    #     for url in self.start_urls:
    #         yield scrapy.Request(
    #             url=url,
    #             headers={
    #                 'User-Agent': random.choice([
    #                     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    #                     "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    #                     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    #                     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0",
    #                     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6; rv:54.0) Gecko/20100101 Firefox/54.0",
    #                 ]),
    #                 "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    #                 "Accept-Encoding": "gzip, deflate, sdch, br",
    #                 "Accept-Language": "en-US,en;q=0.8",
    #                 "Cache-Control": "max-age=0",
    #                 "Connection": "keep-alive",
    #                 # "Host": IndexSpider.allowed_domains,  # 替换为你要爬取的网站域名
    #                 "Upgrade-Insecure-Requests": "1",
    #             },
    #             callback=self.parse,
    #         )
    #

    def parse(self, response):

        # category_node_html 保存response用xpath提取后的大列表,该列表保存了官网页面交易分类的分块数据
        category_node_html = response.xpath('//*[@id="container"]/div[3]/div/div/div[1]/ul/li/a')
        category_node_dict = {}
        # 遍历列表,用Hash方式做到类别与url一一映射
        for node in category_node_html:
            new_node = node.xpath('./text()').extract_first()
            node_url = response.urljoin((node.xpath('./@href').extract_first()))
            category_node_dict[new_node] = node_url
        
        # print(category_node_dict)

        for cate in category_node_dict.keys():
            if cate == '工程建设':
                yield scrapy.Request(category_node_dict[cate], callback=self.cate_gov_parse, meta={'category': cate})


    # 工程建设页面
    def cate_gov_parse(self, response):
        # 解析//*[@id="container"]/div[3]/div/div/div[2]/div[2]
        gov_node_html = response
        print(gov_node_html)


        
            

        