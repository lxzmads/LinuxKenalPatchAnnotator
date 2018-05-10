#coding: utf-8
# Linux kernel's Pages' Common Utils
# @author: XZLiu
# @date: 20180506

import requests
from bs4 import BeautifulSoup
import io,sys,re

# sys.stdout = io.TextIOWrapper(
    # sys.stdout.buffer, encoding='utf-8')

class Utils(object):
    def __init__(self, refspath, logpath):
        self.refspath = refspath
        self.logpath = logpath
    def get_refs(self):
        rq = requests.Session()
        refs = rq.get(self.refspath)
        # print(type(refs.content))
        soup = BeautifulSoup(refs.content, 'html.parser', from_encoding='utf-8')
        # print(soup.original_encoding)
        trs = soup.find(class_='nowrap').find_all('tr')
        # print(trs)
        versions = {}

        for tr in trs[4:]:
            v = tr.td.a
            # print(v)
            if re.match(r'^v\d\.\d(\.\d{1,2})?$',v.string):
                href = 'https://git.kernel.org'+v.get('href')
                # print(href)
                taginfo = rq.get(href)
                soup = BeautifulSoup(taginfo.content, 'html.parser', from_encoding='utf-8')
                hid = soup.find(class_='sha1').a.get('href')[-40:]
                # print(hid)
                versions[v.string] = hid
                # print(tree)
                # doc = config.LOG_PATH+'h='+v.string+'&id='+hid
                # print(doc)
                # soup = BeautifulSoup(gitinfo.content, 'html.parser', from_encoding='utf-8')
                # tree = 'https://git.kernel.org' + soup.find_all(class_='sha1')[1].a.href
                # versions[v] =
                # break
        return versions

    def get_logpath(self, h, hid):
        return self.logpath + 'h=' + h + '&id=' + hid
