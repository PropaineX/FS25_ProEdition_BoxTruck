-- PropaineX flatbed: optional Universal Autoload default loading area.
-- X (side walls + tailgate, or stakes) uses the game's Foldable specialization; this script handles no keys.
FlatbedBody = {}
FlatbedBody.MOD_NAME = g_currentModName
FlatbedBody.SPEC_NAME = g_currentModName .. ".flatbedBody"

function FlatbedBody.prerequisitesPresent(specializations)
    return true
end

function FlatbedBody.initSpecialization()
    -- Kept so saves from 1.4.0.0 (separate tailgate key) still validate; the value is no longer used.
    Vehicle.xmlSchemaSavegame:register(XMLValueType.BOOL,
        "vehicles.vehicle(?)." .. FlatbedBody.SPEC_NAME .. "#tailgateOpen", "Unused since 1.4.0.1", false)
end

function FlatbedBody.registerEventListeners(vehicleType)
    SpecializationUtil.registerEventListener(vehicleType, "onPreLoad", FlatbedBody)
end

function FlatbedBody.getUal(self)
    for i, class in pairs(self.specializations or {}) do
        local name = (self.specializationNames or {})[i]
        if type(name) == "string" and name:sub(-#".universalAutoload") == ".universalAutoload" then return class end
    end
end

function FlatbedBody:onPreLoad(savegame)
    local ual = FlatbedBody.getUal(self)
    if ual == nil or ual.VEHICLE_CONFIGURATIONS == nil or ual.OPTIONS_DEFAULTS == nil or ual.LOADING_AREA_DEFAULTS == nil then return end
    local name = self.configFileName
    if type(name) ~= "string" then return end
    if g_modsDirectory ~= nil and name:sub(1, #g_modsDirectory) == g_modsDirectory then name = name:sub(#g_modsDirectory + 1) end
    -- Never replace ANY saved config group, including a shop opt-out/custom area.
    if ual.VEHICLE_CONFIGURATIONS[name] ~= nil then return end
    local config = {selectedConfigs = ual.ALL or "ALL"}
    for _, item in ipairs(ual.OPTIONS_DEFAULTS) do if item.id ~= nil then config[item.id] = item.default end end
    local area = {}
    for _, item in ipairs(ual.LOADING_AREA_DEFAULTS) do if item.id ~= nil then area[item.id] = item.default end end
    -- Stakes project inward from the deck edge; use their clear width for both bodies.
    area.offset, area.width, area.length, area.height = {0, 1.625, -1.925}, 2.38, 6.70, 2.20
    config.loadArea = {area}
    ual.VEHICLE_CONFIGURATIONS[name] = {[config.selectedConfigs] = config}
end
