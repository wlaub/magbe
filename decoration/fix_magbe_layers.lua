require "math"
require "os"

local selection_tool = require("tools.selection")
local selection_util = require("selections")
local siu = require("selection_item_utils")
local state = require("loaded_state")

local logging = require("logging")

local script = {
    name = "magbe layers fix",
    displayName = "Magbe layers fix",
    tooltip = "",
    parameters = {
        paddingggggggggggggggggggggggggg = false,
        },
    fieldInformation = {
        }
}

function do_it_to_it(texture, decal) 
    local target_depth
    if texture:find('iambad/magbe/gill/h') then
         target_depth=-90
    elseif texture:find('iambad/magbe/gill/') then
         target_depth=-1
    elseif texture:find('iambad/magbe/stem/h') then
         target_depth=-70
    elseif texture:find('iambad/magbe/stem/') then
         target_depth=10000
    elseif texture:find('iambad/magbe/spike/') then
         target_depth=-90
    elseif texture:find('iambad/magbe/tri/s') then
         target_depth=-80
    elseif texture:find('iambad/magbe/tri/') then
         target_depth=-70
    elseif texture:find('iambad/magbe/ball/') then
         target_depth=-80
    elseif texture:find('iambad/magbe/bgr/l') then
         target_depth=14000
    elseif texture:find('iambad/magbe/bgr/s') then
         target_depth=16000
    elseif texture:find('iambad/magbe/bgm/l') then
         target_depth=14000
    elseif texture:find('iambad/magbe/bgm/s') then
         target_depth=16000
    elseif texture:find('iambad/magbe/gmush/') then
         target_depth=-99
    end

    if target_depth ~= nil and target_depth < 12000 then
        if decal.depth == nil or decal.depth > target_depth or decal.depth < target_depth-8 then
            decal.depth = target_depth
        end
    end

end

function script.run(room, args)

    for _,decal in ipairs(room.decalsBg) do
        local texture = decal.texture
        do_it_to_it(texture, decal)
    end

    for _,decal in ipairs(room.entities) do
        if decal._name == 'eow/GlobalDecal' then
            local texture = decal.sprite
            do_it_to_it(texture, decal)
        end
    end



end

return script
