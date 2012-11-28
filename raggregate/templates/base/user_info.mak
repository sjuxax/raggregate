<%inherit file="base.mak"/>

% if edit_mode:
    <form method="POST" action="/user_info?user_id=${u.id}" enctype="multipart/form-data">
        About Me: <textarea name="about_me" cols="50" rows="10">${u.about_me | template_filters.none_as_blank}</textarea><br />
        My Picture: <input type="file" name="picture" /><br />
        Email: <input type="text" name="email" value="${u.email | template_filters.none_as_blank}" /><br />
        <input type="submit" value="Update" />
    </form>
    <br />
    <div id="change_pass_form">
        <b>Change Password for ${u.display_name()}</b>
        <form action="${request.route_url('login', _query=[('act', 'update_pw')])}" method="POST">
            Old Password: <input name="old_password" type="password"><br />
            New Password: <input name="new_password" type="password"><br />
            New Password (Confirm): <input name="new_password_confirm" type="password"><br />
            <input type="submit" value="Update Password" />
        </form>
    </div>
% endif

<h3>${u.display_name()}</h3>
% if u.picture:
    Picture: <img src="/user_imgs/${u.picture_ref.filename}" /><br />
% else:
    Picture: None uploaded yet<br />
% endif
    <br />
About Me: ${u.about_me | template_filters.render_md,n}
    <br />

<h3>Send a Message</h3>
<form method="post" action="/messages/out" id="reply-form">
    Subject: <input type="text" name="subject" /><br />
    Message: <input type="textarea" name="body" /><br />
    To: <span id="new-message-to">${u.display_name()}</span><br />
    <input type="hidden" name="recipient" id="recipient-hidden" value="${u.id}" /><br />
    <input type="submit" value="Send Message"></input>
</form>

<h2>Activity</h2>
            ##<h3>Comments</h3>
            ##% for c in u.comments:
            ##    Comment on <a href=${request.route_url('full', sub_id=c.parent_id)}>${c.load_parent().title}</a>: <br />
            ##    ${c.body} <br />
            ##    <br />
            ##% endfor
            <h3>Submissions</h3>
            % for s in u.submissions:
                Submitted <a href=${request.route_url('full', sub_id=s.id)}>${s.title}</a><br />
                <br />
            % endfor
            </div>
