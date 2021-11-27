0x08040EA4 : r0, r1, r2 = AdvanceRNG()
r0 is returned as next RNG value (top 16 bits)
r1 is overwritten to 0x6073
r2 is overwritten to 0x03004818 (address of RNG value)

0x080FA690 : r0 = ShouldSwap(address r0, address r1, uint8_t r2)
r0 is return value.  If r0 != 0, caller should swap data in r0 and r1.
Calls AdvanceRNG() sometimes (circumstances unknown)

0x080FA48C : SwapMem(address start (r0), uint16_t num_to_swap (r1), unit8_t r2)
Swaps num_to_swap consecutive 16 bit datas at start with start + num_to_swap*16.

0x081E0920 : r0 = Remainder(int32_t dividend (r0), int32_t divisor (r1))
r0 is returned as the remainder when |dividend| is divided by |divisor|.
r1 must not be 0.
r1 and r4 will be unchanged by this function.
r2, r3, and r12 will be overwritten by this function.

0x081E0EB0 : r0 = UnsignedRemainder(uint32_t dividend (r0), int32_t divisor (r1))
r0 is returned as he remainder when |dividend| is divided by |divisor|.
if r1 = 0, returns r0 = 0.
Does not try to re-sign r0 or r1.  Slightly more efficient than Remainder().

0x08006AB0 : CopyBytes(address into (r0), address from (r1))
Copies bytes from r1 into r0, advancing both until a 0xFF is reached.
0xFF is also copied into r0.