require "math"
require "os"

local selection_tool = require("tools.selection")
local selection_util = require("selections")
local siu = require("selection_item_utils")
local state = require("loaded_state")

local script = {
    name = "export spinners",
    displayName = "Export Spinners",
    tooltip = "Export spinners",
    parameters = {
        outfile = "",
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
        for _,entity in ipairs(room.entities) do
            if entity._name == "eow/InvisibleSpinner" then
--                entity.x = entity.x+offset_x
--                entity.y = entity.y+offset_y
                io.write(string.format("{\"x\": %f, \"y\": %f, \"eid\": %i, \"color\":\"%s\"},", 
                    entity.x+room.x, entity.y+room.y, entity._id, entity.color
                    ))
            end

        end
    end
    file:close()

end

return script
