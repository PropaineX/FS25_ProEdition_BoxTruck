local function find(n,name)
 if getName(n)==name then return n end
 for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name);if r then return r end end
end
local comp=find(getRootNode(),'fh16_main_component1')
local bands=loadI3DFile('C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/FS25_BoxTruck_ProEdition/previews/flatbed_underrun_stripes_v1/reflectiveBands.i3d',false,false,false)
assert(bands~=0,'Stripe asset failed to load');link(comp,bands)
print('[UNDERRUN_STRIPES] two0.48m red-white diagonal bands fitted; center plain; reflective behavior UNTESTED')
