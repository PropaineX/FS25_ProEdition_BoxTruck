local root=getRootNode()
local function find(n,name)
 if getName(n)==name then return n end
 for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name); if r then return r end end
end
local comp=find(root,'fh16_main_component1')
local path='C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/FS25_BoxTruck_ProEdition/previews/flatbed_fitted_v1/flatbedPreview.i3d'
local body=loadI3DFile(path,false,false,false); link(comp,body); setTranslation(body,0,0,0)
local boards=find(body,'OPTION_BOARDS'); local stakes=find(body,'OPTION_STAKES')
function flatbedState(kind,opened)
 setVisibility(boards,kind=='boards'); setVisibility(stakes,kind=='stakes')
 local closed={-5.10,-3.83,-2.56,-1.29,-.02,1.25}; local paired={-3.97,-3.83,-1.43,-1.29,1.11,1.25}
 for _,s in ipairs({-1,1}) do
  for j=0,2 do local p=find(boards,'Board hinge '..s..' '..j); if p then setRotation(p,0,0,opened and math.rad(180*s) or 0) end end
  for j=1,6 do local p=find(stakes,'Stake '..s..' '..j); if p then local x,y,z=getTranslation(p); setTranslation(p,x,y,opened and paired[j] or closed[j]) end end
 end
end
local function hideHelpers(n)
 for i=0,getNumOfChildren(n)-1 do local c=getChildAt(n,i); if getHasClassId(c,ClassIds.LIGHT_SOURCE) or getHasClassId(c,ClassIds.CAMERA) then setVisibility(c,false) end; hideHelpers(c) end
end
hideHelpers(comp)
FLATCAM=createCamera('FlatbedReviewCamera',math.rad(38),.05,500); link(root,FLATCAM)
function flatbedView(px,py,pz,tx,ty,tz,fov)
 setTranslation(FLATCAM,px,py,pz); setDirection(FLATCAM,px-tx,py-ty,pz-tz,0,1,0); setFovY(FLATCAM,math.rad(fov or 38)); setCamera(FLATCAM); clearSelection()
end
flatbedState('boards',false); flatbedView(12,6,14,0,1.9,-.4,38)
print('[FLATBED] fitted preview ready')
