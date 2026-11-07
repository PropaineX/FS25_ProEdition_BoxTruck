"""Exercise scripts/ProEditionStoreCategory.lua with a stub StoreManager (not the game).

Checks: the tile is registered when this mod's first store item loads (not before), beside Winston9587's
tile when his section exists, otherwise in our own PropaineX section; base-game items don't trigger it;
it registers once per map load.
Run: python -I source/test_store_category.py   (needs .local/lua-test-runtime)
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.local/lua-test-runtime'))
from lupa import LuaRuntime

STUBS = r'''
g_currentModDirectory = 'C:/mods/BT/'
g_currentModName = 'BT'
g_i18n = {convertText = function(self, t) return t end}
Utils = {overwrittenFunction = function(old, new) return function(self, ...) return new(self, old, ...) end end}
local DATA = {
  ['modDesc.storeCategories.storeType'] = {{name = 'PROPAINEX', title = 'PropaineX Pro Edition'}},
  ['modDesc.storeCategories.storeCategory'] = {{name = 'PROEDITIONTRUCKS', title = 'Pro Edition Trucks', image = 'store_boxTruck.dds', type = 'PROPAINEX'}},
}
XMLFile = {load = function()
  return {
    iterator = function(self, path)
      local i = 0
      return function() i = i + 1; if DATA[path][i] then return i, {path, i} end end
    end,
    getString = function(self, key)
      local base, attr = key[1], nil
      return nil
    end,
    delete = function() end,
  }
end}
-- keys are tables; the script does key .. "#name", so give keys a concat metamethod
local keymt = {__concat = function(k, s) return {k[1], k[2], s} end}
local load = XMLFile.load
XMLFile.load = function()
  local x = load()
  local it = x.iterator
  x.iterator = function(self, path)
    local f = it(self, path)
    return function() local i, k = f(); if i then return i, setmetatable(k, keymt) end end
  end
  x.getString = function(self, k) return DATA[k[1]][k[2]][string.sub(k[3], 2)] end
  return x
end
log = {}
StoreManager = {categoryTypesByName = {}, cats = {},
  loadMapData = function(self) return true end,
  loadItem = function(self, file, baseDir, env) table.insert(log, 'item ' .. file .. ' tile=' .. tostring(self.cats.PROEDITIONTRUCKS)); return true end,
  loadCategoryType = function(self) table.insert(log, 'own section'); self.categoryTypesByName.PROPAINEX = {} end,
  loadCategoryFromXML = function(self) table.insert(log, 'own tile'); self.cats.PROEDITIONTRUCKS = 'PROPAINEX' end,
  addCategory = function(self, name, title, image, typ, dir, after)
    table.insert(log, table.concat({'beside', typ, 'after', after, title, image, dir}, ' ')); self.cats[name] = typ end,
  getCategoryByName = function(self, n) return self.cats[n] end,
}
'''

def run(winston):
    lua = LuaRuntime()
    lua.execute(STUBS)
    lua.execute((ROOT / 'scripts/ProEditionStoreCategory.lua').read_text(encoding='utf-8'))
    lua.execute('StoreManager:loadMapData()')
    if winston:  # Winston's own loadMapData hook runs after ours (mod load order)
        lua.execute('StoreManager.categoryTypesByName.WINSTON9587MODS = {}')
    lua.execute('''
      StoreManager:loadItem("data/base.xml", "", nil)
      StoreManager:loadItem("boxTruck.xml", "C:/mods/BT/", "BT")
      StoreManager:loadItem("flatbedTruck.xml", "C:/mods/BT/", "BT")''')
    return list(lua.eval('log').values())

w = run(True)
assert w == ['item data/base.xml tile=nil',
             'beside WINSTON9587MODS after WINSTON9587MODS Pro Edition Trucks store_boxTruck.dds C:/mods/BT/',
             'item boxTruck.xml tile=WINSTON9587MODS', 'item flatbedTruck.xml tile=WINSTON9587MODS'], w
n = run(False)
assert n == ['item data/base.xml tile=nil', 'own section', 'own tile',
             'item boxTruck.xml tile=PROPAINEX', 'item flatbedTruck.xml tile=PROPAINEX'], n
print('PASS store tile: beside Winston9587 when his section exists, own PropaineX section otherwise; registered once, before our first item, not on base items')
