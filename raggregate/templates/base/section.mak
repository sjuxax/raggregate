<%inherit file="base.mak"/>
        Add section: <br />
            <form action="${request.route_url('section')}" method="POST">
                Name: <input type="text" name="name" /><br />
                <br />
                <input type="submit" value="Add Section" /><br />
            </form>
        <br />
        Extant sections: <br />
        <ul>
        % for s in sections:
            <li><a href="${request.route_url('list', _query=[('section', s.name)])}">${s.name}</a></li>
        % endfor
        </ul>

        Add picture to existing section: <br />
        <form action="${request.route_url('section')}" method="POST" enctype="multipart/form-data">
            Section:
            <select name="section_id">
                % if sections and len(sections) > 0:
                    % for section in sections:
                        <option value="${section.id}">${section.name}</option>
                    % endfor
                % else:
                    <option value="">No Sections</option>
                % endif
            </select>
            <br />
            Picture: <input type="file" name="picture" /><br />
            <input type="submit" name="add_pic_button" value="Submit" />
        </form>
