-- Author: FractalFusion
-- Contibutors: 14flash
--
-- http://tasvideos.org/3186S.html
-- http://tasvideos.org/forum/viewtopic.php?t=4101
-- http://tasvideos.org/forum/viewtopic.php?t=4101&postdays=0&postorder=asc&start=100 me post
-- http://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_data_structure_in_Generation_III
-- ruby/sapphire 0x03004360   3004290 J
-- emerald 0x02024190 J 0x020244EC U
-- firered 0x02024284
-- leafgreen 0x020241e4
-- http://pastebin.com/ZHxPYDsN

local rngAddress=0x3004818
local rngValue
local elipses
local reelInFrames
local reel
local reelText

local bnd,br,bxr=bit.band,bit.bor,bit.bxor

local multspa={
 0x41C64E6D, 0xC2A29A69, 0xEE067F11, 0xCFDDDF21,
 0x5F748241, 0x8B2E1481, 0x76006901, 0x1711D201,
 0xBE67A401, 0xDDDF4801, 0x3FFE9001, 0x90FD2001,
 0x65FA4001, 0xDBF48001, 0xF7E90001, 0xEFD20001,
 0xDFA40001, 0xBF480001, 0x7E900001, 0xFD200001,
 0xFA400001, 0xF4800001, 0xE9000001, 0xD2000001,
 0xA4000001, 0x48000001, 0x90000001, 0x20000001,
 0x40000001, 0x80000001, 0x00000001, 0x00000001}
 
local multspb={
 0x00006073, 0xE97E7B6A, 0x31B0DDE4, 0x67DBB608,
 0xCBA72510, 0x1D29AE20, 0xBA84EC40, 0x79F01880,
 0x08793100, 0x6B566200, 0x803CC400, 0xA6B98800,
 0xE6731000, 0x30E62000, 0xF1CC4000, 0x23988000,
 0x47310000, 0x8E620000, 0x1CC40000, 0x39880000,
 0x73100000, 0xE6200000, 0xCC400000, 0x98800000,
 0x31000000, 0x62000000, 0xC4000000, 0x88000000,
 0x10000000, 0x20000000, 0x40000000, 0x80000000}

local memoryDomain = "System Bus";

local encounterTableAddress = 0x839D29C;
local cave = true
local surf = false
 

--a 32-bit, b bit position, 0 is least significant bit
function getbit(a,b)
 local c=bit.rshift(a,b)
 c=bnd(c,1)
 return c
end

--does 32-bit multiplication
function mult32(a,b)
 local c=bnd(a,0xFFFF0000)/0x10000
 local d=bnd(a,0x0000FFFF)
 local e=bnd(b,0xFFFF0000)/0x10000
 local f=bnd(b,0x0000FFFF)
 local g=bnd(c*f+d*e,0xFFFF)
 local h=d*f
 local i=g*0x10000+h
 return i

end

function gettop(a)
 return(bit.rshift(a,16))
end

rngValue = memory.read_u32_le(rngAddress, memoryDomain);
for i=1,58,1 do
  rngValue = bnd(mult32(rngValue, 0x41C64E6D) + 0x6073, 0xFFFFFFFF);
end
-- TODO: For Super Rod this may not be 1, will read RNG and make adjustments later
console.writeline("Fish cycles: 1");
for i=1,62,1 do
  rngValue = bnd(mult32(rngValue, 0x41C64E6D) + 0x6073, 0xFFFFFFFF);
end
-- TODO: for super rod 2nd+ cycles, this can be lower (it doesn't do the +4), will need to make adjustments.
console.writeline(rngValue)
elipses = math.min(10, (gettop(rngValue) % 10) + 4)
console.writeline("Elipses: "..elipses);
reelInFrames = 21 + 20*elipses
for i=1,reelInFrames,1 do
  rngValue = bnd(mult32(rngValue, 0x41C64E6D) + 0x6073, 0xFFFFFFFF);
end
console.writeline(rngValue)
reel = gettop(rngValue) % 2 == 0
if reel then
  reelText = "Yes";
else
  reelText = "No";
end
console.writeline("Reel in: "..reelText);
console.writeline("---");
console.writeline("");