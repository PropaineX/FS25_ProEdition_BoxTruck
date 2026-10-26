-- Preview only, after saving production scene: cameras/lights are excluded from save.
local function find(n,name)
    if getName(n)==name then return n end
    for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name) if r then return r end end
end
local root=getRootNode()
local comp=find(root,'fh16_main_component1')
local function hide(n)
    for i=0,getNumOfChildren(n)-1 do
        local c=getChildAt(n,i)
        if getHasClassId(c,ClassIds.LIGHT_SOURCE) or getHasClassId(c,ClassIds.CAMERA) then setVisibility(c,false) end
        hide(c)
    end
end
hide(comp)
local oldLight=find(root,'bodyDetailStudioKey')
if oldLight then delete(oldLight) end
BODYDETAILCAM=createCamera('bodyDetailPreview',math.rad(40),.05,500)
link(root,BODYDETAILCAM);excludeFromSave(BODYDETAILCAM,true)
function detailView(px,py,pz,tx,ty,tz,fov)
    local wx,wy,wz=localToWorld(comp,px,py,pz)
    local ax,ay,az=localToWorld(comp,tx,ty,tz)
    setTranslation(BODYDETAILCAM,wx,wy,wz)
    setDirection(BODYDETAILCAM,wx-ax,wy-ay,wz-az,0,1,0)
    setFovY(BODYDETAILCAM,math.rad(fov or 40));setCamera(BODYDETAILCAM)
end
-- Keep custom lettering visible in preview only.
for _,name in ipairs({'curtainLeftProEdition','curtainRightProEdition','doorLeftProEdition','doorRightProEdition'}) do
    local n=find(comp,name) if n then setVisibility(n,true) end
end
detailView(9,3.7,-8.5,0,2.55,-1.4,42)
print('[BODY_DETAIL] Preview ready')
