-- Box Truck Pro Edition (PropaineX)
-- Opens and closes the curtain-sider body: rear barn doors, left curtain, right curtain.
-- The movements are animations in the vehicle XML (boxRearDoors, boxCurtainLeft, boxCurtainRight); playAnimation
-- already sends them to the other players. This spec adds the keys, saves the positions and sends them to players
-- who join later.
-- Keys (game actions, can be changed in the controls menu): X (IMPLEMENT_EXTRA2) = rear doors,
-- Z (IMPLEMENT_EXTRA4) = open/close the selected curtain, U (TOGGLE_TIPSIDE, as on the Krone ProfiLiner) = select
-- the left or right curtain. (v1 had the left curtain on Y; Y is taken by other actions in the game.)

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
