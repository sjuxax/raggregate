<%inherit file="base.mak"/>
Add a message of the day!
<br /><br />
<form action="${request.route_url('motd')}" METHOD="POST">
    Message: <input type="text" name="new_motd"><br />
    Author: <input type="text" name="author"><br />
    Source: <input type="text" name="source"><br />
    Link: <input type="text" name="link"><br />
    <input type="submit" value="Submit">
</form>

%if message != None:
    <br />${message}<br />
%endif

Existing messages:
<ul>
    %for motd in motds:
        % if motd.link:
            <li>${motd.message} - ${motd.author} (<a href="${motd.link}">${motd.source}</a>)</li>
        % else:
            <li>${motd.message} - ${motd.author} (${motd.source})</li>
        % endif
    %endfor
</ul>
