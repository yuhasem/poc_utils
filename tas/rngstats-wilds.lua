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

-- 64
-- 4360 43C4 4428 448C 44F0 4554
-- 45C0 4624

--select pokemon
--frame 9192 delay 9264    (frame 6 delay is 0)    9265    9267-9270 is determine 9270

local defi
-- R/S:
-- local rng=0x3004818
-- E:
local rng=0x03005D80
local i,j
local last=0
local cur
local test
local counter=0
local startvalue=0x000083ED
local indexfind
local index
local clr
local fillColor
local randvalue
--local iter

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
local cave = false
local surf = false
 

--a 32-bit, b bit position, 0 is least significant bit
function getbit(a,b)
 local c=(a >> b)
 c=(c & 1)
 return c
end

--does 32-bit multiplication
function mult32(a,b)
 local c=(a & 0xFFFF0000)/0x10000
 local d=(a & 0x0000FFFF)
 local e=(b & 0xFFFF0000)/0x10000
 local f=(b & 0x0000FFFF)
 local g=((c*f+d*e) & 0xFFFF)
 local h=d*f
 local i=g*0x10000+h
 return i

end

function gettop(a)
 return a >> 16
end

-- draws a 3x3 square
function drawsquare(a,b,lineColor,fillColor)
 gui.drawBox(a,b,a+2,b+2,lineColor,fillColor)
end


while true do

 i=0
 cur=memory.read_u32_le(rng, memoryDomain)
 test=last
 while cur~=test and i<=100 do
  test = (mult32(test, 0x41C64E6D) + 0x6073) & 0xFFFFFFFF
  i=i+1
 end
 gui.text(120,24,string.format("Last RNG value: %x", last))
 last=cur
 gui.text(120,0,string.format("Current RNG value: %x", cur))
 if i<=100 then
  gui.text(120,12,"RNG distance since last: "..i)
 else
  gui.text(120,12,"RNG distance since last: >100")
 end
 
 if i>2 and i<=100 then
  gui.text(2,12,"***\n***\n***")
 end
 
 
 --indexing, a mathematical work
 indexfind=startvalue
 index=0
 for j=0,31,1 do
  if getbit(cur,j)~=getbit(indexfind,j) then
   indexfind=mult32(indexfind,multspa[j+1])+multspb[j+1]
   index=index+(1 << j)
   if j==31 then
    index=index+0x100000000
   end
  end
 end
 gui.text(120,36,index)
 
 test=cur
 gui.text(2,36,"v")
 -- i row j column
 -- 5th row, 4th column is the first value where a pickup will be generated (for A press on XP gain, does not take into account levels, might take longer for large XP gains).
 for i=0,17,1 do
  for j=0,15,1 do
	 -- Default light gray
   clr=0xFFC0C0C0
	 if j % 9 == 0 then
	   -- Dark gray on the tenth row.  While running, this is the column we can line up with.
	   clr = 0xFF404040;
	 end
   randvalue=gettop(test)

	 density = 320
	 if cave then
	   density = density / 2
	 end
	 if surf then
	   density = density / 5
	 end
	 if randvalue % 2880 < density then
	   -- Encounter Generated, black box
	   clr = 0xFF000000;
	 end
	 
	 local slot = randvalue%100;
	 if slot >= 0 and slot < 20 then
	     -- black for boring slot
		 fillColor = 0xFF000000;
	 elseif slot >= 20 and slot < 40 then
	     -- pink for boring slot
	     fillColor = 0xFFFFC0C0;
	 elseif slot >= 40 and slot < 50 then
	     -- Varying grays for 10% slots
	     fillColor = 0xFF404040;
     elseif slot >= 50 and slot < 60 then
		 fillColor = 0xFF808080;
	 elseif slot >= 60 and slot < 70 then
		 fillColor = 0xFFC0C0C0;
	 elseif slot >= 70 and slot < 80 then
		 fillColor = 0xFFFFFFFF;
	 elseif slot >= 80 and slot < 85 then
	     -- 1st 5% slot = magenta
		 fillColor = 0xFFFF00FF;
	 elseif slot >= 85 and slot < 90 then
	     -- 2nd 5% slot = cyan
		 fillColor = 0xFF00FFFF;
	 elseif slot >= 90 and slot < 94 then
	     -- 1st 4% slot = yellow
	     fillColor = 0xFFFFFF00;
	 elseif slot >= 94 and slot < 98 then
	     -- 2nd 4% slot = green
		 fillColor = 0xFF00FF00;
	 elseif slot >= 98 and slot < 99 then
	     -- 1st 1% slot = red
	     fillColor = 0xFFFF0000;
     elseif randvalue%100==99 then
	     -- 2nd 1% slot = blue
		 fillColor = 0xFF0000FF;
   end

   drawsquare(2+4*j,44+4*i, clr, fillColor)

   test=(mult32(test,0x41C64E6D) + 0x6073) & 0xFFFFFFFF
  end
 end
 
 
 emu.frameadvance()

end
