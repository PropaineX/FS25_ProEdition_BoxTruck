local function find(n,name)
 if getName(n)==name then return n end
 for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name);if r then return r end end
end
local comp=find(getRootNode(),'fh16_main_component1')
local gate=loadI3DFile('C:/Users/groov/OneDrive/Documents/My Games/FarmingSimulator2025/MOD PROJECTS/FS25_BoxTruck_ProEdition/previews/flatbed_tailgate_v1/tailgatePreview.i3d',false,false,false)
assert(gate~=0,'Tailgate asset failed to load');link(comp,gate)
print('[TAILGATE] stainless diamond pattern, width2.37m height0.30m; shared rear gate fitted')
