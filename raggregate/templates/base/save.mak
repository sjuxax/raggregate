<%inherit file="base.mak"/>
        <h2>Saved Stories</h2>
		% for s in saved:
            <%include file="story_item.mak" args="story_obj = s, vote_dict = vote_dict"/>
        % endfor
