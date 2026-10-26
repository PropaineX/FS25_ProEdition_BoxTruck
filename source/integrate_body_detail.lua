-- Run once in GIANTS Editor with the STAGED boxTruck.i3d open, then save.
-- New nodes are appended: existing vehicle XML index paths remain stable.
local function find(n, name)
    if getName(n) == name then return n end
    for i=0,getNumOfChildren(n)-1 do
        local v=find(getChildAt(n,i),name)
        if v then return v end
    end
end
local body=find(getRootNode(),'boxBody')
assert(body, 'Missing boxBody')
local targets={
    bodyDetailStaticRails='boxBody', bodyDetailStaticFasteners='boxBody',
    bodyDetailCurtainLeftHardware='curtainLeftClosed',bodyDetailCurtainLeftKeepers='curtainLeftClosed',
    bodyDetailCurtainRightHardware='curtainRightClosed',bodyDetailCurtainRightKeepers='curtainRightClosed',
    bodyDetailCurtainLeftCloth='curtainLeftClosed',bodyDetailCurtainRightCloth='curtainRightClosed',
    bodyDetailDoorLeftSeals='rearDoorLeft',bodyDetailDoorRightSeals='rearDoorRight'
}
for name,_ in pairs(targets) do
    local old=find(body,name)
    if old then delete(old) end
end
local file=BODY_DETAIL_SOURCE
assert(file and file~='', 'Set BODY_DETAIL_SOURCE to staging bodyDetail.i3d path before running')
local imported=loadI3DFile(file,false,false,false)
assert(imported and imported~=0, 'Could not load detail meshes')
local count=0
while getNumOfChildren(imported)>0 do
    local node=getChildAt(imported,0)
    local name=getName(node)
    local parent=find(body,assert(targets[name],'Unexpected detail mesh '..name))
    assert(parent, 'Missing parent for '..name)
    local tx,ty,tz=localToLocal(body,parent,0,0,0)
    -- Body/closed curtains/closed doors share orientation; translation offsets differ.
    link(parent,node)
    setTranslation(node,tx,ty,tz)
    setRotation(node,0,0,0)
    count=count+1
end
delete(imported)
assert(count==10,'Expected ten grouped meshes')
-- Replace block-shaped buckle visuals with open, rounded metal frames.
for _,side in ipairs({'Left','Right'}) do
    setVisibility(find(body,'curtain'..side..'Buckles'),false)
    setVisibility(find(body,'curtain'..side..'Cloth'),false)
end
print('[BODY_DETAIL] Integrated '..count..' grouped visual meshes; ready to save')
