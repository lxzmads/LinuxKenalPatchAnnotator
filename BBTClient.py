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

class BBTA():
    def __init__(self, worker):
        self.INIT_STATE = 1
        self.BEFORE_STATE = 2
        self.IN_STATE = 3
        self.AFTER_STATE = 4
        self.tasklist = []
        self.currentIndex = 0
        self.currentState = 0
        self.ret = []
        self.cant = []
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
        Label(self.lableP, text='PT: ').grid(row=0, column=0, sticky='w')
        self.types = ['Bugs', 'Performance', 'Reliability', 'Maintenance']
        self.cbTypes = Combobox(
            self.lableP, width=10, textvariable=tk.StringVar(), state='readonly')
        self.cbTypes['values'] = self.types
        self.cbTypes.grid(row=0,column=1, sticky='w')
        self.cbTypes.set(self.types[0])

        Label(self.lableP, text='CT:').grid(row=0, column=2, sticky='w')
        self.cryptos = ['Symmetrical', 'Asymmetric', 'Hash']
        self.cbCtyptos = Combobox(
            self.lableP, width=10, textvariable=tk.StringVar(), state='readonly')
        self.cbCtyptos['values'] = self.cryptos
        self.cbCtyptos.grid(row=0, column=3, sticky='w')
        self.cbCtyptos.set(self.cryptos[0])
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

    def start(self):
        self.root.mainloop()

    def get_task(self):
        self.currentIndex = 0
        self.tasklist = self.w.get_task_list()
        # time.sleep(5)
        print(self.tasklist)
        if self.tasklist == None:
            showinfo(message = 'Congratulations! All tasks are done.')
            # self.initState()
            self.bGetTask.configure(state='disabled')
        else:
            if self.tasklist[-1] == 0:
                showinfo(message='Load task from lock!')
            # self.initState()
            # print(self.tasklist)
            self.tasklist.pop()
            self.beforeTaskState()

    def submit_task(self):
        self.w.task_back2redis('bbfin', self.ret, 1)
        self.w.task_back2redis('bbtask', self.cant, 1)
        # self.completedMsg.set(0)
        self.ret = []
        self.cant = []
        self.initState()



#################################################
    def initState(self):
        self.currentState = self.INIT_STATE
        self.remainMsg.set(len(self.tasklist))
        # self.lRemainMsg.configure(text=len(self.tasklist), foreground='blue')
        self.bGetTask.configure(state='disabled')
        self.passMsg.set(0)
        self.completedMsg.set(0)


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


    def inTaskState(self):
        self.currentState = self.IN_STATE
        self.bSaveTask.config(state='normal')
        self.bPassTask.config(state='normal')
        self.bNext.config(state='disabled')


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

    def open_task(self):
        print(self.lfGround.cget('text').split(':'))
        url = self.get_url(self.lfGround.cget('text').split(':')[1])
        webbrowser.open(url)
        self.inTaskState()

    def pass_task(self):
        t = str(self.tasklist[self.currentIndex].decode().split('/')[0])
        status = int(self.tasklist[self.currentIndex].decode().split('/')[1])
        # self.lRemainMsg.configure(text=str(int(self.lRemainMsg.cget('text')) - 1))
        self.cant.append(t + '/' + str(status + 1) + '/' + config.NICK_NAME)
        # print(self.cant)
        self.tasklist.pop(self.currentIndex)
        self.afterTaskState()
        # self.currentIndex += 1
        # display_task()

    def next_task(self):
        self.currentIndex += 1
        self.beforeTaskState()

    def save_task(self):

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
        if self.currentState == self.INIT_STATE:
            self.root.quit()
            self.root.destroy()
            exit()
        else:
            if len(self.ret) != 0:
                self.w.task_back2redis('t_bbfin', self.ret, 1)
            if len(self.cant) != 0:
                self.w.task_back2redis('t_bbtask', self.cant, 1)
            if len(self.tasklist) != 0:
                self.w.task_back2redis('t_bbtask', self.tasklist, 0)
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