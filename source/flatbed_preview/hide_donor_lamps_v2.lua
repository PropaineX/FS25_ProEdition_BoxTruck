-- Scratch preview only: the flatbed has its own rear light bar.
local function hideDonor(n)
 if getName(n)=='backlights' then setVisibility(n,false) end
 for i=0,getNumOfChildren(n)-1 do hideDonor(getChildAt(n,i)) end
end
hideDonor(getRootNode())
print('[FLATBED] donor rear lamps hidden in scratch preview')
