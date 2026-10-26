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

local function find(n,name) if getName(n)==name then return n end for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name) if r then return r end end end
local root=getRootNode()
do local n=find(root,"curtainLeftClosed") if n then setScale(n,1,1,0.0744) end end
do local n=find(root,"curtainLeftClosed") if n then setVisibility(n,false) end end
do local n=find(root,"curtainLeftOpen") if n then setVisibility(n,true) end end
do local n=find(root,"colSideLeftPivot") if n then setTranslation(n,1.25,6.53,0) end end
do local n=find(root,"boardLeft04") if n then setTranslation(n,1.55,1.4,0.4) end end
do local n=find(root,"boardLeft04") if n then setRotation(n,math.rad(0),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft04") if n then setScale(n,1,1,0.42) end end
do local n=find(root,"boardLeft04") if n then setRotation(n,math.rad(90),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft04") if n then setTranslation(n,0.7614,1.3725,0.92) end end
do local n=find(root,"boardLeft08") if n then setTranslation(n,1.55,1.4,-1.85) end end
do local n=find(root,"boardLeft08") if n then setRotation(n,math.rad(0),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft08") if n then setScale(n,1,1,0.42) end end
do local n=find(root,"boardLeft08") if n then setRotation(n,math.rad(90),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft08") if n then setTranslation(n,0.7614,1.3725,0.76) end end
do local n=find(root,"boardLeft12") if n then setTranslation(n,1.55,1.4,-4.105) end end
do local n=find(root,"boardLeft12") if n then setRotation(n,math.rad(0),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft12") if n then setScale(n,1,1,0.42) end end
do local n=find(root,"boardLeft12") if n then setRotation(n,math.rad(90),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft12") if n then setTranslation(n,0.7614,1.3725,0.6) end end
do local n=find(root,"boardLeft03") if n then setTranslation(n,1.55,1.4,0.4) end end
do local n=find(root,"boardLeft03") if n then setRotation(n,math.rad(0),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft03") if n then setScale(n,1,1,0.42) end end
do local n=find(root,"boardLeft03") if n then setRotation(n,math.rad(90),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft03") if n then setTranslation(n,0.7614,1.3725,0.44) end end
do local n=find(root,"boardLeft07") if n then setTranslation(n,1.55,1.4,-1.85) end end
do local n=find(root,"boardLeft07") if n then setRotation(n,math.rad(0),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft07") if n then setScale(n,1,1,0.42) end end
do local n=find(root,"boardLeft07") if n then setRotation(n,math.rad(90),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft07") if n then setTranslation(n,0.7614,1.3725,0.28) end end
do local n=find(root,"boardLeft11") if n then setTranslation(n,1.55,1.4,-4.105) end end
do local n=find(root,"boardLeft11") if n then setRotation(n,math.rad(0),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft11") if n then setScale(n,1,1,0.42) end end
do local n=find(root,"boardLeft11") if n then setRotation(n,math.rad(90),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft11") if n then setTranslation(n,0.7614,1.3725,0.12) end end
do local n=find(root,"boardLeft02") if n then setTranslation(n,1.55,1.4,0.4) end end
do local n=find(root,"boardLeft02") if n then setRotation(n,math.rad(0),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft02") if n then setScale(n,1,1,0.42) end end
do local n=find(root,"boardLeft02") if n then setRotation(n,math.rad(90),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft02") if n then setTranslation(n,0.7614,1.3995,0.92) end end
do local n=find(root,"boardLeft06") if n then setTranslation(n,1.55,1.4,-1.85) end end
do local n=find(root,"boardLeft06") if n then setRotation(n,math.rad(0),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft06") if n then setScale(n,1,1,0.42) end end
do local n=find(root,"boardLeft06") if n then setRotation(n,math.rad(90),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft06") if n then setTranslation(n,0.7614,1.3995,0.76) end end
do local n=find(root,"boardLeft10") if n then setTranslation(n,1.55,1.4,-4.105) end end
do local n=find(root,"boardLeft10") if n then setRotation(n,math.rad(0),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft10") if n then setScale(n,1,1,0.42) end end
do local n=find(root,"boardLeft10") if n then setRotation(n,math.rad(90),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft10") if n then setTranslation(n,0.7614,1.3995,0.6) end end
do local n=find(root,"boardLeft01") if n then setTranslation(n,1.55,1.4,0.4) end end
do local n=find(root,"boardLeft01") if n then setRotation(n,math.rad(0),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft01") if n then setScale(n,1,1,0.42) end end
do local n=find(root,"boardLeft01") if n then setRotation(n,math.rad(90),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft01") if n then setTranslation(n,0.7614,1.3995,0.44) end end
do local n=find(root,"boardLeft05") if n then setTranslation(n,1.55,1.4,-1.85) end end
do local n=find(root,"boardLeft05") if n then setRotation(n,math.rad(0),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft05") if n then setScale(n,1,1,0.42) end end
do local n=find(root,"boardLeft05") if n then setRotation(n,math.rad(90),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft05") if n then setTranslation(n,0.7614,1.3995,0.28) end end
do local n=find(root,"boardLeft09") if n then setTranslation(n,1.55,1.4,-4.105) end end
do local n=find(root,"boardLeft09") if n then setRotation(n,math.rad(0),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft09") if n then setScale(n,1,1,0.42) end end
do local n=find(root,"boardLeft09") if n then setRotation(n,math.rad(90),math.rad(0),math.rad(90)) end end
do local n=find(root,"boardLeft09") if n then setTranslation(n,0.7614,1.3995,0.12) end end
do local n=find(root,"postLeft2") if n then setRotation(n,math.rad(0),math.rad(0),math.rad(0.65)) end end
do local n=find(root,"postLeft2") if n then setTranslation(n,1.22,1.75,-5.05) end end
do local n=find(root,"postLeft1") if n then setRotation(n,math.rad(0),math.rad(0),math.rad(0.65)) end end
do local n=find(root,"postLeft1") if n then setTranslation(n,1.22,1.75,-4.91) end end
detailView(4.1,3.0,-0.1,-1.22,2.85,-2.0,66)
