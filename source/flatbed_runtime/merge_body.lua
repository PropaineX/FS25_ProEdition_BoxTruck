local function find(n,name)
 if getName(n)==name then return n end
 for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name);if r then return r end end
end
local root=getRootNode();local comp=find(root,'fh16_main_component1')
assert(comp,'Volvo main component missing')
local old=find(comp,'boxBody');assert(old,'Expected original box body');delete(old)
local file='C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/FS25_BoxTruck_ProEdition/source/flatbed_runtime/build/flatbedBody.i3d'
local imported=loadI3DFile(file,false,false,false);assert(imported~=0,'Runtime body import failed')
local body=getChildAt(imported,0);assert(getName(body)=='flatbedBody','Unexpected runtime body')
link(comp,body);setTranslation(body,0,0,0);setRotation(body,0,0,0);delete(imported)
-- Retain native rear real-light helpers; hide only obsolete donor lens meshes.
local backlights=find(comp,'backlights')
local function hideShapes(n)
 for i=0,getNumOfChildren(n)-1 do local c=getChildAt(n,i)
  if getHasClassId(c,ClassIds.SHAPE) then setVisibility(c,false) end
  hideShapes(c)
 end
end
if backlights then hideShapes(backlights) end
local plate=find(comp,'licensePlateBack');setTranslation(plate,0,.985,-5.405);setRotation(plate,0,math.pi,0)
clearSelection()
print('[FLATBED_RUNTIME] merged approved body, collisions,belts and native pivots; ready to save scratch file')
