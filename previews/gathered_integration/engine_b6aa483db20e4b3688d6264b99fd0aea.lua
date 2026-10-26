-- Preview-only: open production truck first; never save this scene.
local function find(n,name)
    if getName(n)==name then return n end
    for i=0,getNumOfChildren(n)-1 do local v=find(getChildAt(n,i),name) if v then return v end end
end
local root=getRootNode()
local comp=assert(find(root,'fh16_main_component1'))
local loaded=loadI3DFile(GATHERED_ASSET,false,false,false)
assert(loaded and loaded~=0)
for _,side in ipairs({'Left','Right'}) do
    local parent=assert(find(comp,'curtain'..side..'Open'))
    setVisibility(parent,true)
    setVisibility(assert(find(comp,'curtain'..side..'Closed')),false)
    for i=0,getNumOfChildren(parent)-1 do setVisibility(getChildAt(parent,i),false) end
    for v=1,3 do
        local group=assert(find(loaded,'gathered'..side..v))
        link(parent,group);setTranslation(group,0,0,0);setVisibility(group,v==1)
        for _,design in ipairs({'ProEdition','Krone','FSL','GIANTS'}) do setVisibility(assert(find(group,design)),design=='ProEdition') end
    end
end
delete(loaded)
GATHERED_PREVIEW_CAMERA=createCamera('gatheredPreview',math.rad(38),.05,500)
link(root,GATHERED_PREVIEW_CAMERA);excludeFromSave(GATHERED_PREVIEW_CAMERA,true)
local wx,wy,wz=localToWorld(comp,5.4,3.25,-3.5)
local tx,ty,tz=localToWorld(comp,1.32,2.85,-4.96)
setTranslation(GATHERED_PREVIEW_CAMERA,wx,wy,wz)
setDirection(GATHERED_PREVIEW_CAMERA,wx-tx,wy-ty,wz-tz,0,1,0)
setCamera(GATHERED_PREVIEW_CAMERA)
print('[GATHERED] Attached approved meshes to existing open pivots, exterior Pro Edition, opaque white interior')
