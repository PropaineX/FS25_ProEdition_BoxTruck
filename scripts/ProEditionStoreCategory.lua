-- PropaineX: registers the "Pro Edition Trucks" shop tile declared in modDesc <storeCategories>.
-- The game does not read that modDesc block on its own.
-- The tile goes beside Winston9587's tile (same row) when winston9587_StoreCategory is loaded (user, 2026-11-06);
-- otherwise it gets our own "PropaineX Pro Edition" section from modDesc.
-- It is registered when the store loads this mod's first item: mod items load in queued steps after every
-- mod's StoreManager.loadMapData hook has run, so Winston's section exists by then whatever the mod load order.
ProEditionStoreCategory = {}

local modDirectory = g_currentModDirectory
local modName = g_currentModName
local WINSTON_TYPE = "WINSTON9587MODS"
local WINSTON_TILE = "WINSTON9587MODS"

ProEditionStoreCategory.registered = false

local function register(storeManager)
    ProEditionStoreCategory.registered = true
    local xmlFile = XMLFile.load("proEditionStoreCategories", modDirectory .. "modDesc.xml")
    if xmlFile == nil then
        return
    end

    local besideWinston = storeManager.categoryTypesByName ~= nil and storeManager.categoryTypesByName[WINSTON_TYPE] ~= nil

    if not besideWinston then
        for _, key in xmlFile:iterator("modDesc.storeCategories.storeType") do
            local name = xmlFile:getString(key .. "#name")
            if name ~= nil and (storeManager.categoryTypesByName == nil or storeManager.categoryTypesByName[name:upper()] == nil) then
                storeManager:loadCategoryType(xmlFile, key, nil)
            end
        end
    end

    for _, key in xmlFile:iterator("modDesc.storeCategories.storeCategory") do
        local name = xmlFile:getString(key .. "#name")
        if name ~= nil and storeManager:getCategoryByName(name) == nil then
            if besideWinston then
                local title = g_i18n:convertText(xmlFile:getString(key .. "#title"), modName)
                storeManager:addCategory(name, title, xmlFile:getString(key .. "#image"), WINSTON_TYPE, modDirectory, WINSTON_TILE)
            else
                storeManager:loadCategoryFromXML(xmlFile, key, modDirectory, modName)
            end
        end
    end

    xmlFile:delete()
end

function ProEditionStoreCategory.loadMapData(storeManager, superFunc, ...)
    ProEditionStoreCategory.registered = false
    return superFunc(storeManager, ...)
end

function ProEditionStoreCategory.loadItem(storeManager, superFunc, rawXMLFilename, baseDir, customEnvironment, ...)
    if not ProEditionStoreCategory.registered and (customEnvironment == modName or baseDir == modDirectory) then
        register(storeManager)
    end
    return superFunc(storeManager, rawXMLFilename, baseDir, customEnvironment, ...)
end

StoreManager.loadMapData = Utils.overwrittenFunction(StoreManager.loadMapData, ProEditionStoreCategory.loadMapData)
StoreManager.loadItem = Utils.overwrittenFunction(StoreManager.loadItem, ProEditionStoreCategory.loadItem)
