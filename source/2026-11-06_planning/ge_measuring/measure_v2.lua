-- dump the shed collision vertices above 1.5 m (barn-local), rounded to cm, de-duplicated
local W = "C:/Users/groov/GE_work/goatshed/"
local barn = loadI3DFile(W .. "barn/schafstall_big.i3d", false, false, false)
link(getRootNode(), barn)
local broot = getChildAt(barn, 0)
local shed = getChildAt(broot, 23)
local col = getChildAt(getChildAt(shed, 1), 0)
print("[GS2] node " .. getName(col))
local ok, n, v = pcall(getShapeVertexPositions, col)
print("[GS2] verts " .. tostring(n))
local seen, out = {}, {}
for i = 1, #v, 3 do
  local x, y, z = localToLocal(col, broot, v[i], v[i+1], v[i+2])
  if y > 1.5 then
    local k = string.format("%.2f %.2f %.2f", x, y, z)
    if not seen[k] then seen[k] = true; out[#out+1] = k end
    if #out == 40 then print("[GS2] " .. table.concat(out, ",")); out = {} end
  end
end
if #out > 0 then print("[GS2] " .. table.concat(out, ",")) end
print("[GS2] DONE")
