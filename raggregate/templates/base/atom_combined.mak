<%inherit file="atom_base.mak" />

% for i in interleaved:
    <%
        type_flag = None

        # objects must be comments or stories
        # the body attr is exclusive to comment type
        # if we don't have it on the object, assume a story
        try:
            getattr(i, 'body')
            type_flag = "c"
        except:
            type_flag = "s"
    %>
    % if type_flag == "s":
        <%include file="atom_story_item.mak" args="i=i" />
    % endif
    % if type_flag == "c":
        <% s = i.load_submission() %>
        <%include file="atom_comment_item.mak" args="i=i" />
    % endif
% endfor

