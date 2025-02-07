require "math"
require "os"

local selection_tool = require("tools.selection")
local selection_util = require("selections")
local siu = require("selection_item_utils")
local state = require("loaded_state")

local logging = require("logging")

local script = {
    name = "decal to global",
    displayName = "Decal to Global",
    tooltip = "",
    parameters = {
        paddinggggggggggggggggggggggggggggggggg = false,
        },
    fieldInformation = {
        }
}


function script.run(room, args)

    selection = selection_tool.getSelectionTargets() 
    for _, entity in ipairs(selection) do
        if entity.layer == "decalsBg" then
            entity.layer = 'entities'
            entity._name = 'eow/GlobalDecal'
            entity.sprite = entity.texture
            if entity.depth == nil then
                entity.depth = -10501
            end
            for i,v in pairs(room.decalsBg) do
                if v == entity then
                    table.remove(room.decalsBg, i)
            end
            table.insert(room.entities,0)
        logging.info(entity._name .. ' ' .. entity.layer)

        end
    end
    selection_util.redrawTargetLayers(room, selection)



end

return script
