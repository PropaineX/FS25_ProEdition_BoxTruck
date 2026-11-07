-- Goat milk shed vs Box Truck: measure heights from the real meshes (scratch copies only).
-- Output: "[GS]" lines in editor_log.txt
local W = "C:/Users/groov/GE_work/goatshed/"

local function shapeVerts(s, ref)
  local ok, n, v = pcall(getShapeVertexPositions, s)
  if not ok or not n or n == 0 or type(v) ~= "table" then return nil end
  local out = {}
  for i = 1, #v, 3 do
    local x, y, z = localToLocal(s, ref, v[i], v[i+1], v[i+2])
    out[#out+1] = {x, y, z}
  end
  return out
end

local function walk(node, fn, path)
  for i = 0, getNumOfChildren(node) - 1 do
    local c = getChildAt(node, i)
    local p = path .. "/" .. getName(c)
    if getHasClassId(c, ClassIds.SHAPE) then fn(c, p) end
    walk(c, fn, p)
  end
end

local function bbox(vs)
  local b = {1e9, -1e9, 1e9, -1e9, 1e9, -1e9}
  for _, p in ipairs(vs) do
    b[1] = math.min(b[1], p[1]); b[2] = math.max(b[2], p[1])
    b[3] = math.min(b[3], p[2]); b[4] = math.max(b[4], p[2])
    b[5] = math.min(b[5], p[3]); b[6] = math.max(b[6], p[3])
  end
  return b
end

local function pb(tag, name, b)
  print(string.format("[GS] %s %s | x %.3f..%.3f  y %.3f..%.3f  z %.3f..%.3f", tag, name, b[1], b[2], b[3], b[4], b[5], b[6]))
end

-- 1) BARN: the milk pallet shed (garageWoodRoof, node 0>23)
local barn = loadI3DFile(W .. "barn/schafstall_big.i3d", false, false, false)
link(getRootNode(), barn)
local broot = getChildAt(barn, 0)
local shed = getChildAt(broot, 23)
print("[GS] barn root " .. getName(broot) .. ", shed node " .. getName(shed))
walk(shed, function(s, p)
  local vs = shapeVerts(s, broot)
  if vs then
    pb("SHED", p, bbox(vs))
    -- lowest point above 1.5 m in 0.5 m cells (barn-local x,z): underside of roof / beams
    local cells = {}
    for _, q in ipairs(vs) do
      if q[2] > 1.5 then
        local k = string.format("%d,%d", math.floor(q[1] * 2), math.floor(q[3] * 2))
        if cells[k] == nil or q[2] < cells[k] then cells[k] = q[2] end
      end
    end
    local line = {}
    for k, y in pairs(cells) do
      line[#line+1] = k .. "=" .. string.format("%.2f", y)
      if #line == 60 then print("[GS] CELLS " .. getName(s) .. " | " .. table.concat(line, " ")); line = {} end
    end
    if #line > 0 then print("[GS] CELLS " .. getName(s) .. " | " .. table.concat(line, " ")) end
  end
end, getName(shed))

-- 2) PALLET
local pal = loadI3DFile(W .. "pallet/goatMilkCanPallet.i3d", false, false, false)
link(getRootNode(), pal)
local proot = getChildAt(pal, 0)
local all = {}
walk(proot, function(s, p)
  local vs = shapeVerts(s, proot)
  if vs then pb("PALLET", p, bbox(vs)); for _, q in ipairs(vs) do all[#all+1] = q end end
end, getName(proot))
if #all > 0 then pb("PALLET", "ALL", bbox(all)) end

-- 3) TRUCK: every shape whose top is above 3.0 m (truck root coords)
local trk = loadI3DFile(W .. "truck/boxTruck.i3d", false, false, false)
link(getRootNode(), trk)
local troot = getChildAt(trk, 0)
walk(troot, function(s, p)
  local vs = shapeVerts(s, troot)
  if vs then
    local b = bbox(vs)
    if b[4] > 3.0 then pb("TRUCK", p, b) end
  end
end, getName(troot))
print("[GS] DONE")
