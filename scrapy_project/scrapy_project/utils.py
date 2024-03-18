import json
import re
from scrapy_project.spider_web_settings import conf


def write_errs_log(data):
    file = f'./datas/errs_log_{conf["spider_name"]}-{conf["spider_index_type"]}.txt'
    with open(file, mode='a+', encoding='utf-8') as f:
        f.write(data + '\n')


def write_log(data):
    file = f'./datas/log_{conf["spider_name"]}-{conf["spider_index_type"]}.txt'
    with open(file, mode='a+', encoding='utf-8') as f:
        f.write(data + '\n')


def write_list(data, file=None):
    file = file if file is not None else f'./datas/{conf["spider_target"]}-{conf["spider_index_type"]}-列表.txt'
    with open(file, mode='a+', encoding='utf-8') as f:
        f.write(data + '\n')


def write_details(data):
    file = f'./datas/{conf["spider_target"]}-{conf["spider_index_type"]}-详情.txt'
    with open(file, mode='a+', encoding='utf-8') as f:
        f.write(data + '\n')


def get_item_list(spider_name=''):
    datas = []
    try:
        path = f'./datas/蚌埠/{conf["spider_target"]}-{conf["spider_index_type"]}-列表.txt'
        with open(file=path, mode='r', encoding='utf-8') as f:
            for line in f.readlines():
                data_dict = json.loads(line)
                datas.append(data_dict)
    except Exception as e:
        print(e)
    return datas


def get_errs_urls(spider_name=''):
    datas = []
    # try:
    #     path = f'./datas/errs_log_index-政府采购2.txt'
    #
    #     with open(file=path, mode='r', encoding='utf-8') as f:
    #         for line in f.readlines():
    #             datas = json.loads(line)['datas']
    #             data_dict = json.loads(datas)
    #             datas.append(data_dict)
    # except Exception as e:
    #     print(e)
    return datas


def get_procurement_hefei(spider_name=''):
    datas = []
    try:
        path = f'./datas/procurement_hefei_政府采购.txt'
        with open(file=path, mode='r', encoding='utf-8') as f:
            for line in f.readlines():
                data = dict()
                comps = line.strip().split('🐉')
                if len(comps) != 3:
                    print(line)
                data['id_'], data['title'], data['details_link'] = comps
                datas.append(data)
    except Exception as e:
        print(e)
    return datas


def update_procurement_hefei(data):
    file = './datas/procurement_hefei_政府采购2.txt'
    write_list(data, file)
