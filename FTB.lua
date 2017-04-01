local component = require("component")
local rs = component.redstone
local event = require("event")
local gpu = component.gpu

rs.setOutput(3,15)

while true do
  gpu.setResolution(40,10)
  gpu.fill(1,1,40,10, " ")
  type, _, x, y, z, nick = event.pull("touch")
  if nick == "sh0xx" then
    gpu.setForeground(0xFFFFCC)
    gpu.set(20,5, "Access granted")
    rs.setOutput(3,0)
    os.sleep(1.5)
    rs.Setoutput(3,15)
   else
    gpu.setForeground(0xFF0033)
    gpu.set(20,5,"Access denied")
    os.sleep(1.5)
   end
  end
