# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 22:09:38 2021

@author: 14flash
"""


import rng

def findFrames(seed, tid, sid, fid):
    for i in range(1000):
        # print("%x" % seed)
        top = rng.top(seed)
        # print("%x" % top)
        seed = rng.advanceRng(seed, 1)
        if tid > 0 and top == tid:
            print("TID WRITTEN AT INCREMENT %d" % i)
        if sid > 0 and top == sid:
            print("SID WRITTEN AT INCREMENT %d" % i)
        if fid > 0 and top == fid:
            print("FID WRITTEN AT INCREMENT %d" % i)
            break
        # if top == 0x6BE8:
        #     print("FINAL VALUE AT %d" % i)
        #     break
        
def main():
    tiles = rng.feebasTilesFromSeed(0x3222)
    print(tiles)

if __name__ == '__main__':
    main()