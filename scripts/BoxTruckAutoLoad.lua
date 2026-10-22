-- Box Truck Pro Edition (PropaineX)
-- The truck's own autoload: pallets standing next to an open curtain side or behind the open rear doors are pulled into
-- the box one after the other. You see each one lift, swing to the opening and slide across the floor to its place.
-- Loaded pallets are held with the game's kinematic mount (Mountable:mountKinematic, as the game's AutoLoader uses):
-- they move with the truck and cannot sink into the floor, slide or jiggle. The tension belts leave them alone.
-- Keys (own actions, can be changed in the controls menu): BOXTRUCK_LOAD (left ctrl + L) starts / stops loading,
-- BOXTRUCK_RELEASE (left alt + L) lets the load go (the pallets stay where they are and can be taken off again).
-- Runs on the server; players send their key presses with BoxTruckAutoLoadEvent. The server moves the pallets and the
-- game sends their positions to the other players.

BoxTruckAutoLoad = {}
BoxTruckAutoLoad.MOD_NAME = g_currentModName
BoxTruckAutoLoad.SPEC_NAME = g_currentModName .. ".boxTruckAutoLoad"
BoxTruckAutoLoad.SPEC_TABLE_NAME = "spec_" .. BoxTruckAutoLoad.SPEC_NAME

-- load space in the truck's coordinates (source/build_body.py): top of the floor, half the width between the side
-- boards, front wall and rear doors, free height under the roof bows
BoxTruckAutoLoad.FLOOR_Y = 1.75
BoxTruckAutoLoad.HALF_WIDTH = 1.19
BoxTruckAutoLoad.FRONT_Z = 1.48               -- inside face of the front sheet (1.50)
BoxTruckAutoLoad.REAR_Z = -5.19
BoxTruckAutoLoad.MAX_HEIGHT = 2.30
BoxTruckAutoLoad.PICKUP_RANGE = 6.0        -- pallets up to this far from an opening are picked up
BoxTruckAutoLoad.STEP = 0.05               -- packing grid
BoxTruckAutoLoad.GAP = 0.02                -- between pallets and walls
BoxTruckAutoLoad.SPLIT = 0.5               -- part of the move spent getting to the opening (the rest slides it in)
BoxTruckAutoLoad.LIFT = 0.25               -- extra height of the swing to the opening

-- the openings: animation of BoxTruckBody, side of the box (+x = left)
BoxTruckAutoLoad.OPENINGS = {
    {name = "left",  anim = "boxCurtainLeft"},
    {name = "right", anim = "boxCurtainRight"},
    {name = "rear",  anim = "boxRearDoors"}
}

BoxTruckAutoLoad.COMMAND_START = 1
BoxTruckAutoLoad.COMMAND_STOP = 2
BoxTruckAutoLoad.COMMAND_RELEASE = 3
BoxTruckAutoLoad.COMMAND_STATE = 4           -- server to players: loading or not, number of pallets, message
BoxTruckAutoLoad.COMMAND_NUM_BITS = 3

BoxTruckAutoLoad.MESSAGE_NONE = 0
BoxTruckAutoLoad.MESSAGE_NOTHING = 1
BoxTruckAutoLoad.MESSAGE_FULL = 2
BoxTruckAutoLoad.MESSAGE_NUM_BITS = 2

function BoxTruckAutoLoad.prerequisitesPresent(specializations)
    return SpecializationUtil.hasSpecialization(AnimatedVehicle, specializations)
end

function BoxTruckAutoLoad.initSpecialization()
    local schemaSavegame = Vehicle.xmlSchemaSavegame
    local key = "vehicles.vehicle(?)." .. BoxTruckAutoLoad.SPEC_NAME .. ".load(?)"
    schemaSavegame:register(XMLValueType.STRING, key .. "#uniqueId", "Unique id of a loaded pallet")
    schemaSavegame:register(XMLValueType.FLOAT, key .. "#x", "Place across the box")
    schemaSavegame:register(XMLValueType.FLOAT, key .. "#z", "Place along the box")
    schemaSavegame:register(XMLValueType.FLOAT, key .. "#rot", "Rotation about y")
end

function BoxTruckAutoLoad.registerFunctions(vehicleType)
    SpecializationUtil.registerFunction(vehicleType, "boxTruckAutoLoadCommand", BoxTruckAutoLoad.boxTruckAutoLoadCommand)
    SpecializationUtil.registerFunction(vehicleType, "onUnmountObject", BoxTruckAutoLoad.onUnmountObject)
end

function BoxTruckAutoLoad.registerOverwrittenFunctions(vehicleType)
    SpecializationUtil.registerOverwrittenFunction(vehicleType, "addToPhysics", BoxTruckAutoLoad.addToPhysics)
    SpecializationUtil.registerOverwrittenFunction(vehicleType, "removeFromPhysics", BoxTruckAutoLoad.removeFromPhysics)
end

function BoxTruckAutoLoad.registerEventListeners(vehicleType)
    SpecializationUtil.registerEventListener(vehicleType, "onLoad", BoxTruckAutoLoad)
    SpecializationUtil.registerEventListener(vehicleType, "onDelete", BoxTruckAutoLoad)
    SpecializationUtil.registerEventListener(vehicleType, "onReadStream", BoxTruckAutoLoad)
    SpecializationUtil.registerEventListener(vehicleType, "onWriteStream", BoxTruckAutoLoad)
    SpecializationUtil.registerEventListener(vehicleType, "onRegisterActionEvents", BoxTruckAutoLoad)
    SpecializationUtil.registerEventListener(vehicleType, "onUpdate", BoxTruckAutoLoad)
end

function BoxTruckAutoLoad:onLoad(savegame)
    local spec = self[BoxTruckAutoLoad.SPEC_TABLE_NAME]

    spec.actionEvents = {}
    spec.isLoading = false
    spec.numLoaded = 0
    spec.texts = {
        load = g_i18n:getText("action_boxTruckLoad"),
        stop = g_i18n:getText("action_boxTruckStopLoad"),
        release = g_i18n:getText("action_boxTruckRelease"),
        openFirst = g_i18n:getText("warning_boxTruckOpenFirst"),
        nothing = g_i18n:getText("warning_boxTruckNothing"),
        full = g_i18n:getText("warning_boxTruckFull")
    }

    if self.isServer then
        -- the load space: x across (left +), z along (front +), y up from the floor
        spec.areaNode = createTransformGroup("boxTruckLoadArea")
        link(self.components[1].node, spec.areaNode)
        setTranslation(spec.areaNode, 0, BoxTruckAutoLoad.FLOOR_Y, 0)

        spec.mounted = {}           -- pallet -> {carrier, x, z, sizeX, sizeZ, rot}
        spec.moving = nil           -- the pallet being pulled in
        spec.carriersToDelete = {}
        spec.pendingLoad = {}

        if savegame ~= nil and not savegame.resetVehicles then
            savegame.xmlFile:iterate(savegame.key .. "." .. BoxTruckAutoLoad.SPEC_NAME .. ".load", function(_, key)
                local uniqueId = savegame.xmlFile:getValue(key .. "#uniqueId")
                if uniqueId ~= nil then
                    table.insert(spec.pendingLoad, {
                        uniqueId = uniqueId,
                        x = savegame.xmlFile:getValue(key .. "#x", 0),
                        z = savegame.xmlFile:getValue(key .. "#z", 0),
                        rot = savegame.xmlFile:getValue(key .. "#rot", 0)
                    })
                end
            end)
            spec.pendingLoadTime = 10000    -- give the pallets 10 s to appear after the savegame loaded
        end
    end
end

function BoxTruckAutoLoad:onDelete()
    local spec = self[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    if self.isServer and spec.mounted ~= nil then
        local pallets = {}
        for pallet, _ in pairs(spec.mounted) do
            table.insert(pallets, pallet)
        end
        for _, pallet in ipairs(pallets) do
            pallet:removeDeleteListener(self, BoxTruckAutoLoad.onDeleteLoadedPallet)
            pallet:unmountKinematic()
        end
        spec.mounted = {}
    end
end

function BoxTruckAutoLoad:saveToXMLFile(xmlFile, key, usedModNames)
    local spec = self[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    if spec.mounted == nil then
        return
    end
    local i = 0
    for pallet, data in pairs(spec.mounted) do
        local loadKey = string.format("%s.load(%d)", key, i)
        xmlFile:setValue(loadKey .. "#uniqueId", pallet:getUniqueId())
        xmlFile:setValue(loadKey .. "#x", data.x)
        xmlFile:setValue(loadKey .. "#z", data.z)
        xmlFile:setValue(loadKey .. "#rot", data.rot)
        i = i + 1
    end
end

-- players joining a game get the loading state
function BoxTruckAutoLoad:onReadStream(streamId, connection)
    local spec = self[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    spec.isLoading = streamReadBool(streamId)
    spec.numLoaded = streamReadUInt8(streamId)
end

function BoxTruckAutoLoad:onWriteStream(streamId, connection)
    local spec = self[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    streamWriteBool(streamId, spec.isLoading)
    streamWriteUInt8(streamId, math.min(spec.numLoaded, 255))
end

-- the truck goes in and out of physics (reset, teleport): the load goes with it
function BoxTruckAutoLoad:addToPhysics(superFunc)
    if not superFunc(self) then
        return false
    end
    local spec = self[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    if self.isServer and spec.mounted ~= nil then
        for pallet, _ in pairs(spec.mounted) do
            pallet:addToPhysics()
        end
    end
    return true
end

function BoxTruckAutoLoad:removeFromPhysics(superFunc)
    local ret = superFunc(self)
    local spec = self[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    if self.isServer and spec.mounted ~= nil then
        for pallet, _ in pairs(spec.mounted) do
            pallet:removeFromPhysics()
        end
    end
    return ret
end

---------------------------------------------------------------------------------------------------- keys

function BoxTruckAutoLoad:onRegisterActionEvents(isActiveForInput, isActiveForInputIgnoreSelection)
    if self.isClient then
        local spec = self[BoxTruckAutoLoad.SPEC_TABLE_NAME]
        self:clearActionEventsTable(spec.actionEvents)

        if isActiveForInputIgnoreSelection then
            local _, actionEventId = self:addActionEvent(spec.actionEvents, InputAction.BOXTRUCK_LOAD, self, BoxTruckAutoLoad.actionEventLoad, false, true, false, true, nil)
            spec.loadEventId = actionEventId
            g_inputBinding:setActionEventTextPriority(actionEventId, GS_PRIO_NORMAL)
            _, actionEventId = self:addActionEvent(spec.actionEvents, InputAction.BOXTRUCK_RELEASE, self, BoxTruckAutoLoad.actionEventRelease, false, true, false, true, nil)
            spec.releaseEventId = actionEventId
            g_inputBinding:setActionEventTextPriority(actionEventId, GS_PRIO_NORMAL)
            BoxTruckAutoLoad.updateActionTexts(self)
        end
    end
end

function BoxTruckAutoLoad.actionEventLoad(self, actionName, inputValue, callbackState, isAnalog)
    local spec = self[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    if spec.isLoading then
        self:boxTruckAutoLoadCommand(BoxTruckAutoLoad.COMMAND_STOP)
    elseif not BoxTruckAutoLoad.getIsAnyOpeningOpen(self) then
        g_currentMission:showBlinkingWarning(spec.texts.openFirst, 2000)
    else
        self:boxTruckAutoLoadCommand(BoxTruckAutoLoad.COMMAND_START)
    end
end

function BoxTruckAutoLoad.actionEventRelease(self, actionName, inputValue, callbackState, isAnalog)
    self:boxTruckAutoLoadCommand(BoxTruckAutoLoad.COMMAND_RELEASE)
end

function BoxTruckAutoLoad.updateActionTexts(vehicle)
    local spec = vehicle[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    if spec.loadEventId ~= nil then
        g_inputBinding:setActionEventText(spec.loadEventId, spec.isLoading and spec.texts.stop or spec.texts.load)
    end
    if spec.releaseEventId ~= nil then
        g_inputBinding:setActionEventText(spec.releaseEventId, string.format(spec.texts.release, spec.numLoaded))
        g_inputBinding:setActionEventActive(spec.releaseEventId, spec.numLoaded > 0)
    end
end

-- a key press: on a player's machine it goes to the server, on the server it is carried out
function BoxTruckAutoLoad:boxTruckAutoLoadCommand(command, noEventSend)
    if not self.isServer then
        if not noEventSend then
            g_client:getServerConnection():sendEvent(BoxTruckAutoLoadEvent.new(self, command))
        end
        return
    end

    local spec = self[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    if command == BoxTruckAutoLoad.COMMAND_START then
        spec.isLoading = true
        self:raiseActive()
    elseif command == BoxTruckAutoLoad.COMMAND_STOP then
        spec.isLoading = false
    elseif command == BoxTruckAutoLoad.COMMAND_RELEASE then
        spec.isLoading = false
        local pallets = {}
        for pallet, _ in pairs(spec.mounted) do
            table.insert(pallets, pallet)
        end
        for _, pallet in ipairs(pallets) do
            pallet:unmountKinematic()       -- calls onUnmountObject
        end
    end
    BoxTruckAutoLoad.sendState(self, BoxTruckAutoLoad.MESSAGE_NONE)
end

-- server: tell everybody whether the truck is loading and how many pallets it holds
function BoxTruckAutoLoad.sendState(vehicle, message)
    local spec = vehicle[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    local count = 0
    for _, _ in pairs(spec.mounted) do
        count = count + 1
    end
    BoxTruckAutoLoad.setState(vehicle, spec.isLoading, count, message)
    if g_server ~= nil then
        g_server:broadcastEvent(BoxTruckAutoLoadEvent.new(vehicle, BoxTruckAutoLoad.COMMAND_STATE, spec.isLoading, count, message), nil, nil, vehicle)
    end
end

function BoxTruckAutoLoad.setState(vehicle, isLoading, numLoaded, message)
    local spec = vehicle[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    spec.isLoading = isLoading
    spec.numLoaded = numLoaded
    if vehicle.isClient and vehicle:getIsActiveForInput(true) then
        if message == BoxTruckAutoLoad.MESSAGE_NOTHING then
            g_currentMission:showBlinkingWarning(spec.texts.nothing, 2000)
        elseif message == BoxTruckAutoLoad.MESSAGE_FULL then
            g_currentMission:showBlinkingWarning(spec.texts.full, 2000)
        end
        BoxTruckAutoLoad.updateActionTexts(vehicle)
    end
end

---------------------------------------------------------------------------------------------------- openings

function BoxTruckAutoLoad.getIsOpeningOpen(vehicle, opening)
    if not vehicle:getAnimationExists(opening.anim) then
        return false
    end
    return vehicle:getAnimationTime(opening.anim) > 0.99 and not vehicle:getIsAnimationPlaying(opening.anim)
end

function BoxTruckAutoLoad.getIsAnyOpeningOpen(vehicle)
    for _, opening in ipairs(BoxTruckAutoLoad.OPENINGS) do
        if BoxTruckAutoLoad.getIsOpeningOpen(vehicle, opening) then
            return true
        end
    end
    return false
end

-- the open opening a pallet at x, y, z (load space coordinates) can come in through, and how far it is from it
function BoxTruckAutoLoad.getOpeningFor(vehicle, x, y, z)
    local hw = BoxTruckAutoLoad.HALF_WIDTH
    local range = BoxTruckAutoLoad.PICKUP_RANGE
    if y < -3 or y > 1 then
        return nil
    end
    local best, bestDistance = nil, math.huge
    for _, opening in ipairs(BoxTruckAutoLoad.OPENINGS) do
        if BoxTruckAutoLoad.getIsOpeningOpen(vehicle, opening) then
            local distance = nil
            if opening.name == "left" and x > hw + 0.1 and z > BoxTruckAutoLoad.REAR_Z - 1 and z < BoxTruckAutoLoad.FRONT_Z + 1 then
                distance = x - hw
            elseif opening.name == "right" and x < -hw - 0.1 and z > BoxTruckAutoLoad.REAR_Z - 1 and z < BoxTruckAutoLoad.FRONT_Z + 1 then
                distance = -hw - x
            elseif opening.name == "rear" and z < BoxTruckAutoLoad.REAR_Z - 0.1 and math.abs(x) < hw + 1.5 then
                distance = BoxTruckAutoLoad.REAR_Z - z
            end
            if distance ~= nil and distance < range and distance < bestDistance then
                best, bestDistance = opening, distance
            end
        end
    end
    return best, bestDistance
end

---------------------------------------------------------------------------------------------------- packing

local function overlaps(a, x0, x1, z0, z1)
    return x0 < a.x1 and x1 > a.x0 and z0 < a.z1 and z1 > a.z0
end

-- a free place for a footprint sizeX x sizeZ: rows from the front wall back; in a row, through a side the far side
-- first, through the rear left to right. So a pallet never has to pass one that is already in.
function BoxTruckAutoLoad.findSlot(vehicle, sizeX, sizeZ, opening, blocked)
    local spec = vehicle[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    local hw, gap, step = BoxTruckAutoLoad.HALF_WIDTH, BoxTruckAutoLoad.GAP, BoxTruckAutoLoad.STEP
    if sizeX > 2 * hw - 2 * gap or sizeZ > BoxTruckAutoLoad.FRONT_Z - BoxTruckAutoLoad.REAR_Z - 2 * gap then
        return nil
    end
    local taken = {}
    for _, data in pairs(spec.mounted) do
        table.insert(taken, {x0 = data.x - data.sizeX * 0.5, x1 = data.x + data.sizeX * 0.5, z0 = data.z - data.sizeZ * 0.5, z1 = data.z + data.sizeZ * 0.5})
    end
    if spec.moving ~= nil then
        local m = spec.moving
        table.insert(taken, {x0 = m.target[1] - m.sizeX * 0.5, x1 = m.target[1] + m.sizeX * 0.5, z0 = m.target[3] - m.sizeZ * 0.5, z1 = m.target[3] + m.sizeZ * 0.5})
    end
    for _, b in ipairs(blocked) do
        table.insert(taken, b)
    end

    local xMin, xMax = -hw + gap + sizeX * 0.5, hw - gap - sizeX * 0.5
    local xStart, xEnd, xStep = xMax, xMin, -step           -- far side for the left opening: right (-x) is far
    if opening.name == "left" then
        xStart, xEnd, xStep = xMin, xMax, step
    end
    local z = BoxTruckAutoLoad.FRONT_Z - gap - sizeZ * 0.5
    while z >= BoxTruckAutoLoad.REAR_Z + gap + sizeZ * 0.5 do
        local x = xStart
        while (xStep > 0 and x <= xEnd + 0.001) or (xStep < 0 and x >= xEnd - 0.001) do
            local x0, x1 = x - sizeX * 0.5 - gap * 0.5, x + sizeX * 0.5 + gap * 0.5
            local z0, z1 = z - sizeZ * 0.5 - gap * 0.5, z + sizeZ * 0.5 + gap * 0.5
            local free = true
            for _, a in ipairs(taken) do
                if overlaps(a, x0, x1, z0, z1) then
                    free = false
                    break
                end
            end
            if free then
                return x, z
            end
            x = x + xStep
        end
        z = z - step
    end
    return nil
end

-- is something else (a pallet put in with the forklift, ...) standing on that place?
function BoxTruckAutoLoad:loadSpaceOverlapCallback(transformId)
    if transformId ~= 0 and getHasClassId(transformId, ClassIds.SHAPE) and not getHasTrigger(transformId) then
        local spec = self[BoxTruckAutoLoad.SPEC_TABLE_NAME]
        local object = g_currentMission:getNodeObject(transformId)
        if object ~= self and object ~= spec.checkObject and (object == nil or spec.mounted[object] == nil) then
            spec.isSlotBlocked = true
            return false
        end
    end
    return true
end

function BoxTruckAutoLoad.getIsSlotFree(vehicle, pallet, x, z, sizeX, sizeY, sizeZ, rot)
    local spec = vehicle[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    local wx, wy, wz = localToWorld(spec.areaNode, x, sizeY * 0.5 + 0.05, z)
    local rx, ry, rz = getWorldRotation(spec.areaNode)
    spec.isSlotBlocked = false
    spec.checkObject = pallet
    overlapBox(wx, wy, wz, rx, ry + rot, rz, sizeX * 0.5 - 0.05, sizeY * 0.5 - 0.05, sizeZ * 0.5 - 0.05,
        "loadSpaceOverlapCallback", vehicle, CollisionFlag.VEHICLE + CollisionFlag.DYNAMIC_OBJECT, true, true, false, true)
    spec.checkObject = nil
    return not spec.isSlotBlocked
end

---------------------------------------------------------------------------------------------------- loading

local function smooth(t)
    t = math.max(0, math.min(1, t))
    return t * t * (3 - 2 * t)
end

local function angleTo(from, to)
    local d = (to - from) % (2 * math.pi)
    if d > math.pi then
        d = d - 2 * math.pi
    end
    return d
end

-- server: the next pallet to pull in, or nil and why not
function BoxTruckAutoLoad.startNext(vehicle)
    local spec = vehicle[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    local farmId = vehicle:getActiveFarm()
    local candidates = {}
    for _, pallet in ipairs(g_currentMission.vehicleSystem.vehicles) do
        if pallet.isPallet and not pallet.isDeleted and spec.mounted[pallet] == nil and pallet.mountKinematic ~= nil
            and pallet.dynamicMountType == MountableObject.MOUNT_TYPE_NONE and pallet.size ~= nil
            and g_currentMission.accessHandler:canFarmAccess(farmId, pallet) then
            local x, y, z = worldToLocal(spec.areaNode, getWorldTranslation(pallet.components[1].node))
            local opening, distance = BoxTruckAutoLoad.getOpeningFor(vehicle, x, y, z)
            if opening ~= nil then
                table.insert(candidates, {pallet = pallet, opening = opening, distance = distance})
            end
        end
    end
    if #candidates == 0 then
        return BoxTruckAutoLoad.MESSAGE_NOTHING
    end
    table.sort(candidates, function(a, b) return a.distance < b.distance end)

    local anyTried = false
    for _, c in ipairs(candidates) do
        local pallet = c.pallet
        local sizeX, sizeY, sizeZ, rot
        if pallet.getAutoLoadSize ~= nil then
            sizeX, sizeY, sizeZ = pallet:getAutoLoadSize()
            rot = math.pi * 0.5              -- the game's pallets are loaded turned by 90 deg (Pallet:autoLoad)
        else
            sizeX, sizeY, sizeZ = pallet.size.width, pallet.size.height, pallet.size.length
            rot = 0
        end
        if sizeY <= BoxTruckAutoLoad.MAX_HEIGHT then
            anyTried = true
            -- the game's way round first, then turned by 90 deg
            local tries = {{sizeX, sizeZ, rot}, {sizeZ, sizeX, rot + math.pi * 0.5}}
            for _, try in ipairs(tries) do
                local blocked = {}
                for _ = 1, 4 do
                    local x, z = BoxTruckAutoLoad.findSlot(vehicle, try[1], try[2], c.opening, blocked)
                    if x == nil then
                        break
                    end
                    if BoxTruckAutoLoad.getIsSlotFree(vehicle, pallet, x, z, try[1], sizeY, try[2], try[3]) then
                        BoxTruckAutoLoad.startMove(vehicle, pallet, c.opening, x, z, try[1], sizeY, try[2], try[3])
                        return BoxTruckAutoLoad.MESSAGE_NONE
                    end
                    table.insert(blocked, {x0 = x - try[1] * 0.5, x1 = x + try[1] * 0.5, z0 = z - try[2] * 0.5, z1 = z + try[2] * 0.5})
                end
            end
        end
    end
    return anyTried and BoxTruckAutoLoad.MESSAGE_FULL or BoxTruckAutoLoad.MESSAGE_NOTHING
end

-- server: hang the pallet on a carrier node where it stands, then move the carrier into the box
function BoxTruckAutoLoad.startMove(vehicle, pallet, opening, x, z, sizeX, sizeY, sizeZ, rot)
    local spec = vehicle[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    local componentNode = pallet.components[1].node

    local carrier = createTransformGroup("boxTruckLoadCarrier")
    link(spec.areaNode, carrier)
    local wx, wy, wz = getWorldTranslation(componentNode)
    local qx, qy, qz, qw = getWorldQuaternion(componentNode)
    setWorldTranslation(carrier, wx, wy, wz)
    setWorldQuaternion(carrier, qx, qy, qz, qw)
    pallet:mountKinematic(vehicle, carrier, 0, 0, 0, 0, 0, 0)
    pallet:addDeleteListener(vehicle, BoxTruckAutoLoad.onDeleteLoadedPallet)

    local sx, sy, sz = getTranslation(carrier)
    local rx, ry, rz = getRotation(carrier)
    -- turn the short way: the pallet may go in either way round
    if math.abs(angleTo(ry, rot + math.pi)) < math.abs(angleTo(ry, rot)) then
        rot = rot + math.pi
    end

    -- just outside the opening, level with the floor, in line with the place
    local hw = BoxTruckAutoLoad.HALF_WIDTH
    local entry
    if opening.name == "left" then
        entry = {hw + sizeX * 0.5 + 0.30, 0.03, z}
    elseif opening.name == "right" then
        entry = {-hw - sizeX * 0.5 - 0.30, 0.03, z}
    else
        entry = {x, 0.03, BoxTruckAutoLoad.REAR_Z - sizeZ * 0.5 - 0.30}
    end
    local d1 = MathUtil.vector3Length(entry[1] - sx, entry[2] - sy, entry[3] - sz)
    local d2 = MathUtil.vector3Length(x - entry[1], 0, z - entry[3])

    spec.moving = {
        pallet = pallet,
        carrier = carrier,
        start = {sx, sy, sz},
        startRot = {rx, ry, rz},
        endRot = ry + angleTo(ry, rot),
        entry = entry,
        target = {x, 0, z},
        sizeX = sizeX,
        sizeZ = sizeZ,
        rot = rot,
        time = 0,
        duration = math.max(1.0, math.min(2.5, 0.9 + d1 / 5 + d2 / 4)) * 1000
    }
end

-- server: one step of the pull-in
function BoxTruckAutoLoad.updateMove(vehicle, dt)
    local spec = vehicle[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    local m = spec.moving
    m.time = m.time + dt
    local s = math.min(1, m.time / m.duration)
    local split = BoxTruckAutoLoad.SPLIT
    local x, y, z
    local rx, ry, rz = m.startRot[1], m.startRot[2], m.startRot[3]
    if s < split then
        -- lift and swing round to the opening
        local p = smooth(s / split)
        x = m.start[1] + (m.entry[1] - m.start[1]) * p
        y = m.start[2] + (m.entry[2] - m.start[2]) * p + BoxTruckAutoLoad.LIFT * math.sin(math.pi * p)
        z = m.start[3] + (m.entry[3] - m.start[3]) * p
        rx, ry, rz = rx * (1 - p), ry + (m.endRot - ry) * p, rz * (1 - p)
    else
        -- slide across the floor to the place
        local p = smooth((s - split) / (1 - split))
        x = m.entry[1] + (m.target[1] - m.entry[1]) * p
        y = m.entry[2] + (m.target[2] - m.entry[2]) * p
        z = m.entry[3] + (m.target[3] - m.entry[3]) * p
        rx, ry, rz = 0, m.endRot, 0
    end
    setTranslation(m.carrier, x, y, z)
    setRotation(m.carrier, rx, ry, rz)
    m.pallet:raiseActive()

    if s >= 1 then
        spec.mounted[m.pallet] = {carrier = m.carrier, x = m.target[1], z = m.target[3], sizeX = m.sizeX, sizeZ = m.sizeZ, rot = m.rot}
        spec.moving = nil
        spec.nextDelay = 150
        BoxTruckAutoLoad.sendState(vehicle, BoxTruckAutoLoad.MESSAGE_NONE)
    end
end

-- server: pallets saved on the truck go back to their places
function BoxTruckAutoLoad.updatePendingLoad(vehicle, dt)
    local spec = vehicle[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    local left = {}
    local placed = false
    for _, data in ipairs(spec.pendingLoad) do
        local pallet = g_currentMission.vehicleSystem:getVehicleByUniqueId(data.uniqueId)
        if pallet ~= nil and pallet.mountKinematic ~= nil and pallet.dynamicMountType == MountableObject.MOUNT_TYPE_NONE then
            local sizeX, _, sizeZ = pallet.size.width, pallet.size.height, pallet.size.length
            if pallet.getAutoLoadSize ~= nil then
                sizeX, _, sizeZ = pallet:getAutoLoadSize()
            end
            local turned = math.abs(math.sin(data.rot - (pallet.getAutoLoadSize ~= nil and math.pi * 0.5 or 0))) > 0.5
            if turned then
                sizeX, sizeZ = sizeZ, sizeX
            end
            local carrier = createTransformGroup("boxTruckLoadCarrier")
            link(spec.areaNode, carrier)
            setTranslation(carrier, data.x, 0, data.z)
            setRotation(carrier, 0, data.rot, 0)
            pallet:mountKinematic(vehicle, carrier, 0, 0, 0, 0, 0, 0)
            pallet:addDeleteListener(vehicle, BoxTruckAutoLoad.onDeleteLoadedPallet)
            spec.mounted[pallet] = {carrier = carrier, x = data.x, z = data.z, sizeX = sizeX, sizeZ = sizeZ, rot = data.rot}
            placed = true
        elseif pallet == nil then
            table.insert(left, data)
        end
    end
    spec.pendingLoad = left
    spec.pendingLoadTime = spec.pendingLoadTime - dt
    if spec.pendingLoadTime <= 0 then
        spec.pendingLoad = {}
    end
    if placed then
        BoxTruckAutoLoad.sendState(vehicle, BoxTruckAutoLoad.MESSAGE_NONE)
    end
end

function BoxTruckAutoLoad:onUpdate(dt, isActiveForInput, isActiveForInputIgnoreSelection, isSelected)
    local spec = self[BoxTruckAutoLoad.SPEC_TABLE_NAME]

    if self.isServer then
        for i = #spec.carriersToDelete, 1, -1 do
            local carrier = spec.carriersToDelete[i]
            if entityExists(carrier) and getNumOfChildren(carrier) == 0 then
                delete(carrier)
            end
            table.remove(spec.carriersToDelete, i)
        end

        if #spec.pendingLoad > 0 then
            BoxTruckAutoLoad.updatePendingLoad(self, dt)
            self:raiseActive()
        end

        if spec.moving ~= nil then
            BoxTruckAutoLoad.updateMove(self, dt)
            self:raiseActive()
        elseif spec.isLoading then
            spec.nextDelay = (spec.nextDelay or 0) - dt
            if spec.nextDelay <= 0 then
                local message = BoxTruckAutoLoad.startNext(self)
                if message ~= BoxTruckAutoLoad.MESSAGE_NONE then
                    spec.isLoading = false
                    BoxTruckAutoLoad.sendState(self, message)
                end
            end
            self:raiseActive()
        end

        -- the load moves with the truck: keep the pallets sending their positions to the other players
        if next(spec.mounted) ~= nil and self:getLastSpeed() > 0.1 then
            for pallet, _ in pairs(spec.mounted) do
                pallet:raiseActive()
            end
        end
    end

    if isActiveForInputIgnoreSelection then
        BoxTruckAutoLoad.updateActionTexts(self)
    end
end

-- a pallet left the truck (released, taken by a tension belt, ...): forget it, its carrier goes next frame
function BoxTruckAutoLoad:onUnmountObject(object)
    local spec = self[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    if spec.mounted == nil then
        return
    end
    local data = spec.mounted[object]
    if data ~= nil then
        spec.mounted[object] = nil
        table.insert(spec.carriersToDelete, data.carrier)
        object:removeDeleteListener(self, BoxTruckAutoLoad.onDeleteLoadedPallet)
    elseif spec.moving ~= nil and spec.moving.pallet == object then
        table.insert(spec.carriersToDelete, spec.moving.carrier)
        spec.moving = nil
        object:removeDeleteListener(self, BoxTruckAutoLoad.onDeleteLoadedPallet)
    end
end

-- a loaded pallet was sold, emptied or deleted
function BoxTruckAutoLoad.onDeleteLoadedPallet(self, object)
    local spec = self[BoxTruckAutoLoad.SPEC_TABLE_NAME]
    local data = spec.mounted[object]
    if data ~= nil then
        spec.mounted[object] = nil
        table.insert(spec.carriersToDelete, data.carrier)
    elseif spec.moving ~= nil and spec.moving.pallet == object then
        table.insert(spec.carriersToDelete, spec.moving.carrier)
        spec.moving = nil
    end
    if self.isServer then
        BoxTruckAutoLoad.sendState(self, BoxTruckAutoLoad.MESSAGE_NONE)
    end
end

---------------------------------------------------------------------------------------------------- event

BoxTruckAutoLoadEvent = {}
local BoxTruckAutoLoadEvent_mt = Class(BoxTruckAutoLoadEvent, Event)
InitEventClass(BoxTruckAutoLoadEvent, "BoxTruckAutoLoadEvent")

function BoxTruckAutoLoadEvent.emptyNew()
    return Event.new(BoxTruckAutoLoadEvent_mt)
end

function BoxTruckAutoLoadEvent.new(vehicle, command, isLoading, numLoaded, message)
    local self = BoxTruckAutoLoadEvent.emptyNew()
    self.vehicle = vehicle
    self.command = command
    self.isLoading = isLoading == true
    self.numLoaded = numLoaded or 0
    self.message = message or BoxTruckAutoLoad.MESSAGE_NONE
    return self
end

function BoxTruckAutoLoadEvent:readStream(streamId, connection)
    self.vehicle = NetworkUtil.readNodeObject(streamId)
    self.command = streamReadUIntN(streamId, BoxTruckAutoLoad.COMMAND_NUM_BITS)
    if self.command == BoxTruckAutoLoad.COMMAND_STATE then
        self.isLoading = streamReadBool(streamId)
        self.numLoaded = streamReadUInt8(streamId)
        self.message = streamReadUIntN(streamId, BoxTruckAutoLoad.MESSAGE_NUM_BITS)
    end
    self:run(connection)
end

function BoxTruckAutoLoadEvent:writeStream(streamId, connection)
    NetworkUtil.writeNodeObject(streamId, self.vehicle)
    streamWriteUIntN(streamId, self.command, BoxTruckAutoLoad.COMMAND_NUM_BITS)
    if self.command == BoxTruckAutoLoad.COMMAND_STATE then
        streamWriteBool(streamId, self.isLoading)
        streamWriteUInt8(streamId, math.min(self.numLoaded, 255))
        streamWriteUIntN(streamId, self.message, BoxTruckAutoLoad.MESSAGE_NUM_BITS)
    end
end

function BoxTruckAutoLoadEvent:run(connection)
    if self.vehicle == nil or not self.vehicle:getIsSynchronized() then
        return
    end
    if self.command == BoxTruckAutoLoad.COMMAND_STATE then
        BoxTruckAutoLoad.setState(self.vehicle, self.isLoading, self.numLoaded, self.message)
    elseif not connection:getIsServer() then
        -- a player's key press arrived at the server
        self.vehicle:boxTruckAutoLoadCommand(self.command, true)
    end
end
