<%inherit file="base.mak"/>
<form action="${request.route_url('new_page')}" METHOD="POST">
    <b>${message}</b><br />
    Title: <input type="text" name="title" value="${new_title_text}" maxlength="100" /><br />
    <br />
    Content: <textarea name="description" cols="50" rows="10"></textarea><br />
    Slug: <input type="text" name="slug" value="" maxlength="20" /><br />
    Render Type: <select name="render_type">
        <option value="static_md">Static (Markdown)</option>
        <option value="static_html">Static (HTML)</option>
    </select><br />
    <br />
    <input type="submit" value="Add Page" /><br />
</form>
