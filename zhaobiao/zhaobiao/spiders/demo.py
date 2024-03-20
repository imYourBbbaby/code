import scrapy

abs_domain = "https://ggzy.hefei.gov.cn"

class DemoSpider(scrapy.Spider):
    name = "demo"
    allowed_domains = ["ggzy.hefei.gov.cn"]
    start_urls = ["https://ggzy.hefei.gov.cn/jyxx/002001/engineer2.html", ]

    def parse(self, response):
        category_node_html = response.xpath('//*[@id="container"]/div[3]/div/div/div[1]/ul/li/a')
        category_node_dict = {}

        for node in category_node_html:
            category = node.xpath('./text()').extract_first()
            category_url = response.urljoin(node.xpath('./@href').extract_first())
            category_node_dict[category] = category_url

        for category, category_url in category_node_dict.items():
            yield scrapy.Request(category_url, callback=self.cate_gov_parse, meta={'category': category})

    def cate_gov_parse(self, response):
        category = response.meta['category']
        category_mapping = {
            '工程建设': 7,
            '政府采购': 6,
            '土地矿权': 3,
            '农村产权': 3,
            '其他交易': 4,
            '非进场交易项目': 3
        }

        if category in category_mapping:
            gov_node_xpath = f'//*[@id="container"]/div[3]/div/div/div[2]/div[1]/ul/li[{category_mapping[category]}]/@data-url'
            gov_node_html = response.xpath(gov_node_xpath).get()
            print(abs_domain + gov_node_html)
            yield scrapy.Request(abs_domain + gov_node_html, callback=self.info_parse, meta={'category': category})

    def info_parse(self, response):
        print(response.body.decode('utf-8'))
