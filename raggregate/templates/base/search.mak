<%inherit file="base.mak"/>

        Your search term <b>"${context['request'].params['term']}"</b> returned ${res.result.numFound} results.
        % for s in stories:
            <%include file="story_item.mak" args="story_obj=s, vote_dict=vote_dict" />
        % endfor
