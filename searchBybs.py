#!/usr/bin python
#coding:utf8

import re
import urllib2
from bs4 import BeautifulSoup as bs
from time import clock

def searchByTitle(title, page_num, request_time):

    #start = clock()
    page_str = urllib2.urlopen("http://202.112.134.140:8080/opac/openlink.php?title=%s&page=%s"%(title, page_num)).read()
    #end = clock()
    #print "catch page time:"+str((end-start)/1000000)
    page_tree = bs(page_str)

    result_num = int(page_tree.find('div',attrs={'class':'search_form bulk-actions'}).strong.string)

    book_list = page_tree.find('ol',id="search_book_list").findAll('li')
    for book in book_list[10*(request_time-1):10*request_time-1]:
        marc_no = re.search('marc_no=(\d+)', book.a['href']).group(1)
        title = book.a.string
        author = book.p.contents[2].strip()
        publisher = book.p.contents[4].strip()
        stock = re.match(u"([\u4e00-\u9fa5]+：)(\d+)",book.p.span.contents[0].strip()).group(2)
        left = re.match(u"([\u4e00-\u9fa5]+：)(\d+)",book.p.span.contents[2].strip()).group(2)
        
        book_no, position = getPositionByMarcNo(marc_no)

        getItemInfo(marc_no)
        #print "%s\t%s\t%s\t%s\t%s/%s"%(title,marc_no,author,publisher,left,stock)
        #print "\t%s\t%s"%(book_no, position)


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

    item_dict = {}

    for item in page_tree.find('div',id='item_detail').findAll('dl'):
        dt = item.dt.string
        dd_a = item.dd.a
        dd = u''
        if dd_a:
            dd_a.extract()
            dd += dd_a.string
        if item.dd.string:
            dd += item.dd.string
        item_dict[dt] = dd

    #query douban
    isbn = re.search('isbn=(\d+)', page_str).group(1)
    douban_info_dict = eval(urllib2.urlopen("http://202.112.134.140:8080/opac/ajax_douban.php?isbn=%s"%isbn).read())
    img_url = douban_info_dict['image']
    intro = douban_info_dict['summary']

    print "img:"+img_url
    print "intro:"+intro

    #position & book_no
    tb = page_tree.find('table',id='item')
    for tr in tb.findAll('tr')[1:]:
        tds = tr.findAll('td')
        book_no = tds[0].string.strip()
        position = tds[3]['title'].strip()
        status = tds[4].string.strip()
        print "%s\t%s\t%s"%(book_no,position,status)

    for k in item_dict:
        print k+'\t'+item_dict[k]

def main():

    searchByTitle('最优',1,1)

if __name__ == '__main__':
    main()

