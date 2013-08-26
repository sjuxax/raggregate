<%inherit file="base.mak"/>
<form action="${request.route_url('new_post')}" METHOD="POST">
    <b>${message}</b><br />
    Title: <input type="text" name="title" value="${new_title_text}" maxlength="100" /><br />
    <br />
    <b>At least one of these is required</b><br />
    Description: <textarea name="description" cols="50" rows="10"></textarea><br />
    URL: <input type="text" name="url" value="${new_url_text}" /><br />
    Section: <select name="section_id">
        <option value="">&lt;choose a section&gt;</option>
        % for section in sections:
            % if 'section' in request.session['safe_get'] and section.name == request.session['safe_get']['section']:
                <option value="${section.id}" selected="selected">${section.name}</option>
            % else:
                <option value="${section.id}">${section.name}</option>
            % endif
        % endfor
    </select><br />
    ##% if 'section_id' in request.session['safe_get']:
    ##    <input type="hidden" value="${request.session['safe_get']['section_id']}" name="section_id" />
    ##% endif
    <br />
    <input type="submit" value="Post Story" /><br />
</form>
