<%inherit file="base.mak"/>

% if edit_mode:
    <form method="POST" action="/user_info?user_id=${u.id}" enctype="multipart/form-data">
        <input type="text" name="about_me" />
        <input type="file" name="picture" />
        <input type="submit" value="Update" />
    </form>
% endif

<h3>${u.display_name()}</h3>
% if u.picture:
    Picture: <img src="/user_imgs/${u.picture_ref.filename}" />
% else:
    Picture: None uploaded yet
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
            ##    Comment on <a href="/full/${c.parent_id}">${c.load_parent().title}</a>: <br />
            ##    ${c.body} <br />
            ##    <br />
            ##% endfor
            <h3>Submissions</h3>
            % for s in u.submissions:
                Submitted <a href="/full/${s.id}">${s.title}</a><br />
                <br />
            % endfor
            </div>
