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
0x0805A3FA  ADD sp, -0x10    ; stack pointer manipulation >:(
0x0805A3FC  ADD r5, r0, 0x0  ; r5 = r0  
0x0805A3FE  LDR r1, =0x08030FC9C
0x0805A400  MOV r0, sp
0x0805A402  MOV r2, 0x6
0x0805A404  BL 0x081E26A4    ; call this function
  ; Does this change any values of r0 or r5?
0x0805A408  ADD r4, sp, 0x8
0x0805A40A  LDR r1, =0x0830FCA2
0x0805A40C  ADD r0, r4, 0x0  ; r0 = r4
0x0805A40E  MOV r2, 0x6
0x0805A410  BL 0x081E26A4    ; same function as just above
0x0805A414  MOV r0, 0x0
0x0805A416  STRH r0, [r5, 0x20]  ; Store half word => *(r5 + 0x20) = r0

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
  
0x0805A442  ADD r0, r0, r1
0x0805A444  LSL r0, r0 0x02
0x0805A446  ADD r0, r0, r3
0x0805A448  LDRB r0, [r0, 0x5]
0x0805A44A  STRH r0, [r5, 0x24]
0x0805A44C  LDRB r0, [r2, 0x5]
0x0805A44E  LSL r4, r0, 0x03
0x0805A450  ADD r4, r4, r0
0x0805A452  LSL r4, r4, 0x02
0x0805A454  ADD r4, r4, r3
0x0805A456  ADD r0, r4, 0x0
0x0805A458  BL 0x080605D8
0x0805A45C  LDRB r0, [r4, 0x1]
0x0805A45E  MOV r1, 0x8
0x0805A460  ORR r0, r1
0x0805A462  STRB r0, [r4, 0x1]
0x0805A464  LDRB r0, [r4, 0x18]
0x0805A466  LSL r0, r0, 0x1C
0x0805A468  LSR r0, r0, 0x1C
  ; r0 = uint4_t r0 (??)
0x0805A46A  BL 0x08059C60
0x0805A46E  LDRH r0, [r5, 0x8]
0x0805A470  ADD r0, 0x1
0x0805A472  STRH r0, [r5, 0x8]
  ; Add 1 to what ever is at *(r5 + 8)
0x0805A474  MOV r0, 0x0
0x0805A476  ADD sp, 0x10  ; undo stack pointer manipulation :)
0x0805A478  POP {r4-r6}
0x0805A47A  POP {r1}
0x0805A47C  BX r1  ; return;
```

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
  ; Reading 0 above basically means to use whatever RNG value you got.
0x0805A4E4  ADD r0, r1, 0x4     ; r0 = r1 + 4
  ; Otherwise add 4 to the value we read and use that instead.
  ; I guess this enforces a minimum of some sort?  Maybe for the first elipses of a super/good rod catch?
0x0805A4E6  STRH r0, [r4, 0xE]  ; *(r4 + 14) = r0
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

# Before Catch

* First call: from 0x080005B4
* Second call: from 0x0805A5A8

```
0x0805A590  PUSH {r4,lr}
0x0805A592  ADD r4, r0, 0x0
0x0805A594  BL 0x0805A978       ; what is this function?
0x0805A598  LDRH r0, [r4, 0x8]
0x0805A59A  ADD r0, 0x1
0x0805A59C  STRH r0, [r4, 0x8]
0x0805A59E  BL 0x08085404
0x0805A5A2  LSL r0, r0, 0x18
0x0805A5A4  CMP r0, 0x0
0x0805A5A6  BEQ 0x0805A5B4
  ; RNG is skipped if what was loaded is 0, so we know this was not the case.
0x0805A5A8  BL 0x08040EA4       ; r0 = AdvanceRNG()
0x0805A5AC  MOV r1, 0x1         ; r1 = 1
0x0805A5AE  AND r1, r0          ; r1 = 1 & RNG
  ; r1 = 1 if RNG was odd, 0 if RNG was even
  ; https://www.smogon.com/forums/threads/past-gen-rng-research.61090/page-34#post-3986326 says Feebas determintion is at a different code point entirely, so I'm not sure what the 50/50 chance is for.
  ; In my trace log, r0 = 0x9176, so we get the complicated code!
0x0805A5B0  CMP r1, 0x0
0x0805A5B2  BEQ 0x0805A5BA
  ; If RNG was odd, store 11 at the magic place and then exit
0x0805A5B4  MOV r0, 0xB         ; r0 = 11
0x0805A5B6  STRH r0, [r4, 0x8]  ; *(r4 + 8) = 11
0x0805A5B8  B 0x0805A5E0        ; exit
  ; If RNG was even execute below code
0x0805A5BA  LDR r0, =0x0202E858
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
0x0805A5C8  BL 0x0805975C       ; what does this function do?
  ; Just reading trace log, it looks like this loads another magic byte from 0x0202E858 (at offset 5, it's also 0).
  ; Then it tries to load 0x02020004 = 36 * above magic number + 36
  ; We end up with 2.
... r0 = uint8_t r0
0x0805A5D0  BL 0x0805FE2C       ; what does this function do?
  ; This function just loads a byte from 0x08375611 + r0 (offset loaded from magic above).
  ; That value happened to be 9 for us.
0x0805A5D4  ADD r1, r0, 0x0     ; r1 = r0  ; How was r0 changed by the previous functions?
... r1 = uint8_t r1
0x0805A5DA  ADD r0, r4, 0x0     ; r0 = r4
0x0805A5DC  BL 0x08001F58       ; what does this function do?
                                ; hopefully stores the result of either r0 or r4 somewhere
								; otherwise all this work would be for nothing.
0x0805A5E0  MOV r0, 0x1          ; r0 = 1
0x0805A5E2  POP {r4}             ; return
0x0805A5E4  POP {r1}
0x0805A5E6  BX r1
```