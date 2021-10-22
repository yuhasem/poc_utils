-- Finds TID and FID values that are beneficial for getting Feebas/Milotic.
--
-- Should be run when pressing A will end the opening dialogue and generate
-- TID/SID/FID.
--
-- This script just uses simple frame advancing to check all the values, since
-- FID is extremely difficult to predict.

-- How many frames to advance beyond starting point to check for beneficial
-- values.  Change this if you have tighter or looser timing restrictions.
local maxFramesToWait = 120;
-- The save slot to use while searching.  Change this if you don't want this
-- slot to be overwritten.
local saveSlot = 9;

local memoryDomain = "EWRAM";
local TIDAddress = 0x024EAE;
local FIDAddress = 0x02850A;

-- Stolen from FractalFusion (http://tasvideos.org/3186S.html)
--
-- Why do we even need to do this?  Because Lua doesn't have fixed with
-- integers and is losing information to rounding errors in floating point
-- multiplication (despite the documentation saying this is impossible). I
-- think this makes sense for N64 emulation where 64 bit floating multiplies
-- are common place, but for lighter weigth systems, it feels like Lua was the
-- worst possible choice of language to use for TAS.
function mult32(a,b)
 local c=bit.band(a,0xFFFF0000)/0x10000
 local d=bit.band(a,0x0000FFFF)
 local e=bit.band(b,0xFFFF0000)/0x10000
 local f=bit.band(b,0x0000FFFF)
 local g=bit.band(c*f+d*e,0xFFFF)
 local h=d*f
 local i=g*0x10000+h
 return i

end

function feebasTiles(seed)
  tiles = {};
	local i = 0;
	while (i < 6) do
	  seed = bit.band(mult32(seed, 0x41C64E6D) + 0x3039, 0xFFFFFFFF);
		local tile = bit.band(bit.rshift(seed, 16), 0xFFFF) % 0x1BF;
		if (tile == 0) then
		  tile = 447;
		end
		if (tile >= 4) then
  		table.insert(tiles, tile);
			-- Because this is legitimately easier than finding the length of a
			-- table in lua.
			i = i + 1;
		end
	end
	return tiles;
end

function contains(t, val)
  for index, value in ipairs(t) do
	  if (value == val) then
		  return true;
	  end
	end
	return false;
end

function checkIDs(iteration)
	local buttons = {};
	buttons.A = "True";
	joypad.set(buttons);
	-- This advances to the point where TID/SID are set.
	for i = 1, 75 do
	  emu.frameadvance();
	end
	
	local TID = memory.read_u16_le(TIDAddress, memoryDomain)
	if (TID % 5 ~= 1) then
	  return false;
	end
	
	-- This advances to the points where FID is set, after making sure TID was
	-- viable.
	for i = 1, 3 do
	  emu.frameadvance();
	end
	
	local FID = memory.read_u16_le(FIDAddress, memoryDomain);
	local tiles = feebasTiles(FID);
	if (contains(tiles, 289)) then
	  console.writeline(string.format("i: %d, TID: %05d, FID: %x, contains best tile (289)", iteration, TID, FID, tiles[best]));
		return true;
	end
	if (contains(tiles, 99) or contains(tiles, 428) or contains(tiles, 412) or contains(tiles, 413)) then
	  console.writeline(string.format("i: %d, TID: %05d, FID: %x, contains good tiles:", iteration, TID, FID));
		console.write("\t")
		for index, tile in ipairs(tiles) do
		  console.write(string.format("%d, ", tile));
		end
		console.writeline("");
	end
	return false;
end

-- function testTiles(seed)
  -- local tiles = feebasTiles(seed);
	-- for index, tile in ipairs(tiles) do
		-- console.write(string.format("%d, ", tile));
	-- end
	-- console.writeline("");
-- end

function main()
  console.clear();
	client.unpause();
  savestate.saveslot(saveSlot);
	for i = 1, maxFramesToWait do
	  savestate.loadslot(saveSlot);
		emu.frameadvance();
		savestate.saveslot(saveSlot);
		if (checkIDs(i)) then
		  break;
	  end
	end
	client.pause();
end

main()