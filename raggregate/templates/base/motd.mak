<%inherit file="base.mak"/>
Add a message of the day!
<br /><br />
<form action="${request.route_url('motd')}" METHOD="POST">
Message: <input type="text" name="new_motd"><br />
    Author: <input type="text" name="author"><br />
    <input type="submit" value="Submit">
</form>

%if message != None:
    <br />${message}<br />
%endif

Existing messages:
<ul>
    %for motd in motds:
        <li>${motd.message} - ${motd.author}</li>
    %endfor
</ul>
