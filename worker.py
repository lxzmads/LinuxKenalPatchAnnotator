# coding: utf-8
import os,pickle
import redis

class Worker():
    def __init__(self, redisCli):
        self.redisCli = redisCli
    def get_task_list(self):
        if os.path.exists("pipelock.lock"):
            with open("pipelock.lock", "rb") as f:
                tasklist = pickle.load(f)
                tasklist.append(0)
        else:
            # taskret = []
            with self.redisCli.pipeline() as poppipe:
                while True:
                    try:
                        poppipe.watch('bbtask')
                        tasklist = poppipe.zrange('bbtask',0,9)
                        self.task_locker(tasklist=tasklist)
                        # print(tasklist)
                        if tasklist:
                            poppipe.multi()
                            for item in tasklist:
                                poppipe.zrem('bbtask', item)
                        # else:
                        #     print('There are no more tasks for the time being.')
                            poppipe.execute()
                        break
                    except redis.exceptions.WatchError as _Ewatch:
                        continue
            if len(tasklist) == 0:
                print('All done!')
                return None
            else:
                tasklist.append(1)
                return tasklist
        return tasklist

    def task_locker(self, tasklist=None, filename='pipelock.lock'):
        if tasklist == None:
            try:
                os.remove(filename)
            except Exception as why:
                print(str(why))
        else:
            with open(filename, 'ab+') as f:
                pickle.dump(tasklist,f,0)

    def task_back2redis(self, name, taskdict, score):
        with self.redisCli.pipeline() as redisp:
            for task in taskdict:
                redisp.zadd(name, score, task)
            try:
                redisp.execute()
            except Exception as why:
                print(str(why))
                self.task_locker(taskdict, "redis.lock")
            else:
                self.task_locker(None)
