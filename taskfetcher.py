# coding: utf-8
# Get Tasks and put them into redis.
# @author: XZLiu
# @date: 20180506
import sys
# sys.setrecursionlimit(10000000)
import Utils
import config
from db import Db

import pickle,os,sys,datetime
import requests

from bs4 import BeautifulSoup
from datetime import datetime

dbs = Db()
redisCli = dbs.dbRedis(addrOwner='xzliu', auth=True)
# sys.setrecursionlimit(1000000)

def main():
    # commit = {'age':'','msg':'','ath':'','fls':'','lns':'','id':'','pid':'', 'typ':'0','sta':'0'}
    # from Utils import Utils
    # util = Utils(config.REFS_PATH, config.LOG_PATH)
    # if os.path.exists('refs.pickle'):
    #     try:
    #         with open('refs.pickle','rb') as f:
    #             print('\tloads from file.')
    #             refs = pickle.load(f)
    #     except Exception as why:
    #         print(str(why))
    #         exit
    # else:
    # refs = util.get_refs()
    # with open('refs.pickle','wb') as f:
    # pickle.dump(refs, f, 2)
    # print(type(refs))
    # saverefs(refs)
    with redisCli.pipeline() as redisp:
        req = requests.Session()
        # item_num = 0
        ssum = 0
        # for k,v in refs.items():
        logpath = 'https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/crypto?'
        for i in range(0, 2300, 50):
            logipath = logpath + 'id=0adb32858b0bddf4ada5f364a84ed60b196dbcda&ofs='+str(i)
            r = req.get(logipath)
            soup = BeautifulSoup(
                r.content, 'html.parser', from_encoding='utf-8')
            commit_list = soup.find(class_='nowrap').find_all('tr')[1:]
            for tr in commit_list:
                tds = tr.find_all('td')
                # commit['pid'] = v
                # commit['age'] = get_timestamp(tds[0].span.string)
                # commit['msg'] = tds[1].a.string
                cid = tds[1].a.get('href')[-40:] + '/0'
                # commit['ath'] = tds[2].get_text()
                # commit['fls'] = tds[3].string
                # commit['lns'] = tds[4].get_text()
                # print(cid)
                redisp.zadd('bbtask',0, cid)
                ssum += 1
        try:
            if ssum > 0:
                redisp.execute()
                print('total '+str(ssum) + ' ok')
        except Exception as why:
            print(str(why))

if __name__ == '__main__':
    main()