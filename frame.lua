COUNT = 0

server = nil
ST_sockets = {}
nextID = 1
TOGGLE = false
PAST = 0

function ST_format(id, msg, isError)
	local prefix = "Socket " .. id
	if isError then
		prefix = prefix .. " Error: "
	else
		prefix = prefix .. " Received: "
	end
	return prefix .. msg
end


function ST_received(id)
	local sock = ST_sockets[id]
	if not sock then return end
	while true do
		local p, err = sock:receive(1024)
		if p then
			local keys = tonumber(p)
			local removes = keys ~ PAST

			emu:clearKeys(removes) -- remove past keypresses that differ
			emu:addKeys(keys)

			PAST = keys
		else
			if err ~= socket.ERRORS.AGAIN then
				console:error(ST_format(id, err, true))
				ST_stop(id)
			end
			return
		end
	end
end


function ST_accept()
	local sock, err = server:accept()
	if err then
		console:error(ST_format("Accept", err, true))
		return
	end
	local id = nextID
	nextID = id + 1
	ST_sockets[id] = sock
	sock:add("received", function() ST_received(id) end)
	sock:add("error", function() ST_error(id) end)
	console:log(ST_format(id, "Connected"))
end


function F_counter()
	-- counter to control the screenshot rate
	if COUNT == 5 then 

		-- save screenshot
		local out = emu:saveStateBuffer(1)

		-- send screenshot to all clients
		for _, sock in pairs(ST_sockets) do
			if sock then sock:send( out ) end
		end

		-- if  TOGGLE then
		-- 	emu:addKeys(19)
		-- 	console:log("bitmask")
		-- 	TOGGLE = false
		-- else
		-- 	emu:clearKeys(19)
		-- 	console:log("clear")
		-- 	TOGGLE = true
		-- end

		COUNT = 0
	end
	COUNT = COUNT + 1
end

callbacks:add("frame", F_counter)

local port = 8888
server = nil
while not server do
	server, err = socket.bind(nil, port)
	if err then
		if err == socket.ERRORS.ADDRESS_IN_USE then
			port = port + 1
		else
			console:error(ST_format("Bind", err, true))
			break
		end
	else
		local ok
		ok, err = server:listen()
		if err then
			server:close()
			console:error(ST_format("Listen", err, true))
		else
			console:log("Socket Server Test: Listening on port " .. port)
			server:add("received", ST_accept)
		end
	end
end
