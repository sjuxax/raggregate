<%inherit file="base.mak"/>
Add a message of the day!
<br /><br />
<form action="${request.route_url('motd')}" METHOD="POST">
Message: <input type="text" name="message_to_add"><br />
    Author: <input type="text" name="author"><br />
    <input type="submit" value="Submit">
</form>

%if message != None:
    <br />${message}<br />
%endif

Existing messages:
<ul>
    %for message_of_the_day in messages_of_the_day:
        <li>${message_of_the_day.message} - ${message_of_the_day.author}</li>
    %endfor
</ul>
