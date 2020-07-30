#! /usr/bin/python3

import re
import sys
from utils import *
import IPython

# image03_demogr= '/home/an/work/MRRC_working_scripts/dataManagement/scripts/demogr_test.txt'
image03_demogr= '/home/an/work/MRRC_working_scripts/dataManagement/scripts/image03_demographics_temp.txt'


class bidsDemogr:

    def __init__(self):
        self.taskIntpn = []
        self.keys = []
        self.data = {}


    def read(self, file):

        fc = csvread(file, bids_demogr=True, id='---')

        if 'taskIntpn' in fc[0]:
            self.taskIntpn = fc.pop(0)[1].split( )
            self.keys = fc.pop(0)
        else:
            self.keys = fc.pop(0)

        for dky in self.keys:
            self.data[dky] = []

        for ele in fc:
            for i in range(len(self.keys)):
                try:
                    self.data[self.keys[i]].append(ele[i])
                except:
                    print("Error in demographics! Check this subject: ", ele[1], " demographics info!")
                    sys.exit()

        return self.data


    def write(self):
        raise ValueError('demogr.write not implemented yet')


    def get_datetime(self):
        raise ValueError('demogr.get_datetime not implemented yet')







class bidsSubj:

    def __init__(self):
        self.root = ''
        self.subj = ''
        self.ses = ''
        self.datatype = ''
        self.files = []
        self.filetype = ['.nii.gz', '.json', '.tsv']
        self.scantype = ['T1w', 'SPACE', 'FLASH']


    def splitfiles(self, type, f_l=None):
        if not f_l:
            f_l = self.files
        sf = {}
        for ft in type:
            sf[ft] = [f for f in f_l if ft in f]
        return sf


    def splitfilesbyfiletype(self):
        sf = {}
        for ft in self.filetype:
            sf[ft] = [f for f in self.files if ft in f]
        return sf


    def splitfilesbyscantype(self):
        sf = {}
        for ft in self.scantype:
            sf[ft] = [f for f in self.files if ft in f]
        return sf


    def sortfiles(self, f_l, id, cs=False):
        if cs:
            str = id.replace('?????', '(.+?)')
            s_fl = sorted(f_l,  key = lambda x: re.search(str, x).group(1))

        else:
            str = id.replace('?????', '(.+?)').lower()
            s_fl = sorted(f_l,  key = lambda x: re.search(str, x.lower()).group(1))
        return s_fl


    def get_substr(self, f, id, cs=False):
        if cs:
            str = id.replace('?????', '(.+?)')
            res = re.search(str, f).group(1)

        else:
            str = id.replace('?????', '(.+?)').lower()
            res = re.search(str, f.lower()).group(1)
        return res













if __name__ == '__main__':
    instant = bidsDemogr()
    instant.read(image03_demogr)
