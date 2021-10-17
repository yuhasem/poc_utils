0x08040EA4 : r0, r1, r2 = AdvanceRNG()
r0 is returned as next RNG value (top 16 bits)
r1 is overwritten to 0x6073
r2 is overwritten to 0x03004818 (address of RNG value)

0x080FA690 : r0 = ShouldSwap(address r0, address r1, uint8_t r2)
r0 is return value.  If r0 != 0, caller should swap data in r0 and r1.
Calls AdvanceRNG() sometimes (circumstances unknown)

0x080FA48C : SwapMem(address start (r0), uint16_t num_to_swap (r1), unit8_t r2)
Swaps num_to_swap consecutive 16 bit datas at start with start + num_to_swap*16.