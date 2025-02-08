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


function dump(o)
   if type(o) == 'table' then
      local s = '{ '
      for k,v in pairs(o) do
         if type(k) ~= 'number' then k = '"'..k..'"' end
         s = s .. '['..k..'] = ' .. dump(v) .. ','
      end
      return s .. '} '
   else
      return tostring(o)
   end
end


function do_it(room, entity)
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

    selection = selection_tool.getSelectionTargets() 
    for _, entity in ipairs(selection) do
        if entity.layer == "decalsBg" then
            item = entity.item
            if item.depth == nil then
                item.depth = 9000
            end
            do_it(room, entity)
        elseif entity.layer == "decalsFg" then
            item = entity.item
            if item.depth == nil then
                item.depth = -10501
            end
            do_it(room, entity)
        end

    end
    selection_util.redrawTargetLayers(room, selection)



end

return script
