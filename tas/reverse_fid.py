# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 19:08:35 2021

@author: yuhasem
"""

import rng
import fid

# Lists generated from trendy_text.lua, with some manual cleanup.
CONDITIONS = ['HOT','EXISTS','EXCESS','APPROVED','HAS','GOOD','LESS','MOMENTUM','GOING','WEIRD','BUSY','TOGETHER','FULL','ABSENT','BEING','NEED','TASTY','SKILLED','NOISY','BIG','LATE','CLOSE','DOCILE','AMUSING','ENTERTAINING','PERFECTION','PRETTY','HEALTHY','EXCELLENT','UPSIDE DOWN','COLD','REFRESHING','UNAVOIDABLE','MUCH','OVERWHELMING','FABULOUS','ELSE','EXPENSIVE','CORRECT','IMPOSSIBLE','SMALL','DIFFERENT','TIRED','SKILL','TOP','NON STOP','PREPOSTEROUS','NONE','NOTHING','NATURAL','BECOMES','LUKEWARM','FAST','LOW','AWFUL','ALONE','BORED','SECRET','MYSTERY','LACKS','BEST','LOUSY','MISTAKE','KIND','WELL','WEAKENED','SIMPLE','SEEMS','BADLY']
LIFESTYLE = ['CHORES','HOME','MONEY','ALLOWANCE','BATH','CONVERSATION','SCHOOL','COMMEMORATE','HABIT','GROUP','WORD','STORE','SERVICE','WORK','SYSTEM','TRAIN','CLASS','LESSONS','INFORMATION','LIVING','TEACHER','TOURNAMENT','LETTER','EVENT','DIGITAL','TEST','DEPT STORE','TELEVISION','PHONE','ITEM','NAME','NEWS','POPULAR','PARTY','STUDY','MACHINE','MAIL','MESSAGE','PROMISE','DREAM','KINDERGARTEN','LIFE','RADIO','RENTAL','WORLD']
HOBBIES = ['IDOL','ANIME','SONG','MOVIE','SWEETS','CHAT','CHILD\'S PLAY','TOYS','MUSIC','CARDS','SHOPPING','CAMERA','VIEWING','SPECTATOR','GOURMET','GAME','RPG','COLLECTION','COMPLETE','MAGAZINE','WALK','BIKE','HOBBY','SPORTS','SOFTWARE','SONGS','DIET','TREASURE','TRAVEL','DANCE','CHANNEL','MAKING','FISHING','DATE','DESIGN','LOCOMOTIVE','PLUSH DOLL','PC','FLOWERS','HERO','NAP','HEROINE','FASHION','ADVENTURE','BOARD','BALL','BOOK','FESTIVAL','COMICS','HOLIDAY','PLANS','TRENDY','VACATION','LOOK']

CANDIDATES_MEMO = dict()

class MatchInfo():
    
    def __init__(self, firstWord, secondWord, extraFirstWord='',
                 extraSecondWord='', lottoNumber=-1, extraWordFirstDay=False,
                 endSeed=0):
        self.firstIndex = CONDITIONS.index(firstWord.upper())
        if secondWord in LIFESTYLE:
            self.secondList = 0
            self.secondIndex = LIFESTYLE.index(secondWord.upper())
        else:
            self.secondList = 1
            self.secondIndex = HOBBIES.index(secondWord.upper())
        self.hasExtraWord = extraFirstWord and extraSecondWord
        if extraFirstWord:
            self.extraFirstIndex = CONDITIONS.index(extraFirstWord.upper())
        if extraSecondWord:
            if extraSecondWord in LIFESTYLE:
                self.extraSecondList = 0
                self.extraSecondIndex = LIFESTYLE.index(extraSecondWord.upper())
            else:
                self.extraSecondList = 1
                self.extraSecondIndex = HOBBIES.index(extraSecondWord.upper())
        self.lottoNumber = lottoNumber
        # Needs to be used to find if the lottoNumber matches
        self.endSeed = endSeed
        self.extraWordFirstDay = extraWordFirstDay
        

def candidatesMemoKey(seed, inject):
    if inject < 0 or inject > 8:
        inject = -1
    return f'{seed},{inject}'


def candidateMatches(candidate, index1, list2, index2):
    if candidate.firstTrendyWord & 0x1FF != index1:
        return False
    if (candidate.secondTrendyWord >> 9) % 2 != list2:
        return False
    if candidate.secondTrendyWord & 0x1FF != index2:
        return False
    return True


def candidatesMatch(candidates, matchInfo: MatchInfo):
    if matchInfo.hasExtraWord:
        # We treat the primary word as corresponding to today, i.e., the FID
        # corresponding to that phrase is the one to use
        if matchInfo.extraWordFirstDay:
            # Then the extra word must be in candidates[0]
            if not candidateMatches(candidates[0], matchInfo.extraFirstIndex,
                                    matchInfo.extraSecondList,
                                    matchInfo.extraFirstIndex):
                return -1
            # And we need to find the candidate with the primary word
            for i in range(1,len(candidates)):
                if candidateMatches(candidates[i], matchInfo.firstIndex,
                                    matchInfo.secondList, matchInfo.secondIndex):
                    return candidates[i].FID
            # Yes we ignore lottoNumber when given the extra word.  Lotto
            # numbers are meaningless past the first day, and to have 2 words
            # you must have a multi-day file.
            return -1
        # In this block: We have an extra word given, but we don't know if it
        # was the word on the first day.
        # Find the both words, and return the FID of the primary one if both
        # are found
        extraWordFound = False
        primaryFID = -1
        for i in range(len(candidates)):
            if candidateMatches(candidates[i], matchInfo.extraFirstIndex,
                                matchInfo.extraSecondList,
                                matchInfo.extraSecondIndex):
                extraWordFound = True
            if candidateMatches(candidates[i], matchInfo.firstIndex,
                                matchInfo.secondList, matchInfo.secondIndex):
                primaryFID = candidates[i].FID
        return primaryFID if extraWordFound else -1
    # In this block, we only have the sinlge word, and we assume it is day of.
    if not candidateMatches(candidates[0], matchInfo.firstIndex,
                            matchInfo.secondList, matchInfo.secondIndex):
        return -1
    if matchInfo.lottoNumber >= 0:
        # Make sure the lotto number matches too.
        count = 0
        seed = matchInfo.endSeed
        while rng.top(seed) != matchInfo.lottoNumber:
            count += 1
            # TODO: figure out a better bound than 50.
            if count > 50:
                return -1
            seed = rng.advanceRng(seed, 1)
    return candidates[0].FID
        


def searchAt(seed):
    """
    Finds a list of FIDs (possible places a Feebas could be) matching the info
    given.

    Parameters
    ----------
    seed : TYPE
        DESCRIPTION.

    Yields
    -------
    candidates : List[fid.Candidate]
        A sorted list of Candidate FIDs that can be generated by the given seed.
        May yield duplicates.
    seed : int
        TODO: What should I actually return? There's multiple values that make
        sense here and I don't know what I'll use it for.

    """
    # Advance 1 for SID, and 1 more for frame advance
    seed = rng.advanceRng(seed, 2)
    
    # There are 45 possible places to inject the VBlank RNG advancement
    for inject in range(45):
        # TODO: some of these will duplicate results.  We should have a way to
        # filter early to stop unecessary execution.
        trySeed = seed
        candidates = []
        # There are 5 candidate FIDs to generate
        for i in range(5):
            if CANDIDATES_MEMO.get(candidatesMemoKey(trySeed, inject), None) is None:
                newSeed, candidate = fid.generateCandidateFID(trySeed, inject)
                CANDIDATES_MEMO[candidatesMemoKey(trySeed, inject)] = (newSeed, candidate)
                trySeed = newSeed
            else:
                trySeed, candidate = CANDIDATES_MEMO.get(candidatesMemoKey(trySeed, inject))
            candidates.append(candidate)
            inject -= 9
        candidates.sort()
        yield candidates, trySeed


def main():
    trainerId = 45003
    firstWord = 'REFRESHING'
    secondWord = 'SONGS'
    extraFirstWord = 'WELL'
    extraSecondWord = 'HOBBY'
    # In theory this could be used to better tell the possible starting seeds,
    # so we don't have to try all 65k of them.
    dryBattery = False
    lottoNumber = -1
    
    matchInfo = MatchInfo(firstWord, secondWord, extraFirstWord=extraFirstWord,
                          extraSecondWord=extraSecondWord,
                          lottoNumber=lottoNumber, extraWordFirstDay=False)
        
    topTID = trainerId << 16
    numMatches = 0
    matches = set()
    for i in range(1 << 16):
        seed = topTID + i
        for candidates, cSeed in searchAt(seed):
            matchInfo.endSeed = cSeed
            feebasSeed = candidatesMatch(candidates, matchInfo)
            if feebasSeed >= 0 and feebasSeed not in matches:
                matches.add(feebasSeed)
                print ('Potential Feebas seed %x (from i = %d)' % (feebasSeed, i))
    print('Total matches = %d' % len(matches))


if __name__ == '__main__':
    # main()
    # seed = 27171
    # seed = rng.advanceRng(seed, 1)
    # count = 0
    # while rng.top(seed) != 33452:
    #     count += 1
    #     seed = rng.advanceRng(seed, 1)
    # print(count, seed)
    rand = 2192366299
    for candidates, cSeed in searchAt(rand):
        print(candidates)
