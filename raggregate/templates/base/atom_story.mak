<%inherit file="atom_base.mak" />

% for story in stories:
    <%include file="atom_story_item.mak" args="i=story" />
% endfor

