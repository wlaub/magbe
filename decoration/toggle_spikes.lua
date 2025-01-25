require "math"
require "os"

local selection_tool = require("tools.selection")
local selection_util = require("selections")
local siu = require("selection_item_utils")
local state = require("loaded_state")

local logging = require("logging")

local script = {
    name = "toggle invisible spikes",
    displayName = "Toggle Invisible Sikes",
    tooltip = "",
    parameters = {
        show = false,
        paddinggggggggggggg = false,
        },
    fieldInformation = {
        }
}

function script.run(room, args)

    for _,entity in ipairs(room.entities) do

        for _, match_name in ipairs({'spikesUp', 'spikesLeft', 'spikesRight', 'spikesDown'}) do
            if entity._name == match_name then
               if args.show then

                    if entity['type'] == "waldmo/invisible" then

                        entity['type'] = "waldmo/visible"
                    end
               else
                    if entity['type'] == "waldmo/visible" then
                        entity['type'] = "waldmo/invisible"
                    end

               end
            end
        end
    end

end

return script
