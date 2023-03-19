-- Counts the number of steps taken since the program started running.
local memoryDomain = "EWRAM";
local stepCountAddress = 0x026AC8;
local steps = 0;
local lastValue = -1;

function main()
  console.clear();
	local lastValue = memory.read_u8(stepCountAddress, memoryDomain);
	client.unpause();
  while true do
	  local stepCount = memory.read_u8(stepCountAddress, memoryDomain);
		if (stepCount ~= lastValue) then
		  lastValue = stepCount
			steps = steps + 1
			console.writeline(steps)
	  end
		emu.frameadvance();
	end
	client.pause();
end

main()