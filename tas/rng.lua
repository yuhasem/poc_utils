-- RNG utilities for Ruby/Sapphire/Emerald
rng = {}

local rngAddress = 0x3004818

local mults={
 0x41C64E6D, 0xC2A29A69, 0xEE067F11, 0xCFDDDF21,
 0x5F748241, 0x8B2E1481, 0x76006901, 0x1711D201,
 0xBE67A401, 0xDDDF4801, 0x3FFE9001, 0x90FD2001,
 0x65FA4001, 0xDBF48001, 0xF7E90001, 0xEFD20001,
 0xDFA40001, 0xBF480001, 0x7E900001, 0xFD200001,
 0xFA400001, 0xF4800001, 0xE9000001, 0xD2000001,
 0xA4000001, 0x48000001, 0x90000001, 0x20000001,
 0x40000001, 0x80000001, 0x00000001, 0x00000001}

local adds={
 0x00006073, 0xE97E7B6A, 0x31B0DDE4, 0x67DBB608,
 0xCBA72510, 0x1D29AE20, 0xBA84EC40, 0x79F01880,
 0x08793100, 0x6B566200, 0x803CC400, 0xA6B98800,
 0xE6731000, 0x30E62000, 0xF1CC4000, 0x23988000,
 0x47310000, 0x8E620000, 0x1CC40000, 0x39880000,
 0x73100000, 0xE6200000, 0xCC400000, 0x98800000,
 0x31000000, 0x62000000, 0xC4000000, 0x88000000,
 0x10000000, 0x20000000, 0x40000000, 0x80000000}
 
--does 32-bit multiplication
local function mult32(a,b)
	local c=(a & 0xFFFF0000)/0x10000
	local d=(a & 0x0000FFFF)
	local e=(b & 0xFFFF0000)/0x10000
	local f=(b & 0x0000FFFF)
	local g=((c*f+d*e) & 0xFFFF)
	local h=d*f
	local i=g*0x10000+h
	return i
end

function rng.top(a)
	return a >> 16
end

function rng.current()
	return tonumber(memory.read_u32_le(rngAddress, "System Bus"))
end

function rng.advance(val, steps)
	for i=1,32,1 do
		if bit.check(steps,i-1) then
			val = (mult32(val, mults[i]) + adds[i]) & 0xFFFFFFFF
		end
	end
	return val
end

function rng.index(val)
	local index = 0
	local indexFind = 0
	for i=1,32,1 do
		if bit.check(val, i-1) ~= bit.check(indexFind, i-1) then
			indexFind = (mult32(indexFind, mults[i]) + adds[i]) & 0xFFFFFFFF
			index = index + (1 << i-1)
		end
	end
	return index
end

return rng