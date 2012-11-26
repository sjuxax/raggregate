<%inherit file="atom_base.mak" />

% for comment in comments:
    <% s = comment.load_submission() %>
    <%include file="atom_comment_item.mak" args="i=comment" />
% endfor

