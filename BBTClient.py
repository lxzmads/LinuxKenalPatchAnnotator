# coding: utf-8
import _tkinter
import tkinter as tk
from tkinter.ttk import *
from tkinter import ttk
from tkinter.messagebox import *
from db import Db
import redis
from worker import Worker
import config
import webbrowser
import time
import requests
from bs4 import BeautifulSoup
from Scaffold import Scaffold
import csv
import config



class BBTA():
    def __init__(self, worker):
        self.okkey = config.OKKEY
        self.rkey = config.RKEY
        self.mkey = config.MKEY
        self.scaffold = Scaffold()
        self.dbs = Db()
        self.mongoCli = self.dbs.dbMongo(addrOwner='xzliu',authDb='bbt')
        self.mongod = self.mongoCli.bbt
        self.bulk = self.mongod[self.mkey].initialize_unordered_bulk_op()
        self.req = requests.Session()
        self.currentTask = {}
        self.currentPdict = {}
        self.currentMdict = {}
        self.INIT_STATE = 1
        self.BEFORE_STATE = 2
        self.IN_STATE = 3
        self.AFTER_STATE = 4
        self.tasklist = []
        self.currentIndex = 0
        self.currentState = 0
        self.ret = []
        self.cant = []
        self.oklist = []
        self.w = worker
        self.root = tk.Tk()
        self.root.resizable(0, 0)
        self.root.title('XMU BBTeam Data Anotator')
        self.root.protocol('WM_DELETE_WINDOW', self.exit_task)
        self.tabControl = ttk.Notebook(self.root)  # Create Tab Control
        self.tab1 = ttk.Frame(self.tabControl)  # Create a tab
        self.tabControl.add(self.tab1, text='Work')  # Add the tab
        self.tab2 = ttk.Frame(self.tabControl)  # Add a second tab
        self.tabControl.add(self.tab2, text='Help')  # Make second tab visible
        self.tabControl.pack(expand=1, fill="both")  # Pack to make visible

        Label(
            self.tab2,
            text=
            'Simple Annotator For Linux Kernal Annotation.\n\nJust click and click and work done : ) \n\n  Author: 0xygen\n  Contact: lxzmads@gmail.com',
            # background='gray',
            width=40,
            # wraplength=80,
            anchor='w').grid(
                row=0, column=0, pady=100, padx=70)

        self.lfState = LabelFrame(self.tab1, text='DashBoard:')
        self.lfState.grid(column=0, row=0, padx=8, pady=4)
        ################################################
        Label(self.lfState, text='Remaining:').grid(row=0, column=0,sticky='e')
        self.remainMsg = tk.IntVar()
        self.lRemainMsg = Label(self.lfState, textvariable=self.remainMsg, width=20,foreground='blue')
        self.lRemainMsg.grid(row=0, column=1, padx=20, sticky='w')
        self.bGetTask = Button(self.lfState, text='Get Task', width=10 ,command=self.get_task)
        self.bGetTask.grid(row=0, column=2, padx=10, pady=10, sticky='e')
        ################################################
        Label(self.lfState, text='Completed:').grid(row=1, column=0, sticky='e')
        self.completedMsg = tk.IntVar()
        self.lcompletedMsg = Label(self.lfState, textvariable=self.completedMsg, width=20, foreground='green')
        self.lcompletedMsg.grid(row=1, column=1, padx=20, sticky='w')
        self.bSubmit = Button(self.lfState, text='Submit', width=10, command=self.submit_task, state='disabled')
        self.bSubmit.grid(row=1, column=2, padx=10, pady=10, sticky='e')

        ################################################

        ################################################

        Label(self.lfState, text='Passed:').grid(row=2, column=0, sticky='e')
        self.passMsg = tk.IntVar()
        self.lPassMsg = Label(
            self.lfState, textvariable=self.passMsg, width=20, foreground='red')
        self.lPassMsg.grid(row=2, column=1, padx=20, pady=10, sticky='w')
        ################################################

        self.lfGround = LabelFrame(self.tab1, text='Commit Id:  ')
        self.lfGround.grid(column=0, row=1, padx=8, pady=4)

        self.lableP = tk.Frame(self.lfGround)
        self.lableP.pack()
        # self.lfGround.propagate(0)

        self.patchTypes = [
            'bug', 'performance', 'reliability', 'feature', 'maintenance'
        ]
        self.bugTypes = ['semantic', 'concurrency', 'memory', 'error code']
        self.performTypes = ['speed', 'space']
        self.reliabilityTypes = [
            'robust', 'error enhancement', 'annotation', 'debug'
        ]
        self.features = ['new algorithm']
        self.maintenances = ['refactoring', 'contact changing']
        self.bugConseqs = [
            'corruption', 'crash', 'error', 'deadlock', 'hang', 'leak', 'wrong'
        ]

        Label(
            self.lableP, text='Patch Type: ').grid(
                row=0, column=0, sticky='w', padx=2, pady=2)
        self.cbTypes = Combobox(
            self.lableP, width=10, textvariable=tk.StringVar(), state='disabled', values=self.patchTypes)
        self.cbTypes.grid(row=0, column=1, sticky='w', padx=2, pady=2)
        # self.cbTypes.set(self.patchTypes[0])
        self.cbTypes.bind("<<ComboboxSelected>>", self.cbBugCallback)

        Label(
            self.lableP, text='Sub Type: ').grid(
                row=1, column=0, sticky='w', padx=2, pady=2)
        self.cbSubTypes = Combobox(
            self.lableP, width=10, textvariable=tk.StringVar(), state='disabled')
        self.cbSubTypes.grid(row=1, column=1, sticky='w', padx=2, pady=2)
        # self.cbTypes.set(self.patchTypes[0])
        Label(
            self.lableP, text='Bug Consequence: ').grid(
                row=2, column=0, sticky='w', padx=2, pady=2)
        self.cbBugCons = Combobox(
            self.lableP, width=10, textvariable=tk.StringVar(), state='disabled')
        self.cbBugCons.grid(row=2, column=1, sticky='w', padx=2, pady=2)
        self.cbBugCons.configure(values=self.bugConseqs)

        self.isFp = tk.IntVar()
        self.ckFp = tk.Checkbutton(self.lableP, text="Failure Path", variable=self.isFp, state='disabled')
        self.ckFp.grid(column=3, row=2, sticky='w')
        self.isFp.trace('w', self.fpCallback)
        self.currentPdict['failp'] = 'not'

        Label(
            self.lableP, text='Module Type:').grid(
                row=0, column=2, sticky='w', padx=2, pady=2)
        self.modules = [
            'cipher', 'compress', 'digest', 'randc', 'template', 'interface'
        ]
        self.cbCtyptos = Combobox(
            self.lableP, width=10, textvariable=tk.StringVar(), state='disabled', values=self.modules)
        self.cbCtyptos.grid(row=0, column=3, sticky='w', padx=2, pady=2)

        self.isSyn = tk.IntVar()
        self.ckSyn = tk.Checkbutton(
            self.lableP, text="Syn Option", variable=self.isSyn, state='disabled')
        self.ckSyn.grid(column=3, row=1, sticky='w')
        self.isSyn.trace('w', self.synCallback)
        self.currentPdict['failp'] = 'not'
        self.currentMdict['sync_opt'] = 'syn'
        #################################################
        self.ctrlP = tk.Frame(self.lfGround)
        self.ctrlP.pack()
        self.bOpen = Button(self.ctrlP, text='Open', width=10, command=self.open_task, state='disabled')
        self.bOpen.grid(row=1, column=0, padx=10, pady=10)
        self.bSaveTask = Button(self.ctrlP, text='Save', width=10, state='disabled', command=self.save_task)
        self.bSaveTask.grid(row=1, column=1, padx=10, pady=10)
        self.bPassTask = Button(self.ctrlP, text='Pass', width=10, state='disabled', command=self.pass_task)
        self.bPassTask.grid(row=1, column=2, padx=10, pady=10)
        self.bNext = Button(self.ctrlP, text='Next', width=10, state='disabled', command=self.next_task)
        self.bNext.grid(row=1, column=3, padx=10, pady=10)

    def synCallback(self, *args):
        if self.isSyn.get():
            # showinfo(message='ok')
            self.currentMdict['sync_opt'] = 'syn'
        else:
            self.currentMdict['sync_opt'] = 'asyn'

    def cbBugCallback(self, *args):
        # 'bug', 'performance', 'reliability', 'feature', 'maintenance'
        if self.cbTypes.get() == 'bug':
            self.cbBugCons.configure(state='readonly')
            self.cbSubTypes.configure(state='readonly')
            self.ckFp.configure(state='normal')
        else:
            self.cbSubTypes.set('not bug type')
            self.cbBugCons.set('not bug type')
            self.cbBugCons.configure(state='disabled')
            self.ckFp.configure(state='disabled')
            self.cbSubTypes.configure(state='readonly')

        if self.cbTypes.get() == 'bug':
            self.cbSubTypes.configure(values=self.bugTypes)
            self.cbSubTypes.set(self.bugTypes[0])
        elif self.cbTypes.get() == 'performance':
            self.cbSubTypes.configure(values=self.performTypes)
            self.cbSubTypes.set(self.performTypes[0])
        elif self.cbTypes.get() == 'reliability':
            self.cbSubTypes.configure(values=self.reliabilityTypes)
            self.cbSubTypes.set(self.reliabilityTypes[0])
        elif self.cbTypes.get() == 'feature':
            self.cbSubTypes.configure(values=self.features)
            self.cbSubTypes.set(self.features[0])
        elif self.cbTypes.get() == 'maintenance':
            self.cbSubTypes.configure(values=self.maintenances)
            self.cbSubTypes.set(self.maintenances[0])

    def fpCallback(self, *args):
        if self.isFp.get():
            self.currentPdict['failp'] = 'on failure path'
        else:
            self.currentPdict['failp'] = 'not'

    def start(self):
        self.root.mainloop()

    def get_task(self):
        self.currentIndex = 0
        self.tasklist = self.w.get_task_list()
        # time.sleep(5)
        # print(self.tasklist)
        if self.tasklist == None:
            showinfo(message = 'Congratulations! All tasks are done.')
            # self.initState()
            self.bGetTask.configure(state='disabled')
            self.submit_task()
        else:
            if self.tasklist[-1] == 0:
                showinfo(message='Load task from lock!')
            # self.initState()
            # print(self.tasklist)
            self.tasklist.pop()
            self.beforeTaskState()

    def submit_task(self):
        self.w.task_back2redis(self.okkey, self.ret, 1)
        self.w.task_back2redis(self.rkey, self.cant, 1)
        try:
            self.bulk.execute()
        except Exception as why:
            print('submit_task' + str(why))
        # self.completedMsg.set(0)
        self.ret = []
        self.cant = []
        self.currentMdict = {}
        self.currentPdict = {}
        self.currentTask =  {}
        self.initState()

#################################################
    def initState(self):
        self.currentState = self.INIT_STATE
        self.remainMsg.set(0)
        # self.lRemainMsg.configure(text=len(self.tasklist), foreground='blue')
        self.bGetTask.configure(state='disabled')
        self.passMsg.set(0)
        self.completedMsg.set(0)

        self.bPassTask.configure(state='disabled')
        self.bSaveTask.configure(state='disabled')
        self.bNext.configure(state='disabled')
        self.bGetTask.configure(state='normal')
        self.bSubmit.configure(state='disabled')

        self.ckSyn.configure(state='disabled')
        self.cbCtyptos.configure(state='disabled')
        self.cbTypes.configure(state='disabled')
        self.cbSubTypes.configure(state='disabled')
        self.cbBugCons.configure(state='disabled')
        self.ckFp.configure(state='disabled')


    def beforeTaskState(self):
        self.currentState = self.BEFORE_STATE
        self.root.title('Current: ' + str(self.currentIndex))
        self.lfGround.configure(
            text='Commit Id:' + self.tasklist[self.currentIndex].decode().split('/')[0])
        self.bOpen.configure(state='normal')
        self.remainMsg.set(len(self.tasklist))
        self.bPassTask.configure(state='disabled')
        self.bSaveTask.configure(state='disabled')
        self.bNext.configure(state='disabled')
        self.bGetTask.configure(state='disabled')

        self.ckSyn.configure(state='disabled')
        self.cbCtyptos.configure(state='disabled')
        self.cbTypes.configure(state='disabled')
        self.cbSubTypes.configure(state='disabled')
        self.cbBugCons.configure(state='disabled')
        self.ckFp.configure(state='disabled')


    def inTaskState(self):
        self.currentState = self.IN_STATE
        self.bSaveTask.config(state='normal')
        self.bPassTask.config(state='normal')
        self.bNext.config(state='disabled')

        self.ckSyn.configure(state='normal')
        self.cbCtyptos.configure(state='readonly')
        self.cbTypes.configure(state='readonly')
        self.cbSubTypes.configure(state='disabled')
        self.cbBugCons.configure(state='disabled')
        self.ckFp.configure(state='disabled')


    def afterTaskState(self):
        self.completedMsg.set(self.completedMsg.get()+1)
        # lFinMsg.config(text=str(int(lFinMsg.cget('text')) + 1))
        self.remainMsg.set(self.remainMsg.get()-1)
        self.currentState = self.AFTER_STATE
        if len(self.tasklist) == 0:
            self.bSubmit.config(state='normal')
            self.bNext.configure(state='disabled')
            self.bOpen.configure(state='disabled')
            self.bPassTask.configure(state='disabled')
            self.bSaveTask.configure(state='disabled')
        else:
            self.bSubmit.config(state='disabled')
            self.bNext.configure(state='normal')
            self.bOpen.configure(state='disabled')
            self.bPassTask.configure(state='disabled')
            self.bSaveTask.configure(state='disabled')

            self.ckSyn.configure(state='disabled')
            self.cbCtyptos.configure(state='disabled')
            self.cbTypes.configure(state='disabled')
            self.cbSubTypes.configure(state='disabled')
            self.cbBugCons.configure(state='disabled')
            self.ckFp.configure(state='disabled')

    def open_task(self):
        print(self.lfGround.cget('text').split(':'))
        url = self.get_url(self.lfGround.cget('text').split(':')[1])
        r = self.req.get(url)
        soup = BeautifulSoup(
            r.content, 'html.parser', from_encoding='utf-8')
        time = soup.find(class_='commit-info').find_all('tr')[1].find_all('td')[1].string
        lines = soup.find(class_='diffstat-summary').string
        cid = self.lfGround.cget('text').split(':')[1]
        self.currentTask['time'] = time
        self.currentTask['lines'] = lines
        self.currentTask['cid'] = cid
        print(self.currentTask)
        webbrowser.open(url)
        self.inTaskState()

    def pass_task(self):
        t = str(self.tasklist[self.currentIndex].decode().split('/')[0])
        status = int(self.tasklist[self.currentIndex].decode().split('/')[1])
        # self.lRemainMsg.configure(text=str(int(self.lRemainMsg.cget('text')) - 1))
        self.cant.append(t + '/' + str(status + 1) + '/' + config.NICK_NAME)
        # print(self.cant)
        self.tasklist.pop(self.currentIndex)
        self.currentIndex -= 1
        self.afterTaskState()
        # display_task()

    def next_task(self):
        self.currentIndex += 1
        self.beforeTaskState()

    def save_task(self):
        if self.cbSubTypes.get():
            self.currentPdict['subtype'] = self.cbSubTypes.get()
        else:
            showinfo(message="Please select subtype.")
            return None
        self.currentPdict['consq'] = self.cbBugCons.get()
        if self.cbCtyptos.get():
            self.currentMdict['type'] = self.cbCtyptos.get()
        else:
            showinfo(message="Please select crypto module type.")
            return None

        self.currentTask['pdict'] = self.currentPdict
        self.currentTask['mdict'] = self.currentMdict
        print(self.currentTask)
        ret = self.scaffold.beauty(self.currentTask)
        # print(ret)
        # showinfo(message='waiting')
        if not self.mongod[self.mkey].find_one({'commit_id': ret['commit_id']}):
            self.bulk.find({'commit_id': ret['commit_id']}).upsert().update_one(
                {
                    '$setOnInsert': {
                        'commit_id': ret['commit_id'],
                        'timestamp': ret['timestamp'],
                        'pseq': ret['pseq'],
                        'mseq': ret['mseq'],
                        'size': ret['size']
                    }
                }
            )
        # showinfo(message='ok')
        # print(self.currentTask)
        # print(ret)
        # lStateMsg.config(text=str(int(lStateMsg.cget('text')) - 1))
        t = str(self.tasklist[self.currentIndex].decode().split('/')[0])
        status = int(self.tasklist[self.currentIndex].decode().split('/')[1])
        self.ret.append(t + '/' + str(status + 1) + '/' + config.NICK_NAME)
        self.tasklist.pop(self.currentIndex)
        # pt = self.cbTypes.get()
        # Get information we need and put it into mongo.
        # ct = self.cbCtyptos.get()
        # showinfo(message=pt)
        self.afterTaskState()

    def exit_task(self):
        try:
            self.bulk.execute()
        except Exception as why:
            print(why)
            # continue
        if self.currentState == self.INIT_STATE:
            self.root.quit()
            self.root.destroy()
            exit()
        else:
            print(self.ret)
            print(self.cant)
            print(self.tasklist)
            if len(self.ret) != 0:
                self.w.task_back2redis(self.okkey, self.ret, 1)
            if len(self.cant) != 0:
                self.w.task_back2redis(self.rkey, self.cant, 1)
            if len(self.tasklist) != 0:
                self.w.task_back2redis(self.rkey, self.tasklist, 0)
            self.root.quit()
            self.root.destroy()
            exit()

    def get_url(self, cid):
        return config.COMMIT_PATH+'id='+cid


# for item in self.types:
# typelist.insert(0,item)

# typelist.pack()
# self.lfState.pack()
# self.lfGround.pack()


if __name__ == '__main__':
    dbs = Db()
    redisCli = dbs.dbRedis(addrOwner='xzliu', auth=True)
    worker = Worker(redisCli)
    app = BBTA(worker)

    app.start()