local function hide(n)
 for i=0,getNumOfChildren(n)-1 do local c=getChildAt(n,i)
  if getHasClassId(c,ClassIds.CAMERA) or getHasClassId(c,ClassIds.LIGHT_SOURCE) then setVisibility(c,false) end
  hide(c)
 end
end
hide(getChildAt(getRootNode(),0))
runtimePose(false,0,0);runtimeView(8,4,-12,0,2,-.7,38)
print('[FLATBED_QA] helper overlays hidden for final screenshots')
