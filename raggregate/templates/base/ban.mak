<%inherit file="base.mak"/>
        Add ban: <br />
            <form action="ban" METHOD="POST">
                IP Address: <input type="text" name="ip" /><br />
                Username: <input type="text" name="username" /><br />
                <br />
                Input duration as a timedelta constructor. It is fed directly to the timedelta factory so do not mess around here, you can break things seriously. <br />
                This functionality should never be exposed to a mortal because it can ruin your server. You haven't given the banhammer to anyone who hasn't earned it, have you?<br />
                If someone non-lazy comes around this could be made safe.<br />
                Leave this blank for infinite duration.<br />
                Duration: <input type="text" name="duration" /><br />
                <br />
                <input type="submit" value="Add Ban" /><br />
            </form>
        <br />
        Old bans: <br />
        % for b in bans:
            Added: ${b.added_on}<br />
            User: ${b.username}<br />
            IP Address: ${b.ip}<br />
            <br />
        % endfor
