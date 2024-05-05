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

local goal = 0x800  -- 0xB61  -- dec 2913, 160 RPM

function displayEnd(path, result)
	for i=1,table.getn(path),1 do
		console.writeline(string.format("%x", path[i]))
	end
	displayShort(0, result)
end

function expand(stack)
	local current = pop(stack)
	-- console.writeline(string.format("current state head %x speed %x counter %d", current.result.head, current.result.speed, current.result.counter))
	if current.result.speed >= goal then
		displayEnd(current.path.s, current.result)
		-- console.writeline(current.path.s)
		return true
	end
	if current.result.counter >= 515 then
		return false
	end
	-- TODO: state culling if we know we can't get to the goal from this
	-- position.

	local nexts = topN(permutations(current.result), 3)
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

local test = topN(permutations(blend.State:current()), 3)
for k=1,table.getn(test),1 do
	displayShort(test[k].perm, test[k].result)
end

-- search()

-- DFS TESTING
-- a
-- 1f
-- 1d
-- 1c
-- 2b
-- 24
-- 2f
-- e
-- 1d
-- c
-- c
-- 1f
-- 2    <-- a couple of sus things here, but it did what it promised
-- 5        when I tried myself, I couldn't beat it, so there's that
-- f
-- For 0: 
	-- head: fd3f
	-- speed: b0d
	-- rng: e4f74f32
	-- counter: 515


-- TESTING SLOW PERMUTATION CODE
-- For 1bf:   0b1'1011'1111
	-- head: 49b
	-- speed: 5f7
	-- rng: 3c2b79b5
	-- counter: 71
-- CORRECT

-- For 1fef:   0b1'1111'1110'1111
	-- head: 7db
	-- speed: 5f7
	-- rng: e5115647
	-- counter: 71
-- CORRECT

-- For ef:    0b1110'1111
	-- head: 3fb
	-- speed: 5d7
	-- rng: ef9c842b
	-- counter: 71
-- CORRECT

-- For 3ef:   0b11'1110'1111
	-- head: 65b
	-- speed: 5b7
	-- rng: b7f0318e
	-- counter: 71
-- CORRECT

-- For ff7:    0b1111'1111'0111
	-- head: 252
	-- speed: 5b6
	-- rng: 515cc7ad
	-- counter: 72
-- CORRECT

-- For 3:      0b11   Ayyy, this is the one I used in my 157.  glad to know it was considered 6th best
	-- head: 792
	-- speed: 5b6
	-- rng: c1868b07
	-- counter: 72
-- CORRECT

-- For 37:     0b11'0111
	-- head: 6d2
	-- speed: 596
	-- rng: 37f9c099
	-- counter: 72
-- CORRECT

-- For 0: 
	-- head: 3d2
	-- speed: 596
	-- rng: a853dd23
	-- counter: 72
-- CORRECT

-- For 18:    0b1'1000
	-- head: 3d2
	-- speed: 596
	-- rng: 5c83b48b
	-- counter: 72
-- CORRECT

-- For 3bf:   0b11'1011'1111
	-- head: 748
	-- speed: 596
	-- rng: e9e28d0a
	-- counter: 73
-- CORRECT
