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
        configure_magbe_sound_sources = false,
        },
    fieldInformation = {
        }
}

function script.run(room, args)

    local function do_it_to_it(decal) 

local texture = decal.layers
if texture:find('shroom') then
     local idx = tonumber(string.sub(texture, 7))
     decal.variant = idx/7
     decal.enable_flag = '!disable_shroom'
elseif texture:find('swoop') then
     local idx = tonumber(string.sub(texture, 6))
     decal.variant = idx/7
     decal.enable_flag = '!disable_swoop'
elseif texture:find('organ') then
     local idx = tonumber(string.sub(texture, 6))
     decal.variant = idx/7
     decal.enable_flag = '!disable_organ'
elseif texture:find('shard') then
     local idx = tonumber(string.sub(texture, 6))
     decal.variant = idx/9
     decal.enable_flag = '!disable_shard'
elseif texture:find('thorn') then
     local idx = tonumber(string.sub(texture, 6))
     decal.variant = idx/13
     decal.enable_flag = '!disable_thorn'
elseif texture:find('gd') then
     local idx = tonumber(string.sub(texture, 3))
     decal.variant = idx/10
     decal.enable_flag = '!disable_gd'
end




        if decal.lock then
            return
        end

        decal.lock = false
        if decal.enable_flag == nil then
            decal.enable_flag = ""
        end
        if decal.max_value == nil then
            decal.max_value = 1
        end


        local texture = decal.layers
        if texture:find('shroom') then
             decal.min_distance = 40
             decal.max_distance = 720
             
        elseif texture:find('swoop') then
             decal.min_distance = 40
             decal.max_distance = 720
        elseif texture:find('organ') then
             decal.min_distance = 40
             decal.max_distance = 720
        elseif texture:find('shard') then
             decal.min_distance = 8
             decal.max_distance = 240
             decal.max_value = 1
        end

    end

    for _,decal in ipairs(room.entities) do
        if decal._name == 'eow/MusicLayerSource' then
            do_it_to_it(decal)
        end
    end



end

return script
