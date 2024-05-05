dofile("blend.lua")

-- A comparison function for blend.State, based on what we care about for
-- this particular script.
-- Returns 1 when s1 > s2, -1 when s1 < s2, and 0 when s1 = s2.
function compare(s1, s2)
	-- Faster speed is better.
	if s1.speed > s2.speed then
		-- console.writeline("s1 wins on speed")
		return 1
	elseif s1.speed < s2.speed then
		-- console.writeline("s2 wins on speed")
		return -1
	end
	-- Lower counter is better.
	if s1.counter < s2.counter then
		return 1
	elseif s1.counter > s2.counter then
		return -1
	end
	-- Mister not missing is better.
	if s1.missCounters[1] < s2.missCounters[1] then
		-- console.writeline("s1 wins on miss counter")
		return 1
	elseif s1.missCounters[1] > s2.missCounters[1] then
		-- console.writeline("s2 wins on miss counter")
		return -1
	end
	if s1.miss < s2.miss then
		return 1
	elseif s1.miss > s2.miss then
		return -1
	end
	return 0
end

-- Determines if the given blend.States are equivalent for our purposes.
-- Note that non-equivalent state could still be considered equal by `compare`.
function equals(s1, s2)
	if s1.head ~= s2.head then
		return false
	end
	if s1.speed ~= s2.speed then
		return false
	end
	if s1.rng ~= s2.rng then
		return false
	end
	if s1.counter ~= s2.counter then
		return false
	end
	if s1.shakeHorz ~= s2.shakeHorz then
		return false
	end
	if s1.shakeVert ~= s2.shakeVert then
		return false
	end
	-- Specifically care about Mister missing for where we will be comparing.
	if s1.missCounters[1] ~= s2.missCounters[1] then
		return false
	end
	-- Mister miss can registered just as the player hits around the 3rd cycle,
	-- so it actually ends up being important to check this.
	if s1.miss ~= s2.miss then
		return false
	end
	-- All paths get the same amount of friction by the end, so don't care when
	-- it happens.  Perfect, hit, and miss flags should not be set for where we
	-- are comparing.  Actions taken shouldn't be set for where we are comparing.
	return true
end

-- checks that the given beginning |state| is already listed in |set|.
function contains(set, state)
	for _, v in pairs(set) do
		if equals(v.begin, state) then
			return true
		end
	end
	return false
end

function displayShort(perm, state)
	console.writeline(string.format("For %x: \n\thead: %x\n\tspeed: %x\n\trng: %x\n\tcounter: %d\n", perm, state.head, state.speed, state.rng, state.counter))
end

-- Returns an array of unique player actions and the results they derive.
-- The array elements are of the form {perm=<>, begin=<>, result=<>} where
-- |begin| is the blend.State after player actions, |perm| is a number that
-- represents how to reconstruct that action and |result| is the blend.State
-- after playing through to the next possible action.  Do not depend on the
-- index of the array to have meaning.
function permutations(state)
	-- First find how many frames we can act on.
	local lengthState = state
	local frames = 0
	local fromMinimum = lengthState.speed == 0x80
	-- When we're at minimum speed, we wnat to use misses to influence RNG.  So
	-- track how many frames it takes to get to the point where we can increase
	-- speed.
	if fromMinimum then
		-- technically could avoid the code duplication with XOR?  But I think this
		-- is more understandable.
		while not lengthState:playerCanHit() do
			frames = frames + 1
			lengthState = lengthState:advance()
		end
	-- Otherwise (the normal case) we don't want any misses, so we just use the
	-- frames where we can hit to influence RNG.
	else
		while (lengthState:playerCanHit()) do
			frames = frames + 1
			lengthState = lengthState:advance()
		end
	end
	
	-- then produce the state and result for all possible actions across those
	-- frames.
	-- Think of i as a binary string.  For each frame, look at the jth bit.  If it's
	-- 1 press A, if it's 0 don't press A.  So iterating from [0,2^frames) yields
  -- all possible permutations of A presses that could affect rng wtihout losing
	-- speed.
	local results = {}
	for i=0,bit.lshift(1,frames)-1,1 do
		local checkState = blend.State:copy(state)
		for j=1,frames,1 do
			-- do a player action when the jth bit of i is set.
			checkState = checkState:advance(bit.check(i,j-1))
		end
		-- If we were at minimum, use all hittable frames to increase speed as much
		-- as possible
		if fromMinimum then
			while checkState:playerCanHit() do
				checkState = checkState:advance(true)
			end
		end
		if not contains(results, checkState) then
			local result = checkState:result()
			results[table.getn(results)+1] = {perm=i, begin=checkState, result=result}
			-- displayShort(i, result)
		end 
	end
	return results
end

-- TODO: get top N results, instead of just top 1.
-- Note, iterating over keys in a table is not deterministic so if there are
-- multiple best states (as determined by `compare`), then any one of them
-- could be returned.
function top(results)
	local bestResult
	local bestPerm
	for _, r in pairs(results) do
		if bestResult == nil then
			bestResult = r.result
			bestPerm = r.perm
		else
			-- console.writeline("comparing "..perm.." with "..bestPerm)
			if compare(r.result, bestResult) > 0 then
				bestResult = r.result
				bestPerm = r.perm
			end
		end
	end
	-- displayShort(bestPerm, bestResult)
	return {perm=bestPerm, result=bestResult}
end

function sorter(s1, s2)
	return compare(s1.result, s2.result) > 0
end

function topN(results, n)
	table.sort(results, sorter)
	local top = {}
	for i=1,n,1 do
		if results[i] == nil then
			break
		end
		top[i] = {perm=results[i].perm, result=results[i].result}
	end
	return top
end

function greedy()
	local current = blend.State:current()
	while current.counter < 515 do
		step = top(permutations(current))
		current = step.result
		displayShort(step.perm, step.result)
	end
end

-- greedy()

-- STACK FUNCTIONS
function empty(stack)
	return stack.top == 0
end

function push(stack, el)
	stack.top = stack.top + 1
	stack.s[stack.top] = el
end

function pop(stack)
  if empty(stack) then
		return nil
	end
	local el = stack.s[stack.top]
	stack.s[stack.top] = nil  -- Allow for garbage collection
	stack.top = stack.top - 1
	return el
end

function copy(stack)
	local new = {s={}, top=stack.top}
	for i=1,stack.top,1 do
		new.s[i] = stack.s[i]
	end
	return new
end
-- END STACK FUNCTIONS

local GOAL = 0xB61  -- dec 2913, 160 RPM
-- How many top permutations to keep on each iteration
local WIDTH = 3

function displayEnd(path, result)
	for i=1,table.getn(path),1 do
		console.writeline(string.format("%x", path[i]))
	end
	displayShort(0, result)
end

-- constants for maximum calc
local fastDecision=0x5DB  -- dec 1499
local perfectSlowGain=0x60
local perfectGain=0x20
local friction=0x01

-- Returns the maximum RPM acheivable if all results are perfect
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
  return speed
end

function expand(stack)
	local current = pop(stack)
	-- console.writeline(string.format("current state head %x speed %x counter %d", current.result.head, current.result.speed, current.result.counter))
	if current.result.speed >= GOAL then
		displayEnd(current.path.s, current.result)
		-- console.writeline(current.path.s)
		return true
	end
	if current.result.counter >= 515 then
		return false
	end
	if maximum(current.result) < GOAL then
		return false
	end

	local nexts = topN(permutations(current.result), WIDTH)
	-- push next states in reverse order, so that the best results are tried
	-- first.
	for i=table.getn(nexts),1,-1 do
		local newPath = copy(current.path)
		push(newPath, nexts[i].perm)
		push(stack, {path=newPath, result=nexts[i].result})
	end
	return false
end

-- Depth first search for a high RPM blend.
-- TODO: actually do this.
function search()
	local stack = {s={}, top=0}
	local current = blend.State:current()
	push(stack, {path={s={}, top=0}, result=current})
	while not empty(stack) do
		if expand(stack) then
			break
		end
	end
	console.writeline("Done")
end

-- permutations(blend.State:current())
-- local cur = blend.State:current()
-- local perf1 = cur:advance():advance():advance(true)
-- perf1:print()
-- local perf2 = perf1:advance(true)
-- perf2:print()

-- local test = topN(permutations(blend.State:current()), 3)
-- for k=1,table.getn(test),1 do
	-- displayShort(test[k].perm, test[k].result)
-- end

search()

-- DFS TESTING
-- I just took the maximum first state to keep things reasonably efficient
-- but holy shit did it actually do it!?
-- 7b
-- 7f
-- 39
-- f
-- 19
-- 8
-- 18
-- 8
-- 7
-- f
-- c
-- f
-- 4
-- c
-- 3
-- For 0: 
	-- head: ac0c
	-- speed: b6c
	-- rng: 35650cc6
	-- counter: 516   -- OFF BY ERROR GAHHHHHHHHHHHHHHHHHHHHH.  If the counter actually
-- could reach 516, lassie's perfect would have happened and b6c would happen.  But
-- unfortunately it gets registered and never executed because the blend ends.  So let's
-- fix that up and start trying again.
