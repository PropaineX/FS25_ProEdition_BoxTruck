-- Preview only: tire assets from vehicle wheel configuration. Never save these nodes.
local WHEELS = {
  {node="wheelFrontLeft", isLeft=true, x=0, parts={
    {"$data/shared/wheels/tires/continental/contiHybridHT3/385_65R22_5.i3d","0|0",0.0,nil},
    {"$data/shared/wheels/rims/rim001.i3d","0|0",0.0,{12,22.5}},
    {"$data/shared/wheels/hubs/hubTrucks.i3d","6|0",0.07,{20,21}},
  }},
  {node="wheelFrontRight", isLeft=false, x=0, parts={
    {"$data/shared/wheels/tires/continental/contiHybridHT3/385_65R22_5.i3d","0|0",0.0,nil},
    {"$data/shared/wheels/rims/rim001.i3d","0|0",0.0,{12,22.5}},
    {"$data/shared/wheels/hubs/hubTrucks.i3d","6|1",0.07,{20,21}},
  }},
  {node="wheelBack01Left", isLeft=true, x=0, parts={
    {"$data/shared/wheels/tires/continental/contiHybridHD3/315_80R22_5.i3d","0|0",0.0,nil},
    {"$data/shared/wheels/rims/rim001.i3d","0|0",0.0,{9,22.5}},
  }},
  {node="wheelBack01Left", isLeft=true, x=0.3650, parts={
    {"$data/shared/wheels/tires/continental/contiHybridHD3/315_80R22_5.i3d","0|0",0.0,nil},
    {"$data/shared/wheels/rims/rim001.i3d","0|0",0.0,{9,22.5}},
    {"$data/shared/wheels/hubs/hubTrucks.i3d","5|0",-0.18,{21.1,21.1}},
  }},
  {node="wheelBack01Right", isLeft=false, x=0, parts={
    {"$data/shared/wheels/tires/continental/contiHybridHD3/315_80R22_5.i3d","0|0",0.0,nil},
    {"$data/shared/wheels/rims/rim001.i3d","0|0",0.0,{9,22.5}},
  }},
  {node="wheelBack01Right", isLeft=false, x=-0.3650, parts={
    {"$data/shared/wheels/tires/continental/contiHybridHD3/315_80R22_5.i3d","0|0",0.0,nil},
    {"$data/shared/wheels/rims/rim001.i3d","0|0",0.0,{9,22.5}},
    {"$data/shared/wheels/hubs/hubTrucks.i3d","5|1",-0.18,{21.1,21.1}},
  }},
  {node="wheelBack02Left", isLeft=true, x=0, parts={
    {"$data/shared/wheels/tires/continental/contiHybridHD3/315_80R22_5.i3d","0|0",0.0,nil},
    {"$data/shared/wheels/rims/rim001.i3d","0|0",0.0,{9,22.5}},
  }},
  {node="wheelBack02Left", isLeft=true, x=0.3650, parts={
    {"$data/shared/wheels/tires/continental/contiHybridHD3/315_80R22_5.i3d","0|0",0.0,nil},
    {"$data/shared/wheels/rims/rim001.i3d","0|0",0.0,{9,22.5}},
    {"$data/shared/wheels/hubs/hubTrucks.i3d","5|0",-0.18,{21.1,21.1}},
  }},
  {node="wheelBack02Right", isLeft=false, x=0, parts={
    {"$data/shared/wheels/tires/continental/contiHybridHD3/315_80R22_5.i3d","0|0",0.0,nil},
    {"$data/shared/wheels/rims/rim001.i3d","0|0",0.0,{9,22.5}},
  }},
  {node="wheelBack02Right", isLeft=false, x=-0.3650, parts={
    {"$data/shared/wheels/tires/continental/contiHybridHD3/315_80R22_5.i3d","0|0",0.0,nil},
    {"$data/shared/wheels/rims/rim001.i3d","0|0",0.0,{9,22.5}},
    {"$data/shared/wheels/hubs/hubTrucks.i3d","5|1",-0.18,{21.1,21.1}},
  }},
  {node="wheelBack03Left", isLeft=true, x=0, parts={
    {"$data/shared/wheels/tires/continental/contiHybridHT3/385_65R22_5.i3d","0|0",0.0,nil},
    {"$data/shared/wheels/rims/rim001.i3d","0|0",0.0,{12,22.5}},
    {"$data/shared/wheels/hubs/hubTrucks.i3d","6|0",0.07,{20,21}},
  }},
  {node="wheelBack03Right", isLeft=false, x=0, parts={
    {"$data/shared/wheels/tires/continental/contiHybridHT3/385_65R22_5.i3d","0|0",0.0,nil},
    {"$data/shared/wheels/rims/rim001.i3d","0|0",0.0,{12,22.5}},
    {"$data/shared/wheels/hubs/hubTrucks.i3d","6|1",0.07,{20,21}},
  }},
}
local function D(f) return (string.gsub(f, "%$data/", "G:/SteamLibrary/steamapps/common/Farming Simulator 25/data/")) end
local byName = {}
local function index(node)
    local n = getName(node)
    if byName[n] == nil then byName[n] = node end
    for i = 0, getNumOfChildren(node) - 1 do index(getChildAt(node, i)) end
end
index(getRootNode())
-- tyres and outer rims
local function child(root, path)
    local n = root
    for idx in string.gmatch(path, "%d+") do n = getChildAt(n, tonumber(idx)) end
    return n
end
local function setParamRec(node, name, x, y)
    if getHasClassId(node, ClassIds.SHAPE) and getHasShaderParameter(node, name) then
        setShaderParameter(node, name, x, y, nil, nil, false, -1)
    end
    for i = 0, getNumOfChildren(node) - 1 do setParamRec(getChildAt(node, i), name, x, y) end
end
local function hasParamRec(node, name)
    if getHasClassId(node, ClassIds.SHAPE) and getHasShaderParameter(node, name) then return true end
    for i = 0, getNumOfChildren(node) - 1 do
        if hasParamRec(getChildAt(node, i), name) then return true end
    end
    return false
end
-- WheelVisualPart:setNode: offset along x (mirrored on the right), widthAndDiam as shader parameter or as scale
local function part(p, linkNode, isLeft)
    local root = loadI3DFile(D(p[1]), false, false, false)
    local n = child(root, p[2])
    link(linkNode, n)
    setTranslation(n, p[3] * (isLeft and 1 or -1), 0, 0); setRotation(n, 0, 0, 0)
    local wd = p[4]
    if wd then
        if hasParamRec(n, "widthAndDiam") then
            setParamRec(n, "widthAndDiam", wd[1], wd[2])
        else
            setScale(n, wd[1] * 0.0254, wd[2] * 0.0254, wd[2] * 0.0254)
        end
    end
    delete(root)
end
local partCount = 0
for _, w in ipairs(WHEELS) do
    local ln = byName[w.node]
    if ln == nil then print("[MOCK] missing wheel node " .. w.node) else
        local vw = createTransformGroup("visualWheel"); link(ln, vw); excludeFromSave(vw,true)
        setTranslation(vw, w.x, 0, 0)
        for _, p in ipairs(w.parts) do part(p, vw, w.isLeft); partCount = partCount + 1 end
    end
end
print("[MOCK] wheel parts " .. partCount)

