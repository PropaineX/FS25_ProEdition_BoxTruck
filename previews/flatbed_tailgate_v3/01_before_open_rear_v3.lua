assert(type(flatbedView)=='function','Fitted scene required')
if MILKREVIEW then setVisibility(MILKREVIEW,false) end
local function hideOld(n)
 if getName(n)=='Tailgate_30cm_proposal' then setVisibility(n,false) end
 for i=0,getNumOfChildren(n)-1 do hideOld(getChildAt(n,i)) end
end
hideOld(getRootNode())
flatbedState('boards',false)
flatbedView(3,2.7,-9,0,1.65,-4.7,36)
