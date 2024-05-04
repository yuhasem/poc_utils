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
-- displaying the result.  How do we know the action size?  Where you can
-- press to still get a hit seems variable based on rotation speed.

dofile("blend.lua")

-- useless, but included for completeness
local progressAddress=0x018140
local progressCapAddres=0x01813E
local memoryDomain="EWRAM"

-- constants for maximum calc
local slowDecision=0x1F3
local fastDecision=0x5DB
local oneSixty=2913
local rotPerRPM = 18.206
local perfectSlowGain=0x60
local perfectGain=0x20
local friction=0x01

-- Display stuffs
local names={"Mister", "Laddie", "Lassie"}

function logAction(npc, height, action, color)
	gui.text(350,height,names[npc])
	gui.text(440,height,action,color)
end

-- Display the maximum RPM acheivable if all results are perfect
-- until the end of the blend
-- TODO: this should probably be in blend, despite not actually using
-- blend.State, because it will be used by both display and auto.
function maximum(state)
  local counter = state.counter
  local speed = state.speed
  local head = state.head
  while (counter < 515) do
		counter = counter + 1
		local newHead = head + speed
		for i=0x2000,0xFFFF,0x4000 do
			if (head < i and newHead > i) then
				if (speed < fastDecision) then
					speed = speed + perfectSlowGain
				else
					speed = speed + perfectGain
				end
			end
		end
		head = bit.band(newHead, 0xFFFF)
		if (counter % 6 == 0) then
			speed = speed - friction
		end
  end
  local RPM = speed / rotPerRPM
  gui.text(12,194,string.format("Maximum final RPM: %.2f", RPM))
end


-- Okay, so now I want to think about how to get the program to do create all the
-- possible permutations of inputs and dervie their results for that action.
-- Start by thinking about the normal case.  The first rotation is going to be an
-- exception.
-- function permutations()
  -- read signed, because sometimes the first frame comes while we're <0.
	-- and then we don't have to track the wrap around.
  -- local head = memory.read_s16_le(blendHeadAddress, memoryDomain)
	-- local speed = memory.read_u16_le(rotSpeedAddress, memoryDomain)
	-- local fricCount = memory.read_u8(frictionCounterAddress, memoryDomain)
  -- Let's assume that the frame is aligned with the frist non-miss input in a
	-- cycle.  Let's find how many frames to the last input.
	-- local frames = 0
	-- local checkHead = head
	-- this technically counts one more frame than a hit, but it also
	-- leaves out the frame we're on right now, so it all works out.
	-- while (checkHead < 0x3000) do
	  -- checkHead = checkHead + speed
		-- frames = frames + 1
	-- end
	-- console.writeline("frames to check"..frames)
	
	-- Think of i as a binary string.  For each frame, look at the jth bit.  If it's
	-- 1 press A, if it's 0 don't press A.  So iterating from [0,2^frames) yields
  -- all possible permutations of A presses that could affect rng wtihout losing
	-- speed.
	-- for i=0,bit.lshift(1,frames)-1,1 do
		-- need to keep rng updated spearately for each permutation (and some other state too)
		-- local r = rng.current()
		-- local trackHead = head
		-- local trackSpeed = speed
		-- local trackFric = fricCount
		-- local shakeHorz = 0
		-- local shakeVert = 0
		-- For each permutation, update the state until the end of |frames| inputs.
		-- for j=0,frames-1,1 do
			-- r = rng.advance(r, 1) -- VBlank
			-- console.writeline("vblank for frame "..j)
			-- local newHead = trackHead + trackSpeed
			-- if bit.check(i,j) then
				-- Need to check perfect/hit/miss.  Misses can still happen because we only
				-- checked the last frame when we do nothing, but if we increase speed that
				-- may be beyond the end.
				-- local action = playerAction(trackHead, trackSpeed)
				-- if action == 0 then
					-- trackSpeed = trackSpeed - missLoss
				-- elseif action == 1 then
				  -- if trackSpeed <= fastDecision then
					  -- trackSpeed = trackSpeed + hitGain
					-- end
				-- else
					-- if trackSpeed <= fastDecision then
						-- trackSpeed = trackSpeed + perfectSlowGain
					-- else
						-- trackSpeed = trackSpeed + perfectGain
						-- the updated speed is used to calculate screen shake.
						-- if shakeHorz == 0 then
							-- r = rng.advance(r, 1)
							-- console.writeline("rng for horz shake")
							-- local rand = rng.top(r)
							-- local maxShake = math.floor(trackSpeed / 100) - 10
							-- shakeHorz = (rand % maxShake) - bit.rshift(maxShake, 1)
						-- end
						-- if shakeVert == 0 then
							-- r = rng.advance(r, 1)
							-- console.writeline("rng for vert shake")
							-- local rand = rng.top(r)
							-- local maxShake = math.floor(trackSpeed / 100) - 10
							-- shakeVert = (rand % maxShake) - bit.rshift(maxShake, 1)
						-- end
					-- end
				-- end
				-- r = updateRngForAction(r)
				-- console.writeline("rng for action")
			-- end
		  -- trackHead = newHead
			-- trackFric = trackFric + 1
			-- if trackFric == 6 then
				-- trackSpeed = trackSpeed - friction
				-- trackFric = 0
			-- end
		-- end
		-- console.writeline(string.format("For %x: \n\thead: %x\n\tspeed: %x\n\trng: %x\n", i, trackHead, trackSpeed, r))
	-- end
-- end

-- permutations()

function displayRng(current, previous)
	gui.text(60,0,string.format("Current RNG value: %x", current))
	local currentIndex = rng.index(current)
	gui.text(60,14,"Current RNG index: "..currentIndex)
	gui.text(60,28,string.format("Last RNG value: %x", previous))
	local previousIndex = rng.index(previous)
	gui.text(60,42,"RNG distance since last: "..(currentIndex-previousIndex))
end

function displayState(state)
	local progress = memory.read_u16_le(progressAddress, memoryDomain)
	local cap = memory.read_u16_le(progressCapAddres, memoryDomain)
	gui.text(12,60,string.format("progress: %d, cap: %d", progress, cap))
	gui.text(12,74,string.format("head: %x, speed:", state.head))
	local speedColor = "green"
	if state.speed < slowDecision then
		speedColor = "blue"
	elseif state.speed < fastDecision then
		speedColor = "white"
	elseif state.speed < oneSixty then
		speedColor = "yellow"
	end
	gui.text(200,74,string.format("%x", state.speed),speedColor)
	gui.text(12,88,"counter: "..state.counter..", friction: "..state.friction)
	gui.text(12,102,"shake up "..state.shakeVert.." left "..state.shakeHorz)
	gui.text(12,116,"perfect: "..state.perfect.." hit: "..state.hit.." miss: "..state.miss)
	gui.text(12,130,"        Mt | Ld | Ls")
	gui.text(12,144,string.format("action:  %d |  %d |  %d",state.actionTaken[1],state.actionTaken[2],state.actionTaken[3]))
	gui.text(12,158,string.format("  miss:  %d |  %d |  %d",state.missCounters[1],state.missCounters[2],state.missCounters[3])) 
end

local lastRng = 0

-- local test = blend.State:current()
-- console.writeline(rng.index(test.rng))
-- test = test:advance()
-- console.writeline(rng.index(test.rng))

while true do
  local guiHieght = 84

  local r = rng.current()
	local state = blend.State:current()
  
	displayRng(r, lastRng)
	displayState(state)
	maximum(state)
	
	gui.text(350,60,"Player | Action")
	local lastState = state:copy(state)
	local counter = 0
	while lastState:playerCanHit() or not state:playerCanHit() do
		lastState = state
		state = state:advance(false)
		for i=1,3,1 do
			if lastState.actionTaken[i] == 0 and state.actionTaken[i] == 1 then
				if state.perfect == 1 then
					logAction(i, guiHieght, "Perfect", "red")
				elseif state.hit == 1 then
					logAction(i, guiHieght, "Hit", "white")
				elseif state.missCounters[i] == 1 then
					logAction(i, guiHieght, "Miss", "blue")
				else
					logAction(i, guiHieght, "None", "white")
				end
				guiHieght = guiHieght + 24
			end
		end
		-- saftey check in case some condition I haven't thought of breaks
		counter = counter + 1
		if counter > 90 then
			break
		end
	end

	lastRng = r
	lastState = state
  emu.frameadvance()  
end
