-- Box Truck Pro Edition (PropaineX)
-- Opens and closes the curtain-sider body: rear barn doors, left curtain, right curtain.
-- The movements are animations in the vehicle XML (boxRearDoors, boxCurtainLeft, boxCurtainRight); playAnimation
-- already sends them to the other players. This spec adds the keys, saves the positions and sends them to players
-- who join later.
-- Keys (game actions, can be changed in the controls menu): X (IMPLEMENT_EXTRA2) = rear doors,
-- Z (IMPLEMENT_EXTRA4) = open/close the selected curtain, U (TOGGLE_TIPSIDE, as on the Krone ProfiLiner) = select
-- the left or right curtain. (v1 had the left curtain on Y; Y is taken by other actions in the game.)
-- Universal Autoload (another mod, if installed) loads and unloads the pallets, set up exactly like the game's Krone
-- ProfiLiner (user 2026-10-22: "give me the ProfiLiner's loading and unloading"). The truck hands UAL the ProfiLiner's
-- settings itself (isCurtainTrailer, enableRearLoading, enableSideLoading, one loading area = our load space) for all
-- shop configurations, before UAL sets the truck up: on by default, nothing to pick. As on the ProfiLiner UAL then only
-- picks pallets up through an open curtain or the open rear doors, unloads to the side whose curtain is open and drops
-- its own side key (U is our curtain select). It asks getTipState / getIsUnfolded (the game's trailer and foldable
-- specs on the ProfiLiner): here they report our curtains and doors.

BoxTruckBody = {}
BoxTruckBody.MOD_NAME = g_currentModName
BoxTruckBody.SPEC_NAME = g_currentModName .. ".boxTruckBody"
BoxTruckBody.SPEC_TABLE_NAME = "spec_" .. BoxTruckBody.SPEC_NAME

-- animation name, input action, save attribute, texts for open/close; both curtains share one action (the selected
-- side moves)
BoxTruckBody.PARTS = {
    {anim = "boxRearDoors",    action = "IMPLEMENT_EXTRA2", key = "rearDoors",    open = "action_boxTruckOpenRearDoors",    close = "action_boxTruckCloseRearDoors"},
    {anim = "boxCurtainLeft", action = "IMPLEMENT_EXTRA4", key = "curtainLeft",
        open = "action_boxTruckOpenCurtainLeft", close = "action_boxTruckCloseCurtainLeft",
        curtain = true, select = "action_boxTruckSelectCurtainLeft"},
    {anim = "boxCurtainRight", action = "IMPLEMENT_EXTRA4", key = "curtainRight",
        open = "action_boxTruckOpenCurtainRight", close = "action_boxTruckCloseCurtainRight",
        curtain = true, select = "action_boxTruckSelectCurtainRight"}
}

function BoxTruckBody.prerequisitesPresent(specializations)
    return SpecializationUtil.hasSpecialization(AnimatedVehicle, specializations)
end

function BoxTruckBody.initSpecialization()
    local schemaSavegame = Vehicle.xmlSchemaSavegame
    for _, part in ipairs(BoxTruckBody.PARTS) do
        schemaSavegame:register(XMLValueType.FLOAT, "vehicles.vehicle(?)." .. BoxTruckBody.SPEC_NAME .. "#" .. part.key, "Open position 0..1", 0)
    end
end

function BoxTruckBody.registerEventListeners(vehicleType)
    SpecializationUtil.registerEventListener(vehicleType, "onPreLoad", BoxTruckBody)
    SpecializationUtil.registerEventListener(vehicleType, "onLoad", BoxTruckBody)
    SpecializationUtil.registerEventListener(vehicleType, "onPostLoad", BoxTruckBody)
    SpecializationUtil.registerEventListener(vehicleType, "onReadStream", BoxTruckBody)
    SpecializationUtil.registerEventListener(vehicleType, "onWriteStream", BoxTruckBody)
    SpecializationUtil.registerEventListener(vehicleType, "onRegisterActionEvents", BoxTruckBody)
    SpecializationUtil.registerEventListener(vehicleType, "onUpdate", BoxTruckBody)
end

function BoxTruckBody:onLoad(savegame)
    local spec = self[BoxTruckBody.SPEC_TABLE_NAME]

    spec.actionEvents = {}
    spec.parts = {}
    for _, part in ipairs(BoxTruckBody.PARTS) do
        if self:getAnimationExists(part.anim) then
            table.insert(spec.parts, {
                anim = part.anim,
                action = InputAction[part.action],
                key = part.key,
                openText = g_i18n:getText(part.open),
                closeText = g_i18n:getText(part.close),
                curtain = part.curtain == true,
                selectText = part.select ~= nil and g_i18n:getText(part.select) or nil,
                actionEventId = nil
            })
        else
            Logging.xmlWarning(self.xmlFile, "Box Truck: animation '%s' not found", part.anim)
        end
    end
    spec.curtains = {}
    for _, part in ipairs(spec.parts) do
        if part.curtain then
            table.insert(spec.curtains, part)
        end
    end
    spec.curtainIndex = 1   -- selected curtain (only on this player's machine)
end

function BoxTruckBody:onPostLoad(savegame)
    local spec = self[BoxTruckBody.SPEC_TABLE_NAME]
    local ual = self.spec_universalAutoload
    if ual ~= nil then
        ual.isCurtainTrailer = true
        if self.getTipState == nil then
            self.getTipState = BoxTruckBody.getTipState
        end
        if self.getIsUnfolded == nil then
            self.getIsUnfolded = BoxTruckBody.getIsRearDoorOpen
        end
        -- curtain states seen by updateUalTipside (nil = not looked yet) and the curtain opened last
        spec.ualLeftOpen, spec.ualRightOpen, spec.ualLastOpened = nil, nil, nil
    end
    if savegame ~= nil and not savegame.resetVehicles then
        for _, part in ipairs(spec.parts) do
            local time = savegame.xmlFile:getValue(savegame.key .. "." .. BoxTruckBody.SPEC_NAME .. "#" .. part.key, 0)
            self:setAnimationTime(part.anim, time, true, false)
        end
    end
end

function BoxTruckBody:saveToXMLFile(xmlFile, key, usedModNames)
    local spec = self[BoxTruckBody.SPEC_TABLE_NAME]
    for _, part in ipairs(spec.parts) do
        xmlFile:setValue(key .. "#" .. part.key, BoxTruckBody.getTargetTime(self, part))
    end
end

-- players joining a game get the current positions
function BoxTruckBody:onReadStream(streamId, connection)
    local spec = self[BoxTruckBody.SPEC_TABLE_NAME]
    for _, part in ipairs(spec.parts) do
        self:setAnimationTime(part.anim, streamReadFloat32(streamId), true, false)
    end
end

function BoxTruckBody:onWriteStream(streamId, connection)
    local spec = self[BoxTruckBody.SPEC_TABLE_NAME]
    for _, part in ipairs(spec.parts) do
        streamWriteFloat32(streamId, BoxTruckBody.getTargetTime(self, part))
    end
end

-- where a part ends up: while it moves, the end it is moving to
function BoxTruckBody.getTargetTime(vehicle, part)
    if vehicle:getIsAnimationPlaying(part.anim) then
        local speed = vehicle.spec_animatedVehicle.animations[part.anim].currentSpeed
        return speed > 0 and 1 or 0
    end
    return vehicle:getAnimationTime(part.anim)
end

function BoxTruckBody.getIsOpen(vehicle, part)
    return BoxTruckBody.getTargetTime(vehicle, part) > 0.5
end

function BoxTruckBody:onRegisterActionEvents(isActiveForInput, isActiveForInputIgnoreSelection)
    if self.isClient then
        local spec = self[BoxTruckBody.SPEC_TABLE_NAME]
        self:clearActionEventsTable(spec.actionEvents)

        if isActiveForInputIgnoreSelection then
            for _, part in ipairs(spec.parts) do
                if not part.curtain then
                    local _, actionEventId = self:addActionEvent(spec.actionEvents, part.action, self, BoxTruckBody.actionEventToggle, false, true, false, true, part)
                    part.actionEventId = actionEventId
                    g_inputBinding:setActionEventTextPriority(actionEventId, GS_PRIO_NORMAL)
                end
            end
            if #spec.curtains > 0 then
                local _, actionEventId = self:addActionEvent(spec.actionEvents, InputAction.IMPLEMENT_EXTRA4, self, BoxTruckBody.actionEventToggleCurtain, false, true, false, true, nil)
                spec.curtainEventId = actionEventId
                g_inputBinding:setActionEventTextPriority(actionEventId, GS_PRIO_NORMAL)
                _, actionEventId = self:addActionEvent(spec.actionEvents, InputAction.TOGGLE_TIPSIDE, self, BoxTruckBody.actionEventSelectCurtain, false, true, false, true, nil)
                spec.selectEventId = actionEventId
                g_inputBinding:setActionEventTextPriority(actionEventId, GS_PRIO_NORMAL)
            end
            BoxTruckBody.updateActionTexts(self)
        end
    end
end

function BoxTruckBody.actionEventToggle(self, actionName, inputValue, callbackState, isAnalog)
    local part = callbackState
    local speed = BoxTruckBody.getIsOpen(self, part) and -1 or 1
    self:playAnimation(part.anim, speed, self:getAnimationTime(part.anim), false)
end

function BoxTruckBody.actionEventToggleCurtain(self, actionName, inputValue, callbackState, isAnalog)
    local spec = self[BoxTruckBody.SPEC_TABLE_NAME]
    BoxTruckBody.actionEventToggle(self, actionName, inputValue, spec.curtains[spec.curtainIndex], isAnalog)
end

function BoxTruckBody.actionEventSelectCurtain(self, actionName, inputValue, callbackState, isAnalog)
    local spec = self[BoxTruckBody.SPEC_TABLE_NAME]
    spec.curtainIndex = spec.curtainIndex % #spec.curtains + 1
    BoxTruckBody.updateActionTexts(self)
end

-- keep the help texts right, also when another player moves a part
function BoxTruckBody:onUpdate(dt, isActiveForInput, isActiveForInputIgnoreSelection, isSelected)
    if isActiveForInputIgnoreSelection then
        BoxTruckBody.updateActionTexts(self)
    end
    if self.isServer and self.spec_universalAutoload ~= nil then
        BoxTruckBody.updateUalTipside(self)
        -- a curtain or door still moving: stay active one more frame, so the side is set once it has stopped
        local spec = self[BoxTruckBody.SPEC_TABLE_NAME]
        for _, part in ipairs(spec.parts) do
            if self:getIsAnimationPlaying(part.anim) then
                self:raiseActive()
                break
            end
        end
    end
end

---------------------------------------------------------------------------------------------------- Universal Autoload

-- the ProfiLiner's UAL settings (its entry: isCurtainTrailer, enableRearLoading, enableSideLoading), with our load
-- space: floor top 1.75, from the inside of the front sheet (1.50) to the rear (-5.10), between the side walls, up to
-- the roof bows (the area UAL measured on this truck itself)
BoxTruckBody.UAL_OPTIONS = {isCurtainTrailer = true, enableRearLoading = true, enableSideLoading = true}
BoxTruckBody.UAL_LOADING_AREA = {offset = {0, 1.75, -1.801}, width = 2.4548, length = 6.5989, height = 2.3696}

-- UAL's class table. Every mod runs in its own script environment, so its global "UniversalAutoload" is not visible
-- here; the vehicle's own specialization list has it (UAL adds itself as "<its mod name>.universalAutoload").
function BoxTruckBody.getUal(vehicle)
    if vehicle.specializations ~= nil and vehicle.specializationNames ~= nil then
        for id, specClass in pairs(vehicle.specializations) do
            local name = vehicle.specializationNames[id]
            if type(name) == "string" and name:sub(-#".universalAutoload") == ".universalAutoload" then
                return specClass
            end
        end
    end
    return nil
end

function BoxTruckBody:onPreLoad(savegame)
    local UniversalAutoload = BoxTruckBody.getUal(self)
    if UniversalAutoload == nil or UniversalAutoload.VEHICLE_CONFIGURATIONS == nil
        or UniversalAutoload.OPTIONS_DEFAULTS == nil or UniversalAutoload.LOADING_AREA_DEFAULTS == nil then
        return
    end
    -- the name UAL files the truck under: the vehicle xml path below the mods folder ("FS25_BoxTruck_ProEdition/boxTruck.xml")
    local name = self.configFileName
    if name ~= nil and g_modsDirectory ~= nil and name:sub(1, #g_modsDirectory) == g_modsDirectory then
        name = name:sub(#g_modsDirectory + 1)
    end
    if name == nil then
        return
    end
    -- every option at UAL's default, then the ProfiLiner's; same for the loading area
    local config = {selectedConfigs = UniversalAutoload.ALL or "ALL"}
    for _, v in ipairs(UniversalAutoload.OPTIONS_DEFAULTS) do
        if v.id ~= nil then
            config[v.id] = v.default
        end
    end
    for k, v in pairs(BoxTruckBody.UAL_OPTIONS) do
        config[k] = v
    end
    local area = {}
    for _, v in ipairs(UniversalAutoload.LOADING_AREA_DEFAULTS) do
        if v.id ~= nil then
            area[v.id] = v.default
        end
    end
    for k, v in pairs(BoxTruckBody.UAL_LOADING_AREA) do
        area[k] = type(v) == "table" and {v[1], v[2], v[3]} or v
    end
    config.loadArea = {area}
    -- ours replaces whatever the settings file has for this truck (all configurations)
    UniversalAutoload.VEHICLE_CONFIGURATIONS[name] = {[config.selectedConfigs] = config}
    Logging.info("Box Truck: Universal Autoload set up like the Krone ProfiLiner for '%s'", name)
end

-- a curtain counts as open once it is fully open (as the ProfiLiner's tip state)
function BoxTruckBody.getIsPartFullyOpen(vehicle, animName)
    return vehicle:getAnimationExists(animName) and vehicle:getAnimationTime(animName) > 0.99
        and not vehicle:getIsAnimationPlaying(animName)
end

function BoxTruckBody:getTipState()
    local open = BoxTruckBody.getIsPartFullyOpen(self, "boxCurtainLeft") or BoxTruckBody.getIsPartFullyOpen(self, "boxCurtainRight")
    if open then
        return Trailer ~= nil and Trailer.TIPSTATE_OPEN or 2
    end
    return Trailer ~= nil and Trailer.TIPSTATE_CLOSED or 0
end

function BoxTruckBody:getIsRearDoorOpen()
    return BoxTruckBody.getIsPartFullyOpen(self, "boxRearDoors")
end

-- server: which sides Universal Autoload may use; its own functions send the change to the other players.
-- Loading (UAL's load side picks the pallets by which side of the truck they stand on): both curtains open = both
-- sides, one open = that side, only the rear doors open = "both" (UAL's side triggers stay shut while the curtains
-- are closed, so only the rear one picks up), all closed = none. Until 1.0.2.0 both curtains open meant "left" only:
-- the right side could not load (user, 2026-10-24).
-- Unloading (UAL unloads to one side): the open curtain; both open = the one opened last; none = nowhere.
function BoxTruckBody.updateUalTipside(vehicle)
    local spec = vehicle[BoxTruckBody.SPEC_TABLE_NAME]
    local ual = vehicle.spec_universalAutoload
    local UniversalAutoload = BoxTruckBody.getUal(vehicle)
    if not ual.isAutoloadAvailable or ual.autoloadDisabled or UniversalAutoload == nil
        or UniversalAutoload.setCurrentTipside == nil or UniversalAutoload.setCurrentLoadside == nil then
        return
    end
    local leftOpen = BoxTruckBody.getIsPartFullyOpen(vehicle, "boxCurtainLeft")
    local rightOpen = BoxTruckBody.getIsPartFullyOpen(vehicle, "boxCurtainRight")
    -- remember the curtain opened last (a saved game with both open starts with the left)
    if leftOpen and not spec.ualLeftOpen then
        spec.ualLastOpened = "left"
    end
    if rightOpen and not spec.ualRightOpen then
        spec.ualLastOpened = (leftOpen and spec.ualLeftOpen == nil) and "left" or "right"
    end
    spec.ualLeftOpen, spec.ualRightOpen = leftOpen, rightOpen

    local tipside, loadside = "none", "none"
    if leftOpen and rightOpen then
        tipside, loadside = spec.ualLastOpened or "left", "both"
    elseif leftOpen then
        tipside, loadside = "left", "left"
    elseif rightOpen then
        tipside, loadside = "right", "right"
    elseif BoxTruckBody.getIsPartFullyOpen(vehicle, "boxRearDoors") then
        loadside = "both"
    end
    if ual.currentTipside ~= tipside then
        UniversalAutoload.setCurrentTipside(vehicle, tipside)
    end
    if ual.currentLoadside ~= loadside then
        UniversalAutoload.setCurrentLoadside(vehicle, loadside)
    end
end

function BoxTruckBody.updateActionTexts(vehicle)
    local spec = vehicle[BoxTruckBody.SPEC_TABLE_NAME]
    for _, part in ipairs(spec.parts) do
        if part.actionEventId ~= nil then
            local isOpen = BoxTruckBody.getIsOpen(vehicle, part)
            g_inputBinding:setActionEventText(part.actionEventId, isOpen and part.closeText or part.openText)
        end
    end
    local curtain = spec.curtains[spec.curtainIndex]
    if spec.curtainEventId ~= nil and curtain ~= nil then
        local isOpen = BoxTruckBody.getIsOpen(vehicle, curtain)
        g_inputBinding:setActionEventText(spec.curtainEventId, isOpen and curtain.closeText or curtain.openText)
    end
    if spec.selectEventId ~= nil and curtain ~= nil then
        local other = spec.curtains[spec.curtainIndex % #spec.curtains + 1]
        g_inputBinding:setActionEventText(spec.selectEventId, other.selectText)
    end
end
