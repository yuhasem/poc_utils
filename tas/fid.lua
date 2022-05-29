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
local saveSlot = 0;

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

local wantedTiles = {};
wantedTiles[99] = true;
wantedTiles[100] = true;
wantedTiles[101] = true;
wantedTiles[102] = true;
wantedTiles[103] = true;
wantedTiles[104] = true;
wantedTiles[111] = true;
wantedTiles[112] = true;
wantedTiles[113] = true;
wantedTiles[114] = true;
wantedTiles[115] = true;
wantedTiles[115] = true;
wantedTiles[116] = true;
wantedTiles[117] = true;
wantedTiles[118] = true;
wantedTiles[124] = true;
wantedTiles[125] = true;
wantedTiles[126] = true;
wantedTiles[127] = true;
wantedTiles[128] = true;
wantedTiles[129] = true;
wantedTiles[130] = true;
wantedTiles[131] = true;
wantedTiles[134] = true;
wantedTiles[135] = true;
wantedTiles[136] = true;
wantedTiles[137] = true;
wantedTiles[138] = true;
wantedTiles[139] = true;
wantedTiles[140] = true;
wantedTiles[141] = true;
wantedTiles[142] = true;
wantedTiles[145] = true;
wantedTiles[146] = true;
wantedTiles[147] = true;
wantedTiles[148] = true;
wantedTiles[149] = true;
wantedTiles[150] = true;
wantedTiles[152] = true;
wantedTiles[153] = true;
wantedTiles[154] = true;
wantedTiles[155] = true;
wantedTiles[157] = true;
wantedTiles[159] = true;
wantedTiles[159] = true;
wantedTiles[162] = true;
wantedTiles[163] = true;
wantedTiles[164] = true;
wantedTiles[165] = true;
wantedTiles[166] = true;
wantedTiles[167] = true;
wantedTiles[168] = true;
wantedTiles[169] = true;
wantedTiles[170] = true;
wantedTiles[173] = true;
wantedTiles[174] = true;
wantedTiles[175] = true;
wantedTiles[178] = true;
wantedTiles[181] = true;
wantedTiles[184] = true;
wantedTiles[185] = true;
wantedTiles[186] = true;
wantedTiles[189] = true;
wantedTiles[190] = true;
wantedTiles[191] = true;
wantedTiles[194] = true;
wantedTiles[195] = true;
wantedTiles[196] = true;
wantedTiles[197] = true;
wantedTiles[200] = true;
wantedTiles[201] = true;
wantedTiles[202] = true;
wantedTiles[203] = true;
wantedTiles[204] = true;
wantedTiles[205] = true;
wantedTiles[206] = true;
wantedTiles[208] = true;
wantedTiles[209] = true;
wantedTiles[210] = true;
wantedTiles[211] = true;
wantedTiles[212] = true;
wantedTiles[213] = true;
wantedTiles[214] = true;
wantedTiles[215] = true;
wantedTiles[216] = true;
wantedTiles[217] = true;
wantedTiles[218] = true;
wantedTiles[219] = true;
wantedTiles[220] = true;
wantedTiles[221] = true;
wantedTiles[222] = true;
wantedTiles[223] = true;
wantedTiles[224] = true;
wantedTiles[225] = true;
wantedTiles[226] = true;
wantedTiles[227] = true;
wantedTiles[228] = true;
wantedTiles[229] = true;
wantedTiles[230] = true;
wantedTiles[231] = true;
wantedTiles[232] = true;
wantedTiles[233] = true;
wantedTiles[234] = true;
wantedTiles[236] = true;
wantedTiles[237] = true;
wantedTiles[238] = true;
wantedTiles[239] = true;
wantedTiles[240] = true;
wantedTiles[241] = true;
wantedTiles[242] = true;
wantedTiles[243] = true;
wantedTiles[244] = true;
wantedTiles[245] = true;
wantedTiles[249] = true;
wantedTiles[250] = true;
wantedTiles[251] = true;
wantedTiles[252] = true;
wantedTiles[256] = true;
wantedTiles[257] = true;
wantedTiles[258] = true;
wantedTiles[259] = true;
wantedTiles[263] = true;
wantedTiles[264] = true;
wantedTiles[270] = true;
wantedTiles[271] = true;
wantedTiles[277] = true;
wantedTiles[283] = true;
wantedTiles[412] = true;
wantedTiles[413] = true;
wantedTiles[425] = true;
wantedTiles[426] = true;
wantedTiles[427] = true;
wantedTiles[428] = true;
wantedTiles[438] = true;
wantedTiles[439] = true;
wantedTiles[440] = true;

function containsOneOf(t, values)
  for index, value in ipairs(t) do
	  if (values[value]) then
		  return true;
	  end
	end
	return false;
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
	if (containsOneOf(tiles, wantedTiles)) then
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