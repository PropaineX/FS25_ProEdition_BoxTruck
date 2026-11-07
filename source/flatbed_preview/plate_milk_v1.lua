-- Review only: actual game assets fitted to scratch Volvo, no runtime changes.
local base='C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/FS25_BoxTruck_ProEdition/'
local data='G:/SteamLibrary/steamapps/common/Farming Simulator 25/data/'
local function find(n,name)
 if getName(n)==name then return n end
 for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name); if r then return r end end
end
if type(flatbedState)~='function' then source(base..'source/flatbed_preview/boot_v1.lua') end
local comp=find(getRootNode(),'fh16_main_component1')
if not find(getRootNode(),'Rear underrun round tube') then
 local tube=loadI3DFile(base..'previews/flatbed_round_underrun_v1/roundTube.i3d',false,false,false)
 link(comp,tube); setVisibility(find(comp,'Rear underrun beam'),false)
end
source(base..'source/flatbed_preview/hide_donor_lamps_v2.lua')
local mount=find(comp,'licensePlateBack')
local px,py,pz=localToLocal(mount,comp,0,0,0)
print(string.format('[PLATE_MILK] inherited_plate_center %.6f %.6f %.6f',px,py,pz))
local plateFile=loadI3DFile(data..'maps/mapEU/licensePlates/licensePlatesPL.i3d',false,false,false)
local plate=getChildAt(plateFile,0)
PLATEREVIEW=createTransformGroup('Flatbed_proposed_rear_plate_mount'); link(comp,PLATEREVIEW)
setTranslation(PLATEREVIEW,0,.985,-5.405); setRotation(PLATEREVIEW,0,math.pi,0)
link(PLATEREVIEW,plate); setTranslation(plate,0,0,0); setRotation(plate,0,0,0); delete(plateFile)
print('[PLATE_MILK] proposed_plate_center 0 0.985 -5.405; full framed plate 0.53 x 0.13 m; plate rear lamp-bar gap >=0.345m per side')
flatbedState('boards',false)
flatbedView(2,1.5,-9,0,.95,-5.3,30)

function buildMilkReview()
 MILKREVIEW=createTransformGroup('Flatbed_milk_load_review_20_pallets'); link(comp,MILKREVIEW)
 local source=loadI3DFile(data..'objects/pallets/goatMilkCanPallet/goatMilkCanPallet.i3d',false,false,false)
 local pallet=getChildAt(source,0)
 local woodFile=loadI3DFile(data..'objects/pallets/shared/euroPallet/euroPallet.i3d',false,false,false)
 local wood=getChildAt(woodFile,0); link(pallet,wood); setTranslation(wood,0,0,0); delete(woodFile)
 for layer=0,1 do
  for row=0,4 do
   for side=0,1 do
    local p=clone(pallet,true,false,false); link(MILKREVIEW,p)
    setName(p,string.format('Milk pallet layer%d row%d side%d',layer+1,row+1,side+1))
    setTranslation(p,side==0 and -.475 or .475,1.625+layer*.98,.675-row*1.30)
    setRotation(p,0,math.pi/2,0)
   end
  end
 end
 delete(source)
 print('[PLATE_MILK] loaded 20 real goat-milk pallets: 2 across x5 rows x2 layers; bottom y1.625 upper y2.605 root; layer pitch0.98m')
 print('[PLATE_MILK] visual lid top expected3.685root /3.385above-ground; lid/upper-pallet overlap requires gameplay review')
 flatbedState('stakes',false)
 flatbedView(9,5,-13,0,2.3,-.6,38)
end

function measureMilkReview()
 local b={1e9,-1e9,1e9,-1e9,1e9,-1e9}
 local function walk(n)
  local name=getName(n)
  if getHasClassId(n,ClassIds.SHAPE) and name~='col' and name~='fillTrigger' and name~='dynamicMountTrigger' and name~='tensionBeltMesh' and not string.find(name,'floorCollision') and not string.find(name,'Milk pallet layer') then
   local ok,count,v=pcall(getShapeVertexPositions,n)
   if ok and type(v)=='table' then for j=1,#v,3 do
    local x,y,z=localToLocal(n,comp,v[j],v[j+1],v[j+2]); b[1]=math.min(b[1],x);b[2]=math.max(b[2],x);b[3]=math.min(b[3],y);b[4]=math.max(b[4],y);b[5]=math.min(b[5],z);b[6]=math.max(b[6],z)
   end end
  end
  for i=0,getNumOfChildren(n)-1 do walk(getChildAt(n,i)) end
 end
 walk(MILKREVIEW)
 print(string.format('[PLATE_MILK] visual_load_bounds_root x%.4f..%.4f y%.4f..%.4f z%.4f..%.4f',unpack(b)))
end
print('[PLATE_MILK] plate preview ready; milk builder available')
