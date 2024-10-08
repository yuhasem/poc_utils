# Notes

## Timing for TID/SID/FID

TID = Trainer ID; SID = Secret ID; FID = Feebas Seed;

Initial seed on frame of A press
0x4E867D5F

On Trainer ID:
--?
0xD68C29B2 <<<< 77th advance so TID and SID are only in this frame

On Feebas ID:
0x0A90A830 <<<< 115th advance
0x6BE88C9E <<<< 121st advance

so multiple RNG calls on frame of Feebas set.  Need to find out which one is doing it.

Feebas Seed: 0xB691 (with (0x1424) in the same word)

~~Nothing obvious standing out (not a direct copy, not an xor with anything else I have).~~

It is a direct copy and I'm not sure how I missed this before.  However, the number of calls seems variable.  In another example I found 27 calls on the FID frame, the 11th of which was the FID.  I have a feeling I recorded something wrong in my original notes above...

Let's get more examples:

Initial Seed | TID | Calls to TID | SID | Calls to SID | FID | Calls to FID
-|-|-|-|-|-|-
0x29E07E85 | 0xF4E7 | 76 | 0x61A2 | 77 | 0x14E2 | 112
0xC8D91624 | 0xD5C4 | 76 | 0x20DC | 77 | 0xB0C0 | 120
0x81D5DB2D | 0x3D13 | 76 | 0xF51C | 77 | 0x7DD6 | 96
0x7B2F0FEA | 0xD51C | 76 | 0xED94 | 77 | 0xBEA7 | 96

So there is a variable number of RNG calls.  This might require a deeper understanding of what's going on here (and maybe not just on the FID frame).

I wonder what the FID looks like on consecutive A press frames?

Initial Seed | FID | Calls to FID
-|-|-
0x0CE80BF4 | 0xB140 | 103
0x6529CF57 | 0xA432 | 113
0x44442A7E | 0xA432 | 112
0xB16CDC19 | 0xA432 | 111
0x4ABFB518 | 0xF51C | 111
0x655DCBAB | 0xF51C | 110
0xAE403242 | 0xF51C | 109
0x61B1E28D | 0xF51C | 108
0xD1D2CC7C | 0xB140 | 95
0x34F7393F | 0xA432 | 105
0x266EF246 | 0xA432 | 104
0x5332DC41 | 0xA432 | 103
0xC709F620 | 0xA432 | 102
0x44FBEC13 | 0xF51C | 102
0x8AE3AE8A | 0xD5C4 | 111
0x8ADBBD35 | 0xF0CA | 87

So it actually seems very stable around the seed.  I wonder if there's some kind of rejection sampling happening here?

## FID generation conclusion

FID generation is the most devilishly brilliant thing I've seen done with RNG.

The game generates 5 candidate FIDs.  These candidates contain both the seed and 16 bits with 2 separate randomly generated values used for sorting FIDs (placing the winning FID in the first slot).  During the generation of this comparison value, the game generates a variable number of random numbers based on its pseudo-random number generator.

This is super simple and easy to emulate and predict.  But there's a catch.

60 times a second, the GBA signals an interrupt to the CPU to execute the "VBlank" routine.  This is generally used to tell games that it's okay to write to VRAM to update the sprites on screen.  Pokemon does that, but also uses this as an opprtunity to advance the games RNG once.

Ordinarily this wouldn't be a problem.  The ARM7TDMI is running at 16.78 MHz, so can execute 280,000 instructions between VBlank events.  The FID generation routine takes around 10,000 instructions.

But FID generation doesn't run at the start of the frame.  It runs very close to the end of the frame.  In fact, it appears designed so that the VBlank routine occuers most frequently during the 2nd candidate, right as it's using RNG to generate a random number of RNG calls.  That is, exactly when advancing the RNG has the most chaotic effect.

On an emulator it would be possible (though difficult) to tell exactly when the VBlank interrupt will occur and get perfect FID generation results.  On actual hardware, however, I think variations in the CPU clock cycle could easily throw this off by a few instructions.  Basically FID generation is designed to use *actual* randomness in its generation, despite only having a psuedo-random number generator available.

## FID generation (raw notes and deciphering)

FID at address 0x0202850A

Setting a break point for writes to that address don't show anything.  Maybe I need to align on word?

Getting a crash in the VBA-next core when I try to frame advance :/ (looks to be when it's disassembling in the breakpoint.  this tells me nothing.)

Can the address in the debugger be trusted as is?  0x080FA4E0.  It looks like it is updating before the crash so I'm going with yes.

So now I need to disassemble around 0x080FA4E0.  Instruction set: https://www.ecs.csun.edu/~smirzaei/docs/ece425/arm7tdmi_instruction_set_reference.pdf

And here's a ~~better~~ more complete datasheet: http://ww1.microchip.com/downloads/en/DeviceDoc/DDI0029G_7TDMI_R3_trm.pdf

```
0x080FA4E0  STREQ r1, [r0], -#0xC68    ; If Z flag set, Write what's in r1 to the address stored in r0, then r0 = r0 - 0xC68
```

So r0 should contain 0x080FA4E0 when this is executed and r1 should contain FID. And Z should be set.

Last time I was disassembling it was the Zilog Z80, which has the RET instruction code.  ARM7 doesn't have this, so it might be tougher to tell when "functions" end.  Also because the debugger is crashing in BizHawk, stepping out of a "function" to figure out call point is going to be *really* hard.  At least ARM7 is 32-bit set size instructions so I know everything is aligned.

Let's look a the instructions before 0x080FA4E0 to see if I can figure out what's setting up r1 and r0.

```
0x080FA4D0  STMVSDA r3!, {r1,r5,r11,sp,lr}^  ; "push" onto the stack r1, r5, r11, sp, lr
0x080FA4D4  LDMVSDA r1!, {r4,r5,r11,sp,lr}^  ; "pop" the stack into r4, r5, r11, sp, and lr  ; LDM = Load Multiple, VS = If Overflow Set, DA decrement address by 4 after each load
     ;  STM followed by LDM is basically "push" and "pop".  lr is "Link Register" (r14). sp is "Stack Pointer" (r13).
		 ;  Normally you' use the PC in the LDM as a way to return to caller, apparently.
		 ;  But why are we messing with the stack here!?
0x080FA4D8  RSBVS r6, r1, r0, lsr #0x20      ; r6 = (r0 >> 0x20) - r1 ; If Overflow Set
0x080FA4DC  RSBVSS r6, r3, r2, lsr r0        ; r6 = (r2 >> r0) - r3   ; RSB = Reverse Subtract, VS = If Overflow Set, S = Also Update Flags
                                             ;  I don't see r6 used anywhere immediately, so I'm going to ignore this line for now.
0x080FA4E0  STREQ r1, [r0], -#0xC68          ; the write
```

Instruction `BL` is "Branch with Link" which sets LR to the current SP and then jumps to a defined place.  That's basically a "function call" and it's why moving LR into PC (via `STM`, `LDM`) is a "return."

Okay, looking a bit above, there are Coprocessor invoking functions.  I need to find a true GBA datasheet/specs to figure out which coprocessor this is and what it's doing.  When I disasseblemd Pokemon TCG for GBC, they sometimes manipulated the stackpointer when they loaded new data from the banks, to access information there.  Maybe that's what's happening here?

https://problemkaputt.de/gbatek.htm might have better documentation on GBA internals?  Nothing about coprocessors, from what I can tell, but one line stood out to me as important: "The game pak ROM is mirrored to three address regions at 08000000h, 0A000000h, and 0C000000h, these areas are called Wait State 0-2. Different access timings may be assigned to each area (this might be useful in case that a game pak contains several ROM chips with different access times each)."

Or maybe the onboard Z80 really is the only coprocessor and all the [undefined] I'm seeing is passing instructions to it.  That would be interesting.  I was under the impression the Z80 was only used for backward compatibility with GB/GBC games.  Based on the ARM7 datasheet, this isn't even multiprocessing, so I'm not sure why the Z80 would be used at all.

Maybe this is using the thumb instruction set?  The code seems more self-consistent that way.  It also means the set is happening at 0x080FA4DC and 0x080FA4DE (which could be the debugger breaking the instruction after the write, for why I got the wrong PC).

So there's a `BX` ARM7 instruction which is "Branch and exchange instruction set," so that's what's could happen to get into Thumb mode.  I don't see the same for Thumb, so I guess you just have to return and it swaps the instruction set back.

"The Thumb instruction set is a subset of the ARM instruction set, and is intended to 
permit a higher code density (smaller memory requirement) than the ARM instruction set in 
many applications."  Yeah, so it's almost certainly coded using mostly Thumb.

So let's take another look at the write site.  Using this for details about instructions: http://bear.ces.cwru.edu/eecs_382/ARM7-TDMI-manual-pt3.pdf

```
0x080FA4D0  LDR r2, [r4, #0x0]  ; r2 = *r4 (dereference), r3 = *(r4 + 4) (one word offset)
0x080FA4D2  LDR r3, [r4, #0x4]
0x080FA4D0  LDR r0, [r6, #0x0]  ; r0 = *r6, r1 = *(r6 + 4)
0x080FA4D6  LDR r1, [r6, #0x4]  
0x080FA4D8  STR r0, [r4, #0x0]  ; *r4 = r0, *(r4 + 4) = r1
0x080FA4DA  STR r1, [r4, #0x4]
0x080FA4DC  STR r2, [r6, #0x0]  ; *r6 = r2, *(r6 + 4) = r3
0x080FA4DE  STR r3, [r6. #0x4]  ; What we've done is swapped the 64 bits at address r4 with the 64 bits at address r6.
0x080FA4E0  ADD r0, r5, #0x1
```

Okay, so what it looks like is that the FID was calculated in *r4 (probably some "free" memory for any computations) and now we're moving it to *r6 (it's "permanent home" so to speak).  So r6 should be 0x0202850A (or there abouts) and *r4 should be FID.

Let's start looking at the control structure around here to see if I can pin down some values

```
...  ; swap *r4 and *r6
0x080FA4E0  ADD r0, r5, #0x1   ; r0 = r5 + 1
0x080FA4E2  LSL r0, r0, #0x10  ; r0 = r0 << 16
0x080FA4E4  LSR r5, r0, #0x10  ; r5 = r0 >> 16
    ; r5 = bottom 16 bits of r5 + 1
0x080FA4E6  CMP r5, r7
0x080FA4E8  BCC $080FA4BA      ; "Branch if C clear" -> C is clear if a borrow is required -> C is clear if r7 > r5
    ; if r5 <= r7 goto 0x080FA4BA
0x080FA4EA  MOV r1, r8         ; r1 = r8 (needed because high registers not accesible for normal operations in Thumb mode)
0x080FA4EC  LSL r0, r1, #0x10  ; r0 = r1 << 16
0x080FA4EE  LSR r2, r0, #0x10  ; r2 = r0 >> 16
    ; r2 = bottom 16 bits of r8
		; r8 was stored as outer loop counter, makes sense for compare
0x080FA4F0  CMP r2, r7
0x080FA4F2  BCC $080FA4A8
    ; if r2 <= r7 goto 0x080FA4A8
		; so looks like we're in a double loop here, and both r2 and r5 need to be > r7 to exit.
0x080FA4F4  POP {r3-r5}        ; fetch r3, r4, and r5 off the stack
0x080FA4F6  MOV r8, r3         ; r8 = r3
0x080FA4F8  MOV r9, r4         ; r9 = r4
0x080FA4FA  MOVE r10, r5       ; r10 = r5
0x080FA4FC  POP {r4-r7}        ; fetch r4, r5, r6, r7 off the stack
0x080FA4FE  POP {r0}           ; fetch r0 off the stack
    ; These POP/MOV are likely just resetting the stack/registers to how they were when we entered
		; i.e., doing a clean return
		; And if called with BL, bottom of the stack will be PC+4, so the BX r0 makes perfect sense as a "return" call
0x080FA500  BX r0
    ; fetched off the stack, so I expect no shenanigans with bottom bit changing instruction mode.
```

Okay now let's look around at 0x080FA4A8 where the outer loop begins

```
0x080FA48C  PUSH {r4-r7,lr}    ; lr is link register.  You'll notice this mirrors the end of the function so I'm conident this is the start.
0x080FA48E  MOV r7, r10
0x080FA490  MOV r6, r9
0x080FA492  MOV r5, r8
0x080FA494  PUSH {r5-r7}       ; so r4, r5, r6, r7, r8, r9, r10 or unmodified at the end of the function
0x080FA496  MOV r9, r0         ; r0/r9 appears to be the "argument" to the function
0x080FA498  LSL r1, r1, #0x10  ; r1 also an arg
0x080FA49A  LSR r7, r1, #0x10  ; r7 = bottom 16 of r1
0x080FA49C  LSL r2, r2, #0x18  ; r2 also an arg
0x080FA49E  LSR r2, r2, #0x18  ; r2 = bottom 8 bits of r2
0x080FA4A0  MOV r10, r2        ; r10 = r2
0x080FA4A2  MOV r2, #0x0       ; r2 = 0
0x080FA4A4  CMP r2, r7
0x080FA4A6  BCS $080FA4F4      ; "Branch if C set" -> C is set if no borrow is required -> C is set if r2 >= r7
    ; if 0 >= r7 goto 0x080FA4F4 (end of the function)
0x080FA4A8  ADD r1, r2 #0x1
```

This also gives me an idea how to detect "function" starts and ends.  Start: Look for `PUSH {lr}`.  End: Look for `POP {rx} BX rx`

So r1, r2, and r9 are all used somewhere in the function, with r0 being an accumulator of sorts.  Now let's look at the body of the loop to see how r4 and r6 get setup.  Also, if r1 = 0, this function is a no-op.

```
0x080FA4A8  ADD r1, r2 #0x1    ; r1 = r2 + 1
    ; increment outer loop counter (r2 holds increment counter at branch, and 0 at entry)
0x080FA4AA  LSL r0, r1, #0x10
0x080FA4AC  LSR r5, r0, #0x10  ; r5 = bottom 16 of r1
    ; r5 is inner loop counter, initialized to outer loop counter + 1
0x080FA4AE  MOV r8, r1         ; r8 = r1
    ; r8 stores outer loop counter
0x080FA4B0  CMP r5, r7
0x080FA4B2  BCS $080FA4EA      ; if r5 >= r7 goto 0x080FA4EA (break inner loop)
0x080FA4B4  LSL r0, r2, #0x03  ; r0 = r2 << 3  or  r0 = 8 * outer_loop_counter
    ; Shift left 3 aligns this to a 64 bit address!!
0x080FA4B6  MOV r1, r9         ; r1 = r9
0x080FA4B8  ADD r6, r1, r0     ; r6 = r1 + r0
    ; r9 was an address!  and r0 is using the loop counter to index a place ahead of that!
0x080FA4BA  LSL r0, r5, #0x03  ; r0 = r5 << 3
    ; the shift left 3 aligns this to 64 bits of memory, the size of a candidate FID
0x080FA4BC  MOV r1, r9         ; r1 = r9
0x080FA4BE  ADD r4, r1, r0     ; r4 = r1 + r0
    ; same thing here but using r5 as the index.
0x080FA4C0  ADD r0, r4, #0x0   ; r0 = r4
0x080FA4C2  ADD r1, r6, #0x0   ; r1 = r6
0x080FA4C4  MOV r2, r10        ; r2 = r10
0x080FA4C6  BL 0x$080FA690       ; Call function at 0x080FA690
0x080FA4CA  LSL r0, r0, #0x18  ; r0 = only bottom 8 of r0 left in
0x080FA4CC  CMP r0, #0x0
0x080FA4CE  BEQ 0x080FA4E0      ; if r0 = 0 goto 0x080FA4E0 (skip the swap but don't break the inner loop)
...  ; swap *r4 and *r6
```

Now for the fun part:  trying to make sense of all this.  Something like

```
0x080FA48C(r1, r2, uint16_t arr[]) {
	for (i = 0; i < 5; i++) {
		for (j = i + 1; j < 5; j++) {
			unit8_t r0 = shouldCopy()
			if (r0 != 0) {
			  arr[i] = arr[j]
			}
		}
	}
}
```

Those array address (arr[i] and arr[j]) are set into r0 and r1 right before the function call.  And what we got passed in as r2 we're setting back to r2 before the function call.  I wonder if that function call modifies those values at all?  Need to determine if these are really arguments.

(I still don't understand the reliance on LSL/LSR.)

```
0x080FA690 is now located at the bottom.
```

I'm assuming little endian-ness because that's the default and nothing I'm seeing says it should be different.  Which means a 0 offset half word is taking least significant 16 bits and a 2 offset half word is taking the most significant 16 bits.

Is it really worth fully understanding this function?  The return decides if we copy data, and we already know that we do (because we found this function by setting a breakpoint when the copy occurred).  If 0x08040EA4 doesn't use write to r3/r5, then there's no point in investigating further.

```
0x08040EA4  LDR r2, [0x08040EB8] (=0x03004818)  ; I'm...not familiar with this syntax. Ah, 0x08.. is in the ROM not RAM, so the value is always the same and it's just showing me the value
        A6  LDR r1, [r2, #0x0]
				A8  LDR r0, [0x08040EBC] (=0x41C64E6D)
				AA  MUL r0, r1  ; god bless single cycle multiplication
				AC  LDR r1, [0x08040EC0] (=0x00006073)
				AE  ADD r0, r0, r1
			 EB0  STR r0, [r2, 0x0]
			  B2  LSR r0, r0, #0x10   ; r0 = r0 >> 16
				B4  BX lr
```

This is the AdvanceRNG function (pretty apparent thanks to the syntax showing the values that are being loaded).  I'll start a functions.md doc to write these figured out ones down.

I have a theory as to why all the LSL/LSR (sometimes redundantly).  If the game was compiled, then it's likely they would have types and variables.  So if a variable was declared as type `uint16_t` or equivalent (unsigned 16 bit integer), then the compiler would think "oh, I have to make sure this is 16 bits" and so does `<<16` followed by `>>16` to ensure the top 16 bits are cleared.

0x080FA690 is a "should copy" function.  It's not writing to the place that gets copied from, but that's what I need to know.  I may come back to this if I need to understand when it copies, but I think this is enough to know for now.

Let's look back at 0x080FA48C.  I should be able to see the Link Register when this gets called (even if BizHawk's disassembler crashes again), which will tell me where this is getting called from.

After much bullshit with BizHawk's debugger not breakpointing when it said "Breakpoint Hit," I took out a bigger hammer:  Trace Logger.  This shit just logs ALL the commands that were run (Around 80k in the frame I'm interested).  It logs the PC after the instruction ran, and also uses odd numbers because of Thumb mode, but I managed to find that the code above is in fact running and is called from around 0x080FA226.

```
0x080FA21C  LDR r0, [0x080FA23C] (=0x02028508)
    ; right around 0x0202850A (FID) so that makes sense and validates that this wasn't a waste.
0x080FA21E  MOV r1, #0x5
0x080FA220  MOV r2, #0x0
0x080FA222  BL 0x080FA48C  ; Call SwapMem(r0, r1, r2)
    ; r1 is loop limit, so it will only copy 4 addresses (matches observation). r2 is passed through to ShouldSwap()
0x080FA226  POP {r3,r4}
0x080FA228  MOV r8, r3
0x080FA22A  MOV r9, r4
0x080FA22C  POP {r4-r7}
0x080FA22E  POP {r0}
0x080FA230  BX r0
```

Yay! This goes somewhere!  So let's look at what's being done above to see how the memory is setup before the swap.

```
0x080FA19C  PUSH {r4-r7,lr}
0x080FA19E  MOV r7, r9
0x080FA1A0  MOV r6, r8
0x080FA1A2  PUSH {r6,r7}
0x080FA1A4  MOV r6, #0x0
    ; r6 appears to be a loop counter.
0x080FA1A6  LDR r7, [0x080FA1D4] (=0x02025734)
0x080FA1A8  LDR r0, [0x080FA1D8] (=0x00002DD4)
0x080FA1AA  ADD r0, r0, r7
0x080FA1AC  MOV r9, r0
    ; r9 = 0x02028508
0x080FA1AE  MOV r1, #0x1
0x080FA1B0  MOV r8, r1
    ; r8 = 1, constant
    ; LOOP STARTS BELOW HERE
0x080FA1B2  MOV r0, #0xA
0x080FA1B4  BL 0x080EB74C
    ; This sets r0 to a vlue where 7 bits are the passed in value and 9 bits are a random number
		; between 0 and a size indexed by the passed in value
0x080FA1B8  LSL r4, r6, #0x03
    ; << 3 means r6 may also be used as an index to a uint64_t[].
0x080FA1BA  ADD r5, r4, r7
    ; so r7 is probably an address = 0x02025734
0x080FA1BC  LDR r2, [0x080FA1DC] (=0x00002DD8)
0x080FA1BE  ADD r1, r5, r2
    ; r1 = 0x0202850C + index
0x080FA1C0  STRH r0, [r1, #0x0]  ; *r1 = r0
    ; r0 is index + random size, stored into memory here
0x080FA1C2  BL 0x08040EA4
    ; r0 = AdvanceRNG()
0x080FA1C6  MOV r1, r8
0x080FA1C8  AND r1, r0           ; r1 = r0 & 1
0x080FA1CA  CMP r1, #0x0
0x080FA1CC  BEQ 0x080FA1E0       ; if r0 % 2 == 0 goto 0x080FA1E0
0x080FA1CE  MOV r0, #0xC         ; r0 = 0xC
0x080FA1D0  B 0x080FA1E2
...  ; This also just data that's used elsewhere in the function. (Reference Addresses)
0x080FA1E0  MOV r0, #0xD
     ; r0 = 13 if r0 % 2 == 0 else 12
0x080FA1E2  BL 0x080EB74C
    ; This sets r0 to a vlue where 7 bits are the passed in value and 9 bits are a random number
		; between 0 and a size indexed by the passed in value
0x080FA1E6  LDR r2, [0x080FA234] (=0x00002DDA)
0x080FA1E8  ADD r1, r5, r2
     ; r1 = 0x0202850E + index
		 ; assuming r5 is unchanged 
0x080FA1EA  STRH r0, [r1, #0x0]  ; *r1 = r0
     ; r0 is index + random size, stored into memory here
0x080FA1EC  BL 0x08040EA4
     ; r0 = AdvanceRNG()
0x080FA1F0  ADD r3, r4, r7
     ; r3 = 0x02025734 + index
		 ; assuming r7 and r4 are unchanged
0x080FA1F2  MOV r2, r8           ; r2 = 1
0x080FA1F4  AND r2, r0           ; r2 = RNG & 1
     ; r2 is a coinflip!!
0x080FA1F6  LDR r5, [0x080FA238] (=0x00002DD5)
0x080FA1F8  ADD r3, r3, r5
     ; r3 = 0x02028509 + index
0x080FA1FA  LSL r2, r2, #0x06    ; r2 = either 0 or 64
0x080FA1FC  LDRB r0, [r3, #0x0]  ; r0 = *r3 (1 byte)
0x080FA1FE  MOV r5, #0x41
0x080FA200  NEG r5, r5
0x080FA202  ADD r1, r5, #0x0     ; r1 = -0x41
0x080FA204  AND r0, r1           ; r0 = *r3 & 0xFFFFFFBF  (B = 0b1011)
0x080FA206  ORR r0, r2           ; it's just a regular or, don't let the extra r confuse you.
     ; you see that bit we left out of the mask above?  lol, we're going to maybe set it here.
		 ; It's because this is left out of SetPotentialFID.  We're essentially ensuring that it'said
		 ; random because SetPotentialFID can't.
0x080FA208  STRB r0, [r3, #0x0]  ; write it back
     ; honestly wtf
0x080FA20A  MOV r1, r9
    ; r1 = 0x02028508
0x080FA20C  ADD r0, r4, r1
    ; r0 = 0x02028508 + index
		; assuming r4 is unchanged
0x080FA20E  BL 0x080FA760        ; SetPotentialFID(r0)
0x080FA212  ADD r0, r6, #0x1
0x080FA214  LSL r0, r0 #0x10
0x080FA216  LSR r6, r0 #0x10  ; uint16_t r6 = r6 + 1
    ; increment loop counter
0x080FA218  CMP r6, #0x4
0x080FA21A  BLS 0x080FA1B2    ; if r6 <= 4 go back to near the top
... ; SwapMem and exit
```

Large, but mostly seems to be delegating logic.  Based on what I know, 0x080EB74C is probably the best place to search next.  It takes (0x0202850C + index) as an arg and those values then get swapped down 4 into the FID.

```
    ; so far seen called with r0 = 10, 12, 13
0x080EB74C  PUSH {r4,lr}
0x080EB74E  LSL r0, r0, #0x10
0x080EB750  LSR r4, r0, #0x10  ; r4 = uint16_t r0
    ; so far I know of the values 10, 12, and 13 being passed into this function
0x080EB752  BL $0x08040EA4     ; r0 = AdvanceRNG()
0x080EB756  LSL r0, r0, #0x10
0x080EB758  LSR r0, r0, #0x10  ; r0 = uint16_t r0
0x080EB75A  LDR r1, [0x080EB798] (=0x083df072)
0x080EB75C  ADD r1, r4, r1
0x080EB75E  LDRB r1, [r1, #0x0]
    ; given input r4 = 10, 12, 13 -> r1 = 0x45 (69), 0x2D (45), 0x36 (54)
		; size_t r1 ??
0x080EB760  BL 0x081E0920      ; call r0 = Remainder(r0, r1)
    ; so r1 is some data indexed (by r4) in an array at 0x083df072
		; The return here is a random number modulo that data, and the index (r4) is unchanged
0x080EB764  LSL r0, r0, #0x10
0x080EB766  LSR r2, r0, #0x10  ; r2 = uint16_t r0
    ; r2 is a number between 0 and the "size" given by the input index.
0x080EB768  CMP r4, #0x0
0x080EB76A  BEQ 0x080EB778
0x080EB76C  CMP r4, #0x15
0x080EB76E  BEQ 0x080EB778
0x080EB770  CMP r4, #0x12
0x080EB772  BEQ 0x080EB778
0x080EB774  CMP r4, #0x13
0x080EB776  BNE 0x080EB786
    ; if (r4 != 0 && r4 != 21 && r4 != 18 && r4 != 19) goto 0x080EB786
		; This is always true for the values I'm investigating.
0x080EB778  LDR r1, [0x080EB79C] (=0x083DE158)
0x080EB77A  LSL r0, r4, #0x02  ; word aligned address?
0x080EB77C  ADD r0, r0, r1
0x080EB77E  LDR r1, [r0, #0x0]
    ; if r0 = 0 -> r1 = 0x083DBFA4
		; if r0 = 18 -> r1 = 0x083DDBB4
		; if r0 = 19 -> r1 = 0x083DDCE6
		; if r0 = 21 -> r1 = 0x083DDF60
0x080EB780  LSL r0, r2, #0x01  ; half word aligned address?
0x080EB782  ADD r0, r0, r1
0x080EB784  LDRH r2, [r0, #0x0]  ; need to figure out if r0/r2/r4 are set by the subroutines above
    ; looking at 0x083DBFA4, this seems to be an array of data, but I can't tell what of
		; Numbers look like 0x0187, 0x0124, 0x0164, 0x0077, 0x0118, 0x0186, ...
		; similar for other indecies given above
0x080EB786  MOV r0, #0x7f
0x080EB788  AND r0, r4     ; bottom 7 bits of r4
0x080EB78A  LSL r0, r0, #0x09  ; then shift left 9
0x080EB78C  LDR r1, [0x080EB7A0] (=0x000001ff)
0x080EB78E  AND r2, r1
0x080EB790  ORR r0, r2
		; r0 = 0b0000'0000'0000'0000'xxxx'xxxy'yyyy'yyyy
		;                           from r4 ^  from r2 ^
		; r4 being the index, r2 being a number loaded from an array with random index.
		; r2 = 0x083DE158[index][rng(0,0x083DF072[index])]
		; The sizes I've seen are all less than 512, so there's no information loss here.
0x080EB792  POP {r4}
0x080EB794  POP {r1}
0x080EB770  BX r1
```

One thing that stands out to me is that there is no `STR` command.  So it's not directly writing to FID or FID-swap.  The address would have been passed in as r1, but it looks the result (r0) is getting stored into that address.  So let's focus on what r0 gets returned as.

~~Need to understand subroutine 0x081E0920.~~  I'll spare the massive text blob since it's very uninteresting once you understand the function.  0x081E0920 returns in r0 the remainder of r0 divided by r1.

Still not quite sure what to call 0x080EB74C.  It is returning both the given index and a random size.  Are either used by the callers?  Nope, just stored, but I already verified this is not what is written into the FID.  So something else is at play.

Going up one step. To understand 0x080FA19C there is one more subroutine 0x080FA760.

```
    ; args: r0 = address around 0x02028508
0x080FA760  PUSH {r4,r5,lr}
0x080FA762  ADD r5, r0, #0x0  ; r5 = r0
0x080FA764  BL 0x08040EA4     ; r0 = AdvanceRNG()
... uint16_t r0;
0x080FA76C  MOV r1, #0x62
0x080FA76E  BL 0x081E0EB0     ; r0 = UnsignedRemainder(RNG, 0x62)  ; NOTE: In Ruby, this is a call to 0x081E0F20 instead
... uint16_t r4 = r0;
0x080FA776  CMP r4, #0x32
0x080FA778  BLS 0x080FA7A2    ; BLS = Branch unsigned lower or same
    ; if a random number in [0, 0x62) is <= 0x32, no more RNG calls.
0x080FA77A  BL 0x08040EA4     ; r0 = AdvanceRNG()
... uint16_t r0;
0x080FA782  MOV r1, #0x62
0x080FA784  BL 0x081E0EB0     ; NOTE: In Ruby, this is a call to 0x081E0F20 instead
... uint16_t r4 = r0;
0x080FA78C  CMP r4, #0x50
0x080FA78E  BLS 0x080FA7A2
    ; if a random number in [0, #0x62) is <= 0x50, no more RNG calls.
0x080FA790  BL 0x08040EA4     ; r0 = AdvanceRNG()
... uint16_t r0;
0x080FA798  MOV r1, #0x62
0x080FA79A  BL 0x081E0EB0    ; NOTE: In Ruby, this is a call to 0x081E0F20 instead
... uint16_t r4 = r0;
    ; r4 = rand[0, #0x62)
    ; LABEL: Done-with-rng
0x080FA7A2  ADD r1, r4, #0x0  ; r1 = r4
    ; r1 = rand[0, #0x62) but it's more likely to be on the lower side.
0x080FA7A4  ADD r1, #0x1E     ; 0x62 + 0x1E = 0x80 ; 0b1000'0000
    ; r1 = rand[0x1E, 0x80)
0x080FA7A6  MOV r0, #0x7f
0x080FA7A8  AND r1, r0
    ; bottom 7 bits does not lose any information.
0x080FA7AA  LSL r1, r1, #0x07
    ; r1 = and move them up 7 bits
0x080FA7AC  LDRH r2, [r5, #0x0]  ; LOAD HALF WORD
0x080FA7AE  LDR r0, [0x080FA7E4] (=0xFFFFC07F)  ; 0b1111'1111'1111'1111'1100'0000'0111'1111
0x080FA7B0  AND r0, r2
0x080FA7B2  ORR r0, r1
    ; load something from *r5 and replace [7:13] with r1 
0x080FA7B4  STRH r0, [r5, #0x0]
    ; And write it back
0x080FA7B6  BL 0x08040EA4     ; r0 = AdvanceRNG()
... uint16_t r0;
0x080FA7BE  ADD r1, r4, #0x1
    ; r1 = rand[0x1, 0x63)
0x080FA7C0  BL 0x081E0920     ; r0 = Remainder(r0, r1)   ; Note: In Ruby this is a call to 0x081E0990 instead.
    ; r0 = RNG % rand[0x1, 0x63)
0x080FA7C4  ADD r0, #0x1E     ; r0 += 30
    ; r0 = rand[0, 0x80)
0x080FA7C6  MOVE r1, #0x7f
0x080FA7C8  AND r0, r1        ; take only last 7 bits of r0
    ; shouldn't lose information without this.
0x080FA7CA  LDRB r2, [r5, #0x0]  ; LOAD BYTE
0x080FA7CC  MOV r1, #0x80     ; r1 = 0b0100'0000
0x080FA7CE  NEG r1, r1        ; r1 = 0b1...'1100'0000  ; only 7 bit immediates, I guess?
0x080FA7D0  AND r1, r2        ; only the 2 bits of r2
0x080FA7D2  ORR r1, r0        ; r1 = top 2 bits of r2 and bottom 7 bits of r0.
0x080FA7D4  STRB r1, [r5, #0x0]  ; write it back
0x080FA7D6  BL 0x08040EA4     ; r0 = AdvanceRNG()
0x080FA7DA  STRH r0, [r5, #0x2]  ; write RNG in the top half of the word we were messing with.
    ; This is, without a doubt, the FID generating write.
		; *r5 = XXXX'XXXX'XXXX'XXXX'??YY'YYYY'YWZZ'ZZZZ
		;      RNG (Potential FID)^
		;  whatever was there before ^
		;       rand[0x1E,0x80) (weighted low)^
		;      whatever was there before | RNG ^
		;    rand[0x0,0x80) (almost perfectly unifrom)^
0x080FA7DC  POP {r4,r5}
0x080FA7DE  POP {r0}
0x080FA7E0  BX r0
```

I've started abbreviating the LSL/LSR by 16 because it's just to tedious.

Well, this has variable number of RNG calls, which is certainly something I'm looking for.  I am convinced 0x080FA7D6 is the FID generating RNG call, because nothing else I've seen writes RNG directly to memory.  Now I just have to puzzle out how many RNG calls happen before it... Also we have loops.  Do we generate multiple possible FIDs and only copy in one we want?

0x081E0EB0 is a slightly different remainder function, which appears to assume it's inputs aren't negative and which is slightly more efficient.  I would like to highlight the most pointles piece of code I've ran across so far:

```
0x081E0F66  PUSH {lr}
0x081E0F68  BL 0x081E08A4
0x081E086C  MOV r0, 0x0
0x081E086E  POP {pc}
...
0x081E08A4  MOV pc, lr    ; what the actual fuck
```

I'd also like to point out that there's a single instruction multiply limited to 34 cycles (with early termination) that could be used for random ranges.  But instead they chose to actually do remainders and implement in a super inefficient way...

```
; The dream random range function:
0x00  BL 0x0x08040EA4
0x04  MOV r1, <max>
0x06  MUL r0, r1
0x08  LSR r0, r0, #0x10
```

I'll call 0x080FA760 "SetPotentialFID".  Takes in address in r0 and writes a potential fid to the top half word, and some curated RNG in the bottom half word.

To take stock, the memory map before SwampMem should look like:

```
     15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0
0x00  ?  ?  A  A  A  A A A A R B B B B B B
0x02 FID
0x04  0  0  0  1  0  1 0 X X X X X X X X X
0x06  0  0  0  1  1  0 N Y Y Y Y Y Y Y Y Y
```

Where R is a random bit, A is a random number in [0x1E, 0x80) (weighted low), B is a random number in [0x0, 0x80), X is rng(0,0x083DE158[0xA]), Y is the same thing with 0xA replace by either 0xC or 0xD (depending on N, another random bit).

This is repeated 5 times.  RNG is called 7-9 times, FID being the last call.  So overall I should expect between 7 and 45 RNG calls betwee SID and FID. Hmmm....One time I saw 43... And one time I saw only 10, so that fits the bill.

I'm going to code something up that generates this memory map.  Then I can at least experiment with what the starting RNG call is for some of these (in case more are burned before this starts).  After this I'll try to understand the SwapMem (especially ShouldSwap) better.

Okay.  I've coded up the algorithm, but there's a problem.  Every 16.743 milliseconds, the game runs a "VBlank" routine (basically on frame advance) which also makes a call to RNG.  That happens right in the middle of FID generation, typically between the frist and second candidate.  It doeesn't happen between a particular set of RNG calls either.  So I either need to predict when it will run, or hope to god the auxillary values aren't that important for FID selection.

I should probably follow up on that last point.  How does the selection algorithm work?  I glossed over it on the first encounter.

```
0x080FA690  PUSH {r4,r5,lr}
0x080FA692  ADD r3, r0, #0x0
0x080FA694  ADD r5, r1, #0x0
    ; So r0 and r1 are args.  r3 should be the "lower" address, r5 should be the "higher address"
		; r3 and r5 are addresses of the candidate FIDs we might want to swap
0x080FA696  LSL r2, r2, #0x18
    ; r2 is arg, but no idea what it represents (was an arg in the previous function, too, but unused).
		; It is passed in as 0.
0x080FA698  LSR r2, r2, #0x18
0x080FA69A  ADD r0, r2, #0x0
    ; uint8_t r0 = r2  (0 at start)
0x080FA69C  CMP r2, #0x1
0x080FA69E  BEQ 0x080FA6D6        ; if r2 = 1 goto 0x080FA6D6 (never used?)
0x080FA6A0  CMP r2, #0x1
0x080FA6A2  BGT 0x080FA6AA        ; if r2 > 1 goto 0x080FA6AA (never used?)
0x080FA6A4  CMP r2, #0x0
0x080FA6A6  BEQ 0x080FA6B0        ; if r2 == 0 goto 0x080FA6B0 (start here)
0x080FA6A8  B 0x080FA752
0x080FA6AA  CMP r2, #0x0
0x080FA6AC  BEQ 0x080FA702
0x080FA6AE  B 0x080FA752
0x080FA6B0  LDRB r0, [r3, #0x0]  ; Load *byte* at r3 + 0
    ; first byte is [A R B B B B B B] with the definitions above
0x080FA6B2  LSL r1, r0, #0x19
0x080FA6B4  LDRB r0, [r5, #0x0]
0x080FA6B6  LSL r0, r0, #0x19
    ; so now r1 is B from the lower candidate and r0 is B from the higher candidate.
0x080FA6B8  CMP r1, r0
0x080FA6BA  BHI 0x080FA74E        ; "Branch if C set and Z clear (unsigned higher)".  Unsighed Higher is like Greater Than but treats the arguments as unsigned.
    ; if B(lower FID) > B(upper FID) return true;
		; Since this is the first comparison done, it is the most important for understanding FID swaps.
		; It is also the most influenced by the VBlank >:(
0x080FA6BC  CMP r1, r0
0x080FA6BE  BCC 0x080FA6FE
    ; if B(lower FID) < B(upper FID) return false;
		; so we only have an issue if the *same* random number got generated.
		; This also explains why it's so stable.  This is the call right before the FID, so the 2 are almost always a pair.
		; If a FID happens to have a lower predecessor call, it gets picked a LOT.
0x080FA6C0  LDRH r0, [r3, #0x0]  ; Load *half-word* at r3 + 0
0x080FA6C2  LSL r3, r0, #0x12
0x080FA6C4  LDRH r0, [r5, #0x0]
0x080FA6C6  LSL r2, r0, #0x12
0x080FA6C8  LSR r1, r3, #0x19
0x080FA6CA  LSR r0, r2, #0x19
    ; r1 = A from lower candidate and r0 = A from upper candidate
0x080FA6CC  CMP r1, r0
0x080FA6CE  BHI 0x080FA74E
    ; if A(lower FID) > A(upper FID) return true;
0x080FA6D0  LSR r1, r3, #0x19
0x080FA6D2  LSR r0, r2, #0x19
0x080FA6D4  B 0x080FA6FA
    ; if A(lower FID) == A(upper FID) advance rng;  return false in any case.
0x080FA6D6  LDRH r0, [r3, #0x0]  ; r0 = bottom 16 bits of *r3
0x080FA6D8  LSL r4, r0, #0x12    ; r4 = r0 << 18
0x080FA6DA  LDRH r0, [r5, #0x0]  ; r0 = bottom 16 bits of *r5
0x080FA6DC  LSL r2, r0, #0x12    ; r2 = r0 << 18
0x080FA6DE  LSR r1, r4, #0x19    ; r1 = r4 >> 25
0x080FA6E0  LSR r0, r2, #0x19    ; r0 = r2 >> 25
    ; so r1 = *r3 >> 7, r0 = *r5 >> 7, which are the addresses we are considering swapping.
0x080FA6E2  CMP r1, r0
0x080FA6E4  BHI 0x080FA74E       ; if (r1 > r0) then goto 0x080FA74E
    ; if the addresses are in different "blocks" of 32 words, return true
0x080FA6E6  LSR r1, r4, #0x19    ; r1 = r4 >> 25
0x080FA6E8  LSR r0, r2, #0x19    ; r0 = r2 >> 25
0x080FA6EA  CMP r1, r0
0x080FA6EC  BCC 0x080FA6FE       ; if "Unsigned lower" (r1 < r0) goto 0x080FA6FE
    ; if ((*r3 / 128) < (*r5 / 128)) return 0;
		; why tho
0x080FA6EE  LDRB r0, [r3, #0x0]  ; r0 = bottom 8 bits of *r3
0x080FA6F0  LSL r1, r0, #0x19    ; r1 = r0 << 25
0x080FA6F2  LDRB r0, [r5, #0x0]  ; r0 = bottom 8 bits of *r5
0x080FA6F4  LSL r0, r0, #0x19    ; r0 = r0 << 25
    ; r1 = *r3 << 25, r0 = *r5 << 25
0x080FA6F6  CMP r1, r0
0x080FA6F8  BHI 0x080FA74E       ; if (r1 > r0) return true
    ; if ((*r3 /%) > (*r5 % 128)), return true
0x080FA6FA  CMP r1, r0
0x080FA6FC  BCS 0x080FA752       ; if (r1 >= 0) goto calling 0x08040EA4
    ; really only happens if r1 == r0 (equal position in blocks of 64 words)
0x080FA6FE  MOV r0, #0x0         ; r0 = 0   (returning false)
    ; return false
0x080FA700  B 0x080FA75A         ; goto goto exit (why are there 2 branches??)
0x080FA702  LDRB r0, [r3, #0x0]
0x080FA704  LSL r1, r0, #0x19
0x080FA706  LDRB r0, [r5, #0x0]
0x080FA708  LSL r0, r0, #0x19
0x080FA70A  CMP r1, r0
0x080FA70C  BHI 0x080FA74E
0x080FA70E  CMP r1, r0
0x080FA710  BCC 0x080FA6FE
0x080FA712  LDRH r0, [r3, #0x0]
0x080FA714  LSL r4, r0, #0x12
0x080FA716  LDRH r0, [r5, #0x0]
0x080FA718  LSL r2, r0 #0x12
0x080FA71A  LSR r1, r4, #0x19
0x080FA71C  LSR r0, r2, #0x19
0x080FA71E  CMP r1, r0
0x080FA720  BHI 0x080FA74E
0x080FA722  LSR r1, r4, #0x19
0x080FA724  LSR r0, r2, #0x19
0x080FA726  CMP r1, r0
0x080FA728  BCC 0x080FA6FE
0x080FA72A  LDRH r1, [r3, #0x2]
0x080FA72C  LDRH r0, [r5, #0x2]
0x080FA72E  CMP r1, r0
0x080FA730  BHI 0x080FA74E
0x080FA732  CMP r1, r0
0x080FA734  BCC 0x080FA6FE
0x080FA736  LDRH r1, [r3, #0x4]
0x080FA738  LDRH r0, [r5, #0x4]
0x080FA73A  CMP r1, r0
0x080FA73C  BHI 0x080FA74E
0x080FA73E  CMP r1, r0
0x080FA740  BCC 0x080FA6FE
0x080FA742  LDRH r1, [r3, #0x6]
0x080FA744  LDRH r0, [r5, #0x6]
0x080FA746  CMP r1 ,r0
0x080FA748  BHI 0x080FA74E
0x080FA74A  CMP r1, r0
0x080FA74C  BCC 0x080FA6FE
0x080FA74E  MOV r0, #0x1         ; r0 = 1 (should be read as "success")
    ; return true
0x080FA750  B 0x080FA75A         ; goto exit
0x080FA752  BL 0x08040EA4        ; r0, r1, r2 = AdvanceRNG()
0x080FA756  MOV r1, #0x1         ; r1 = 1
    ; AdvanceRNG and return false
		; why tho, double checked, it's not using this value at all.
0x080FA758  AND r0, r1           ; r0 = r0 & r1, essentially return false if either r0 or r1 is set
0x080FA75A  POP {r4,r5}          ; exit
0x080FA75C  POP {r1}
0x080FA75E  BX r1
```

## FID prediction

So I know there are 2 words in each FID candidate and that the first word is a comparator and the Feebas Seed, but I don't know what the last word is yet.  I suspect they'd be tied to trendy phrase given the connection between chaning trendy phrase and seed change.  It's also generated as 2 separate 16 bit sections, both of which have similar generation.

1. Let's prove that this is actually the case
2. Can this be used to predict the seed?  That is, if we know the trendy phrase and the TID, can we use that to work out what the Feebas Seed (and threfore tiles) must be?

Let's see if memory address 0x0202850C or 0x0202850E gets read while talking to NPCs in Dewford.

I set breakpoints for reading both address and they both got hit 2 times every frame, even outside Dewford.  (I hear there's anti-cheat checksumming going on behind the scenes, I wonder if that's involved?).  3 frames after pressing A on a Dewford NPC (1 frame before text screen appears), they both get called 3 times.  That's the frame I should investigate.

My values by the way are 0x1437 and 0x1819 for the mystery word with trendy phrase "ALONE TEST"

I tracelogged the frame with the extra check (since the VBA-next still doesn't have great breakpoint support).

Gets set in r1 around command 0x080FA5EF.  0x1437 gets placed in r1 shortly afterword (0x080EB507).  Appears in r5 around 0x080EB4CB, but that appears to be a return from the previous calls.  Immediately afterword if adds 2 (second mystery bits) and loads 0x1819 into r1.

I don't see any other places where 0x0202850C is in a register, so this looks like the correct place to check out what it's doing.

```
0x080FA5DC  PUSH {lr}
0x080FA5DE  LDR r0, [0x080FA5F8] (=0x0202E8CC)
0x080FA5E0  LDRH r1, [r0, 0x00]    ; r1 = *0x0202E8CC
	; I'm not familiar with what's in memory here
0x080FA5E2  LSL r1, r1, 0x03       ; r1 <<= 3
0x080FA5E4  LDR r0, [0x080FA5FC] (=0x02028508)
0x080FA5E6  ADD r1, r1, r0         ; r1 = 0x02028508 + 8 * (*0x0202E8CC)
0x080FA5E8  LDR r0, [0x080FA600] (=0x020231CC)
0x080FA5EA  ADD r1, 0x04           ; r1 += 4
  ; If 0x0202E8CC points to a 0, then this makes sense, it would sett r1 to 0x0202850C which
	; is the memory address we saw.
	; I wonder if 0x0202E8CC is a pointer to which "candidate" to use, but I don't know why it would need that.
0x080FA5EC  MOV r2, 0x02           ; r2 = 2
0x080FA5EE  MOV r3, 0x01           ; r3 = 1
0x080FA5F0  BL 0x080EB4D4          ; function call
0x080FA5F4  POP {r0}
0x080FA5F6  BX r0
  ; return
```

My guess would be 0x080EB4D4 is going to get some string data, or pointer to string data.

```
  ; Args:
	;   r0 = an address (0x020231CC)
	;   r1 = ??
	;   r2 = inner loop limit + 1
	;   r3 = outer loop limit
0x080EB4D4  PUSH {r4-r7,lr}
0x080EB4D6  MOV r7, r9
0x080EB4D8  MOV r6, r8
0x080EB4DA  PUSH {r6, r7}
0x080EB4DC  ADD sp, -0x04         ; stack pointer -= 4 (!?)
0x080EB4DE  ADD r4, r0, 0x0       ; r4 = r0
  ; r0 was set to the address 0x020231CC
0x080EB4E0  ADD r5, r1, 0x0       ; r5 = r1
  ; r1 was set to the address of the mystery bits
0x080EB4E2  LSL r2, r2, 0x10
... ; uint16_t r3;
0x080EB4E8  MOV r9, r3
  ; r9 = outer loop limit
0x080EB4EA  LDR r0, [0x080EB55C] (=0xFFFF0000)
0x080EB4EC  ADD r2, r2, r0
0x080EB4EE  LSR r7, r2, 0x10
  ; r7 = inner loop limit
	; uint16_t = r2 - 1 (with a way too obtuse way of subtracting 1) (probably to avoid bad stuff around 0 - 1?)
0x080EB4F0  MOV r0, 0x0
0x080EB4F2  CMP r0, r9
0x080EB4F4  BCS 0x080EB544        ; if (0 >= r9) skip outer loop
  ; skip outer loop if the counter was 0
0x080EB4F6  MOV r6, 0x0           ; r6 = 0
0x080EB4F8  ADD r0, 0x1           ; r0 += 1
0x080EB4FA  MOV r8, r0            ; r8 = r0
0x080EB4FC  CMP r6, r7
0x080EB4FE  BCS 0x080EB528        ; if (0 >= r7) skip inner loop
  ; skip inner loop if the counter was 0
0x080EB500  LDR r2, [0x080EB560] (=0x0000FFFF)
0x080EB502  LDRH r1, [r5, 0x0]    ; Load the 16 bits at r5 into r1 (the top mystery bits in our case)
0x080EB504  ADD r0, r4, 0x0       ; r0 = r4
0x080EB506  STR r2, [sp, 0x0]     ; store r2 on the stack
0x080EB508  BL 0x080EB41C         ; function call
0x080EB50C  ADD r4, r0, 0x0       ; r4 = r0
0x080EB50E  LDRH r0, [r5, 0x0]    ; Load the 16 bits at r5 into r0
0x080EB510  LDR r2, [sp, 0x0]     ; load r2 from the stack
  ; So it looks like we're using the stack to store some data temporarily.
	; Are we really out of working memory?  Or does the function call use this data too somehow?
0x080EB512  CMP r0, r2
0x080EB514  BEQ 0x080EB51C        ; if (r0 == r2) skip a few instructions ahead
0x080EB516  MOV r0, 0x0           ; r0 = 0
0x080EB518  STRB r0, [r4, 0x0]    ; *r4 = 0
0x080EB51A  ADD r4, 0x1           ; r4++
0x080EB51C  ADD r5, 0x2           ; r5 += 2
0x080EB51E  ADD r0, r6, 0x1
... uint16_t r6 = r0              ; r6++
0x080EB524  CMP r6, r7
0x080EB526  BCC 0x080EB502        ; if (r6 < r7) continue inner loop
  ; next inner loop         
0x080EB528  LDRH r1, [r5, 0x0]    ; Load the 16 bits from r5 into r1
0x080EB52A  ADD r5, 0x2           ; r5 += 2
0x080EB52C  ADD r0, r4, 0x0       ; r0 = r4
0x080EB52E  BL 0x080EB41C         ; function call
0x080EB532  ADD r4, r0, 0x0       ; r4 = r0
0x080EB534  MOV r0, 0xFE          ; r0 = 0xFE
0x080EB536  STRB r0, [r4, 0x0]    ; *r4 = 0xFE
0x080EB538  ADD r4, 0x1           ; r4++
0x080EB53A  MOV r1, r8
... uint16_t r0 = r1              ; r0 = r8
0x080EB540  CMP r0, r9
0x080EB542  BCC 0x080EB4F6        ; if (r0 < r9) continue inner loop
  ; next outer loop
0x080EB544  SUB r4, 0x1           ; r4--
0x080EB546  MOV r0, 0xFF          ; r0 = 0xFF
0x080EB548  STRB r0, [r4, 0x0]    ; *r4 = 0xFF
0x080EB54A  ADD r0, r4, 0x0       ; r0 = r4
0x080EB54C  ADD sp, 0x4           ; undo stack pointer manipulation above
0x080EB54E  POP {r3, r4}
0x080EB550  MOV r8, r3
0x080EB552  MOV r9, r4
0x080EB554  POP {r4-r7}
0x080EB556  POP {r1}
0x080EB558  BX r1
  ; return
```

```
  ; Args:
	;   r0 = an address (0x020231CC)
	;   r1 = the mystery bits
0x080EB41C  PUSH {r4-r7,lr}
0x080EB42E  ADD r5, r0, 0x0   ; r5 = r0 (r5 now holds the address 0x020231CC)
0x080EB420  LSL r6, r1, 0x10
  ; r6 holds the mystery bits shifted 16 bits left, which actually matters later
0x080EB422  LSR r4, r6, 0x10
  ; uint16_t r4 = r1
0x080EB424  ADD r7, r4, 0x0
0x080EB426  ADD r0, r4, 0x0   ; r4 gets moved into both r7 and r0 (r0 probably arg for next call)
 ; r0, r1, r4, and r7 are all holding the mystery bits at this point
0x080EB428  BL 0x080EB39C     ; ValidateWord(r0)
0x080EB42C  LSL r0, r0, 0x18
0x080EB42E  CMP r0, 0x0       ; essentially checking if the last 8 bits of r0 are 0 (uint8_t r0 == 0)
0x080EB430  BEQ 0x080EB440    ; if word is valid, go here.
0x080EB432  LDR r1, [0x080EB4EC] (=0x0842C904)
  ; if (r0 != 0) then r1 = 0x0842C904
	; Around this memory address:
	;   0xAC 0xAC 0xAC 0xFF
	; So it would copy 3 0xAC bytes into 0x020231CC.  I wonder if that's code point for '?'.  Not ASCII at any rate.
0x080EB434  ADD r0, r5, 0x0   ; r0 = 0x020231CC for this next function call
0x080EB436  BL 0x08006AB0     ; CopyBytes(into r0, from r1)
0x080EB43A  B 0x080EB4C6
  ; return
... data
0x080EB440  LDR r0, [0x080EB45C] (=0x0000FFFF)
  ; if (r0 == 0) then r0 = 0xFFFF
0x080EB442  CMP r4, r0
0x080EB444  BEQ 0x080EB4C0    ; If "mystery bits" == 0xFFFF, goto exit.
0x080EB446  LSR r1, r6, 0x19  ; r1 is now the index from the mystery bits
  ; relevant indecies are 0xA, 0xC, and 0xD
0x080EB448  LDR r2, [0x080EB460] (=0x000001FF)
  ; 0x01FF is a mask for the non-index portion of the mystery bits!
0x080EB44A  AND r2, r7        ; r7 probably still holding the mystery bits, so r2 is now the non-index portion
0x080EB44C  CMP r1, 0x13
0x080EB44E  BGT 0x080EB464
0x080EB450  CMP r1, 0x12
0x080EB452  BGE 0x080EB478
0x080EB454  CMP r1, 0x0
0x080EB456  BEQ 0x080EB468
0x080EB458  B 0x080EB488      ; This is the relevant branch
... data
0x080EB464  CMP r1, 0x15
0x080EB466  BNE 0x080EB488
0x080EB468  MOV r0, 0xB
0x080EB46A  ADD r1, r2, 0x0
0x080EB46C  MUL r1, r0
0x080EB46E  LDR r0, [0x080EB474] (=0x81F7114)
0x080EB470  ADD r1, r1, r0
0x080EB472  B 0x080EB4B8
... data
0x080EB478  MOV r0, 0xD  ; 0XD = emoticon for angel laughing its ass off
0x080EB47A  ADD r1, r2, 0x0
0x080EB47C  MUL r1, r0
0x080EB47E  LDR r0, [0x080EB484] (=0x081F82C8)
0x080EB480  ADD r1, r1, r0
0x080EB482  B 0x080EB4B8
... data
  ; RELEVANT BRANCH HERE
0x080EB488  LDR r0, [0x080EB4CC] (0x083DE158)   ; r0 = 0x083DE158
  ; This is a list (is it the same one used to constuct? -> no)
0x080EB48A  LSL r1, r1, 0x02                    ; r1 *= 4 (makes it a offset in the 0x083DE158 array)
0x080EB48C  ADD r1, r1, r0     ; r1 = address of ?? corresponding to the index of mystery bits
0x080EB48E  LDR r1, [r1, 0x0]  ; r1 = a word obtained from 0x083DE158[index]
  ; 0xA -> r1 = 0x083DD0F5
	; 0xC -> r1 = 0x083DD4E0
	; 0xD -> r1 = 0x083DD629
	; none of these addresses have data ??
0x080EB490  SUB r0, r2, 0x1    ; r0 = r2 - 1.  (r2 was the non-index portion of the mystery bits)
... uint16_t r2 = r2 - 1
0x080EB496  LDR r0, [0x080EB4D0] (0x0000FFFF)  ; r0 = 0xFFFF
0x080EB498  CMP r2, r0
0x080EB49A  BEQ 0x080EB4B8     ; if r2 == -1 (i.e. if the non-index mystery bits were 0 originally)
  ; if non-index mystery bits are 0, copy immediately.
0x080EB49C  ADD r3, r0, 0x0    ; r3 = 0xFFFF
  ; LOOP STARTS AFTER HERE
0x080EB49E  LDRB r0, [r1, 0x0] ; r0 = byte at r1.  (r1 is an address from the address of the max number of bits).
0x080EB4A0  ADD r1, 0x1        ; r1++
0x080EB4A2  SUB r2, 0x1        ; r2--
0x080EB4A4  CMP r0, 0xFF
0x080EB4A6  BEQ 0x080EB4B0     ; if r0 = 0xFF 
0x080EB4A8  LDRB r0, [r1, 0x0]
0x080EB4AA  ADD r1, 0x1
0x080EB4AC  CMP r0, 0xFF
0x080EB4AE  BNE 0x080EB4A8
0x080EB4B0  LSL r0, r2, 0x10
0x080EB4B2  LSR r2, r0, 0x10
0x080EB4B4  CMP r2, r3
0x080EB4B6  BNE 0x080EB49E
  ; The above code is going through ALL of the words (seperated by 0xFF) to find the one indexed by r2.
	; It does this by reading the 0xFF, adding 1 to r1, substracting 1 from r2, and then looping until it sees a 0xFF.
	; Once r2 == -1, they know they've hit the one they want (r2 starts 1 less than the non-index mystery bits).
0x080EB4B8  ADD r0, r5, 0x0   ; can branch to this to exit
  ; r0 = 0x020231CC
0x080EB4BA  BL 0x08006AB0     ; CopyBytes(into r0, from r1)
  ; So the r2^th word from the list at 0x083DD0F5, 0x083DD4E0, or 0x083DD629 gets copied into 0x020231CC
0x080EB4BE  ADD r5, r0, 0x0
0x080EB4C0  MOV r0, 0xFF
0x080EB4C2  STRB r0, [r5, 0x0]
0x080EB4C4  ADD r0, r5, 0x0
0x080EB4C6  POP {r4-r7}
0x080EB4C8  POP {r1}
0x080EB4CA  BX r1
```

0x83DD0F5: C2, C9, CE, FF, BF, D2, C3, CD, CE, CD, FF, ...

What if it's ascii but the upper bit set to 1 (for some reason)?

B I N _ ? Q C M N M _ 

Well that doesn't look right...

My trendy phrase has changed to "PREPOSTEROUS SONG"...

"PREPOSTEROUS" and "ALONE" are both part of the "CONDITIONS" list...which is the 10th one from the top (0xA).  "SONG" is part of the "HOBBIES" list which is 13th (0xD) and "TEST" is part of the "LIFESTYLE" list which is 12th (0xC).  That's a great match to lead us in the right direction.

Now unfortunately the "CONDITIONS" list starts "ABESNT", "ALONE", "AMUSING" which does not match with the data I was just reading above (length or letter matches).

My seeds for ALONE TEST were 0x1437 and 0x1819.  My values for PREPOSTEROUS SONG were 0x142E and 0x1A02

```
0x1437 = 0b[0001'010][0'0011'0111]
        index (0xA) ^
               position (dec 55) ^
0x1819 = 0b[0001'100][0'0001'1001]
        index (0xC) ^
               position (dec 25) ^
0x142E = 0b[0001'010][0'0010'1110]
        index (0xA) ^
               position (dec 46) ^
0x1A02 = 0b[0001'101][0'0000'0010]
        index (0xD) ^
               position (dec 2) ^
```

List 10 should have a max of 0x45 = dec 69, so this isn't simply in reverse order either.  It's legitamately unordered and must get reordered when inputting a new one (I'm only mildly terrified at this).

0x083DD629 : C3 BE C9 C6 FF BB C8 C3 C7 BF FF CD C9 C8 C1 FF C7 C9 D0 C3 BF FF ...

So CD C9 C8 C1 FF shound by S O N G _

Cool, they're ordered like the alphabet then.  Then the 12th list starts IDOL_ANIME_SONG_MOVIE_...

```
CopyBytes(into r0, from r1)
  Args:
	  r0 = an address that we're writing to.
		r1 = an address that we're reading from.
	
	Reads bytes from r1 (incrementing pointer after each read) and copies them into r0.
	Terminates after copying an 0xFF into r0.
0x08006AB0  ; short and rather unintersting, so leaving out for brevity
```

```
  ; Called before any copy, so might be relevant.
ValidateWord(uint16_t word (r0))
	Args:
	  r0 = mystery bits
	Returns:
	  r0 = 0 if word is valid, 1 otherwise.
0x080EB39C  PUSH {r4,r5,lr}
0x080EB39E  LSL r1, r0, 0x10
0x080EB3A0  LSR r3, r1, 0x10
0x080EB3A2  LDR r0, [0x080EB3C0] (=0x0000FFFF)
0x080EB3A4  CMP r3, r0
0x080EB3A6  BEQ 0x080EB40A
0x080EB3A8  LSR r2, r1, 0x19
  ; r2 = index bits of r0
0x080EB3AA  LDR r5, [0x080EB3C4] (=0x000001FF)
0x080EB3AC  AND r5, r3
  ; r5 = non-index bits of r0
0x080EB3AE  CMP r2, 0x15
0x080EB3B0  BHI 0x080EB414
0x080EB3B2  CMP r2, 0x13
0x080EB3B4  BGT 0x080EB3C8
0x080EB3B6  CMP r2, 0x12
0x080EB3B8  BGE 0x080EB3CC
0x080EB3BA  CMP r2, 0x0
0x080EB3BC  BEQ 0x080EB3CC
0x080EB3BE  B 0x080EB400
... data
0x080EB3C8  ; there's a branch to here
... truncated irrelevant bits
  ; RELEVANT BIT STARTS BELOW HERE
0x080EB400  LDR r0, [0x080EB410] (=0x083DF072)
  ; 0x083DF072 is a list (is it the same one used to constuct?)
0x080EB402  ADD r0, r2, r0
  ; r2 is index from mystery bits
0x080EB404  LDRB r0, [r0, 0x0]
	; 0xA -> r0 = 0x45
	; 0xC -> r0 = 0x2D
	; 0xD -> r0 = 0x36
0x080EB406  CMP r5, r0
0x080EB408  BCS 0x080EB414     ; if r5 >= r0 goto exit-ish
  ; If r5 >= r0, then the non-index portion of the mystery bits is invalid, since that's the
	; maximum number it should be.
	; I think this entire function is checking the validity of the mystery bits.
0x080EB40A  MOV r0, 0x0        ; r0 = 0
0x080EB40C  B 0x080EB416
0x080EB40E  LSL r0, r0, 0x0    ; nop
0x080EB410  BL 0x0815D48E      ; never executed in our path.
0x080EB414  MOV r0, 0x1
  ; bool ret = false;
	; if (r5 >= r0) {
	;   ret = true;
	; }
0x080EB416  POP {r4, r5}
0x080EB418  POP {r1}
0x080EB41A  BX r1
```

## Initial RNG seed Ruby

Looking into seed planting on Ruby (RNG, not berries)

0x08040ECD does something with RNG: STR r0, [r1] where r1 is adress of RNG, so this is likely the seed plant.

This function is right after the RNG advance in code so that makes sense too.  Now where is this called from?

```
0x08040EC8  LDR r1, [0x08040ED0] (=0x03004818)
  ; puts RNG address into r1
0x08040ECA  STR r0, [r1, 0x0]
  ; writes contents of r0 into RNG address
0x08040ECC  BX rl
  ; return
```

Appears to be called from 0x080003F8

```
0x080003DA  LSL r0, r0, 0x0
0x080003DC  ASR r0, r6, 0x1D
0x080003DE  LSL r0, r0, 0xC
0x080003E0  LSL r4, r7, 0x10
0x080003E2  LSL r0, r0, 0x0
  ; above is likely just data
0x080003E4  PUSH {LR}
0x080003E6  BL 0x0800968C
  ; What does this function do?  Probably picks the initial seed
0x080003EA  ADD r2, r0, 0x0       ; r2 = r0
0x080003EC  LSR r0, r2, 0x10      ; r0 = r2 >> 16
  ; r0 = r0 >> 16
0x080003EE  LDR r1, [0x080003FC] (=0x0000FFFF)
0x080003F0  AND r1, r2            ; r1 = r1 & r2
  ; r0 = bottom 16 bits of r2
0x080003F2  EOR r0, r1            ; r0 = r0 ^ r1
  ; r0 = bottom 16 bits of the return from 0x0800968C XOR top 16 bits of the return from 0x0800968C.
	; Hey, that matches what's going on with Sapphire
	; So I guess the formula in 0x0800968C is different which causes the different seed.
	;  It's not >:(
0x080003F4  BL 0x08040EC4
  ; plant seed
0x080003F8  POP {r0}
0x080003FA  BX r0
```

```
0x0800968C  PUSH {r4, lr}
0x0800968E  LDR r4, [0x080096C0] (=0x03000460)   ; the value at this register seems to be a constant: 0x02050722
  ; Actually, this is probably the place in memory where it reads time from.  When disabling real time it changed to 0x05010110
	; 0xXXXXXXXX
	;    ^ day of the week
	;      ^ this byte is the day
	;        ^ this byte is the month
	;         ^ tens of years after 2000
	;          ^ years after the decade
	; 0xXXXXXXXX (immediately following the previous)
	;    ^ ?? (always 0x40?)
	;     ^ tens of seconds after the minute
	;      ^ seconds after the last 10s increment.
	;       ^ 10s of minutes after the hour
	;        ^ minutes after the last ten minute increment
	;         ^ tens of hours after midnight
	;          ^ hours after the last ten hour increment within a day (eww...)
0x08009690  ADD r0, r4, 0x0      ; r0 = r4
0x08009690  BL 0x080092B4
  ; I'd be willing to bet this transforms Unix time into the god awful format described above
0x08009696  ADD r0, r4, 0x0      ; r0 = r4
0x08009698  BL 0x0800920C
  ; r0 = DaysAfter2000()
... r0 = uint16_t (r0)
0x080096A0  LSL r1, r0, 0x01     ; r1 = r0 << 1
0x080096A2  ADD r1, r1, r0       ; r1 = r1 + r0
0x080096A4  LSL r0, r1, 0x04     ; r0 = r1 << 4
0x080096A6  SUB r0, r0, r1       ; r0 = r0 - r1
0x080096A8  LSL r0, r0 0x05      ; r0 = r0 << 5
0x080096AA  LDRB r2, [r4, 0x4]   ; r2 = 4 byte offset from adress r4
  ; r2 = hours (in weird format)
0x080096AC  LSL r1, r2 , 0x04    ; r1 = r2 << 4
0x080096AE  SUB r1, r1, r2       ; r1 = r1 - r2
0x080096B0  LSL r1 ,r1, 0x02     ; r1 = r1 << 2
0x080096B2  ADD r0, r0, r1       ; r0 = r0 + r1
0x080096B4  LDRB r4, [r4, 0x5]   ; r4 = 5 bytes offset from address r4
  ; r4 = minutes (in weird format)
0x080096B6  ADD r0, r0, r4       ; r0 = r0 + r4
0x080096B8  POP {r4}
0x080096BA  POP {r1}
0x080096BC  BX r1                ; return
  ; days = DaysAfter2000()
	; days = days * 1440
	; hoursAdd = hours

...
0x080092B4  PUSH {r4, lr}
0x080092B6  ADD r2, r0, 0x0
...


; DaysAfter2000(r0 = weirdTimeAddress)
0x0800920C  PUSH {r4-r6, lr}
  ; r0 = adress of time
0x0800920E  ADD r6, r0, 0x0
0x08009210  LDRB r0, [r6, 0x0]
  ; r0 = years after 2000
0x08009212  BL 0x08009120       ; GetIntegerValueOfFuckedUpByte(years)
0x08009216  ADD r5, r0, 0x0
0x08009218  LSL r5, r5, 0x18
0x0800921A  LSR r5, r5, 0x18
  ; uint8_t r5 = GetYears()
0x0800921C  LDRB r0, [r6 0x1]
  ; r0 = month
0x0800921E  BL 0x08009120       ; GetIntegerValueOfFuckedUpByte(month)
0x08009222  ADD r4, r0, 0x0
0x08009224  LSL r4, r4, 0x18
0x08009226  LSR r4, r4, 0x18
  ; unit8_t r4 = GetMonth()
0x08009228  LDRB r0, [r6, 0x2]
  ; r0 = day of the month
0x0800922A  BL 0x08009120       ; GetIntegerValueOfFuckedUpByte(day)
0x0800922E  ADD r2, r0, 0x0
0x08009230  LSL r2, r2, 0x18
0x08009232  LSR r2, r2, 0x18
  ; uint8_t r2 = GetDays()
0x08009234  ADD r0, r5, 0x0
0x08009236  ADD r1, r4, 0x0
0x08009238  BL 0x08009180       ; r0 = GetDaysAfter2000(r0, r1, r2)
0x0800923C  LSL r0, r0, 0x10
0x0800923E  LSR r0, r0, 0x10
0x08009240  POP {r4-r6}
0x08009242  POP {r1}
0x08009244  BX r1


; GetIntegerValueOfFuckedUpByte(r0)
0x08009120  PUSH {lr}
0x08009122  LSL r0, r0, 0x18
0x08009124  LSR r2, r0, 0x18
  ; r2 = uint8_t (r0)
0x08009126  CMP r2, 0x9F
0x08009128  BHI 0x08009132
  ; if r2 > 0x9F go here
0x0800912A  MOV r3, 0xF       ; r3 = 0xF
0x0800912C  AND r3, r2        ; r3 = r3 & r2
0x0800912E  CMP r3, 0x9
0x08009130  BLS 0x08009136
  ; if r3 <= 0x9 go here
0x08009132  MOV r0, 0xFF      ; r0 = 0xFF
0x08009134  B 0x08009144      ; goto end;
0x08009136  LSR r1, r0, 0x1C  ; r1 = r0 >> 28  (only top 4 bits of r0 are left)
0x08009138  MOV r0, 0xF       ; r0 = 0xF
0x0800913A  AND r1, r0        ; r1 = r1 & 0xF
0x0800913C  LSL r0, r1, 0x2   ; r0 = r1 << 2
0x0800913E  ADD r0, r0, r1    ; r0 = r0 + r1
0x08009140  LSL r0, r0, 0x01  ; r0 = r0 << 1
0x08009142  ADD r0, r0, r3    ; r0 = r0 + r3
0x08009144  POP {r1} 
0x08009146  BX r1
  ; if (r0 > 159) { return 0xFF; }
	; uint8_t bottom = r0 & 0xF
	; if (thing > 9) { return 0xFF; }
	; uint8_t top = (r0 >> 4) & 0xF
	; r0 = 10*top + bottom
	; Guess what!  These are all stored so that the top byte represents a 10s place and the bottom byte represents the ones byte
	; So we just return the integer value!

	
; GetDaysAfter2000(r0 = years, r1 = months, r2 = days)
0x08009180  PUSH {r4-r7, lr}
0x08009182  MOV r7, r8
0x08009184  PUSH {r7}
... Make sure all the inputs are bytes
0x08009192  MOV r8, r2
0x08009194  MOV r5, 0x0
0x08009196  SUB r4, r7, 0x1
0x08009198  CMP r4, 0x0
0x0800919A  BLT 0x080091C0
0x0800919C  LDR r1, [0x08009204] (=0x0000016D) (decimal 365)
0x0800919E  ADD r0, r5, 1
... r5 = uint16_t (r0)
  ; this is a for loop with r5 as the counter
... r0 = uint8_t (r4)
0x080091A8  BL 0x08009148
... r0 = uint8_t (r0)
0x080091B0  CMP r0, 0x1
0x080091B2  BNE 0x080091BA
0x080091B4  ADD r0, r5, 0x1
... r5 = uint16_t (r0)
0x080091BA  SUB r4, 0x1
0x080091BC  CMP r4, 0x0
0x080091BE  BGE 0x0800919C
0x080091C0  SUB r0, r6, 0x1
0x080091C2  CMP r0, 0x0
0x080091C4  BLE 0x080091D8
0x080091C6  LDR r1, [0x08009208] (=0x081E7634)
0x080091C8  ADD r4, r0, 0x0
0x080091CA  LDMIA r1!, {r0}
0x080091CC  ADD r0, r5, r0
... r5 = uint16_t (r0)
0x080091D2  SUB r4, 0x1
0x080091D4  CMP r4, 0x0
0x080091D6  BNE 0x080091CA
0x080091D8  CMP r6, 0x2
0x080091DA  BLS 0x080091CA
0x080091DC  ADD r0, r7, 0x0
0x080091DE  BL 0x08009148
... r0 = uint8_t (r0)
0x080091E6  CMP r0, 0x1
0x080091E8  BNE 0x080091F0
0x080091EA  ADD r0, r5, 0x1
.. r5 = uint16_t (r0)
0x080091F0  MOVE r1, r8
0x080091F2  ADD r0, r5, r1       ; this is the final step after the for loop adding the days of the month
... r5 = uint16_t (r0)
0x080091F8  ADD r0, r5, 0x0
0x080091FA  POP {r3}
0x080091FC  MOVE r8, r3
0x080091FE  POP {r4-r7}
0x08009200  POP {r1}
0x08009202  BX r1
```

## Lotto number generation next to FID determination

The lotto number appears to be set at 0x02026B0A on the same frame as the start of FID determination.

0x080692A0 seems to be the instruction that sets it based on a trace log

```
080692A2:      8004  strh r4, [r0, #0]              R0:02026B0A R1:0806929F R2:0000404B R3:0300402D R4:000010EE R5:00000000 R6:030033A9 R7:00000000 R8:0300402D R9:00000000 R10:00000000 R11:00000000 R12:00000001 R13:03007E10 R14:0806929F R15:080692A4 CPSR:2000003F SPSR:00000000
```

r4 contains 0x10EE which is what I see written at the end of the frame.

It makes it into r4 around 0x08069296, so let's look at what's happening in that block of code.

```
16BitWrite : Writes r1 into a memory offset given by r0.  Retruns an error bit into r0
0x08069290  PUSH {r4,lr}
0x08069292  LSL r0, r0, 0x10
0x08069294  LSR r0, r0, 0x10
0x08069296  LSL r1, r1, 0x10
0x08069298  LSR r4, r1, 0x10
0x0806929A  BL 0x08069230      ; This is just setting up the write address
0x0806929E  CMP r0, 0x0
0x080692A0  BEQ 0x080692A8
0x080692A2  STRH r4, [r0, 0x0]
0x080692A4  MOV r0, 0x1
0x080692A6  B 0x080692AA
0x080692A8  MOV r0, 0x0
0x080692AA  POP {r4}
0x080692AC  POP {r1}
0x080692AE  BX r1
```

So it gets passed in as r1.  Need to go one level up.

```
Write0x02026B0A : Wrties a 32 bit number from r0 into 0x02026B0A
0x08145D34  PUSH {r4, lr}
0x08145D36  ADD r1, r0, 0x0    ; r1 = r0
0x08145D38  LSR r4, r1, 0x10   ; r4 = r1 >> 16
0x08145D3A  LSL r1, r1, 0x10   ; r1 = r1 << 16
0x08145D3C  LSR r1, r1, 0x10   ; r1 = r1 >> 16
0x08145D3E  LDR r0, 0x08145d54 (=0x0000404B)
0x08145D40  BL 0x08069290      ; The call that I found via trace log.
0x08145D44  LDR r0, 0x08145d58 (=0x0000404C)
0x08145D46  ADD r1, r4, 0x0
0x08145D48  BL 0x08069290      ; It's called twice!?
0x08145D4C  POP {r4}
0x08145D4E  POP (r0}
0x08145D50  BX r0
```

```
08145A98  PUSH {r4,lr}
08145A9A  BL 0x08040EA4  ; r0 = AdvanceRNG()
08145A9E  ADD r4, r0, 0x0
08145AA0  LSL r4, r4, 0x10
08145AA2  LSR r4, r4, 0x10
  ; r4 is a 16 bit random number
08145AA4  BL 0x08040EA4  ; r0 = AdvanceRNG()
08145AA8  LSL r0, r0, 0x10
08145AAA  ORR r0, r4     ; r0 = r0 | r4
  ; r0 is a 32 bit random number
08145AAC  BL 0x08145D34  ; Writes both r0 and r4 (??) into scratch space
08145AB0  LDR r0, 0x08145AC0 (=0x00004045)
08145AB2  MOV r1, 0x0
08145AB4  BL 0x08069290  ; Also just calls the writer directly
  ; Write 0 into 0x02026AFE
08145AB8  POP {r4}
08145ABA  POP {r0}
08145ABC  BX r0
```

Cool, so it is a random number.  I was surprised to see it written as 32 bits when only 16 would be used for the lotto number.  Now, can I find the order of when the RNG call happens?  If it happens before the FID determination, then it's no more useful than TID, but would be easier to use for non-starting day finding.  If it hapens after FID determination, it can be used for precision.

From RNG `0x8736A383` I get 49 advances to `0x10EE`.  Same game has Feebas seed `0xE7F2` with 18 advances away.  So Lotto happens after FID.

24 frames after A press to load game, new lotto determination happens.  FID changes on same frame.  These changed based on pressing A on different frames, so it is RNG.

RNG calls:

* 0x080005B4
* 0x08145ACA
* 0x08084C62

Hmmm, why is that all of them...

Has it determined it earlier and is just loading it?  I don't see any write instructions for the relevant values either...

I don't see any frames with suitable chunks of RNG to load this...but it's definitely doing the regular FID generating because the trendy phrase is valid.

```
PopulateNewDayLottoNumber()
0x08145AC4  PUSH {r4,r5,lr}
... r4 = uint16_t r0
0x08145ACA  BL 0x08040EA4  ; r0 = AdvanceRNG()
... r1 = uint16_t r0
0x08145AD2  SUB r0, r4, 0x1  ; r4 appears to be a loop counter in this context
... r4 = uint16_t r0
  ; r4--;
0x08145AD8  LDR r0, 0x08145B00 (=0x0000FFFF)
0x08145ADA  CMP r4, r0
0x08145ADC  BEQ 0x08145AF4
  ; if r4 == -1, write and exit
0x08145ADE  LDR r5, 0x08145B04 (=0x41C64E6D)
0x08145AE0  LDR r3, 0x08145B08 (=0x00003039)
0x08145AE2  ADD r2, r0, 0x0
  ; r2 = -1
0x08145AE4  ADD r0, r1, 0x0
  ; r0 = RNG
0x08145AE6  MUL r0, r5
0x08145AE8  ADD r0, r1, r3
  ; r0 = new RNG, but not quite the same as regular AdvanceRNG
0x08145AEA  SUB r0, r4, 0x1
... r4 = uint16_t r0
  ; r4--
0x08145AF0  CMP r4, r2
0x08145AF2  BNE 0x08145AE4
0x08145AF4  ADD r0, r1, 0x0
0x08145AF6  BL 0x08145D34  ; Writes r0 into scratch space (documented above)
0x08145AFA  POP {r4,r5}
0x08145AFC  POP {r0}
0x08145AFE  BX r0
```

So actually 0x08145ACA is the call that sets the new lotto number!  Interesting.  Then is the new FID generated entirely from 0x08084C62 using only a single random number?

```
0x08084C60  PUSH {lr}
0x08084C62  BL 0x08040EA4  ; r0 = AdvanceRNG()
... r0 = uint16_t r0
0x08084C6A  MOV r1, 0x64  ; r1 = 100
0x08084C6C  BL 0x081E0F20
  ; Need to figure out what this is doing.
... r1 = uint8_t r0
0x08084C74  ADD r2, r1, 0x0
0x08084C76  CMP r1, 0x3b  ; 0x3b = 59.  Doesn't ring a bell.
0x08084C78  BHI 0x08084C7E
  ; if r1 > 0x3b do ...
0x08084C7A  MOV r0, 0x0
0x08084C7C  B 0x08084CB0  ; goto exit
0x08084C7E  ADD r0, r1, 0x0
0x08084C80  SUB r0, 0x3c  ; Subtracting 60, actually. 59 + 1
... r0 = uint8_t r0
0x08084C86  CMP r0, 0x1d  ; 0x1d = 29.
0x08084C88  BHI 0x08084C8E
0x08084C8A  MOV r0, 0x1
0x08084C8C  B 0x08084CB0
  ; This kind of block repeated many times
0x08084C8E  ADD r0, r1, 0x0
0x08084C90  SUB r0, 0x5a  ; 0x5a = 90.  59 + 1 + 29 + 1
... r0 = uint8_t r0
0x08084C96  CMP r0, 0x4
0x08084C98  BHI 0x08084C9E
0x08084C9A  MOV r0, 0x2
0x08084C9C  B 0x08084CB0
0x08084C9E  ADD r0, r2, 0x0
0x08084CA0  SUB r0, 0x5F  ; 0x5F = 95.  59 + 1 + 29 + 1 + 4 + 1
... r0 = uint8_t r0
0x08084CA6  CMP r0, 0x3
0x08084CA8  BLS 0x08084CAE
0x08084CAA  MOV r0, 0x4
0x08084CAC  B 0x08084CB0
0x08084CAE  MOV r0, 0x3
0x08084CB0  POP {r1}
0x08084CB2  BX r1

; rng = AdvanceRNG() % 100
; if (rng < 60) {
;   return 0;
; } else if (rng < 90) {
;   return 1;
; } else if (rng < 95) {
;   return 2;
; } else if (rng < 99) {
;   return 3;
; } else {
;   return 4;
; }
```


I wonder if this is determining which FID index to make the new one?  60% chance to not change?  I could check that.  Also could go one level up to see where this is called from.

```
0x080854A8  PUSH {r4-r6,lr}
0x080854AA  ADD r6, r0, 0x0
0x080854AC  MOV r0, 0x0          ; r0 = 0
0x080854AE  STRB r0, [r6, 0x0]
  ; Set r6 to 0 (r6 is what was passed in from r0)
0x080854B0  BL 0x08084D8C
  ; Not sure yet
  ; Likely returns an index of some kind
...r3 = uint16_t r0
0x080854B8  LDR r0, [0x08085430] (=0x0000FFFF)
0x080854BA  CMP r3, r0
0x080854BC  BEQ 0x080854DA
  ; if the function call earlier returns -1, goto 0x080854DA
0x080854BE  LDR r2, [0x080854E4] (=0x0839D46C)
  ; r2 = 0x0839D46C (is that an address or a codepoint?) used like an address.
0x080854C0  LSL r1, r3, 0x2    ; r1 = index * 4
0x080854C2  ADD r1, r1, r3     ; r1 = r1 + index
0x080854C4  LSL r1, r1, 0x2    ; r1 = r1 * 4
  ; r1 = 20 * index
0x080854C6  ADD r0, r2, 0x4    ; r0 = r2 + 4
0x080854C8  ADD r0, r1, r0     ; r0 = r1 + r0
  ; r0 = address + 4 + 20*index
0x080854CA  LDR r5, [r0, 0x0]  ; r5 = *r0
0x080854CC  ADD r2, 0x8        ; r2 = r2 + 8
0x080854CE  ADD r1, r1, r2     ; r1 = r1 + r2
  ; r1 = address + 8 + 20*index
0x080854D0  LDR r4, [r1, 0x0]  ; r4 = *r1
  ; so r4 and r5 are 2 consecutive words in memory
  ; more over, they're used as addresses themselves
0x080854D2  CMP r5, 0x0
0x080854D4  BNE 0x080854E8
  ; if r5 != 0, goto 0x080854E8
0x080854D6  CMP r4, 0x0
0x080854D8  BNE 0x080854EE
  ; if r5 == 0 && r4 != 0, goto 0x080854EE
0x080854DA  MOV r0, 0x0        ; r0 = 0
0x080854DC  B 0x0808552E
  ; if r5 == 0 && r4 == 0, return 0;
... data
0x080854E8  CMP r4, 0x0
0x080854EA  BNE 0x08085520
  ; if r5 !=0 && r4 != 0, goto 0x08085520
0x080854EC  B 0x08085520
  ; otherwise goto to the same instruction
  ; just...why
0x080854EE  MOV r0, 0x1         ; r0 = 1
0x080854F0  STRB r0, [r6, 0x0]  ; *r6 = 1
0x080854F2  BL 0x08084C60       ; r0 = rand[0,4] weighted low
0x080854F6  LSL r0, r0, 0x18    ; r0 <<= 24
0x080854F8  LDR r1, [r4, 0x4]   ; r1 = *(r4 + 4)
0x080854FA  B 0x08085528        ; jump to finishing statements
  ;
  ; from here
0x080854FC  BL 0x08040EA4       ; AdvanceRNG(), but this can literally never be called
... r0 = uint16_t r0
0x08085504  MOV r1, 0x64
0x08085506  BL 0x081E0F20
... r0 = uint16_t r0
0x0808550E  CMP r0, 0x4f
0x08085510  BLS 0x08085520
0x08085512  MOV r0, 0x1
0x08085514  STRB r0, [r6, 0x0]
0x08085516  BL 0x08084C60       ; r0 = rand[0,4] weighted low
0x0808551A  LSL r0, r0, 0x18
0x0808551C  LDR r1, [r4, 0x4]
0x0808551E  B 0x08085528
  ;
  ; to here, not sure how this can be executed.
0x08085520  BL 0x08084BA4
  ; Not sure yet
  ; But this skips over the rand number generation, so I'm fairly certain this is no the code path we're interested in.
0x08085524  LSL r0, r0, 0x18
0x08085526  LDR r1, [r5, 0x4]
0x08085528  LSR r0, r0, 0x16    ; r0 >>= 22
  ; previous calls shifted this left 24, so this is effectively 4*r0, as an 8 bit number
0x0808552A  ADD r0, r0, r1      ; r0 += r1
0x0808552C  LDRH r0, [r0, 0x2]  ; r0 = *(r0 + 2)
  ; where r0 is r4 + 2 + 4*rand
0x0808552E  POP {r4-r6}
0x08085530  POP {r1}
0x08085532  BX r1

In practive my execution had r4 = 0x0839B604, which loaded into r1 0x0839B5F0, and r0 was 0 (60% chance).  The last load set r0 to 0x48.  Immediately after the function return 0x48 got stored into 0x02029814.  I have nothing setup to watch that address, so I don't know what it is. 0x0300 is usually scratch space though, while 0x0202 is persistent, so it doesn't look like this RNG is being used for anything :(
```

Looking a little more closely at the full memory map when the FID changes on day change:  The comparators change!  And then after they do, the FIDs are reordered, so the Feebas Seed and trendy phrases stay the same but get put into different places.  Interesting!  So if you never change the trendy phrase, I wonder if that means you can perpetually get the same 5 trendy phrases cycling in Dewford, and the same fishing spots cycling for Feebas.  At the same time, there's not enough RNG happening to change the compartors via randomness.  Is there really a deterministic way these swap through days?

So with dry battery, you actually have a really easy path to determint the Feebas seed on any day.  The trainer ID is perserved as knowledge of what RNG was when all the FIDs were generated, so you just have to find which FID generated the trendy phrase that you have today and read the same Feebas seed.

With live battery things are still a bit tricky because there's more options for what RNG generated the trainer ID.  But if you oberve the trendy phrases over multiple days, you could probably narrow it down and determine which starting seed could generate both.  My experiments showed you can narrow it down to ~25 seeds with just 1 day's knowledge.  And since there are much more than 25 possible trendy phrases, I'd wager you only need to see 2 days to get almost perfect knowledge of the Feebas seed.

With live battery in the context of speedrun, you'd still have to use the lotto number as the determining factor in which is the true seed.

One more note.  It seems that entering the game on different frames doesn't change which FID gets swapped into the top spot.  Matches with the fact that I don't see a RNG call for the swap.  I wonder if it's always the same swap?  [0,1,2,3,4] -> [1,3,0,4,2].  That would cycle through all 5 over 5 days.  Now the question is whether that literally cycles infinitely, or if it regenerates it at some point.

More experimentation!

It does not cycle regularly.  It modifes the Comparator part of the FID deterministically based on date, but then just re-sorts them, such that the FID0 is not guaranteed to change, and sometimes the other FIDs swap.  The comparator changes seem fairly stable around date, like it's just some simple addition happening here (and mostly to the lower bits with the upper bits remaining unchanged).

I'd also like to close on what happens to the FIDs when you change Trendy Phrase.


## Emerald

RNG advance function 0x0806F5CC

RNG calls on candidate frame:
- 0x0811EE3A
- 0x081224E8
- 0x0811EE3A
- 0x08122520
- 0x08122B28
- 0x08122B7A
- 0x08122B9A
- 0x0811EE3A
- 0x081224E8
- 0x0811EE3A
- 0x08122520
- 0x08122B28
- 0x08122B3E
- 0x08122B54
- 0x08122B7A
- 0x08122B9A
- 0x0811EE3A
- 0x081224E8
- 0x0811EE3A
- 0x08122520
- 0x08122B28
- 0x08122B3E
- 0x08122B7A
- 0x08122B9A
- 0x0811EE3A
- 0x081224E8
- 0x0811EE3A
- 0x08122520
- 0x08122B28
- 0x08122B7A
- 0x08122B9A
- 0x0811EE3A
- 0x081224E8
- 0x0811EE3A
- 0x08122520
- 0x08122B28
- 0x08122B7A
- 0x08122B9A
- 0x08177556
- 0x08177560
- 0x0818E618
- 0x0819FBD6

So the pattern is \[with prediction on what it's doing]
- 0x0811EE3A  \[pick random word from list]
- 0x081224E8  \[pick list 50/50]
- 0x0811EE3A  \[pick random word from list]
- 0x08122520  \[comp 1 bit]
- 0x08122B28  \[comp upper 1]
- 0x08122B3E (optional)  \[comp upper 2]
- 0x08122B54 (optional)  \[comp upper 3]
- 0x08122B7A  \[comp lower]
- 0x08122B9A  \[FID]

Let's verify that the numbers are the same, and then that would be perfect for reverse fid.

Deciding word from list (0x0811EE38):  Same for my purpose.  There's a slight difference in that the index is multipled by 8 and then offset by 4.  There must be extra data in these lists which means it needs to be indexed like this.

Choosing list (around 0x081224EC): Same for my purpose.  0xC and 0xD values unchanged per RNG being even or odd.  More duplicated code in Emerald than R/S for no reason?

Comparator single bit: exactly the same.

Comp upper 7 (around 0x08122B28): Exactly the same.

Comp lower 7 (around 0x08122B7E): Exactly the same.

FID (around 0x08122B9E): Exactly the same.

So reverse fid just needs to take account for the new TID -> FID timing.

