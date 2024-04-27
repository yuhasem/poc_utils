-- The RNG state space of berry blending is too big and the occurrence of
-- 160 RPM is to rare for me to do this unassissted.  So here's a program
-- to navigate to the best results.

-- The premise is this:  There is a limited time we have to influence the
-- RNG while the blend head is close to us without reducing the RPM.
-- Reducing the RPM with a miss is never made back (even with perfect NPC
-- manipulation because of it).  So we consider the events on those frames
-- a single action, and do a graph search through the actions to find the
-- best result.

-- The depth of the search is probably only 16.  Maybe a 17th is possible
-- with the fastest results?  The first action has 14 frames, so 2^14
-- actions, although not all of them are distinct.  The state we care about
-- leaving player control is: <RNG index, RPM, blend head angle, time counter>.
-- Most of the time RPM will not change between actions.  RNG index typically
-- looks like a function of the number of A presses, although this isn't
-- always true.  Blend head angle and time counter are more likely to vary
-- based on the inputs to get into the action than the output of the action.
-- Most spins will have 4-6 frames, so an average of around 40 actions.
-- Doing an exhaustive search isn't feasible.  Because the state expansion
-- is much larger at the start of the sequence, A* probably isn't a good
-- fit either.  Most of those first actions will get tried when it's not
-- possible to get stellar RNG on a single cycle later on.  Depth first
-- search seems a good candidate.  It won't find the optimal way to get to
-- 160 RPM, but it will find a way (if it exists) efficiently.

-- Consider taking only the top K results from each action (K=[3,5]).
-- It could reduce the branching factor enough for A* to be feasible and
-- may not affect DFS too much while being much more efficient space-wise.

-- Need a way to order the results of an action.

-- Let's start by generating all possible actions, deduplicating, and
-- displaying the result.

-- Decision 1: Emualte or simulate?  Simulating would be a lot more
-- efficient, but it will take longer to get working because I don't
-- understand all of the ways RNG works for actions.

----------------------
-- CONSTANTS
----------------------
-- important addresses
local rngAddress=0x3004818
local blendHeadAddress=0x2018054
local rotSpeedAddress=0x02018056
-- counts up 1 each frame. when this is 5, rolls over to 0 and applies friction
local frictionCounterAddress=0x0201807E
local counterAddress=0x0201812C
-- used to determine the action size?
local playerMissesAddress=0x2018150
-- used to determine number of RNG calls
local screenShakeHorzAddress=0x02018144
local screenShakeVertAddress=0x02018146

-- The game uses integer division against this number to determine odds,
-- instead of the usual remainder.  We can make things easier to
-- understand and more efficient if we reverse this to check a multiple of
-- this "percent" against RNG.
local onePercent=655

local playerHead=0x20
local laddieHead=0x60
local lassieHead=0xA0
local misterHead=0xE0

local slowDecision=0x1F3
local fastDecision=0x5DB

local missLoss=0x40
local hitGain=0x40
local perfectSlowGain=0x60
local perfectGain=0x20

local friction=0x01

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
----------------------
-- END CONSTANTS
----------------------

--does 32-bit multiplication
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

function gettop(a)
 return(bit.rshift(a,16))
end

local rng
local blendHead
local rotSpeed
local frictionCount
local shakeHorz
local shakeVert
local rotations
local initBlendHead
local laddieAction
local lassieAction
local misterAction
local perfect
local hit
local miss

-- Display stuffs
local guiHieght

function logMiss(npc)
  gui.text(10,guiHieght,npc)
  gui.text(100,guiHieght,"Miss","blue")
  guiHieght = guiHieght + 24
  -- TODO: actually there's a countdown for misses
  -- In practice, doesn't matter since you need to manipulate no misses anyway.
  miss = 1
end

function logNone(npc)
  gui.text(10,guiHieght,npc)
  gui.text(100,guiHieght,"None")
  guiHieght = guiHieght + 24
end

function logHit(npc)
  gui.text(10,guiHieght,npc)
  gui.text(100,guiHieght,"Hit")
  guiHieght = guiHieght + 24
  hit = 1
end

function logPerfect(npc)
  -- TODO: for now assuming the shake disappears by the time we get
  -- to the next input.  In reality, we'll need to update shake
  -- accordingly
  if (shakeHorz == 0) then
    rng = bit.band(mult32(rng, 0x41C64E6D) + 0x6073, 0xFFFFFFFF)
  end
  if (shakeVert == 0) then
    rng = bit.band(mult32(rng, 0x41C64E6D) + 0x6073, 0xFFFFFFFF)
  end
  gui.text(10,guiHieght,npc)
  gui.text(100,guiHieght,"Perfect","red")
  guiHieght = guiHieght + 24
  perfect = 1
end



-- TODO: these could be parameterized further as well
function laddieRng()
  local name = "Laddie"
  if (laddieAction == 1) then
    return
  end
  rng = bit.band(mult32(rng, 0x41C64E6D) + 0x6073, 0xFFFFFFFF)
  rand = gettop(rng)
  if (rotSpeed < slowDecision) then
    if (rand < 66*onePercent) then
	  logHit(name)
	else
	  logPerfect(name)
	end
  else
    if (rand < 10*onePercent) then
	  logMiss(name)
	elseif (rand < 40*onePercent) then
	  logNone(name)
	elseif (rand < 65*onePercent) then
	  logHit(name)
	else
	  logPerfect(name)
	end
  end
end

function lassieRng()
  local name = "Lassie"
  if (lassieAction == 1) then
    return
  end
  rng = bit.band(mult32(rng, 0x41C64E6D) + 0x6073, 0xFFFFFFFF)
  rand = gettop(rng)
  -- console.writeline(string.format("lassie acting on rng: %x", rand))
  if (rotSpeed < slowDecision) then
    if (rand < 89*onePercent) then
	  logHit(name)
	else
	  logPerfect(name)
	end
  else
    if (rand < 5*onePercent) then
	  logMiss(name)
	elseif (rand < 55*onePercent) then
	  logNone(name)
	elseif (rand < 60*onePercent) then
	  logHit(name)
	else
	  logPerfect(name)
	end
  end
end

function misterRng()
  local name = "Mister"
  if (misterAction == 1) then
    return
  end
  rng = bit.band(mult32(rng, 0x41C64E6D) + 0x6073, 0xFFFFFFFF)
  rand = gettop(rng)
  -- console.log(string.format("mister acting on rng: %x", rand))
  if (rotSpeed < slowDecision) then
    -- Due to a bug, there is no 25% chance to Perfect and the result
	-- will always be hit.
    logHit(name)
  elseif (rotSpeed < fastDecision) then
    -- console.log("medium speed decision")
    if (rand < 10*onePercent) then
	  logMiss(name)
	elseif (rand < 20*onePercent) then
	  logNone(name)
	elseif (rand < 80*onePercent) then
	  logHit(name)
	else
	  logPerfect(name)
	end
  else
    -- console.log("high speed decision")
    if (rand < 30*onePercent) then
	  logMiss(name)
	elseif (rand < 70*onePercent) then
	  logNone(name)
	elseif (rand < 90*onePercent) then
	  logHit(name)
	else
	  logPerfect(name)
	end
  end
end

function updateRngForAction()
  rng = bit.band(mult32(rng, 0x41C64E6D) + 0x6073, 0xFFFFFFFF)
  local rand = gettop(rng)
  -- Always burn 3.
  rng = bit.band(mult32(rng, 0x41C64E6D) + 0x6073, 0xFFFFFFFF)
  rng = bit.band(mult32(rng, 0x41C64E6D) + 0x6073, 0xFFFFFFFF)
  rng = bit.band(mult32(rng, 0x41C64E6D) + 0x6073, 0xFFFFFFFF)
  -- When odd, burn 3 more
  if (bit.band(rand, 1) == 1) then
    rng = bit.band(mult32(rng, 0x41C64E6D) + 0x6073, 0xFFFFFFFF)
    rng = bit.band(mult32(rng, 0x41C64E6D) + 0x6073, 0xFFFFFFFF)
    rng = bit.band(mult32(rng, 0x41C64E6D) + 0x6073, 0xFFFFFFFF)
  end
end


while true do
  guiHieght = 48

  rng = memory.read_u32_le(rngAddress, memoryDomain)
  blendHead = memory.read_u16_le(blendHeadAddress, memoryDomain)
  rotSpeed = memory.read_u16_le(rotSpeedAddress, memoryDomain)
  frictionCount = memory.read_u8(frictionCounterAddress, memoryDomain)
  shakeHorz = memory.read_s16_le(screenShakeHorzAddress, memoryDomain)
  shakeVert = memory.read_s16_le(screenShakeVertAddress, memoryDomain)
  
  rotations = 0
  initBlendHead = blendHead
  -- should these technically be loaded?  Or just know not to run the script
  -- when one of them is potentially already set.
  laddieAction = 0
  lassieAction = 0
  misterAction = 0
  -- similarly, don't run the script if one of these actions is in the queue.
  -- need to track these because the rotSpeed and RNG adjustments happen 1
  -- frame late
  perfect = 0
  hit = 0
  miss = 0

  while (rotations < 1) do
    -- VBlank
    rng = bit.band(mult32(rng, 0x41C64E6D) + 0x6073, 0xFFFFFFFF)
  
    -- update rotation values
    local newBlendHead = blendHead + rotSpeed
    if (blendHead < initBlendHead and newBlendHead >= initBlendHead) then
      rotations = rotations + 1
    end
    blendHead = bit.band(newBlendHead, 0xFFFF)
    frictionCount = frictionCount + 1
    if (frictionCount == 6) then
      rotSpeed = rotSpeed - friction  -- assuming we're never at minimum?
  	frictionCount = 0
    end
    
    -- update rotation based on hits (must happen before NPC RNG)
    if (miss == 1) then
  	updateRngForAction()
      rotSpeed = rotSpeed - missLoss
      miss = 0
    end
    if (hit == 1) then
  	updateRngForAction()
      if (rotSpeed <= fastDecision) then
  	  rotSpeed = rotSpeed + hitGain
  	end
  	hit = 0
    end
    if (perfect == 1) then
  	updateRngForAction()
      if (rotSpeed <= fastDecision) then
  	  rotSpeed = rotSpeed + perfectSlowGain
  	else
  	  rotSpeed = rotSpeed + perfectGain
  	end
  	perfect = 0
    end
  
    -- check for npc actions
    local adjustedHead = bit.rshift(blendHead, 8) + 0x18
    if (adjustedHead > (laddieHead + 0x14) and adjustedHead < (laddieHead + 0x28)) then
      laddieRng()
  	  laddieAction = 1
    else
      laddieAction = 0
    end
    if (adjustedHead > (lassieHead + 0x14) and adjustedHead < (lassieHead + 0x28)) then
	  -- console.writeline(string.format("%x", blendHead))
      lassieRng()
  	  lassieAction = 1
    else
      lassieAction = 0
    end
	-- >= here is not an error, it's actually different for Mister.
    if (adjustedHead >= (misterHead + 0x14) and adjustedHead < (misterHead + 0x28)) then
      misterRng()
  	  misterAction = 1
    else
      misterAction = 0
    end
  end
  
  emu.frameadvance()
  
end

