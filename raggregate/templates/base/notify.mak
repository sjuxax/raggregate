<%inherit file="base.mak"/>
        <h2>Notified Stuff</h2>
		% for s in notifyd_stories:
            <%include file="story_item.mak" args="story_obj = s, vote_dict = vote_dict"/>
        % endfor
		% for s in notifyd_comments:
            Comment ${s.id}
        % endfor
        % if 'message' in request.session:
            <h3>${request.session['message']}</h3>
        % endif
