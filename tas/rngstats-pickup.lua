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

dofile("rng.lua")

local defi
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

local memoryDomain = "System Bus";

-- draws a 3x3 square
function drawsquare(a,b,lineColor,fillColor)
 gui.drawBox(a,b,a+2,b+2,lineColor,fillColor)
end


while true do

 cur=rng.current()
 distance=rng.index(cur) - rng.index(last)
 gui.text(120,24,string.format("Last RNG value: %x", last))
 last=cur
 gui.text(120,0,string.format("Current RNG value: %x", cur))
 gui.text(120,12,"RNG distance since last: "..distance)

 
 if distance>2 and distance<=100 then
  gui.text(2,12,"***\n***\n***")
 end
 
 
 --indexing, a mathematical work
 index = rng.index(cur)
 gui.text(120,36,index)
 
 
 test=cur
 gui.text(2,36,"v")
 -- i row j column
 -- 5th row, 4th column is the first value where a pickup will be generated (for A press on XP gain, does not take into account levels, might take longer for large XP gains).
 for i=0,17,1 do
  for j=0,23,1 do
   if j%2==0 then
	  -- A draker gray for values we can't get
    clr=0xFFA0A0A0
   else
	  -- A light gray for values we can get
    clr=0xFFC0C0C0
   end
   randvalue=rng.top(test)

	 if randvalue%10 == 0 then
	   -- If a Pickup would be generated on this frame, color the box black
	   clr = 0xFF000000;
	 end
	 
	 local item = randvalue%100;
	 -- These Item values haven't fully been verified yet.  May need some revising.
	 if item >= 0 and item <= 29 then
	   -- Super Potion
		 fillColor = 0xFF606060;
	 elseif item >= 30 and item <= 39 then
	   -- Full Heal
	   fillColor = 0xFFA0A0A0;
	 elseif item >= 40 and item <= 49 then
	   -- Ultra Ball -> Magenta
	   fillColor = 0xFFFF00FF;
   elseif item >= 50 and item <= 59 then
		 -- Rare Candy -> Red
		 fillColor = 0xFFFF0000;
	 elseif item >= 60 and item <= 69 then
	   -- Full Restore -> Green
		 fillColor = 0xFF00FF00;
	 elseif item >= 70 and item <= 79 then
	   -- Revive -> White
		 fillColor = 0xFFFFFFFF;
	 elseif item >= 80 and item <= 89 then
	   -- Nugget -> Black
		 fillColor = 0xFF000000;
	 elseif item >= 90 and item <= 94 then
	   -- Protein -> Blue
		 fillColor = 0xFF0000FF;
	 elseif item >= 95 and item <= 98 then
	   -- PP Up -> Cyan
	   fillColor = 0xFF00FFFF;
   elseif randvalue%100==99 then
	   -- King's Rock -> Yellow
		 fillColor = 0xFFFFFF00;
   end

   drawsquare(2+4*j,44+4*i, clr, fillColor)

   test=rng.advance(test, 1)
  end
 end
 
 
 emu.frameadvance()

end
