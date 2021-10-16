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
0x080FA4E2  LSL r0, r0, #0x10  ; r0 = r0 << 10
0x080FA4E4  LSR r5, r0, #0x10  ; r5 = r0 >> 10
    ; Uhhh.. WTF?  LSL = *Logical* shift left and LSR = *Logical* shift right, which means it's shifting in 0s
		; hmmm....the only way this would make r5 change is if r5 had 1s in the high 10 bits
		; So this is effectively "clearing" the top 10 bits of r5, after adding 1 to it.
		; And sets r0 as a side effect, but that's probably an accumulator and will be overwritten?
		;
		; r5 = (r5 + 1) & 0x003FFFFF
0x080FA4E6  CMP r5, r7
0x080FA4E8  BCC $080FA4BA      ; "Branch if C clear" -> C is clear if a borrow is required -> C is clear if r7 > r5
    ; if r5 <= r7 goto 0x080FA4BA
0x080FA4EA  MOV r1, r8         ; r1 = r8 (needed because high registers not accesible for normal operations in Thumb mode)
0x080FA4EC  LSL r0, r1, #0x10  ; r0 = r1 << 10
0x080FA4EE  LSR r2, r0, #0x10  ; r2 = r0 >> 10
    ; r2 = r8 & 0x003FFFFF
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
0x080FA496  MOV r9, r0         ; r9 appears to be the "argument" to the function
0x080FA498  LSL r1, r1, #0x10  ; r1 also an arg
0x080FA49A  LSR r7, r1, #0x10  ; r7 = r1 & 0x003FFFFF
0x080FA49C  LSL r2, r2, #0x18  ; r2 also an arg
0x080FA49E  LSR r2, r2, #0x18  ; r2 = r2 & 0x00003FFF
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
0x080FA4AC  LSR r5, r0, #0x10  ; r5 = r1 & 0x003FFFFF
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
0x080FA4CA  LSL r0, r0, #0x18  ; r0 = r0 << 18
0x080FA4CC  CMP r0, #0x0
0x080FA4CE  BEQ $080FA4E0      ; if r0 = 0 goto 0x080FA4E0 (skip the swap but don't break the inner loop)
...  ; swap *r4 and *r6
```

Now for the fun part:  trying to make sense of all this.  Something like

```
0x080FA48C(r1, r2, uint16_t arr[]) {
	for (i = 0; i < r7; i++) {
		for (j = i; j < r7; j++) {
			r0 = 0x080FA690()
			if (r0 % (1 << 18) != 0) {
			  arr[i] = arr[j]
			}
		}
	}
}
```

Those array address (arr[i] and arr[j]) are set into r0 and r1 right before the function call.  And what we got passed in as r2 we're setting back to r2 before the function call.  I wonder if that function call modifies those values at all?  Need to determine if these are really arguments.

(I still don't understand the reliance on LSL/LSR.)
