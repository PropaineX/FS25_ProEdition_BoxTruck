assert(type(flatbedView)=='function','Fitted scene required')
if MILKREVIEW then setVisibility(MILKREVIEW,false) end
local function hideGate(n)
 if getName(n)=='Tailgate_30cm_proposal' then setVisibility(n,false) end
 for i=0,getNumOfChildren(n)-1 do hideGate(getChildAt(n,i)) end
end
hideGate(getRootNode())
flatbedState('stakes',false)
flatbedView(12,3.4,-.5,0,2,-.5,34)
print('[STAKE_MOTION] native XML channels sampled; 0.7s full travel')
