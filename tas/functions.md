0x08040EA4 : r0, r1, r2 = AdvanceRNG()
r0 is returned as next RNG value shifted right by 10 bits.
r1 is overwritten to 0x6073
r2 is overwritten to 0x03004818 (address of RNG value)
