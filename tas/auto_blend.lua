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

-- Returns a table of unique player actions and the results they derive.
-- The returned table is of the form {perm={begin=<>, result=<>}, ...}
-- where |begin| is the blend.State after player actions, |perm| is a number that
-- represents how to reconstruct that action and |result| is the blend.State
-- after playing through to the next possible action.  Note that |perm| is a
-- number, but it may be 0, so use `pairs` to iterate through the result, not
-- `ipairs`.
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
			results[i] = {begin=checkState, result=result}
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
	for perm, states in pairs(results) do
		local result = states.result
		if bestResult == nil then
			bestResult = result
			bestPerm = perm
		else
			-- console.writeline("comparing "..perm.." with "..bestPerm)
			if compare(result, bestResult) > 0 then
				bestResult = result
				bestPerm = perm
			end
		end
	end
	-- displayShort(bestPerm, bestResult)
	return {perm=bestPerm, result=bestResult}
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

local goal = 0xB61  -- dec 2913, 160 RPM

-- Depth first search for a high RPM blend.
-- TODO: actually do this.
function search()
	local stack = {s={}, top=0}
	local current = blend.State:current()
	push(stack, current)
	while not empty(stack) do
	
	end
end


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
