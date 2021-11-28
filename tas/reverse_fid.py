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


def candidateMatches(candidate, index1, list2, index2):
    if candidate.firstTrendyWord & 0x1FF != index1:
        return False
    if (candidate.secondTrendyWord >> 9) % 2 != list2:
        return False
    if candidate.secondTrendyWord & 0x1FF != index2:
        return False
    return True


def searchAt(seed, index1, list2, index2):
    fidMatches = set()
    # Advance 1 for SID, and 1 more for frame advance
    seed = rng.advanceRng(seed, 2)
    # The first candidate is always generated with no problem with VBlank
    seed, firstCandidate = fid.generateCandidateFID(seed)

    # Starting with the second candidate FID, things get chaotic due to VBlank.
    # Within the 2nd word, the trendy phrase can be changed based on where the
    # VBlank occurs.  If it doesn't, it may affect which FID is generated.
    # This can all affect the number of RNG advances during the 2nd FID, which
    # means we have different possibilities to check for subsequent FIDs as
    # well.
    for inject in range(9):
        nextSeed, candidate = fid.generateCandidateFID(seed, inject)
        candidates = [firstCandidate, candidate]
        # 3 more FIDs to generate.
        for i in range(3):
            nextSeed, candidate = fid.generateCandidateFID(nextSeed)
            candidates.append(candidate)
        candidates.sort()
        if candidateMatches(candidates[0], index1, list2, index2):
            fidMatches.add(candidates[0].FID)
    return fidMatches


def main():
    trainerId = 59900
    firstWord = 'WELL'
    secondWord = 'DESIGN'
    
    firstIndex = CONDITIONS.index(firstWord.upper())
    if secondWord in LIFESTYLE:
        secondList = 0
        secondIndex = LIFESTYLE.index(secondWord.upper())
    else:
        secondList = 1
        secondIndex = HOBBIES.index(secondWord.upper())
        
    topTID = trainerId << 16
    numMatches = 0
    for i in range(1 << 16):
        seed = topTID + i
        matches = searchAt(seed, firstIndex, secondList, secondIndex)
        if len(matches) > 0:
            numMatches += len(matches)
            print('Potential seed @ i = %d with %s matches' % (i, matches))
    print('Total matches = %d' % numMatches)


if __name__ == '__main__':
    main()
