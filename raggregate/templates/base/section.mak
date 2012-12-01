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
