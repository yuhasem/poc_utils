dofile("./rng.lua")

local savePtr = 0x3005D8C
-- Advance function: 0x0806F5CA
local rngPtr = 0x03005D80
local memoryDomain = "System Bus";

-- TID?  0x02000552, 0x02020000, or 0x02024AA2
-- SID?
-- RNG? 0x03005D80, 

while true do
	local save = memory.read_u32_le(savePtr, memoryDomain)
	gui.text(200, 20, string.format("save ptr: %x", save))
	
	local tid2 = memory.read_u16_le(0x02020000, memoryDomain)
	gui.text(200, 50, "tid "..tid2)
	local tid3 = memory.read_u16_le(save-0xFA2, memoryDomain)
	gui.text(200, 66, "tid? "..tid3)
	local sid = memory.read_u16_le(save-0xFA0, memoryDomain)
	gui.text(200, 82, "sid "..sid)
	
	local r = memory.read_u32_le(rngPtr, memoryDomain)
	gui.text(390, 20, string.format("current rng: %x", r))
	gui.text(390, 36, "rng index: "..rng.index(r))
	

	local candidatesStart = save + 0x2E68

	for i=0,4,1 do
		local candidate = candidatesStart + 8*i
		local comparator = memory.read_u16_le(candidate, memoryDomain)
		local feebas = memory.read_u16_le(candidate + 2, memoryDomain)
		local trendy1 = memory.read_u16_le(candidate + 4, memoryDomain)
		local trendy2 = memory.read_u16_le(candidate + 6, memoryDomain)
		
		gui.text(10,74*i+20,string.format("comp: %x", comparator))
		gui.text(10,74*i+36,string.format("feebas: %x", feebas))
		gui.text(10,74*i+52,string.format("word1: %x", trendy1))
		gui.text(10,74*i+68,string.format("word2: %x", trendy2))
	end
	
	emu.frameadvance()
end