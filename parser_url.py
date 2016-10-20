# -*- coding: utf-8 -*-
import sys
import urlparse
import traceback
import time
import random
import re
from bs4 import BeautifulSoup
#import requests
from selenium import webdriver
from pyvirtualdisplay import Display
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

MODE = 0  # NOMARL MODE 

item_info = {
        #商品url
        "url":"",   
        #商品id
        "id":"",
        #商品平台，tmall or taobao
        "platform":"",
        #商品标题
        "title":"",
        #商品原价
        "full_price":"",
        #商品优惠价
        "price":"",
        #运费
        "TransportFee":"",
        #封面图
        "cover_img":"",
        #其他图
        "other_img":[],
        #库存
        "stock":"",
        #商品详情页
        "detail":"",
        #sku id及价格
        "sku_map":{},
        #套餐类型,通过sku_id关联
        "tclx":{},
        #颜色分类,通过sku_id关联
        "ysfl":{},
        }

def open_driver():
    if MODE == 1:
        # 采用request模拟http get在性能上非常有优势，但tb做了反爬，通过此模式会导致优惠价格及运输费用信息抓不到,此模式保留暂不可用。
        driver = requests.session()
    elif MODE == 0:
        # 为了解决部分字段抓不到的问题，采用webdriver的方案
        display = Display(visible=0, size=(800, 600))
        display.start()
        driver =webdriver.Chrome('chromedriver')
        #driver.implicitly_wait(1)
    return driver

def close_driver(driver):
    if MODE == 0:
        driver.close()

#获取页面
def http_get(url,driver):
    '''
    if MODE == 1:
        try:
            rsp = driver.get(index_url,headers=get_ua(index_url))
            return rsp.content
        except Exception as e:
            print("error http_get %s" % e)
            return None
    elif MODE == 0:
    '''
    try:
        driver.get(url)
        html = driver.page_source
        return html
    except Exception as e:
        print("error http_get %s" % e)
        return None

#解析tm页面
def parser_tmall(html):
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.text
        item_info["title"] = title
        try:
            main_soup = soup.find('dl',attrs={"class":"tm-price-panel"})
            full_price = main_soup.text.replace('\n','').replace('\r','').strip()
            item_info["full_price"] = full_price
        except:
            item_info["full_price"] = ''
        try:
            main_soup = soup.find('div',attrs={"class":"tm-promo-price"})
            price = main_soup.text.replace('\n','').replace('\r','').strip()
            item_info["price"] = price
        except:
            item_info["price"] = ''
        try:
            main_soup = soup.find('div',attrs={"class":"tb-postAge"})
            TransportFee  = main_soup.text.replace('\n','').replace('\r','').replace('','').strip()
            item_info["TransportFee"] = TransportFee
        except:
            item_info["TransportFee"] = ''

        try:
            main_soup = soup.find('em',attrs={"id":"J_EmStock"})
            stock  = main_soup.text.replace('\n','').replace('\r','').strip()
            item_info["stock"] = stock
            
        except:
            item_info["stock"] = ''
        try:
            main_soup = soup.find('ul',attrs={"id":"J_AttrUL"})
            detail  = main_soup.text.strip()
            item_info["detail"] = detail
        except:
            item_info["detail"] = ''

        try:
            main_soup = soup.find('ul',attrs={"id":"J_UlThumb"})
            sub_soup = main_soup.find_all('img')
            p=re.compile(r'_\d{2,3}x\d{2,3}.+$')
            cover_img = p.split(sub_soup[0].get('src'))[0]
            item_info["cover_img"] = cover_img
        except:
            item_info["cover_img"] = ''

        try:
            item_info["other_img"].append(p.split(sub_soup[1].get('src'))[0])
        except:
            pass
        try:
            item_info["other_img"].append(p.split(sub_soup[2].get('src'))[0])
        except:
            pass
        try:
            item_info["other_img"].append(p.split(sub_soup[3].get('src'))[0])
        except:
            pass
        try: 
            item_info["other_img"].append(p.split(sub_soup[4].get('src'))[0])
        except:
            pass
        try:
            sku = re.search(r'skuMap.+}}',html).group().split('skuMap     :')[-1]
            item_info['sku_map'] = sku
        except:
            item_info['sku_map'] = ''

        try:
            _main_soup = soup.find('ul',attrs={"data-property":u"颜色分类"})
            sub_soup = _main_soup.find_all('li')
            for sku in sub_soup:
                sku_id = sku.get('data-value')
                sku_name = sku.find('span').text.strip()
                item_info['ysfl'].update({sku_id:sku_name})
        except:
            item_info['yxfl'] = {}

        try:
            _main_soup = soup.find('ul',attrs={"data-property":u"套餐类型"})
            sub_soup = _main_soup.find_all('li')
            for sku in sub_soup:
                sku_id = sku.get('data-value')
                sku_name = sku.find('span').text.strip()
                item_info['tclx'].update({sku_id:sku_name})
        except:
            item_info['tclx'] = {}

#解析tb页面
def parser_taobao(html):
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.title.text
        item_info["title"] = title
        try:
            main_soup = soup.find('div',attrs={"class":"tb-property-cont"})
            full_price = main_soup.text.replace('\n','').replace('\r','').strip()
            item_info["full_price"] = full_price
        except:
            item_info["full_price"] = ''
        try:
            main_soup = soup.find('div',attrs={"class":"tb-promo-item-bd"})
            price = main_soup.text.replace('\n','').replace('\r','').strip()
            item_info["price"] = price
        except:
            item_info["price"] = ''
        try:
            main_soup = soup.find('div',attrs={"id":"J_logistic"})
            TransportFee  = main_soup.text.replace('\n','').replace('\r','').strip()
            item_info["TransportFee"] = TransportFee
        except:
            item_info["TransportFee"] = ''

        try:
            main_soup = soup.find('ul',attrs={"class":"tb-onsite-setup-options"})
            TransportFee  = main_soup.text.replace('\n','').replace('\r','').strip()
            item_info["TransportFee"] += TransportFee
        except:
            pass

        try:
            main_soup = soup.find('span',attrs={"id":"J_SpanStock"})
            stock  = main_soup.text.replace('\n','').replace('\r','').strip()
            item_info["stock"] = stock
        except:
            item_info["stock"] = ''
        try:
            main_soup = soup.find('ul',attrs={"class":"attributes-list"})
            detail  = main_soup.text.strip()
            item_info["detail"] = detail
        except:
            item_info["detail"] = ''
        try:
            main_soup = soup.find('ul',attrs={"id":"J_UlThumb"})
            sub_soup = main_soup.find_all('img')
            p=re.compile(r'_\d{2,3}x\d{2,3}.+$')
            cover_img = p.split(sub_soup[0].get('src'))[0]
            item_info["cover_img"] = cover_img
        except:
            item_info["cover_img"] = ''

        try:
            item_info["other_img"].append(p.split(sub_soup[1].get('src'))[0])
        except:
            pass
        try:
            item_info["other_img"].append(p.split(sub_soup[2].get('src'))[0])
        except:
            pass
        try:
            item_info["other_img"].append(p.split(sub_soup[3].get('src'))[0])
        except:
            pass
        try: 
            item_info["other_img"].append(p.split(sub_soup[4].get('src'))[0])
        except:
            pass
        try:
            sku_map = re.search(r'skuMap.+}}',html).group().split('skuMap     :')[-1]
            item_info['sku_map'] = sku_map
        except:
            item_info['sku_map'] = ''
        try:
            _main_soup = soup.find('ul',attrs={"data-property":u"颜色分类"})
            sub_soup = _main_soup.find_all('li')
            for sku in sub_soup:
                sku_id = sku.get('data-value')
                sku_name = sku.find('span').text.strip()
                item_info['ysfl'].update({sku_id:sku_name})
        except:
            item_info['yxfl'] = {}

        try:
            _main_soup = soup.find('ul',attrs={"data-property":u"套餐类型"})
            sub_soup = _main_soup.find_all('li')
            for sku in sub_soup:
                sku_id = sku.get('data-value')
                sku_name = sku.find('span').text.strip()
                item_info['tclx'].update({sku_id:sku_name})
        except:
            item_info['tclx'] = {}

#解析页面
def parser_url(url,driver):
    try:

        if 'item.taobao.com' in url:
            platform =  "taobao"
        elif 'detail.tmall.com' in url:
            platform = "tmall"
        else:
            print "url input error"
            return False
        item_info["platform"] = platform  
        item_info["url"] = url
        param_d = urlparse.urlparse(url).query
        param_dict = urlparse.parse_qs(param_d)
        item_info["id"] = param_dict['id']
        html = http_get(url,driver)
        if html == None:
            return
        if platform == "tmall":
            parser_tmall(html)
        elif platform == "taobao":
            parser_taobao(html)

        for k,v in item_info.items():
            print "%s:%s" % (k,v)

    except Exception as e: 
        print "%s" % traceback.print_exc()
        #print "parser failed!",e 

if __name__ == '__main__':
    if len(sys.argv) <2:
        print '''pls input url,eg:python parser_url "https://item.taobao.com/item.htm?id=521661648713"'''
        exit()
    url = sys.argv[1]
    #初始化爬虫驱动,如果批量抓取或通过其他程序调用，只需要open一次，否则影响性能。
    driver = open_driver()
    #starttime = datetime.datetime.now()

    #解析页面内容
    parser_url(url,driver)

    #endtime = datetime.datetime.now()
    #print (endtime - starttime).seconds
    #关闭爬虫驱动
    close_driver(driver)
