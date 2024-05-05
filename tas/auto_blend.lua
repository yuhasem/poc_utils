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

function contains(set, state)
	for k, _ in pairs(set) do
		if equals(k, state) then
			return true
		end
	end
	return false
end

-- Returns a table of unique player actions and the results they derive.
-- The returned table is of the form {state={perm=<perm>, r=<result>}, ...}
-- where state is the blend.State after player actions, perm is a number that
-- represents how to reconstruct that action and result is the blend.State
-- after playing through to the next possible action.
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
		local checkState = state
		for j=1,frames,1 do
			-- do a player action when the jth bit of i is set.
			checkState = checkState:advance(bit.check(i,j-1))
		end
		if not contains(results, checkState) then
			local result = checkState:result()
			results[checkState] = {perm=i, r=result}
			-- console.writeline(string.format("For %x: \n\thead: %x\n\tspeed: %x\n\trng: %x\n\tcounter: %d\n", i, result.head, result.speed, result.rng, result.counter))
		end 
	end
	return results
end

-- TODO: get top N results, instead of just top 1.
function top(results)
	local best
	for state, result in pairs(results) do
		if best == nil then
			best = state
		else
			console.writeline("comparing "..results[state].perm.." with "..results[best].perm)
			if compare(results[state].r, results[best].r) > 0 then
				best = state
			end
		end
	end
	local r = results[best]
	console.writeline(string.format("For %x: \n\thead: %x\n\tspeed: %x\n\trng: %x\n\tcounter: %d\n", r.perm, r.r.head, r.r.speed, r.r.rng, r.r.counter))
end

local best = top(permutations(blend.State:current()))

-- TODO: greedily search for a path to the end

-- TEST
-- For 0: 
	-- head: 58a
	-- speed: a8e
	-- rng: bd961bf6
	-- counter: 504
-- MATCHED

-- For 1: 
	-- head: 58a
	-- speed: a8e
	-- rng: d68e28eb
	-- counter: 504
-- MATCHED

-- For 2: 
	-- head: fd9b
	-- speed: aaf
	-- rng: 20b22759
	-- counter: 503
-- MATCHED

-- For 3: 
	-- head: fddb
	-- speed: acf
	-- rng: 72fe541d
	-- counter: 503
-- MATCHED

-- For 4: 
	-- head: 58a
	-- speed: a8e
	-- rng: d68e28eb
	-- counter: 504
-- MATCHED

-- For 5: 
	-- head: fd7b
	-- speed: acf
	-- rng: caefea68
	-- counter: 503
-- MATCHED

-- For 6: 
	-- head: fedb
	-- speed: aef
	-- rng: 72fe541d
	-- counter: 503
-- MATCHED

-- For 7: 
	-- head: fd9b
	-- speed: aaf
	-- rng: 39e8eb4e
	-- counter: 503
-- MATCHED

-- For 8: 
	-- head: 58a
	-- speed: a8e
	-- rng: d68e28eb
	-- counter: 504
-- MATCHED

-- For 9: 
	-- head: 58a
	-- speed: a8e
	-- rng: b9778860
	-- counter: 504
-- MATCHED

-- For a: 
	-- head: fedb
	-- speed: aef
	-- rng: 72fe541d
	-- counter: 503
-- MATCHED

-- For b: 
	-- head: 74a
	-- speed: aae
	-- rng: 5153a6d
	-- counter: 504
-- MATCHED

-- For c: 
	-- head: 58a
	-- speed: a8e
	-- rng: b9778860
	-- counter: 504
-- MATCHED

-- For d: 
	-- head: 34a
	-- speed: a4e
	-- rng: 41888c44
	-- counter: 504
-- MATCHED

-- For e: 
	-- head: ff5b
	-- speed: acf
	-- rng: caefea68
	-- counter: 503
-- MATCHED

-- For f: 
	-- head: fedb
	-- speed: aef
	-- rng: 16fc7da2
	-- counter: 503
-- MATCHED


