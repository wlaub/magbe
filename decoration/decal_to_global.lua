require "math"
require "os"

local selection_tool = require("tools.selection")
local selection_util = require("selections")
local siu = require("selection_item_utils")
local state = require("loaded_state")
local pu = require("placement_utils")
local entities = require("entities")

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

function do_it_global(room, entity)
    local item = entity.item
    local sprite = item.texture
    sprite = string.sub(sprite, 8)

    local itemTemplate = {
        _name = "eow/GlobalDecal",
        sprite = sprite,
        x = item.x,
        y = item.y,
        scaleX = item.scaleX,
        scaleY = item.scaleY,
        rotation = item.rotation,
        color = item.color,
        depth = item.depth,
        flag = "",
        }

    pu.placeItem(room, 'entities', itemTemplate)
end

function script.run(room, args)

    local selection = selection_tool.getSelectionTargets() 
    for _, entity in ipairs(selection) do
        if entity.layer == "decalsBg" then
            local item = entity.item
            if item.depth == nil then
                item.depth = 9000
            end
            do_it_global(room, entity)
        elseif entity.layer == "decalsFg" then
            local item = entity.item
            if item.depth == nil then
                item.depth = -10501
            end
            do_it_global(room, entity)
        end

    end
    selection_util.redrawTargetLayers(room, selection)



end

return script
