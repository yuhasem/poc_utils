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
	while (lengthState:playerCanHit()) do
		frames = frames + 1
		lengthState = lengthState:advance()
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

local goal = 0x780  -- 0xB61  -- dec 2913, 160 RPM

function displayEnd(path, result)
	for i=1,table.getn(path),1 do
		console.writeline(string.format("%x", path[i]))
	end
	displayShort(0, result)
end

function expand(stack)
	local current = pop(stack)
	console.writeline(string.format("current state head %x speed %x counter %d", current.result.head, current.result.speed, current.result.counter))
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
end

-- permutations(blend.State:current())
-- local cur = blend.State:current()
-- local perf1 = cur:advance():advance():advance(true)
-- perf1:print()
-- local perf2 = perf1:advance(true)
-- perf2:print()
-- search()


-- GREDDY PATH TESTING
-- Length 15 is a good start.  And only took a second or 2 to run.
-- For 8: 
	-- head: 420
	-- speed: 650
	-- rng: bd92a833
	-- counter: 113   - correct prediction on ending

-- For 18:  0b1'1000
	-- head: 604
	-- speed: 6c9
	-- rng: 56e0b1c9
	-- counter: 152   - correct prediction on ending (chaining works!)

-- For 2f:  0b10'1111
	-- head: 2c2
	-- speed: 743
	-- rng: 7d4ff1eb
	-- counter: 188   - correct prediction

-- For 1: 
	-- head: 4ab
	-- speed: 77d
	-- rng: 2d76e7a
	-- counter: 223   - correct prediction

-- For 3d:  0b11'1101
	-- head: d8
	-- speed: 7d8
	-- rng: 5fdc29c4
	-- counter: 256   - correct prediction

-- For 1e:  0b1'1110
	-- head: 2be
	-- speed: 832
	-- rng: 516aec8c
	-- counter: 288   - correct prediction

-- For c: 
	-- head: 64b
	-- speed: 86d
	-- rng: bc7ff753
	-- counter: 319   - correct prediction

-- For 1f:  0b1'1111
	-- head: 108
	-- speed: 8c8
	-- rng: cab1dd0c
	-- counter: 348   - correct prediction

-- For 1: 
	-- head: 2d8
	-- speed: 904
	-- rng: f079c54a
	-- counter: 377   - correct prediction (it took a miss!?)

-- For 7: 
	-- head: 7dc
	-- speed: 91f
	-- rng: 1cc65c91
	-- counter: 406   - correct prediction (the in progress miss was tracked correctly!)

-- For 3: 
	-- head: 100
	-- speed: 95a
	-- rng: 40b0e1bb
	-- counter: 433   - correct prediction

-- For 1f:  0b1'1111
	-- head: 3ca
	-- speed: 9d6
	-- rng: fa620ce6
	-- counter: 460   - correct prediction

-- For f: 
	-- head: ff18
	-- speed: a32
	-- rng: a621e65c
	-- counter: 485   - correct prediction

-- For 5: 
	-- head: 1be
	-- speed: a8d
	-- rng: 8247a8b9
	-- counter: 510   - correct prediction

-- For d: 
	-- head: 472
	-- speed: b09
	-- rng: 16fc7da2
	-- counter: 534   - it found a triple perfect, but sadly the blend ends before hitting it.
	
-- 150.12 RPM.  I get to keep my job for now.  And I probably need to teach it to take the speed
-- at frame 515, not at the result of that cycle.  Okay 

-- DFS TESTING
-- 28
-- 5f
-- 2c   -- PNM ??
-- b    -- HPN ??
-- 6    -- HNN ??  Okay something's gone wrong.
-- b
-- 7
-- f
-- 1
-- 7
-- 0
-- 1d
-- 1f
-- 1f
-- f
-- For 0: 
	-- head: cf4c
	-- speed: b0c
	-- rng: 99e93f07
	-- counter: 516

-- current state head 792 speed 5b6 counter 72
-- current state head 420 speed 650 counter 113
-- current state head 7c4 speed 6e9 counter 152
-- current state head 55f speed 763 counter 187  <-- it expects an extra perfect here?
-- current state head b2 speed 7de counter 220
-- 28
-- 5f
-- 2c  <-- corresponding to this step
-- b
-- For 0: 
	-- head: b2
	-- speed: 7de
	-- rng: 17f31272
	-- counter: 220

-- For 2c: 
	-- head: 55f   -- actual: 0x3bf
	-- speed: 763    -- actual: 0x743
	-- rng: b688dd1f   -- actual: 0x137963CC
	-- counter: 187    -- correct
-- This is a double perfect.  Could it have got the wrong shake values?
-- Yes! But not at all in the way I expected!
--   AFTER PERFECT 1:
-- head: 1c7f, speed: 709
-- rng: f90389b9                <---- RNG is correct, so it did the right number of rolls
-- counter: 155, friction: 5
-- shake up 0 left 0            <---- but actual shake values were -3, 0
-- perfect 0 hit 0 miss 0
-- "1": "0"
-- "2": "0"
-- "3": "0"

-- "1": "0"
-- "2": "0"
-- "3": "0"

--   AFTER PERFECT 2:
-- head: 2388, speed: 728
-- rng: 45df96b3               <----- And because shake values were wrong above, RNG becomes wrong here
-- counter: 156, friction: 0
-- shake up -1 left 0
-- perfect 0 hit 0 miss 0
-- "1": "0"
-- "2": "0"
-- "3": "0"

-- "1": "0"
-- "2": "0"
-- "3": "0"

