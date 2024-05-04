-- Utilities for tracking Berry Blender states.
dofile("rng.lua")

blend = {}  -- package

-- where the blend head is pointed
local blendHeadAddress=0x2018054
-- how fast the blend head is currently moving per frame
local rotSpeedAddress=0x02018056
-- counts how many frames passed in the current blend
local counterAddress=0x0201812C
-- counts up 1 each frame. when this is 5, rolls over to 0 and applies friction
local frictionCounterAddress=0x0201807E
-- how far shifted the screen is in each direction.
local screenShakeHorzAddress=0x02018144
local screenShakeVertAddress=0x02018146
-- used to determine the action size?
local playerMissesAddress=0x2018150
-- active hits and misses per npc
local misterResultAddress=0x03002A32
local laddieResultAddress=0x03002A34
local lassieResultAddress=0x03002A36
local missActiveAddress=0x03004B9C
local missCounterAddress=0x03004BA0
local missNpcAddress=0x03004BA4  -- 1 = misster, 2 = laddie, 3 = lassie
local misterActionTaken=0x03004B28
local laddieActionTaken=0x03004B50
local lassieActionTaken=0x03004B78
local memoryDomain = "System Bus"

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

-- The game's result enumeration
local PERFECT = 0x4523
local HIT = 0x5432
local MISS = 0x2345

-- The game uses these numbers to index by NPC.
local MISTER = 1
local LADDIE = 2
local LASSIE = 3

blend.State = {}

function blend.State:new(head, speed, rng, counter, friction, shakeHorz,
		shakeVert, perfect, hit, miss, actionTaken, missCounters)
  s = {}
	s.head = head or 0
	s.speed = speed or 0
	s.rng = rng or 0
	s.counter = counter or 0
	s.friction = friction or 0
	s.shakeHorz = shakeHorz or 0
	s.shakeVert = shakeVert or 0
	s.perfect = perfect or 0
	s.hit = hit or 0
	s.miss = miss or 0
	s.actionTaken = {}
	s.missCounters = {}
	for i=1,3,1 do
		s.actionTaken[i] = actionTaken[i] or 0
		s.missCounters[i] = missCounters[i] or 0
	end
	setmetatable(s, self)
	self.__index = self
	return s
end

function blend.State:current()
	local misterRes = memory.read_u16_le(misterResultAddress, memoryDomain)
	local laddieRes = memory.read_u16_le(laddieResultAddress, memoryDomain)
	local lassieRes = memory.read_u16_le(lassieResultAddress, memoryDomain)
	local perfect = 0
	if (misterRes == PERFECT or laddieRes == PERFECT or lassieRes == PERFECT) then
		perfect = 1
	end
	local hit = 0
	if (misterRes == HIT or laddieRes == HIT or lassieRes == HIT) then
		hit = 1
	end
	local miss = 0
	if (misterRes == MISS or laddieRes == MISS or lassieRes == MISS) then
		miss = 1
	end
	-- TODO: loaded misses and whether an NPC has taken an action this cycele.
	local actionTaken = {
		memory.read_u8(misterActionTaken, memoryDomain),
		memory.read_u8(laddieActionTaken, memoryDomain),
		memory.read_u8(lassieActionTaken, memoryDomain),
	}
	local missCount = memory.read_u8(missCounterAddress, memoryDomain)
	local missNpc = memory.read_u8(missNpcAddress, memoryDomain)
	local missActive = memory.read_u8(missActiveAddress, memoryDomain)
	local missCounter = {}
	if missActive > 0 then
		missCounter[missNpc] = missCount
	end
	return blend.State:new(
			memory.read_u16_le(blendHeadAddress, memoryDomain),
			memory.read_u16_le(rotSpeedAddress, memoryDomain),
			rng.current(),
			memory.read_u16_le(counterAddress, memoryDomain),
			memory.read_u8(frictionCounterAddress, memoryDomain),
			memory.read_s16_le(screenShakeHorzAddress, memoryDomain),
			memory.read_s16_le(screenShakeVertAddress, memoryDomain),
			perfect,
			hit,
			miss,
			actionTaken,
			missCounter)
end

function blend.State:copy(s)
	n = blend.State:new(s.head, s.speed, s.rng, s.counter, s.friction, s.shakeHorz,
							 s.shakeVert, s.perfect, s.hit, s.miss, s.actionTaken, s.missCounters)
	return n
end

-- Prints the state.  A convenience function for testing.
function blend.State:print()
	console.writeline(string.format("head: %x, speed: %x", self.head, self.speed))
	console.writeline(string.format("rng: %x", self.rng))
	console.writeline("counter: "..self.counter..", friction: "..self.friction)
	console.writeline("shake up "..self.shakeVert.." left "..self.shakeHorz)
	console.writeline("perfect "..self.perfect.." hit "..self.hit.." miss "..self.miss)
	console.writeline(self.actionTaken)
	console.writeline(self.missCounters)
end

function blend.State:shakeRng(dir)
	s = self:copy(self)
	s.rng = rng.advance(s.rng, 1)
	local rand = rng.top(s.rng)
	-- console.writeline(string.format("rand: %x", rand))
	local maxShake = math.floor(s.speed / 100) - 10
	local res = (rand % maxShake) - bit.rshift(maxShake, 1)
	-- console.writeline("result: "..res)
	if dir == "horz" then
		s.shakeHorz = res
	elseif dir == "vert" then
		s.shakeVert = res
	end
	return s
end

function blend.State:advanceRngForAction()
	s = self:copy(self)
	s.rng = rng.advance(s.rng, 1)
	local rand = rng.top(s.rng)
	-- Always burn 3.
	s.rng = rng.advance(s.rng, 3)
	if bit.check(rand, 0) then
		-- Sometimes burn 3 more.
		s.rng = rng.advance(s.rng, 3)
	end
	return s
end

-- Returns a State which has an advanced frame and update head, friction, etc.
function blend.State:advanceFrameState()
	s = self:copy(self)
	s.head = bit.band(s.head + s.speed, 0xFFFF)
	s.rng = rng.advance(s.rng, 1)
	s.counter = s.counter + 1
	s.friction = s.friction + 1
	if s.friction == 6 then
		-- accounts for not slowing down below minimum
		s = s:advanceSpeed(-friction, -friction)
		s.friction = 0
	end
	return s
end

function blend.State:advanceSpeed(slowGain, fastGain)
	s = self:copy(self)
	if s.speed <= fastDecision then
		s.speed = s.speed + slowGain
	else
		s.speed = s.speed + fastGain
	end
	if s.speed < 0x80 then
		s.speed = 0x80
	end
	return s
end

-- Returns a State with advanced actions determined on previous frames
-- (perfect, hit, and misses).
function blend.State:advanceActions()
	s = self:copy(self)
	if s.perfect == 1 then
		if s.speed >= fastDecision and s.shakeHorz == 0 then
			s = s:shakeRng("horz")
		end
		if s.speed >= fastDecision and s.shakeVert == 0 then
			s = s:shakeRng("vert")
		end
		s = s:advanceSpeed(perfectSlowGain, perfectGain):advanceRngForAction()
		s.perfect = 0
	end
	if s.hit == 1 then
		s = s:advanceSpeed(hitGain, 0):advanceRngForAction()
		s.hit = 0
	end
	if s.miss == 1 then
		s = s:advanceSpeed(-missLoss, -missLoss):advanceRngForAction()
		s.miss = 0
	end
	-- needs to happen after the miss check
	for i=1,3,1 do
		if s.missCounters[i] > 0 then
			s.missCounters[i] = s.missCounters[i] + 1
			if s.missCounters[i] == 6 then
				s.miss = 1
				s.missCounters[i] = 0
			end
		end
	end
	-- needs to happen after shake rng.  Yes, it reduces the same turn that
	-- it's generated.
	if s.shakeHorz > 0 then
		s.shakeHorz = s.shakeHorz - 1
	elseif s.shakeHorz < 0 then
		s.shakeHorz = s.shakeHorz + 1
	end
	if s.shakeVert > 0 then
		s.shakeVert = s.shakeVert - 1
	elseif s.shakeVert < 0 then
		s.shakeVert = s.shakeVert + 1
	end
	return s
end

local npcActions = {
	{{0, 0, 101}, {10, 20, 80}, {30, 70, 91}},
	{{0, 0, 66}, {10, 41, 66}, {10, 41 ,66}},
	{{0, 0, 89}, {5, 56, 61}, {5, 56, 61}},
}

function blend.State:npcAction(index)
	s = self:copy(self)
	-- read the odds table based on rotation speed
	local odds = npcActions[index][3]
	if s.speed < slowDecision then
		odds = npcActions[index][1]
	elseif s.speed < fastDecision then
		odds = npcActions[index][2]
	end
	-- then generate a random number and act on it
	s.rng = rng.advance(s.rng, 1)
	local rand = rng.top(s.rng)
	-- console.writeline(string.format("with rand %x", rand))
	-- console.writeline(odds)
	if rand < odds[1]*onePercent then
		-- miss
		s.missCounters[index] = 1
	elseif rand < odds[2]*onePercent then
		-- none, intentionally empty
	elseif rand < odds[3]*onePercent then
		-- hit
		s.hit = 1
	else
		-- perfect
		s.perfect = 1
	end
	return s
end

function blend.State:checkAction(npcIndex, npcHead)
	s = self:copy(self)
	local adjustedHead = bit.rshift(self.head, 8) + 0x18
	if (adjustedHead > (npcHead + 0x14) and adjustedHead < (npcHead + 0x28)) then
		-- console.writeline("npc "..npcIndex.."is considering action")
		if s.actionTaken[npcIndex] ~= 1 then
			s = s:npcAction(npcIndex)
			s.actionTaken[npcIndex] = 1
		end
	else
		-- NOTE: for some reason, Mister's action bit clears faster than it
		-- should (in the game's memory) but he still only takes 1 action.
		-- It's unclear to me why, but :advance() predicts the right things
		-- so it's not much of an issue, just a glitch in the display.
		s.actionTaken[npcIndex] = 0
	end
	return s
end

function blend.State:advanceNpcActions()
	-- Note the "-1" after misterHead.  Mister's lower bound check is technically
	-- >= instaed of >, but to reuse code we can just lower head because these are
	-- integer checks.  In theory this means there's a bug on Mister's upper bound
	-- check, but in reality you will never get the speed fast enough to skip over
	-- the whole range like that.
	-- TODO: store heads as an array?  Then checkAction behavior is entirely
	-- determined by just the NPC index.
	return self:checkAction(LADDIE, laddieHead):checkAction(LASSIE, lassieHead):checkAction(MISTER, misterHead-1)
end

function blend.State:playerCanHit()
	local advancedHead = bit.band(self.head + self.speed, 0xFFFF)
	return (advancedHead >= 0x800 and advancedHead < 0x3000) and (self.head <= 0x3000 or self.head > 0xF000)
end

function blend.State:playerAction()
	local advancedHead = bit.band(s.head + s.speed, 0xFFFF)
	if (advancedHead < 0x0800 or s.head > 0x3000) then
	  return self:advanceSpeed(-missLoss, -missLoss):advanceRngForAction()
	end
	-- BUG: no perfect at 0x1B9C, 0x9BF
	-- BUG: no perfect at 0x1AC6, 0x9FA
	-- Other results:
	--   perfect at 0x1290, 0xA92
	--   perfect at 0x14B8, 0xAEE
	if (advancedHead > 0x1C00 and s.head < 0x1F00) then
	  return self:advanceSpeed(perfectSlowGain, perfectGain):advanceRngForAction()
	end
	return self:advanceSpeed(hitGain, 0):advanceRngForAction()
end

function blend.State:advance(withPlayerAction)
	s = self:advanceFrameState()
	if withPlayerAction then
		s = s:playerAction()
	end
	return s:advanceActions():advanceNpcActions()
end

-- returns the blend.State that will result if the given blend.State is left to
-- play without user inputs until the blend head reaches the next "top."
function blend.State:result()

end

return blend