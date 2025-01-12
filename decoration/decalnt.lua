require "math"
require "os"

local selection_tool = require("tools.selection")
local selection_util = require("selections")
local siu = require("selection_item_utils")
local state = require("loaded_state")

local script = {
    name = "count decals",
    displayName = "Count Decals",
    tooltip = "Count decals",
    parameters = {
        outfile = "decals.txt",
        prefix = "decals/iambad/magbe/",
        },
    fieldInformation = {
        oufile = {
            fieldType = "loennScripts.directFilepath",
            extension = "*"
            }
        }
}

function script.prerun(args)

    counts = {}
    for _,room in ipairs(state.map.rooms) do
        for _,decal in ipairs(room.decalsFg) do
            if decal.texture:find('^' .. args.prefix) ~= nil then
                key = decal.texture:sub(args.prefix:len()+1)
                if counts[key] ~= nil then
                    counts[key] = counts[key] + 1
                else
                    counts[key] = 1
                end
            end

        end
        for _,decal in ipairs(room.decalsBg) do
            if decal.texture:find('^' .. args.prefix) ~= nil then
                key = decal.texture:sub(args.prefix:len()+1)
                if counts[key] ~= nil then
                    counts[key] = counts[key] + 1
                else
                    counts[key] = 1
                end
            end

        end
    end

    tkeys = {}
    for k,v in pairs(counts) do
        table.insert(tkeys, k)
    end
    table.sort(tkeys)

    local file = io.open(args.outfile, "w")
    io.output(file)
    io.write(string.format("#%s\n", args.prefix))
--    for k,v in pairs(counts) do
    for _, k in ipairs(tkeys) do
        io.write(string.format("%i %s\n", counts[k],k))
    end        
    file:close()

end

return script
