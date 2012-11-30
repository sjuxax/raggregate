<%inherit file="base.mak"/>
Add a message of the day!
<br /><br />
<form action="${request.route_url('motd')}" METHOD="POST">
    <table>
        <tr>
            <th>Message: </th>
            <td><input type="text" name="message_to_add"></td>
            <td><i>Required</i></td>
        </tr>
        <tr>
            <th>Author:</th>
            <td><input type="text" name="author"></td>
        </tr>
        <tr>
            <th>Source:</th>
            <td><input type="text" name="source"></td>
        </tr>
        <tr>
            <th>Source URL:</th>
            <td><input type="text" name="link"></td>
        </tr>
        <tr>
            <th>Date of message:</th>
            <td><input type="text" name="datestring"></td>
        </tr>
        <tr>
            <td colspan=2 align=center>
                <input type="submit" name="add_motd_button" value="Submit">
            </td>
        </tr>
    </table>
</form>

% if motds and len(motds) > 0:
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
% endif

%if message != None:
    <br />${message}<br />
%endif
