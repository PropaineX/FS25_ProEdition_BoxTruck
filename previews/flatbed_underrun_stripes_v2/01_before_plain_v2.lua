assert(type(flatbedView)=='function','Fitted scene required')
local function hideOld(n)
 if string.find(getName(n),'Reflective safety band') then setVisibility(n,false) end
 for i=0,getNumOfChildren(n)-1 do hideOld(getChildAt(n,i)) end
end
hideOld(getRootNode())
if MILKREVIEW then setVisibility(MILKREVIEW,false) end
flatbedState('boards',false)
flatbedView(2,1.5,-9,0,.95,-5.3,30)
