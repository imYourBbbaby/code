# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhaobiaoItem(scrapy.Item):
    project_name = scrapy.Field()  # 项目名称
    project_id = scrapy.Field()  # 项目简号
    purchaser = scrapy.Field()  # 采购人名称
    financial_commission_num = scrapy.Field()  # 财政委托编号
    platform = scrapy.Field()  # 交易平台
    budget_amount = scrapy.Field()  # 预算金额
    budget_amount_unit = scrapy.Field()  # 预算金额单位
    method = scrapy.Field()  # 采购方式/招标方式
    project_type = scrapy.Field()  # 招标项目类型
    is_ppp = scrapy.Field()  # 是否PPP项目
    department_num = scrapy.Field()  # 监督部门编号
    department_name = scrapy.Field()  # 监督部门名称
    agency = scrapy.Field()  # 代理机构
    project_date = scrapy.Field()  # 项目建立时间
    approval_name = scrapy.Field()  # 立项批文名称
    approval_department = scrapy.Field()  # 项目审批单位

    attachments = scrapy.Field()  # 附件


class ProcurementNotice(scrapy.Item):  # 采购公告
    purchaser = scrapy.Field()
    procurement_date = scrapy.Field()  # 采购公告见证时间
    address = scrapy.Field()  # 项目地址
    title = scrapy.Field()  # 公告标题
    content = scrapy.Field()  # 公告正文
    attachments = scrapy.Field()  # 附件


class QAChanges(scrapy.Item):  # 答疑变更
    ...


class BidResult(scrapy.Item):  # 中标结果
    title = scrapy.Field()
    content = scrapy.Field()
    attachments = scrapy.Field()  # 附件


class EntryTransactionCertificate(scrapy.Item):  # 进场交易见证书
    ...


class NotificationOfAward(scrapy.Item):  # 中标通知书
    title = scrapy.Field()  # 标题
    section_num = scrapy.Field()  # 标段编号
    section_name = scrapy.Field()  # 标段名称
    tenderer = scrapy.Field()  # 建设单位
    agency = scrapy.Field()  # 代理机构
    bid_amount = scrapy.Field()  # 中标（成交）价 金额
    bid_amount_unit = scrapy.Field()  # 中标（成交）价 单位
    bid_company = scrapy.Field()  # 中标单位
    issuance_date = scrapy.Field()  # 发放日期
    attachments = []  # 附件


class ContractAndPerformance(scrapy.Item):  # 合同及履约
    title = scrapy.Field()
    content = scrapy.Field()  # 正文
    attachments = []  # 附件


class IndexItem(scrapy.Item):
    # 列表栏属性
    _id = scrapy.Field()  # 数据库中表的_id
    title = scrapy.Field()  # 标题
    text = scrapy.Field()  # 文本
    city = scrapy.Field()  # 所在城市
    status = scrapy.Field()  # 状态: 正在公式/公示结束
    method = scrapy.Field()  # 采购方式: 单一来源/公开招标/竞争性磋商/...
    date = scrapy.Field()  # 日期
    details_link = scrapy.Field()  # 详情链接

    # 详情页属性
    project = ZhaobiaoItem()  # 项目登记
    notice = ProcurementNotice()  # 采购公告
    # qa = QAChanges()  # 答疑变更
    # certificate = EntryTransactionCertificate()  # 进场交易见证书
    bid_results = []  # 中标结果
    notifications = []  # 中标通知书
    sections = scrapy.Field()  # 分包
    # contracts = []  # 合同及履约

    error = scrapy.Field()  # 异常信息

