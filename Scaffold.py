# coding: utf-8
# @author: XZ.Liu
# @date: 20180510
"""
    This class is some useful tools for BBT Anotator to interact with mongodb.break

"""
class Scafflod(object):
    def __init__():
        pass
    def pdict2Pseq(pdict):
        """
        Transfer patch type dict to patch type seq and then put it into mongoDB.

        :pdict: With keys of "ptype" means patch type, "subtype" is sub type of patch type before,
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
        
    def task2Pseq(ptype, subtype, consq = None, failp = False):
        """
        Trans