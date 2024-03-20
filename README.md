# Scrapy解释与重构

## 2024.03.19
- 根据页面信息Copy了参考文件的item.py文件
- 重写了parse方法
- 添加了cate_gov_parse方法,用于'工程建设'页面的函数call_back(正在debug)

## 2024.03.20
- 完善了cate_gov_parse方法, 利用xpath将各种招标项目的url收集完毕,下一步进行页面的正则化提取