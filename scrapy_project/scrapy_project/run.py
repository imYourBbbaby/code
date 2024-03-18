
from scrapy_project.spider_web_settings import conf
from scrapy import cmdline

# 定义要定时执行的任务函数
def my_task():
    print("Task is running...")
    # 运行爬虫
    cmdline.execute(['scrapy', 'crawl', conf['spider_name']])


if __name__ == '__main__':
    my_task()
