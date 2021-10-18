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

Nothing obvious standing out (not a direct copy, not an xor with anything else I have).

## FID generation

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
    ; r5 is inner loop counter, initialized to outer loop counter
0x080FA4AE  MOV r8, r1         ; r8 = r1
    ; r8 stores outer loop counter
0x080FA4B0  CMP r5, r7
0x080FA4B2  BCS $080FA4EA      ; if r5 >= r7 goto 0x080FA4EA (break inner loop)
0x080FA4B4  LSL r0, r2, #0x03  ; r0 = r2 << 3  or  r0 = 8 * outer_loop_counter
    ; Shift left 3 aligns this to a 16 bit address!!
0x080FA4B6  MOV r1, r9         ; r1 = r9
0x080FA4B8  ADD r6, r1, r0     ; r6 = r1 + r0
    ; r9 was an address!  and r0 is using the loop counter to index a place ahead of that!
0x080FA4BA  LSL r0, r5, #0x03  ; r0 = r5 << 3
0x080FA4BC  MOV r1, r9         ; r1 = r9
0x080FA4BE  ADD r4, r1, r0     ; r4 = r1 + r0
    ; same thing here but using r5 as the index.
0x080FA4C0  ADD r0, r4, #0x0   ; r0 = r4
0x080FA4C2  ADD r1, r6, #0x0   ; r1 = r6
0x080FA4C4  MOV r2, r10        ; r2 = r10
0x080FA4C6  BL $080FA690       ; Call function at 0x080FA690
0x080FA4CA  LSL r0, r0, #0x18  ; r0 = only bottom 8 of r0 left in
0x080FA4CC  CMP r0, #0x0
0x080FA4CE  BEQ 0x080FA4E0      ; if r0 = 0 goto 0x080FA4E0 (skip the swap but don't break the inner loop)
...  ; swap *r4 and *r6
```

Now for the fun part:  trying to make sense of all this.  Something like

```
0x080FA48C(r1, r2, uint16_t arr[]) {
	for (i = 0; i < r7; i++) {
		for (j = i; j < r7; j++) {
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
0x080FA690  PUSH {r4,r5,lr}
0x080FA692  ADD r3, r0, #0x0
0x080FA694  ADD r5, r1, #0x0
    ; So r0 and r1 are args.  r3 should be the "lower" address, r5 should be the "higher address"
		; r3 and r5 are addresses whose data we might want to swap
0x080FA696  LSL r2, r2, #0x18
    ; r2 is arg, but no idea what it represents (was an arg in the previous function, too, but unused).
0x080FA698  LSR r2, r2, #0x18
0x080FA69A  ADD r0, r2, #0x0      ; r0 = bottom 8 bits of r2
0x080FA69C  CMP r2, #0x1
0x080FA69E  BEQ 0x080FA6D6        ; if r2 = 1 goto 0x080FA6D6
0x080FA6A0  CMP r2, #0x1
0x080FA6A2  BGT 0x080FA6AA        ; if r2 > 1 goto 0x080FA6AA
0x080FA6A4  CMP r2, #0x0
0x080FA6A6  BEQ 0x080FA6B0
0x080FA6A8  B 0x080FA752
0x080FA6AA  CMP r2, #0x0
0x080FA6AC  BEQ 0x080FA702
0x080FA6AE  B 0x080FA752
0x080FA6B0  LDRB r0, [r3, #0x0]  ; Load *byte* at r3 + 0
0x080FA6B2  LSL r1, r0, #0x19
0x080FA6B4  LDRB r0, [r5, #0x0]
0x080FA6B6  LSL r0, r0, #0x19
0x080FA6B8  CMP r1, r0
0x080FA6BA  BHI 0x080FA74E        ; "Branch if C set and Z clear (unsigned higher)".  Unsighed Higher is like Greater Than but treats the arguments as unsigned.
0x080FA6BC  CMP r1, r0
0x080FA6BE  BCC 0x080FA6FE
0x080FA6C0  LDRH r0, [r3, #0x0]  ; Load *half-word* at r3 + 0
0x080FA6C2  LSL r3, r0, #0x12
0x080FA6C4  LDRH r0, [r5, #0x0]
0x080FA6C6  LSL r2, r0, #0x12
0x080FA6C8  LSR r1, r3, #0x19
0x080FA6CA  LSR r0, r2, #0x19
0x080FA6CC  CMP r1, r0
0x080FA6CE  BHI 0x080FA74E
0x080FA6D0  LSR r1, r3, #0x19
0x080FA6D2  LSR r0, r2, #0x19
0x080FA6D4  B 0x080FA6FA
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
    ; << 3 means r6 may also be used as an index to a uint16_t[].
0x080FA1BA  ADD r5, r4, r7
    ; so r7 is probably an address (0x02025734 if it's not modified by 0x080EB74C)
0x080FA1BC  LDR r2, [0x080FA1DC] (=0x00002DD8)
0x080FA1BE  ADD r1, r5, r2
    ; r1 = 0x0202850C + index
0x080FA1C0  STRH r0, [r1, #0x0]  ; *r1 = r0
    ; r0 is index + random size, stored into memory here
0x080FA1C2  BL 0x08040EA4
    ; This likely sets r0 to a new value.
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
     ; This likely sets r0 to a new value
0x080FA1F0  ADD r3, r4, r7
     ; r3 = 0x02025734 + index
		 ; assuming r7 and r4 are unchanged
0x080FA1F2  MOV r2, r8           ; r2 = 1
0x080FA1F4  AND r2, r0           ; r2 = r0 & 1
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
0x080FA208  STRB r0, [r3, #0x0]  ; write it back
     ; honestly wtf
0x080FA20A  MOV r1, r9
    ; r1 = 0x02028508
0x080FA20C  ADD r0, r4, r1
    ; r0 = 0x02028508 + index
		; assuming r4 is unchanged
0x080FA20E  BL 0x080FA760
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
0x080EB786  MOV r0, #0x7f  ; hello negative 1
0x080EB788  AND r0, r4     ; bottom 7 bits of r4
0x080EB78A  LSL r0, r0, #0x09  ; then shift left 9
0x080EB78C  LDR r1, [0x080EB7A0] (=0x000001ff)
0x080EB78E  AND r2, r1
0x080EB790  ORR r0, r2
		; r0 = 0b0000'0000'0000'0000'xxxx'xxxy'yyyy'yyyy
		;                           from r4 ^  from r2 ^
		; r4 being the index, r2 being a random number between 0 and "size"
		; The sizes I've seen are all less than 512, so there's no information loss here.
0x080EB792  POP {r4}
0x080EB794  POP {r1}
0x080EB770  BX r1
```

One thing that stands out to me is that there is no `STR` command.  So it's not directly writing to FID or FID-swap.  The address would have been passed in as r1, but it looks the result (r0) is getting stored into that address.  So let's focus on what r0 gets returned as.

~~Need to understand subroutine 0x081E0920.~~  I'll spare the massive text blob since it's very uninteresting once you understand the function.  0x081E0920 returns in r0 the remainder of r0 divided by r1.

Still not quite sure what to call 0x080EB74C.  It is returning both the given index and a random size.  Are either used by the callers?
