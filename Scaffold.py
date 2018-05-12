# coding: utf-8
# @author: XZ.Liu
# @date: 20180510
from datetime import datetime
"""
    This class is some useful tools for BBT Anotator to interact with mongodb.break

"""
class Scaffold(object):
    def __init__(self):
        pass
    def pdict2Pseq(self, pdict):
        """
        Transform patch type dict to patch type sequence(str) and then put it into mongoDB.

        :pdict: With keys of "subtype" is sub type of patch type below,
                "consq" is consequence of bug (None if patch type is not bug at all), "failp" also
                gets meaning when patch type is bug, and it means whether the bug happens on the
                failure path.

                Patch type tree (all lowercase):
                    - 1: bug
                        - 11: semantic
                        - 12: concurrency
                        - 13: memory
                        - 14: error code
                    - 2: performance
                        - 21: speed
                        - 22: space
                    - 3: reliability
                        - 31: robust
                        - 32: error enhancement
                        - 33: annotation
                        - 34: debug
                    - 4: feature
                        - 41: new algorithm
                    - 5: maintenance
                        - 51: refactoring
                        - 52: contact changing
                Bug consequence:
                    - 0: not bug type
                    - 1: corruption
                    - 2: crash
                    - 3: error
                    - 4: deadlock
                    - 5: hang
                    - 6: leak
                    - 7: wrong
                Failure path:
                    - 0: not bug type
                    - 1: on failure path
                    - 2: not
        """
        type_dict = {
            "semantic": "11",
            "concurrency": "12",
            "memory": '13',
            "error code": "14",
            "speed": "21",
            "space": "22",
            "robust": "23",
            "error enhancement": "24",
            "annotation": "33",
            "debug": "34",
            "new algorithm": "41",
            "refactoring": "51",
            "contact changing": "52",
        }
        consq_dict ={
            "not bug type": "0",
            "corruption": "1",
            "crash": "2",
            "error": "3",
            "deadlock": "4",
            "hang": "5",
            "leak": "6",
            "wrong": "7"
        }
        failure_dict = {
            'not bug type': '0',
            'on failure path': "1",
            'not': '2'
        }
        pseq = type_dict[pdict["subtype"]] + consq_dict[pdict['consq']] + failure_dict[pdict['failp']]

        return pseq

    def mdict2Mseq(self, mdict):
        """
        Transform patch type of module dict to sequence(str).

        :type: Module sub type. The probably values are "symmetric" "asymmetric" ""

            Module type tree:
                - 1: cipher
                - 2: compress
                - 3: digest
                - 4: randc
                - 5: template
                - 6: interface
        :sync_opt: Whether the cipher in synchronous or asynchronous. Possible values are "syn" and "asyn".
            tree:
                - 1: syn
                - 2: asyn 
        """
        s_dict = {
            'cipher': '1',
            'compress': '2',
            'digest': '3',
            'randc': '4',
            'template': '5',
            'interface': '6'
        }
        sync_dict = {
            'syn': '1',
            'asyn': '2'
        }
        mseq = s_dict[mdict['type']] + sync_dict[mdict['sync_opt']]
        return mseq


    def get_timestamp(self, s):
        """ Parse timestamp from specific time string."""
        return datetime.strptime(s[:10], '%Y-%m-%d').timestamp()

    def beauty(self, dirty):
        """ 
        Get beautiful json array from data dict passed from front-end.

        :dirty: Dirty data dict throwed from front-end. Something like
                {
                    'pdict': {},
                    'mdict': {},
                    'time': '2015-05-12',
                    'cid': '1605b8471d64c855bc2493abf3adf6a1ebc3e645',
                    'lines': '-6/+2',
                    'files': '1'
                }

        :return: Beautified dict.
        """
        pseq = self.pdict2Pseq(dirty['pdict'])
        mseq = self.mdict2Mseq(dirty['mdict'])
        timestamp = self.get_timestamp(dirty['time'])
        commit_id = dirty['cid']
        size = int(dirty['lines'].split(',')[1].strip()[:-11]) + int(
            dirty['lines'].split(',')[2].strip()[:-10])
        return {
            "commit_id": commit_id,
            "pseq": pseq,
            "mseq": mseq,
            "timestamp": timestamp,
            "size": size
        }