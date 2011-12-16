<%inherit file="base.mak"/>

<%block name="html_title">
    ${story.title} on ${site_name}
</%block>

% if logged_in:
    <script type="text/javascript">
    var md_lock = 0;

    $(document).ready(function() {
        crf = $('#comment-reply-form').detach();
        $('.comment-reply').click(function(e) {
            crf.css('display', 'block');
            $($(e.target).closest('.comment')).append(crf);
            $('#comment_parent').attr('value', ($(e.target).attr('id')).replace('reply-', ''));
            $('#parent_type').attr('value', 'comment');
        });
        $('.comment-edit-link').click(function(e) {
            erf = crf.clone()
            $(erf).children('form').attr('action', '${request.route_url("full", sub_id = story.id)}?op=edit&comment_id=' + $(e.target).attr('data-comment-id'))
            erf.css('display', 'block');
            $($(erf).children('#reply-text')).text('Edit your Reply...')
            $(erf).find('#body-textarea').val($('#body-md-' + $(e.target).attr('data-comment-id')).text())
            $($(e.target).closest('.comment')).append(erf);
        });
        sef = $('#story-edit-form').detach();
        $('.story-edit-link').click(function(e) {
            sefi = sef.clone()
            sefi.css('display', 'block');
            $('#description').replaceWith(sefi);
        });

        mdtable = $('#markdown-explanation-table').detach();
        $('#included').on("click", ".markdown-link", function() { 
            if (md_lock == 1) {
                mdtable.css('display', 'none');
                mdtable = mdtable.detach();
                md_lock = 0;
            } else {
                mdtable.css('display', 'block');
                $(this).closest('.mdholder').append(mdtable);
                md_lock = 1;
           }
        });

    });
    </script>
% endif

<style type="text/css">
    td { border: 2px black solid; padding: 2px; }
    th { border: 1px black solid; }
    table {border: 2px black solid; }
</style>

    % if success == False:
        <h1>${message}</h1>
    % else:
        <i>click the title to proceed to posted article; scroll down for commentary</i><br />
        <br />
        <%include file="story_item.mak", args="story_obj = story, vote_dict = story_vote_dict"/>
        <div id="description" class="story-description">
            ${story.description | template_filters.render_md,n}
        </div>
        ##@TODO: make functionality to determine whether a user is logged in on display a reusable function
        ## I have vague memories of this but think it's on the server side, need to create a def that can
        ## be used in the Mako templates to determine this, would be much better that way.
        % if (logged_in and request.session['users.id'] == str(story.added_by)) or logged_in_admin:
            <a href="javascript:void(0)" class=" story-edit-link logged-in-only ">edit this description</a><br/>
        % endif
        <h2>Comments</h2>
        <div id="markdown-explanation-table" style="display: none;">
            click "markdown" again to close<br />
            <table style="border-width: 2px;">
                <tr>
                    <th>Markdown</th>
                    <th>Output</th>
                </tr>
                <tr>
                    <td>*italic*</td>
                    <td><i>italic</i></td>
                </tr>
                <tr>
                    <td>**bold**</td>
                    <td><b>bold</b></td>
                </tr>
                <tr>
                    <td>link to [github](https://github.com)</td>
                    <td>link to <a href="https://github.com">github</a></td>
                </tr>
                <tr>
                    <td>&gt;blockquote</td>
                    <td><blockquote>blockquote</blockquote></td>
                </tr>
              </table>
        </div>
        % if 'logged_in' in request.session:
            <h3> Add a new comment </h3>
            <form method="post" id="story-reply-form" action="${request.route_url('full', sub_id = story.id)}">
                <textarea name="body" cols="50" rows="10"></textarea>
                <div class="mdholder">
                    <i>You can use <a href="javascript:void(0)" class="markdown-link">markdown</a> to format your comment.</i>
                </div>
                <input type="hidden" name="comment_parent" id="comment_parent-story" value="${story.id}" />
                <input type="hidden" name="parent_type" id="parent_type-story" value="story" />
                <br />
                <input type="submit" value="Add Comment"></input>
            </form>
        % else:
            You can leave a comment after you log in (use the box on the right of your screen).<br />
            <br />
        % endif
        <%def name="print_comment_tree(c, margin)">
            <%include file="comment_item.mak", args="comment = c, margin = margin, vote_dict = comment_vote_dict"/>
            <%
            if str(c.id) in comments['tree']:
                margin += 25
                for c_i in comments['tree'][str(c.id)]:
                    print_comment_tree(comments['dex'][c_i], margin)
            %>
        </%def>
        ## print comments starting at roots
		% for c in comments['allowed_roots']:
            ${print_comment_tree(comments['dex'][c], 0)}
        % endfor
        % if len(comments['allowed_roots']) < 1:
            <i>no comments yet</i>
        % endif
        % if next_page:
            <br />
            <a href="${request.route_url('full', sub_id=template_filters.get_submission_identifier_for_url(story), _query = [('page_num', next_page)])}">next page &rarr;</a>
        % endif
        % if prev_page:
            <br />
            <a href="${request.route_url('full', sub_id=template_filters.get_submission_identifier_for_url(story), _query = [('page_num', prev_page)])}">prev page &larr;</a>
        % endif
        <div id="comment-reply-form" style="clear: both; display: none;">
        <b id="reply-text">Enter your Reply</b><br />
        <form method="post" id="comment-reply-form-real" action="${request.route_url('full', sub_id = story.id)}">
            <textarea id="body-textarea" cols="50" rows="10" name="body"></textarea>
            <div class="mdholder">
                <i>You can use <a href="javascript:void(0)" class="markdown-link">markdown</a> to format your comment.</i>
            </div>
            <input type="hidden" name="comment_parent" id="comment_parent" value="${story.id}" />
            <input type="hidden" name="parent_type" id="parent_type" value="story" />
            <br />
            <input type="submit" value="Add Comment"></input>
        </form>
        </div>

        <div id="story-edit-form" style="clear: both; display: none;">
            <b id="story-edit-text">Edit your description</b><br />
            <form method="post" id="story-edit-form-real" action="${request.route_url('full', sub_id = template_filters.get_submission_identifier_for_url(story))}">
                <textarea id="description-textarea" cols="50" rows="10" name="description-textarea">${story.description|h}</textarea>
                <br />
                <input type="submit" value="Edit Story"></input>
            </form>
        </div>

    % endif
