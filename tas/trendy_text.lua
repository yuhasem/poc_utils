local tenthListAddress = 0x083DD0F5;
local twelthListAddress = 0x083DD4E0;
local thirteenthListAddress = 0x083DD629;

local tenthListLength = 0x45;
local twelthListLength = 0x2D;
local thirteenthListLength = 0x36;

local memoryDomain = "System Bus";


function getWords(list, length)
  local i = 0;
	local wordList = {};
	local nextWord = "";
	while i < length do
		local character = memory.read_u8(list, memoryDomain)
		list = list + 1
		-- console.writeline(character)
		if character == 0xFF then
			i = i + 1
			table.insert(wordList, nextWord)
			-- console.write(nextWord.." ")
			nextWord = ""
		else
			offset = character - 0xBB
			if offset < 0 or offset > 26 then
				nextChar = ' '
			else
				nextChar = string.char(string.byte('A') + offset)
			end
			nextWord = nextWord..nextChar
		end
		-- emu.frameadvance()
	end
	return wordList
end

function main()
  console.clear();
	words = getWords(tenthListAddress, tenthListLength);
	console.write("[")
	for _, word in ipairs(words) do
	  console.write("'"..word.."',")
	end
	console.write("]")
	console.writeline()
	console.writeline()
	words = getWords(twelthListAddress, twelthListLength);
	console.write("[")
	for _, word in ipairs(words) do
	  console.write("'"..word.."',")
	end
	console.write("]")
	console.writeline()
	console.writeline()
	words = getWords(thirteenthListAddress, thirteenthListLength);
	console.write("[")
	for _, word in ipairs(words) do
	  console.write("'"..word.."',")
	end
	console.write("]")
	console.writeline()
	console.writeline()
end

main()