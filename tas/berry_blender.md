# Berry Blending RNG

Can we manipulate the NPCs into hitting more perfects by pressing A at incorrect times?  Will this ever save time?

# Conclusion

There is a progress counter at 0x02018140 and a progress "cap" at 0x0201813E.  When the progress counter reaches 1000, the blending is done.  The progress counter will increase by 2 every frame, while it is less than the progress cap.  The progres cap increases whenever you or an NPC gets a hit, even if that hit doesn't increase the RPM.  It is possible to get enough hits yourself to keep the progress cap above the progress counter.

Therefore, manipulating NPC actions doesn't save time.

This can only be invalidated if there is a way to increase the progress counter by more than 2 per frame.

# Notes

I see that there's an RNG call just before the pointer reaches an NPC.  Then when they press, there is 4, 7, or 9 RNG calls on that frame.  The frame with all those RNG calls is usually immediately after the frame with a single RNG call, but sometimes it happens up to 5 frames away (this appears to be when generating an X?).

My hypothesis is that the first RNG call is a decision about if the NPC is successful or not, and the next set of calls determines whether to follow through with that decision.  Actually I'm really not certain about these second set of calls.

Observations:

| First RNG result | Dleay to next block of RNG | Number of RNG calls in 2nd block | Result |
| - | - | - | - |
| 0xCEBF | 1 | 4 | Perfect |
| 0xC757 | 1 | 7 | Perfect |
| 0xC85B | 1 | 4 | Hit |
| 0x3E41 | - | - | None |
| 0x56B7 | - | - | None |
| 0x70A8 | - | - | None |
| 0x6FC9 | 1 | 4 | Hit |
| 0xFD12 | 1 | 6 | Perfect |
| 0xB4F1 | - | - | None |
| 0x6F8D | 1 | 4 | Hit |
| 0x3E4D | - | - | None |
| 0x7391 | - | - | None |
| 0x9181 | 1 | 7 | Hit |
| 0x9C4B | 1 | 9 | Perfect |
| 0x3AA1 | 6 | 4 | Miss |
| 0x7069 | 1 | 7 | Hit |
| 0xB9A8 | 1 | 6 | Perfect |
| 0xB21B | - | - | Miss |

Oh, there's also variable amounts of RNG being burned whenever the player makes an input.

## First Call

With tracelog I found that the call is happening from 0x0804FA66.  I expect that the result of the RNG is written somewhere in memory because it needs to be accessed frames later when the hit actually happens.

0x0804FA14 seems to be the start of the function.  Can't see the ending yet.

```
0x0804FA14  PUSH {r4-r6,lr}
... r4 = uint8_t(r0)
0x0804FA1A  LDR r6, 0x0804FA98 (=0x03004854)
0x0804FA1C  LDR r3, r6
0x0804FA1E  ADD r0, r3, 0x0
0x0804FA20  ADD r0, 0x54
  ; r0 = (*0x03004854) + 0x54
  ; where I'm looking, this is set to 0x02018000.  Valid EWRAM, so looks promising.
0x0804FA22  LDRH r0, [r0, 0x0]
  ; set to 0x6094 where I'm looking, but changes every frame.
  ; So whatever is setting this probably also needs to be known.
  ; r0 = random? number loaded from memory
  ; This actually looks like it might be the angle for the blending head.
0x0804FA24  MOV r1, 0xC0
0x0804FA26  LSL r1, r1, 0x5
  ; r1 = 0b0001'1000'0000'0000
0x0804FA28  ADD r0, r0, r1  ; r0 = r0 + r1  ; 0x1800 + 0xNNNN
  ; This could be looking ahead to see if there's an NPC nearby. 0x1800/0xFFFF ~= 9% of a rotation
0x0804FA2A  LDR r1, 0x0804FA9C (=0x0000FFFF)
0x0804FA2C  AND r0, r1
  ; r0 = uint16_t(r) ...why didn't you just do the LSL/LSR?
0x0804FA2E  ADD r1, r3, 0x0  ; r1 = ptr to around rotation memory
0x0804FA30  ADD r1, 0xA6     ; but really where setting r1 to a whole new ptr.
0x0804FA32  LDRB r1, [r1, 0x0]
  ; r1 = *(0x020180A6).  For me this is locked to 0x02.
0x0804FA34  LSR r2, r0, 0x8
  ; r2 = top 8 bits of adjusted blending head angle
0x0804FA36  LDR r0, 0x0804FAA0 (=0x082162AB)
0x0804FA38  ADD r1, r1, r0
0x0804FA3A  LDRB r1, [r1, 0x0]
  ; so r1 used a ptr to get an offset for another ptr to load a thing.
  ; This is loading something out of ROM.  Data for the berry blending config perhaps?
  ; word at 0x082162AB = 0xA060E020.  Little endian, so 0x02 offset is 0x60.
  ; Each NPC's head is just after these rotations.
0x0804FA3C  ADD r0, r1, 0x0
  ; r0 = 0x60 (meaning?)
0x0804FA3E  ADD r0, 0x14   ; r0 += 0x14
0x0804FA40  CMP r2, r0
  ; comparing r2 (top 8 bits of adjusted blending head anlge) t0 r0 (0x74?)
  ; 0x74 would make sense as an angle, but I don't see 0x02 changing, so this would
  ; be locked to a single NPC's location.  I can't figure out why that would be the case.
0x0804FA42  BLS 0x0804FB24  ; LS = unsigned lower of same -> if (r2 <= r0)
0x0804FA44  ADD r0, 0x14  ; r0 += 0x14
0x0804FA46  CMP r2, r0
0x0804FA48  BCS 0x0804FB24  ; CS = unsigned higher or same -> if (r2 >= r0)
  ; if (adjusted angle <= 0x74 || adjusted angle >= 0x88) { goto 0x0804FB24; }
  ; so it looks like this is checking that we're actually close enough to an NPC head
  ; to do a comparison.
0x0804FA4A  LDR r2, 0x0804FAA4 (=0x03004B20)
  ; if we're still here, we're close to an NPC head.
  ; set r2 to a IWRAM pointer
0x0804FA4C  LSL r1, r4, 0x02  ; r1 = 4*r4
  ; r4 was an 8 bit value passed in as r0 to this function.  In my case r4 was 0x1.
0x0804FA4E  ADD r0, r1, r4    ; r0 = 4*r4+r4 = 5*r4
0x0804FA50  LSL r0, r0, 0x3   ; r0 = 8*5*r4 = 40*r4
  ; r0 is now an offset to some block in IWRAM.  40 (0x28) byte structures it looks like?
  ; what I see is 2 words of data at 40 byte offsets.  The rest is 0s.  I see 16 blocks like this.
  ; Offset 1 has the words:
  ;  0x4B48: 08 04 FA 15
  ;  0x4B4C: 0b 02 00 01
  ;  0x4B50: 00 00 00 01  (This 01 is set after the frame, it was 0 before the frame and becomes 0 again 4 frames later.)
0x0804FA52  ADD r2, r0, r2
  ; r2 points to a 40 byte data block.
0x0804FA54  MOV r5, 0x8
0x0804FA56  LDSH r0, [r2, r5]
  ; load the half word 8 bytes into the data block.  Should be 0x0000 for me?
0x0804FA58  ADD r5, r1, 0x0
  ; r5 = 4*arg0
0x0804FA5A  CMP r0, 0x0
0x0804FA5C  BNE 0x0804FB32
  ; if (r0 != 0) { goto 0x0804FB32; }
0x0804FA5E  LDR r1, 0x0804FAA8 (=0x0000014B)
0x0804FA60  ADD r0, r3, r1
  ; r0 = 0x201814B  (ptr to something, close to wehre the rotation angle is).
0x0804FA62  LDRB r0, [r0, 0x0]  ; 0x00 for me, doesn't appear to be changing.
0x0804FA64  CMP r0, 0x0
0x0804FA66  BNE 0x0804FB10
  ; if (r0 != 0) { goto 0x0804FB10; }
0x0804FA68  BL 0x08040EA4  ; r0 = AdvanceRng()
  ; I don't understand the last 2 filter conditions yet, but now we can advance RNG.
... r0 = uint16_t(r0)
0x0804FA70  LDR r1, 0x0804FAAC (=0x0000028F)
0x0804FA72  BL 0x081E0E38  ; function call
  ; And do something immediately with that RNG?
  ; r0 = RNG % 0x28F ?  No, not quite, inputs 0x93AD and 0x28F yielded 0x39.  % would be 0x1D6.
  ;   integer division?  That gets 0x39.
... r2 = uint8_t(r0)
0x0804FA7A  ADD r3, r2, 0x0  ; r3 = RNG // 0x28F
0x0804FA7C  LDR r0, [r6, 0x0]
  ; r6 probably still 0x03004854, a pointer to a block of data/pointers in EWRAM
0x0804FA7E  ADD r0, 0x56
0x0804FA80  MOV r6, 0x0
0x0804FA82  LDSH r1, [r0, r6]
  ; r1 = *(0x02018056)  0x0652 for me, it's rotation speed.
0x0804FA84  LDR r0, 0x0804FAB0 (=0x000001F3)
0x0804FA86  CMP r1, r0
0x0804FA88  BGT 0x0804FACC 
  ; if (rotation speed > 0x1F3) { goto 0x0804FACC; }
  ; something special to do if the rotation speed is VERY low, I guess.
0x0804FA8A  CMP r2, 0x42
0x0804FA8C  BLS 0x0804FABC  ; if (RNG//0x28F <= 0x42) { goto 0x0804FABC; }
  ; if (RNG > 0xA8DE) { do something special? }
0x0804FA8E  LDR r1, 0x0804FAB4 (=0x03002A20)
0x0804FA90  LDR r0, 0x0804FAB8 (=0x00004523)
0x0804FA92  STRH r0, [r1, 0x14]
  ; *0x03002A34 = 0x4523  ; ??  ; yep, this does get written sometimes.  0x5432 also gets written sometimes.
  ; what are these magic numbers
0x0804FA94  B 0x0804FAF4  ; skip over the data block
... data
```

So first half of this function seems to just be filters.  I'm surprised I didn't see a way to changae which angle it's checking.  Is there just a different block of code for each NPC?  That wouldn't make much sense.

Before I look at the second half of this function, I would like to see a bit about what's being done with RNG.

```
0x081E0E38: r0 = IntegerDivision(r0, r1)
```

Okay, then moving on.  What's after the data portion of this function?  Repetition.

```
0x0804FABC  LDR r1, 0x0804FAC4 (=0x03002A20)
0x0804FABE  LDR r0, 0x0804FAC8 (=0x00005432)
0x0804FAC0  STRH r0, [r1, 0x14]
0x0804FAC2  B 0x0804FAF4
  ; *0x03002A34 = 0x5432, then fuck off down the ROM a bit.
... data
0x0804FACC  CMP r2, 0x41
0x0804FACE  BLS 0x0804FAD6
  ; if (RNG//0x28F <= 0x41), don't write a thing.
  ; i.e. if (RNG//0x28F > 0x41) { *0x03002A34 = 0x4523 }
0x0804FAD0  LDR r1, 0x0804FB00, (=0x03002A20)  ; guh, why is this repeated in the rom so much?
0x0804FAD2  LDR r0, 0x0804FB04, (=0x00004523)
0x0804FAD4  STRH r0, [r1, 0x14]
0x0804FAD6  ADD r0, r2, 0x0
0x0804FAD8  SUB r0, 0x29
  ; r0 = RNG//0x28F - 0x29  ; this could be negative.
... r0 = uint8_t(r0)
0x0804FADE  CMP r0, 0x18
0x0804FAE0  BHI 0x0804FAE8  ; HI = unsigned higher,
  ; if (RNG//0x28F - 0x29 > 0x18  || < 0), don't write a thing,
0x0804FAE2  LDR r1, 0x0804FB00 (=0x03002A20)
0x0804FAE4  LDR r0, 0x0804FB08 (=0x00005432)
0x0804FAE6  STRH r0, [r1, 0x14]
  ; i.e. if (0 < RNG//0x28F - 0x29 <= 0x18) { *0x03002A34 = 0x5432 }
0x0804FAE8  CMP r3, 0x9
0x0804FAEA  BHI 0x0804FAF4
  ; if (RNG//0x28F > 0x9) { goto 0x0804FAF4 }
0x0804FAEC  MOV r0, 0x2
0x0804FAEE  MOV r1, 0x5
0x0804FAF0  BL 0x0804F8B0  ; function call
  ; Lots of paths ignore this function call, so check it out later.
0x0804FAF4  LDR r0, 0x0804FB0C (=0x03004B20)  ; yes, that IS a B, not an A
0x0804FAF6  ADD r1, r5, r4  ; r5 = 4*arg0, r4 = arg0
0x0804FAF8  LSL r1, r1, 0x3  ; r1 = 8*5*arg0
0x0804FAFA  ADD r1, r1, r0
  ; r1 = 40 byte block in that same group from before.
0x0804FAFC  MOV r0, 0x1
  ; r0 = 1 then fuck off down the ROM some more
0x0804FAFE  B 0x0804FB30
... data
0x0804FB10  LDR r0, 0x0804FB1C, (=0x03002A20)
0x0804FB12  LDR r1, 0x0804FB20, (=0x00004523)
0x0804FB14  STRH r1, [r0, 0x14]
  ; *0x03002A34 = 0x4523
0x0804FB16  MOV r0, 0x1
0x0804FB18  STRH r0, [r2, 0x8]
  ; write a 1 at an 8 byte offset in the 40 byte data structure
0x0804FB1A  B 0x0804FB32
  ; exit
... data
0x0804FB24  LDR r0, 0x0804FB38 (=0x03004B20)
0x0804FB26  LSL r1, r4, 0x2
0x0804FB28  ADD r1, r1, r4
0x0804FB2A  LSL r1, r1, 0x3
0x0804FB2C  ADD r1, r1, r0
  ; setup r1 to point to write 40 byte block again.
0x0804FB2E  MOV r0, 0x0
  ; default case: write a 0, but some paths skip to the write instruction and over this.
0x0804FB30  STRH r0, [r1, 0x8]
  ; write whatever is in r0 to the 8 byte offset in the 40 byte data structure
0x0804FB32  POP {r4-r6}
0x0804FB34  POP {r0}
0x0804FB36  BX r0
  ; return;
```

I at least have the right bits of memory to look at to experiment further.  And I now know where blending head and rotation speed is stored in memory, so I can watch those as well.

At angle 0x0800, hits are able to happen for angle 0x2000.  At angle 0x1AB6, perfects happen.

| Angle | RNG | `RNG//0x28F` | IWRAM 0x2A34 | Result | Note |
| - | - | - | - | - | - |
| 0x5FE8 | 0xCEBF | 0x50 | 0x4523 | Perfect | |
| 0x9FC8 | 0xC757 | 0x4D | 0x0000 | Perfect | 0x2A36 has 0x4523 |
| 0xDE58 | 0xC85B | 0x4E | 0x0000 | Hit | 0x2A32 has 0x5432 |
| 0x629C | 0x3E41 | 0x18 | 0x0000 | None | |
| 0x9F5E | 0x56B7 | 0x21 | 0x0000 | None | |
| 0xDC0E | 0x70A8 | 0x2C | 0x0000 | None | |
| 0x6158 | 0x6FC9 | 0x2B | 0x5423 | Hit | |
| 0x9DD4 | 0xFD12 | 0x62 | 0x0000 | Perfect | 0x2A36 has 0x4523 |
| 0xE188 | 0xB4F1 | 0x46 | 0x0000 | None | |
| 0x62B8 | 0xD58B | 0x53 | 0x4523 | Perfect |
| 0xA194 | 0x3AB6 | 0x16 | 0x0000 | Miss | 0x2A36 has 0x2345 frame before the miss |

Okay, so it looks like 0x4523 means Perfect, 0x5432 means Hit, and 0x2345 means Miss.  It also looks like 0x03002A30 is length 4 array of 16 bit referring to the result, each index corresponding to a player.

I'm also guessing that each player has there own thresholds.  These weren't passed into the function I was looking at and I didn't see any way they could vary, so maybe there really is a routine for each player?

Also snooping around 0x02018000 to see if there's anything else worth uncovering around here.  0x02018058 is 2 bytes varying every frame.  0x0201805A locked to 0x229C?  0x18058 also looks like an angle...  It's slightly behind the other one but getting update the same way based on rotation speed.  I don't think I saw this being read for NPC RNG, but it wouldn't surprise me if this was a min/max for player hits/perfect ranges.  0x0201807E is 1 byte counting 0-5 inclusive, advancing 1 per frame.

A bunch of stuff around 0x0201812C varying.  0x018144 chaned to 1 on player hit?  0x01812C counting up 1 per frame.  0x01813C potentionally being re-written to the same value every frame (ditto: 0x018154-0x018160, 0x01817C).  0x018140 counting up 2 per frame.

- 0x018168: 2 bytes.  Horizontal position of blending head? 0xFF00 is max down (-0x100), 0x0100 is max up.
- 0x01816A: 2 bytes.  Vertical position of blending head?  0xFF00 is max left (-0x100), 0x0100 is max right.
- 0x01816C: 2 bytes.  Opposite of 0x01816A.
- 0x01816E: 2 bytes.  Duplicate of 0x018168.
- 0x018170: 4 bytes.  Seems to be related to rotation?  0 at the top and full right, negative in between, and positive outside that range.  Max is a little over 0x10000 at around Laddie's blend head.
- 0x018174: 4 bytes.  Seems to be related to rotation?  Min value is negative around player's blend head, max value opposite that.

I was hoping to find the progress meter, but nothing seems to match unless it's one of the counters.  They do stop advancing at the end, value 0x218 and 0x3E8.  0x3E8 = 1000 decimal.  That seems like a good bet for being the progress counter.  Let's investigate that some more.  0x218 = 536, might just be a timer. 

0x018144 Screen shake value?  0x018152 also got set at that time.

0x018130 byte changed to FF when rotation stopped (from 0x14). Then started counting down.  Then it reached 0 and started counting up again?

- 0x01814C/4E/50: Player scores. 2 bytes each.  Perfect/Hit/Miss.
- 0x018152/54/56: Mister scores. ditto.
- 0x018158/5A/5C: Laddie scores. ditto.
- 0x01815E/60/62: Lassie scores. ditto.
- 0x018164: Ranks. 1 byte each.  Player/Mister/Laddie/Lassie.

## Counter investigation

0x018140 starts at 0.  With no A presses it first advances when Laddie hits a perfect. It advanced by 4.  It advanced by 4 again when Lassie got a regular Hit.  4 Again on Mister hit.

Actually for each of those it advanced by 2 on 2 consecutive frames.  This time Laddie hits a perfect and it increases by 2 on 3 consecutive frames.  Lassie gets regular hit and same result 2 each on 3 frames.  Mister regular hit gets 2 each on 4 frames.  Laddie perfect 2 each on 5 frames.  Lassie perfect: 2 each on 6 frames.  Eventually those chains last long enough that it kind of looks like it's increasing monotonically, but it stops if no one makes an input for a while.

0x01812C always advanced by 1 per frame for the whole thing.

Misses don't increase progress, but they don't decrease it either.  And they do change rotation speed and burn RNG, so could be useful outside of making the slow down at the end come faster.

Player Hit: 2 on 1 frame the first, 2 on 2 frames for the next few after that. Overlappiong the counters with consecutive A presses doesn't affect the result.  

- Hit 5 is where it bumps up to 3 frames.  This is also wehere rotation speed goes above 20 RPM (0x17F at time of hit).
- Hit 6 is 4 frames (rotation 0x1BF). 
- Hit 7 is 4 frames (rotation 0x1FF).
- Hit 8 is 4 frames (rotation 0x23F).
- Hit 9 is 5 frames (rotation 0x27F, 35.1 RPM).
- Hit 10 is 5 frames (rot 0x2BE).
- Hit 11 is 6 frames (rot 0x2FE, 42.07 RPM).
- Hit 12 (Perfect) is ??.  Laddie hits a perfect so the chain keeps going.  Hard to tell where it stops.

If I wait to make the frist Hit perfect, it get 2 frames instead of 1.  I bet there's something tracking how many frames are left to increase progress for.  Let me see if I can find something that matches observations now that I know what I'm looking for.

0x0201813E looks to be the progress cap.  It increases only when a player or NPC makes a hit, and then progress increases by 2 until it is >= that value.  This makes it a lot easier to see how much it's increasing by per A press.  Misses do not decrease it (but maybe there's a chain mechanic that would limit the progress per Hit?)

Wait a fucking minute.  At the start I can spam 17 inputs in a row and rack up 175 progress cap.  All the other rotations I can get max 3 hits in.  What if I just slow it way the fuck down when it comes my turn and then get 17 inputs in a row again!

- Naïve: 175 leaving my control, 246 coming back into my control. 403 leaving my control (time 78)
- Insane: 175 leaving my control, 240 coming back into my control.  430 leaving my control (time 97)

So ~5.1 progress per frame the standard way and ~4.4 progress per frame the insane way.  Not immeidately better to just wholy adopt that approach, but it may have some merits in moderation. e.g. if I break by 1 I end up with 425 leaving my control (1 extra hit) at time 79 = ~5.4 progress per frame.

https://www.youtube.com/watch?v=zBEPHIsd3do

## RNG Manipulation

Does this even matter?  As long as progress cap is over progress it doesn't matter what the NPCs are doing and you can get enough cap to last for an entire rotation.

You are limited by the 2 increase to progress each frame.  Unless that can be broken, nothing you do really matters excpet for keeping progress cap above progress.

Okay, but if we can make it above 160 RPM twice in 6 blends, we can skip an entire round of the berry blender.  This is...not trivial, but seems to be possible.  16 cycles = 48 NPC actions + 16 player actions = 64 opportunites for perfect.  64\*1.76 RPM = 112.64 RPM.  Cap before Hit stops increasing: 85.58 RPM.  85.58 RPM + 112.64 RPM = 198.22.  So up to 21 actions can be non-optimal.  3 at the start are reserved for this before the 85.58 cap is actually hit.  So 27 out of 45 NPC actions need to be perfect?  (This is wrong, practice tells me it should be more like 36 our of 45.)  I forgot to include friction slowing things down...

Until I've shown it impossible (by any reasonable means), I will assume that it is possible and try to find the path that accomplishes it.

So what do I make of the Laddie RNG above?

```
// There this data structure that I don't understand.
struct fortyByte {
	int32 unknown1,
	int32 unknown2,
	// Not perfectly confident in this.
	int16 actionThisCycle,
	int16 unknown3,
	int32 unknown4,
	int32 unknown5,
	int32 unknown6,
	int32 unknown7,
	int32 unknown8,
	int32 unknown9,
	int32 unknown10,
}
fortyByte[16] stuff;
int16[3] result;
int16 PERFECT = 0x4523, HIT = 0x5432, MISS = 0x2345;

// index always 1?
void laddieRng(int16 index) {
	// First it checks that the blending head is in the right location.
	int8 adjustedHead = (blendHead + 0x1800) >> 8
	int8 laddieHead = 0x74
	if (adjustedHead <= laddieHead) {
		stuff[index].actionThisCycle = 0;
		return;
	}
	laddieHead += 0x14  // laddieHead = 0x88
	if (adjustedHead >= laddieHead) {
		stuff[index].actionThisCycle = 0;
		return;
	}
	if (stuff[index].actionThisCycle != 0) {
		return;
	}
	// This is always 0 for me, so I have no idea what it could be
	if (*0x0201814B != 0) {
		result[1] = PERFECT;
		stuff[index].actionThisCycle = 1;
		return;
	}
	// Note: 655 is about 1/100 of the rand range 65536.  So this is
	// doing a very inaccurate measure of percentage chance to do a
	// thing.
	int16 rand = AdvanceRng() / 655;
	if (rotationSpeed > 0x1F3) {
		if (rand > 0x41) {
			result[1] = PERFECT;
		}
		int16 adjustedRand = rand - 0x29;
		if (adjustedRand >= 0 || adjustedRand <= 0x18) {
			result[1] = HIT;
		}
		if (rand <= 0x9) {
			0x0804F8B0(0x2, 0x5);  // Miss
		}
		stuff[index].actionThisCycle = 1;
		return;
	}
	if (rand <= 0x42) {
		result[1] = HIT;
		stuff[index].actionThisCycle = 1;
		return;
	}
	result[1] = PERFECT;
	stuff[index].actionThisCycle = 1;
	return;
}
```

So interestingly it does different things when the roatation speed is "high."  I completely forgot about this 0x0804F8B0 function.  I wonder what it's doing?  It might be setting up when to fire a miss, based on the fact that I don't see miss getting set anywhere, and that happens several frames after this code runs.

This adjusted rand is also really annoying to reason about.  Well 0x18 + 0x29 = 0x41, so maybe not.

Slow rotation:
- 66% chance to Hit
- 34% chance to Perfect

Fast rotation:
- 35% chance to Perfect
- 25% chance to Hit
- 30% chance to None
- 10% chance to Miss

Let's verify that 0x0804F8B0 is actually a miss kind of thing.

```
0x804F8B0  PUSH {r4,r5,lr}
... r5 = uint8_t(r0)
... r4 = uint8_t(r1)
0x804F8BE  LDR r0, 0x0804F8E0 (=0x0804F865)  ; this is passing a function as an argument!
0x804F8C0  MOV r1, 0x50
0x804F8C2  BL 0x0807AAAC   ; it looks like this picks an index to write to.
... r0 = uint8_t(r0)
0x804F8CA  LDR r2, 0x0804F8E4 (=0x03004B20)
0x804F8CC  LSL r1, r0, 0x02
0x804F8CE  ADD r1, r1, r0
0x804F8D0  LSL r1, r1, 0x03
0x804F8D2  ADD r1, r1, r2
  ; get the index to a 40 byte block.
0x804F8D4  STRH r4, [r1, 0xA]
0x804F8D6  STRH r5, [r1, 0xC]
  ; then write the args directly in there.
0x804F8D8  POP {r4,r5}
0x804F8DA  POP {r0}
0x804F8DC  BX r0
```

And experimentally verifying that 0x2, and 0x5 are written to memory in one of these blocks.  It was 0x4B98 in this case (index 3).  Othter things change in this block when it gets set up (is it because my miss was in there?), offset 0: 0xAC75 -> 0xF865, offset 2: 0x0807 -> 0x0804.  0x4BA0 starts counting up 1 per frame.  When it hits 6 the X is displayed.  This same block gets reuse for a Mister miss later in the cycle.  0x4BA4 is 0x1 instead of 0x2, 0x4BA0 does the same counter thing.  0x4B9C (1 byte) seems to be a flag for whether this is active or not.

And by changing inputs, I see that this only gets written before a miss.  So I'm convinced that this is just code to set up the delayed miss.

Okay, so what about the other NPCs?  I'm guessing they have similar functions but with different values.

Mister called around 0x0804F928.  Hmmm.. Not a drop in replacement.

```
; r0 as an arg, gets placed as a uint8_t into r5.
; loads blend head angle, but then take a little detour
0x0804F8F6
  MOV r1, 0x1
  BL 0x0804F18C  ; my guess is this is checking the angle is correct.  To be verified later.
... r0 = uint8_t(r0)
if (r0 = 0x2) { goto 0x0804F906 (essentially a continue} else {goto 0x0804F9FC}
0x0804F906
  ; Lookup in that 40-byte array, using arg0 as index.
  ; Loads the 8 byte offset (should be actionThisCycle)
  ; r6 = r1, where r1 was 4*arg0
if (actionThisCycle = 0) { goto 0x0804F91C (continue) } else { goto 0x0804A0A) }
0x0804F91C
  LDR r0, [r4, 0x0]  ; r4 = 0x03004854, it's going to load 0x02018000.
  ; The load the byte at offset 0x14B.  This is the one I couldn't figure out before
  ; but was associated with always generating a Perfect.
if (*0x0201814B != 0) { goto 0x0804F9DE }
0x0804F924
  ; uint16_t r0 = AdvanceRng();
  ; r1 = rand // 0x28F;  ; good
  ; r3 = r1;
  LDSH r2, [r0, r4]  ; r2 = rotationSpeed
if (rotationSpeed > 0x1F3) { goto 0x0804F984 }
if (r1 <= 0x4B) { goto 0x0804F970 }  ; BLS
  LDR r1, 0x0804F968 (=0x03002A20)
  LDR r0, 0x0804F96C (=0x00004523)  ; Perfect!
  B 0x0804F974
  ; yeah there's another big data block here.
0x0804F970
  LDR r1, 0x0804F97C (=0x03002A20)
  LDR r0, 0x0804F980 (=0x00005432)  ; Hit!
0x0804F974
  STRH r0, [r1, 0x12]  ; this offset agrees with my previous observations
  LDR r0, 0x0804F980 (=0x00005432)  ; Hit?  I don't see anything branching here directly.
  B 0x0804F9E2
... more data
0x0804F984
  LDR r0, 0x0804F9A0 (=0x000005DB)  ; ??
if (rotationSpeed > 0x5DB) { goto 0x0804F9B2 }  ; oh god that's only like 80 RPM
if (rand // 0x28F > 0x50) { goto 0x0804F9DE }  ; BHI
  ; r0 = rand // 0x28F - 0x15
if (adjustedRand < 0 ||  > 0x3B) { goto 0x0804F9AC }  ; BHI
  ; r1 = the result block
  ; r0 = HIT
  B 0x0804F9E2
... more data
0x0804F9AC
if (rand // 0x28F > 0x9) { goto 0x0804F9E4 }  ; BHI
  B 0x0804F9D4
0x0804F9B2
if (rand // 0x28F > 0x5A) { goto 0x0804F9DE }  ; BHI
  ; r0 = rand // 0x28F - 0x47
if (adjustedRand < 0 ||  > 0x13) { goto 0x0804F9D0 }  ; BHI
  ; r1 = the result block
  ; r0  = hit
  B 0x0804F9E2
... yep, more data
0x0804F9D0
  CMP r3, 0x1d  ; r3 is rand // 0x28F
  BHI 0x0804F9E4  ; if (rand // 0x28F > 0x1D) { goto 0x0804F9E4 (mark the action for the cycle then exit) }
0x0804F9D4
  MOV r0, 0x1
  MOV r1, 0x5
  BL 0x0804F8B0  ; This is the miss conditions
  B 0x0804F9E4
0x0804F9DE
  ; r1 = result block
  ; r0 = PERFECT
0x0804F9E2 
  STRH r0, [r1, 0x12]
0x0804F9E4
  ; r0 = 0x03004b20  ; the 40 byte structure
  ; r1 = 40*argo0 + r0
  ; r0 = 1
  B 0x0804FA08
... even more data
0x0804F9FC
  ; r1 = 40*arg0 + 40bytestructureptr
0x0804FA06
  ; r0 = 0
0x0804FA08
  STRH r0, [r1, 0x8]
0x0804FA0A
  POP {r4-r6}
  POP {r0}
  BX r0
```

So three tiers in this one.  0x1F3 is ~28 RPM RPM, 0x5DB is ~83 RPM.

When Rotation Speed <= 0x1F3
- 100% to Hit
- (There should be a 25% chance to Perfect, but I think there's a bug in this code.  Verify via experiment!  Yep 0xDD51 yeilded a hit.)

When Rotation Speed > 0x1F3 <= 0x5DB
- 20% to Perfect
- 60% to Hit
- 10% to None
- 10% to Miss

When Rotation Speed > 0x5DB
- 10% to Perfect
- 20% to Hit
- 60% to None
- 10% to Miss

Alright, 1 more.  What are Lassie's numbers?  RNG called from near 0x0804FB8C.

```
; arg0 is probably an index again.
0x0804FB3C
  PUSH {r4-r6, lr}
  ; r4 = uint8_t(arg0)
  ; r3 = ptr to blending mem map
  ; r0 = blend head angle
  MOV r1, 0xC0
  LSR r1, r1, 0x05  ; r1 = 0b0001'1000'0000'0000
  ADD r0, r0, r1
  LDR r1, .. (=0x0000FFFF)
  AND r0, r1
  ADD r1, r3, 0x0
  ADD r1, 0xA8
  LDRB r1, [r1, 0x0]
  LSR r2, r0, 0x08
  LDR r0, .. (=0x082162AB)
  ADD r1, r1, r0
  LDRB r1, [r1, 0x0]
  ADD r0, r1, 0x0
  ADD r0, 0x14
    ; this all just comparing the blend head angle, just like Laddie.
    ; Only the byte we load is 0xA0
  CMP r2, r0
  BLS 0x0804FC50  ; actionThisCycle = 0 and exit
  ADD r0, 0x14
  CMP r2, r0
  BCS 0x0804FC50  ; actionThisCycle = 0 and exit
    ; that was all just angle comparison to know if we needed to take an action or not
  LDR r2, .. (=0x03004B20)
  ; r0 = 40*argo0;  r2 = r0
  MOV r6, 0x8
  LDSH r0, [r2, r6]
  ADD r6, r1, 0x0  ; r6 = 4*arg0
  CMP r0, 0x0
  BNE 0x0804FC5E
    ; if weve already taken an action, don't do another one
  LDR r1, .. (=0x0000014B)
    ; r0 = 0x0201814B  ; the special byte
    ; if (r0 != 0) { goto: 0x0804FC3C }
  BL 0x08040EA4  ; r0 = AdvanceRng();
  ..
  LDR r1, .. (=0x0000028F)
  ; r2 = rand // 0x28F
  LDR r0, [r5, 0x0]  ; r5 should be 0x03004852, a ptr to the ptr to blend mem map
  ADD r0, 0x56
  MOV r3, 0x0
  LDSH r1, [r0, r3]  ; r1 = rotationSpeed
  LDR r0, .. 0x000001F3
  CMP r1, r0
  BGT 0x0804FBF0  ; if rotationSpeed > 0x1F3
  CMP r2, 0x58
  BLS 0x0804FBE0
  ; r0 = PERFECT
  ; store result
  B 0x0804FC22
.. data
0x0804FBE0
  ; r0 = HIT
  ; store result
  B 0x0804FC22
0x0804FBF0
  CMP r2, 0x3c
  BLS 0x0804FC04  ; if rand <= 0x3C
  ; r0 = PERFECT
  B 0x0804FC14
... data
0x0804FC04
  ADD r0, r2, 0x0
  SUB r0, 0x38  ; r0 = rand - 0x38
  CMP r0, 0x4
  BHI 0x0804FC16  ; if adjustedRand < 0 ||  > 0x4
  ; r0 = hit
0x0804FC14
  ; store result
0x0804FC16
  CMP r2, 0x4
  BHI 0x0804FC22
  ; 0x0804F8B0(0x3, 0x5)  ; store MISS as result
0x0804FC22
  ; r1 = ptr to actionThisCycle
  ; r0 = 1
  B 0x0804FC5C

0x0804FC3C
  ; store PERFECT at offeset 0x16 (agrees with observations that this is Lassie)
  MOV r0, 0x1
  ; actionThisCycle = 1
  B 0x0804FC5E
  
  
0x0804FC50
  ; r0 = ptr to that 40byte array
  ; r1 = 40*arg0
  MOV r0, 0x0
0x0804FC5C
  STRH r0, [r1, 0x8]
0x0804FC5E
  POP {r4-r6}
  POP {r0}
  BX r0
```

So Lassie is 

If rotationSpeed <= 0x1F3
- 11% to Perfect
- 89% to Hit

If rotationSpeed > 0x1F3
- 40% to Perfect
- 50% to Hit
- 5% to None
- 5% to Miss

Fortunately there is consistency in all of them that the lowest RNG values will be Miss, then None, then Hit, then Perfect at the top.  So here's a compilation of all the chances:

|     | <28 RPM |     | >28 RPM, <83 RPM | | |      | >83 RPM |   |     |         |
| NPC | Hit | Perfect | Miss | None | Hit | Perfect | Miss | None | Hit | Perfect |
| --- | --- | ------- | ---- | ---- | --- | ------- | ---- | ---- | --- | ------- |
| Laddie | 66% | 34%  | 10%  | 30%  | 25% | 35%     | same | | | |
| Lassie | 89% | 11%  | 5%   | 5%   | 50% | 40%     | same | | | |
| Mister | 100% | 0%  | 10%  | 10%  | 60% | 20%     | 10%  | 60%  | 20% | 10%     |

Beware of off-by-one errors.

## Variable RNG

Why does RNG get burned on displaying the result?  Why is it variable?