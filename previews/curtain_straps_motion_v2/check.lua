if SHAPE_PREVIEW then delete(SHAPE_PREVIEW) end
local root=getRootNode()
for i=0,getNumOfChildren(root)-1 do local n=getChildAt(root,i); if getName(n):sub(1,8)=='gathered' then setVisibility(n,false) end end
SHAPE_PREVIEW=loadI3DFile(assert(SHAPE_ASSET,"Set SHAPE_ASSET to the prepared preview asset"),false,false,false)
link(root,SHAPE_PREVIEW)
for i=0,getNumOfChildren(SHAPE_PREVIEW)-1 do
 local g=getChildAt(SHAPE_PREVIEW,i)
 setVisibility(g,getName(g)=='gatheredLeft1' or getName(g)=='previewSun')
 for j=0,getNumOfChildren(g)-1 do local n=getChildAt(g,j); setVisibility(n,getName(n)=='cloth' or getName(n)=='ProEdition' or getName(n)=='whiteInnerLining' or getName(n)=='curtainBand' or getName(n)=='curtainStraps' or getName(n)=='curtainBuckles'); setShaderParameter(n,'curtainShape',.5,.5,0,0,false) end
end
SHAPE_CAMERA=createCamera('shapeMotionCamera',math.rad(45),.05,500)
link(root,SHAPE_CAMERA)
setTranslation(SHAPE_CAMERA,11,3.0,3.36)
setDirection(SHAPE_CAMERA,1,0,0,0,1,0)
setCamera(SHAPE_CAMERA)
print('[SHAPE CHECK] Closed geometry loaded')
