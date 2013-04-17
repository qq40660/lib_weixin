#!/usr/bin python
#coding:utf8

import re
import sys
import urllib2
from bs4 import BeautifulSoup as bs
import time
from time import clock

class BookInfo:

    book_title = ''
    book_author = ''
    book_publisher = ''
    book_stock = 0
    book_left = 0
    book_pic = ''
    book_intro = ''

    def __init__(self, title,intro,pic_url):

        self.book_title = title
        self.book_intro = intro
        self.book_pic = pic_url

def writeNewsMessage(fromUser, toUser, book_list):

    link_url = 'http://libweixin.duapp.com'
    item_list = []
    for book in book_list:
        
        item_template = ''' 
                 <item>
                 <Title><![CDATA[%s]]></Title> 
                 <Description><![CDATA[%s]]></Description>
                 <PicUrl><![CDATA[%s]]></PicUrl>
                 <Url><![CDATA[%s]]></Url>
                 </item>
        '''%(book.book_title, book.book_intro, book.book_pic, link_url)
        item_list.append(item_template)

    template = '''
             <xml>
             <ToUserName><![CDATA[%s]]></ToUserName>
             <FromUserName><![CDATA[%s]]></FromUserName>
             <CreateTime>%s</CreateTime>
             <MsgType><![CDATA[news]]></MsgType>
             <ArticleCount>%s</ArticleCount>
             <Articles>
             %s
             </Articles>
             <FuncFlag>1</FuncFlag>
             </xml> 
    '''%(toUser, fromUser, int(time.time()), len(item_list), ''.join(item_list))

    return template


def searchByTitle(title, page_num, request_time):
    
    #一次返回5个结果 default
    default_num = 5
    page_result_num = 20 #网页每次展示20个结果

    #start = clock()
    page_str = urllib2.urlopen("http://202.112.134.140:8080/opac/openlink.php?title=%s&page=%s"%(title, page_num)).read()
    #end = clock()
    #print "catch page time:"+str((end-start)/1000000)
    page_tree = bs(page_str)

    #确定起始、结束位置
    #result_num 总结果数
    result_num = int(page_tree.find('div',attrs={'class':'search_form bulk-actions'}).strong.string)
    begin = page_result_num*(page_num-1) + 5*(request_time-1) 
    end = page_result_num*(page_num-1) + 5*request_time-1
    if begin >= result_num:
        print "No More Result"
        return
    else:
        begin = 5*(request_time-1)
    if end >= result_num:
        end = result_num - page_result_num*(page_num-1)
    else:
        end = 5*request_time

    #bookInfo list
    book_items = []
    book_list = page_tree.find('ol',id="search_book_list").findAll('li')
    for book in book_list[begin:end]:
        marc_no = re.search('marc_no=(\d+)', book.a['href']).group(1)
        title = book.a.string
        author = book.p.contents[2].strip()
        publisher = book.p.contents[4].strip()
        stock = re.match(u"([\u4e00-\u9fa5]+：)(\d+)",book.p.span.contents[0].strip()).group(2)
        left = re.match(u"([\u4e00-\u9fa5]+：)(\d+)",book.p.span.contents[2].strip()).group(2)
        
        #book_no, position = getPositionByMarcNo(marc_no)

        img_url, intro = getItemInfo(marc_no)
        book_item = BookInfo(title, intro, img_url)
        print book_item.book_title
        book_items.append(book_item)
        print "%s\t%s\t%s\t%s\t%s/%s"%(title,marc_no,author,publisher,left,stock)
        #print "%s\t%s"%(img_url, intro)
        #print "\t%s\t%s"%(book_no, position)

    return book_items

def getPositionByMarcNo(marc_no):

    page_str = urllib2.urlopen("http://202.112.134.140:8080/opac/ajax_item.php?marc_no="+marc_no).read()
    page_tree = bs(page_str)
    
    m_book_no = ''
    m_position = set()
    for tr in page_tree.findAll('tr')[1:]:
        tds = tr.findAll('td')
        book_no = tds[0].string.strip()
        position = tds[3]['title'].strip()
        m_position.add(position)
        m_book_no = book_no
    position = '/'.join(m_position)

    return m_book_no, position

def getItemInfo(marc_no):

    page_str = urllib2.urlopen("http://202.112.134.140:8080/opac/item.php?marc_no=%s"%marc_no).read()
    page_tree = bs(page_str)

    #item_dict = {}
    #for item in page_tree.find('div',id='item_detail').findAll('dl'):
    #    dt = item.dt.string
    #    dd_a = item.dd.a
    #    dd = u''
    #    if dd_a:
    #        dd_a.extract()
    #        dd += dd_a.string
    #    if item.dd.string:
    #        dd += item.dd.string
    #    item_dict[dt] = dd

    #query douban
    isbn = re.search('isbn=(\d+)', page_str).group(1)
    douban_info_dict = eval(urllib2.urlopen("http://202.112.134.140:8080/opac/ajax_douban.php?isbn=%s"%isbn).read())
    img_url = douban_info_dict['image']
    intro = douban_info_dict['summary']

    #print "img:"+img_url
    #print "intro:"+intro

    return img_url, intro

    #position & book_no
    #tb = page_tree.find('table',id='item')
    #for tr in tb.findAll('tr')[1:]:
    #    tds = tr.findAll('td')
    #    book_no = tds[0].string.strip()
    #    position = tds[3]['title'].strip()
    #    status = tds[4].string.strip()
    #    print "%s\t%s\t%s"%(book_no,position,status)

    #for k in item_dict:
    #    print k+'\t'+item_dict[k]

def main():
    args = sys.argv[1:]
    page = int(args[0])
    request_time = int(args[1])

    books = searchByTitle('小王子',page,request_time)
    tt = writeNewsMessage("sujunyang","wangshu",books)
    print tt

if __name__ == '__main__':
    main()

