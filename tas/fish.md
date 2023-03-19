# Fish RNG Investigation

3 frames have 2 RNG advances.  1 once overworld is loaded, 1 once text box appears, 1 just before "Oh! A bite!"

I expect the number of "." and whether a catch appears to both be randomly generated.  The number of times it cycles through before reeling in may also be randomly generated, even though I fairly cetrain it's always 1 for Old Rod.

## Overworld Load

Trace logging to find where RNG is called.  I don't see it anywhere?  Did my trace logger run out of buffer before it was called?  Yes it was just a size issue.  @100,000 lines, both calls show up

* First call: from 0x080005B4
* Second call: from 0x0805A418

`0x080005B4` is shared between all of them, so is probably the VBlank RNG call.  Let's start looking at `0x0805A418`.

* r13 = stack pointer
* r14 = link register
* r15 = program counter

```
0x0805A3F8  PUSH {r4-r6,lr}
...
  ; below here is interesting portion.  r0 was just stored so nothing overwritten
0x0805A418  BL 0x08040EA4    ; r0 = AdvanceRNG()
0x0805A41C  MOV r2, 0x26     ; r2 = 0x26 = 38
0x0805A41E  LDSH r1, [r5, r2]    ; Load half word, not quite in the same position as the store earlier
  ; r5 is a passed in value (r0 initially)
  ; r1 = *(r5 + 38)
0x0805A420  LSL r1, r1, 0x1 ; r1 <<= 1
0x0805A422  MOV r2, sp      ; r2 = stack pointer (??)
0x0805A424  ADD r6, r2, r1  ; r6 = r2 + r1
  ; r6 = stack_pointer + 2*(*(r5 + 38))
... ; r0 = uint16_t r0
0x0805A42A  ADD r4, r4, r1  ; r4 += r1
  ; r4 = stack_pointer + 8 + 2*(*(r5 + 38))
0x0805A42C  MOV r2, 0x0     ; r2 = 0
0x0805A42E  LDSH r1, [r4, r2]  ; r1 = *r4
  ; r4 is related to stack pointer, so now this kind of makes sense.  kind of...
0x0805A430  BL 0x081E0920      ; r0 = Remainder(r0, r1)  => r0 = r0 % r1
0x0805A434  LDRH r1, [r6, 0x0]  ; r1 = *r6
0x0805A436  ADD r1, r1, r0      ; r1 = r1 + RNG
  ; So it looks like r6 = minimum something and r4 = range.
  ; Then r1 ends in the range [minimum, minimum + range)
0x0805A438  STRH r1, [r5, 0x22]
  ; And then we write r1 back to memory around r5, which was and argument (r0) to this function
  ; So the caller has to setup the stack correctly, and tell us the memory point.
  ; Looking at the trace logger the values at this point were:
  ;   r0 = 0x0  <- expected to be range
  ;   r1 = 0x1  <- was loaded as 1 and stayed 1
  ;   r4 = 0x03007DFC  <- should be address of range
  ;   r5 = 0x03004BE8  <- should be the place it's written (might stay static over the whole fish?)
  ;     technically 0x03004C0A is the address to watch (why store half when this should just be a byte?)
  ;   r6 = 0x03007DF4  <- should be address of base
  ; 0x0300FFFF is the top of the stack?  I don't know why I thought it started higher.
  ; 0x03000000 is apparently also being used for as scratch space, which I thought was reserved for 0x02000000
  ; We either need to read the calling code or repeat this exercise with Super Rod to figure out the ranges
0x0805A43A  LDR r3, =0x030048A0
0x0805A43C  LDR r2, =0x0202E858
0x0805A43E  LDRB r1, [r2, 0x5]
0x0805A440  LSL r0, r1, 0x03  ; r0 = r1 << 3
  ; RNG overwritten at this point so interesting portion ends.
...
0x0805A478  POP {r4-r6}
0x0805A47A  POP {r1}
0x0805A47C  BX r1  ; return;
```

This almost certainly is determining how many times to cycle through elipses.

# Text Box Appear

* Frist call: from 0x080005B4
* Second call: from 0x0805A4C8

```
0x0805A4B4  PUSH {r4,lr}
0x0805A4B6  ADD r4, r0, 0x0     ; r4 = r0
0x0805A4B8  BL 0x08072020       ; What do you do?
0x0805A4BC  LDRH r0, [r4, 0x8]  ; r0 = *(r4 + 8)
0x0805A4BE  ADD r0, 0x1         ; r0++
0x0805A4C0  MOV r1, 0x0         ; r1 = 0
0x0805A4C2  STRH r0, [r4, 0x8]  ; *(r4 + 8) = r0  (this has been incremented)
0x0805A4C4  STRH r1, [r4, 0xA]  ; I guess this is zeroing the word, since r4 + 0xE will be written to later.
0x0805A4C6  STRH r1, [r4, 0xC]
0x0805A4C8  BL 0x0804EA4        ; r0 = AdvanceRNG()
... ; r0 = uint16_t r0
0x0805A4D0  MOV r1, 0xA         ; r1 = 10
0x0805A4D2  BL 0x081E0EB0       ; r0 = UnsignedRemainder(r0, r1)
  ; r0 = RNG % 10
0x0805A4D6  ADD r1, r0, 0x0     ; r1 = r0
  ; r1 in [0, 10)
0x0805A4D8  ADD r0, r1, 0x1     ; r0++
  ; r0 in [1, 11)
0x0805A4DA  STRH r0, [r4, 0xE]  ; RNG stored at *(r4 + 14)
0x0805A4DC  MOV r2, 0x20        ; r2 = 32
0x0805A4DE  LDSH r0, [r4, r2]   ; r0 = *(r4 + 32)
  ; What is stored here?
  ; Trace logger says it loaded 0 during our trial
0x0805A4E0  CMP r0, 0x0
0x0805A4E2  BNE 0x0805A4E8      ; if r0 != 0 goto 0x...4E8
  ; Reading not 0 above basically means to use whatever RNG value you got.
0x0805A4E4  ADD r0, r1, 0x4     ; r0 = r1 + 4
  ; Otherwise add 4 to the value we read and use that instead.
  ; I guess this enforces a minimum of some sort?  Maybe for the first elipses of a super/good rod catch? (or all catches?)
0x0805A4E6  STRH r0, [r4, 0xE]  ; *(r4 + 14) = r0
  ; r4 = 0x03004BE8 at this point according to trace log
0x0805A4E8  MOV r1, 0xE         ; r1 = 14
0x0805A4EA  LDSH r0, [r4, r1]   ; r0 = *(r4 + 14)  (RNG was stored here earlier)
0x0805A4EC  CMP r0, 0x9
0x0805A4EE  BLE 0x0805A4F4      ; if r0 <= 9 goto 0x...AF4
0x0805A4F0  MOV r0, 0xA         ; r0 = 10
0x0805A4F2  STRH r0, [r4, 0xE]  ; *(r4 + 14) = r0
  ; The rest of this function basically just reads the value for number of elipses, making sure the maximum is 10.
0x0805A4F4  MOV r0, 0x1         ; r0 = 1
  ; And then 1 is stored in r0.  Some sort of success indicator, I guess?
  ; The function was probably declared a "bool" in whatever language this was compiled from.
  ; So it felt it needed to return that even if it's always going to happen
0x0805A4F6  POP {r4}            ; exit
0x0805A4F8  POP {r1}
0x0805A4FA  BX r1
```

This is almost certainly counting how many elipses to print in each cycle.  20 frames per elipse, so manipulating this is one of the best ways to save time!

So (RNG % 10) + 1.  There's also the chance at +4.  Do I understand when that happens?

# Before Catch

* First call: from 0x080005B4
* Second call: from 0x0805A5A8

```
0x0805A590  PUSH {r4,lr}
0x0805A592  ADD r4, r0, 0x0
0x0805A594  BL 0x0805A978       ; what is this function?
  ; Loads things out of 0x0202E858 and 0x02020004
  ; It's Looooooooooooong but not very branchy.
  ; Probably worth investigating because it might be setting up all the memory.
  ; If not, have to look into the parent.
  ; Probably need to look into the parent anyway, because I still have no idea how "success" is actually determined.
0x0805A598  LDRH r0, [r4, 0x8]
0x0805A59A  ADD r0, 0x1
0x0805A59C  STRH r0, [r4, 0x8]
  ; Are we doing a for loop in an obscure way here?
  ; Note: this gets overriden with 11 if RNG is odd
0x0805A59E  BL 0x08085404
  ; above function returns either 0 or 1
0x0805A5A2  LSL r0, r0, 0x18
0x0805A5A4  CMP r0, 0x0
0x0805A5A6  BEQ 0x0805A5B4
  ; RNG is skipped if what was loaded is 0, so we know this was not the case.
  ; But when is this the case?  Maybe when you're in the later cycles of a multi-cycle fish.
  ; At that point it shouldn't be letting the fish escape, so we need to signal some success always.
0x0805A5A8  BL 0x08040EA4       ; r0 = AdvanceRNG()
0x0805A5AC  MOV r1, 0x1         ; r1 = 1
0x0805A5AE  AND r1, r0          ; r1 = 1 & RNG
  ; r1 = 1 if RNG was odd, 0 if RNG was even
  ; https://www.smogon.com/forums/threads/past-gen-rng-research.61090/page-34#post-3986326 says Feebas determintion is at a different code point entirely, so I'm not sure what the 50/50 chance is for.
  ; In my trace log, r0 = 0x9176, so we get the complicated code!
0x0805A5B0  CMP r1, 0x0
0x0805A5B2  BEQ 0x0805A5BA
  ; If RNG was odd, store 11 at the magic place and then exit
  ; So what does 11 signal?
  ; And while we're at it, what's r4?  It's an address but I don't know what is stored there
0x0805A5B4  MOV r0, 0xB         ; r0 = 11
0x0805A5B6  STRH r0, [r4, 0x8]  ; *(r4 + 8) = 11
  ; This appears to be "success" but why is "failure" so complicated?
0x0805A5B8  B 0x0805A5E0        ; exit
  ; If RNG was even execute below code
0x0805A5BA  LDR r0, =0x0202E858
  ; This is the same address that's being used in the "Load4BitValue" functions.
  ; Those use offset 5 for the magic value, below we use offset 4
0x0805A5BC  LDRB r0, [r0, 0x4]  ; Load a magic byte into r0
  ; In my trace log the loaded value was 0.
0x0805A5BE  LSL r4, r0, 0x04    ; r4 = r0 << 4
0x0805A5C0  ADD r4, r4, r0      ; r4 = r4 + r0
0x0805A5C2  LSL r4, r4, 0x02    ; r4 = r4 << 2
  ; r4 = 68 * r0 (where r0 is the magic loaded byte)
  ; I guess there's a list of data structures here that are 68 bytes long.
  ; Nothing jumps out to me as needing to be exactly that long.
0x0805A5C4  LDR r0, =0x02020004
0x0805A5C6  ADD r4, r4, r0      ; r4 = r4 + r0
0x0805A5C8  BL 0x0805975C       ; Load4BitValue
  ; Just reading trace log, it looks like this loads another magic byte from 0x0202E858 (at offset 5, it's also 0).
  ; Then it tries to load 0x030048A0 = 36 * above magic number + 24
  ; We end up with 2.
... r0 = uint8_t r0
0x0805A5D0  BL 0x0805FE2C       ; LoadFromOffset(r0)
  ; This function just loads a byte from 0x08375611 + r0 (offset loaded from magic above).
  ; That value happened to be 9 for us.
0x0805A5D4  ADD r1, r0, 0x0     ; r1 = r0  ; How was r0 changed by the previous functions?
... r1 = uint8_t r1
0x0805A5DA  ADD r0, r4, 0x0     ; r0 = r4
  ; r0 is an address around 0x02020004 at this point.
0x0805A5DC  BL 0x08001F58       ; StoreR1AndSetFlags(r0, r1)
0x0805A5E0  MOV r0, 0x1         ; r0 = 1
0x0805A5E2  POP {r4}            ; return
0x0805A5E4  POP {r1}
0x0805A5E6  BX r1
```

Given the other RNG is understood, this is probably determining whether a catch happens.  Which I don't fully understand, but is important for scripting because there's no delays that we can use to manipulate this separate from other values.

```
StoreR1AndSetFlags(r0, r1)
  ; r0 = address.  This + 0x2A is where r1 is stored.  This + 0x3F is where flags will be set
  ; r1 = byte to store
  ; The byte at ro + 0x3F will preserve the value set at the 3rd bit.  The 1st, 5th, 6th, 7th, and 8th bits will be set.  The 2nd and 4th bits will be unset.
0x08001F58  ADD r2, r0, 0x0
0x08001F5A  ADD r2, 0x2A
0x08001F5C  STRB r1, [r2, 0x0]
  ; So r0 is an address, and r1 is what we're saving.
  ; r1 seems to be loaded in the caller, with a lot of complicated logic for figuring out where to load from
0x08001F5E  ADD r0, 0x3F
0x08001F60  LDRB r1, [r0, 0x0]
  ; r1 loaded now from a different place
  ; loaded byte, and we store a byte, so just focus on the last 8 bits.
0x08001F62  MOV r2, 0x4          ; r2 = 4
0x08001F64  ORR r1, r2           ; r1 = loaded_stuff | 4
0x08001F66  MOV r2, 0x11         ; r2 = 11
0x08001F68  NEG r2, r2           ; r2 = -11  (0xFFFFFFF5)
0x08001F6A  AND r1, r2           ; r1 = (loaded_stuff | 4) & (0xFFFFFFF5)
  ;   0bxxxx'xxxx
  ; | 0b0000'0100
  ; =
  ;   0b0000'0x00
  ; & 0b1111'0101
  ; =
  ;   0b1111'0x01
  ; Maybe some flag setting?  Not sure what this could correspond to at all.
  ; And remember it only does this half the time (determined by RNG)
  ; The rest of the time it just writes 0xB (0b1011) to some point in memory
0x08001F6C  STRB r1, [r0, 0x0]
  ; And because that adress was written over, this probably isn't the same place in memory.
0x08001F6E  BX LR
```

```
LoadFromOffset(r0) = r0
  ; r0 = offset to 0x8375611 block of memory
  ; returns in r0 the loaded byte
0x0805FE2C  LSL r0, r0, 0x18
0x0805FE2E  LSR r0, r0, 0x18
  ; make sure r0 is a byte
0x0805FE30  LDR r1, =0x8375611
0x0805FE32  ADD r0, r0, r1
0x0805FE34  LDRB r0, [r0, 0x0]
0x0805FE36  BX LR
```

```
Load4BitValue()
  ; Uses the value at 0x0202E85D to load a value from the 0x030048A0 block of memory
  ; returns is r0 the 4 lower bits of the loaded byte.
  ; This method takes no inputs, it only depends on the state of memory
0x0805975C  LDR r2, =0x030048A0
0x0805975E  LDR r0, =0x0202E858
0x08059760  LDRB r1, [r0, 0x5]
  ; Load a byte from 0x0202E85D
0x08059762  LSL r0, r1, 0x03    ; r0 = r1 << 3
0x08059764  ADD r0, r0, r1      ; r0 = r0 + r1
0x08059766  LSL r0, r0, 0x02    ; r0 = r0 << 2
  ; r0 = 36 * r1 (where r1 is the loaded byte)
0x08059768  ADD r0, r0, r2
  ; r0 is now address in 0x030048A0 block
0x0805976A  LDRB r0, [r0, 0x18]
  ; load the byte (but actually only 4 bits) and then return
... r0 = uint4_t(r0)
0x08059770  BX LR

...
; This function right below caught my eye as being 90% the same
0x0805977C  LDR r2, =0x030048A0
0x0805977E  LDR r0, =0x0202E858
0x08059780  LDRB r1, [r0, 0x5]
0x08059782  LSL r0, r1, 0x03
0x08059784  ADD r0, r0, r1
0x08059786  LSL r0, r0, 0x02
0x08059788  ADD r0, r0, r2
0x0805978A  LDRB r0, [r0, 0x18]
0x0805978C  LSR r0, r0, 0x04
  ; The only difference is here we return everything EXCEPT the lower 4 bits
  ; while the above function returns ONLY the lower 4 bits.
0x0805978E  BX LR

...
; And right below is a function that does almost the same thing, but the offset is 0xB instead of 0x18
```

```
; If this returns 0 we skip RNG and write 11 to a magic byte.
0x08085404  PUSH {lr}
0x08085406  BL 0x08084D8C
  ; Brief glance at the code for this function, it's looking at 0x0839D3B4, but not iterating over the list.
... r2 = uint16_t(r0)
... if (r2 == 0x0000FFFF) return 0;
... uint32_t r1 = 0x0839D3C4 + (20 * r2)  // That address is ROM data, not sratch space!
... r0 = *r1
... if (r0 == 0) return 0 else return 1;
; I can't understand the memory section at 0x0839D3C4.  There are at least patterns every 20 bytes, but
; for the most part the data at the position it's reading is going to be 0.
; It looks like there might be indexes to different addresses at some points: 00839B9xx is common.
```

Ok, fuck it, this is too complicated.  Maybe it really is just a 50/50 and odd = failure, even = success.  I could check that easily and empirically verify this.

0x53BF -> Failure
0x1D75 -> Failure
0x916B -> Failure
0x9176 -> Success
0xA738 -> Success
0xD600 -> Success
0x49FE -> Success
0xCE1B -> Failure
0xE7F2 -> Success
0xE310 -> Success
0x97DF -> Failure
0xEABB -> Failure
0xE2B9 -> Failure

Looks right to me!

# Extra RNG

Okay, so while walking through Granite Cave there's randomly frames that are burning 9+ RNG advances and I don't know from what.  But at this particular point I need to burn as many as possible so might as well see if I can trigger this as much as possible.

Trace log shows the following (non V-Blank) points:

* 0x0805CF26
* 0x0805CEA2
* 0x0805CF26
* 0x0805CEA2
* 0x0805CF26
* 0x0805CEA2
* 0x0805CF26
* 0x0805CEA2
* 0x0805CF26
* 0x0805CEA2

So it looks like one function that gets iterated through at least up to 5 times.

0x0805CF26 is using RNG to read something off the stack.  oh god why...
