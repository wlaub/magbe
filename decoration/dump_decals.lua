require "math"
require "os"

local selection_tool = require("tools.selection")
local selection_util = require("selections")
local siu = require("selection_item_utils")
local state = require("loaded_state")

local script = {
    name = "dump decals",
    displayName = "Dump Decals",
    tooltip = "Dump decals",
    parameters = {
        outfile = "decal_dump.txt",
        },
    fieldInformation = {
        oufile = {
            fieldType = "loennScripts.directFilepath",
            extension = "*"
            }
        }
}

function script.prerun(args)

    local file = io.open(args.outfile, "w")
    io.output(file)
 
    for _,room in ipairs(state.map.rooms) do
        for _,decal in ipairs(room.decalsFg) do
            io.write(string.format("FG %s %s\n",decal.texture, room.name))
        end
        for _,decal in ipairs(room.decalsBg) do
            io.write(string.format("BG %s %s\n",decal.texture, room.name))
        end
        for _,decal in ipairs(room.entities) do
            if decal._name == 'eow/GlobalDecal' then
            io.write(string.format("BG %s %s\n","decals/"..decal.sprite, room.name))
            end
        end
    end

end

return script
