

function onBegin()
    disableMovement()

    say("waldmo_consume_me_normal")

end


function onEnd(room, wasSkipped)
    enableMovement()
end

