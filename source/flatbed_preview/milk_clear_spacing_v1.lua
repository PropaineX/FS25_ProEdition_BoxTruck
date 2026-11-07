assert(MILKREVIEW,'Milk preview must be loaded first')
local changed=0
for i=0,getNumOfChildren(MILKREVIEW)-1 do
 local n=getChildAt(MILKREVIEW,i)
 if string.find(getName(n),'layer2') then
  local x,y,z=getTranslation(n); setTranslation(n,x,2.710,z); changed=changed+1
 end
end
assert(changed==10,'Expected ten upper-layer pallets')
flatbedState('stakes',false)
flatbedView(13,2.7,-.4,0,2.2,-.4,34)
measureMilkReview()
print('[PLATE_MILK] visual-only spacing alternative: upper tier y2.710, pitch1.085m, ten upper pallets raised0.105m; UAL behavior unchanged')
