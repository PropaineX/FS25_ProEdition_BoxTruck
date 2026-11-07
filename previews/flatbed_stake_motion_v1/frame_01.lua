local function find(n,name) if getName(n)==name then return n end for i=0,getNumOfChildren(n)-1 do local r=find(getChildAt(n,i),name);if r then return r end end end
local n=find(getRootNode(),"Stake -1 1"); assert(n,"stake missing"); setTranslation(n,-1.23000000,1.62000000,-5.01928571)
local n=find(getRootNode(),"Stake -1 3"); assert(n,"stake missing"); setTranslation(n,-1.23000000,1.62000000,-2.47928571)
local n=find(getRootNode(),"Stake -1 5"); assert(n,"stake missing"); setTranslation(n,-1.23000000,1.62000000,0.06071429)
local n=find(getRootNode(),"Stake 1 1"); assert(n,"stake missing"); setTranslation(n,1.23000000,1.62000000,-5.01928571)
local n=find(getRootNode(),"Stake 1 3"); assert(n,"stake missing"); setTranslation(n,1.23000000,1.62000000,-2.47928571)
local n=find(getRootNode(),"Stake 1 5"); assert(n,"stake missing"); setTranslation(n,1.23000000,1.62000000,0.06071429)