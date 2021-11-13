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
local rng=0x3004818
local i,j
local last=0
local cur
local test
local counter=0
local startvalue=0x000083ED
local indexfind
local index
local clr
local randvalue
--local iter

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

-- draws a 3x3 square
function drawsquare(a,b,c)
 gui.box(a,b,a+2,b+2,c)
end


while true do

 i=0
 cur=memory.readdword(rng)
 test=last
 while bit.tohex(cur)~=bit.tohex(test) and i<=100 do
  test=mult32(test,0x41C64E6D) + 0x6073
  i=i+1
 end
 gui.text(120,20,"Last RNG value: "..bit.tohex(last))
 last=cur
 gui.text(120,0,"Current RNG value: "..bit.tohex(cur))
 if i<=100 then
  gui.text(120,10,"RNG distance since last: "..i)
 else
  gui.text(120,10,"RNG distance since last: >100")
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
   index=index+bit.lshift(1,j)
   if j==31 then
    index=index+0x100000000
   end
  end
 end
 gui.text(120,30,index)
 
 
 test=cur
 gui.text(2,36,"v")
 -- i row j column
 for i=0,17,1 do
  for j=0,23,1 do
   if j%2==0 then
    clr=0xA0A0A0FF
   else
    clr=0xC0C0C0FF
   end
   randvalue=gettop(test)

   if randvalue%100>=50 and randvalue%100<=59 then
    if randvalue%10==0 then
      clr=0x00C0C0FF
    else
      clr=0x00FFFFFF
    end
   elseif randvalue%100==99 then
    if randvalue%10==0 then
       clr=0x00C000FF
    else
       clr=0x00FF00FF
    end
   else
    if randvalue%10==0 then
     clr=0x0000FFFF
    end
   end

   drawsquare(2+4*j,44+4*i, clr)

   test=mult32(test,0x41C64E6D) + 0x6073
  end
 end
 
 
 emu.frameadvance()

end
