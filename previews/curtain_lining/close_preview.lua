local function find(n,name) if getName(n)==name then return n end for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name) if r then return r end end end
setVisibility(find(getRootNode(),'curtainRightInnerLining'),true)
detailView(.85,2.8,.7,-1.2,2.8,-3.3,68)
