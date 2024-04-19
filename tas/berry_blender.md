# Berry Blending RNG

Can we manipulate the NPCs into hitting more perfects by pressing A at incorrect times?  Will this ever save time?

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
  ; what I see is 2 wrods of data at 40 byte offsets.  The rest is 0s.  I see 16 blocks like this.
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
0x0804FA8C  BLS 0x0804FABC  ; if (output <= 0x42) { goto 0x0804FABC; }
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