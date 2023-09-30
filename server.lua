lastkeys = nil
server = nil
ST_sockets = {}
nextID = 1

COUNT = 0
START = false
GTIME = nil
GINDEX = 0

GROOT = ""
GCURR = ""

function ST_stop(id)
	local sock = ST_sockets[id]
	ST_sockets[id] = nil
	sock:close()
end

function ST_format(id, msg, isError)
	local prefix = "Socket " .. id
	if isError then
		prefix = prefix .. " Error: "
	else
		prefix = prefix .. " Received: "
	end
	return prefix .. msg
end

function ST_error(id, err)
	console:error(ST_format(id, err, true))
	ST_stop(id)
end

function ST_received(id)
	local sock = ST_sockets[id]
	if not sock then return end
	while true do
		local p, err = sock:receive(1024)
		if p then
			if p ~= "alive?" then

				 for _, verb, typ  in string.gmatch(p, "(%w+)%s+(%w+)%s*(%w*)%s*'?(.-)'?") do
					if verb == "set" and typ == "root" then
						GROOT = string.match(p, "%b''")
						GROOT = string.gsub(GROOT, "'", '')
						console:log("changed root directory: ".. GROOT)

					elseif verb == "set" and typ == "curr" then
						GCURR = string.match(p, "%b''")
						GCURR = string.gsub(GCURR, "'", '')
						console:log("changed curr directory: ".. GCURR)

					elseif verb == "start" then
						console:log("start recording...")
						START = true

					elseif verb == "stop" then
						console:log("stop recording...")
						START = false
				    end
				 end

			end
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
	if START ~= true then
		return
	end

	if COUNT == 10 then -- every 100 ms
		local time = os.time(os.date("!*t"))

		if time == GTIME then
			GINDEX = GINDEX + 1
		else
			GINDEX = 0
		end

		local filename = time .. "_" .. GINDEX

		local keys = emu:getKeys()

		emu:screenshot(GROOT .. "/" .. GCURR .."/pics/" .. filename .. ".png")

		for _, sock in pairs(ST_sockets) do
			if sock then sock:send( tostring( keys ) .. "<->" .. filename) end
		end

		GTIME = time

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
