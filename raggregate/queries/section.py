from raggregate.models.submission import Submission
from raggregate.models.comment import Comment
from raggregate.models.vote import Vote
from raggregate.models.section import Section

import sqlahelper

dbsession = sqlahelper.get_session()

def get_sections(parent = None):
    if parent:
        r = dbsession.query(Section).filter(Section.parent == parent).all()
    else:
        r = dbsession.query(Section).filter(Section.parent == None).all()

    return r

def get_section_by_id(id):
    return dbsession.query(Section).filter(Section.id == id).one()

def get_section_by_name(name):
    return dbsession.query(Section).filter(Section.name == name).one()

def add_section_picture(orig_filename, new_prefix, up_dir, image_file):
    import time
    import os
    import tempfile

    new_filename = "{0}-{1}.jpg".format(new_prefix, time.time())

    full_path = os.path.join(up_dir, new_filename)

    import hashlib
    skip_seek = False

    try:
        image_file.seek(0)
    except AttributeError:
        # we want a file, so if this isn't a file, make one.
        tmp_f = tempfile.TemporaryFile()
        # urllib2.urlopen object passed, read is implemented
        # or maybe not, and then just assume the string is the binary data
        # and ready to be written directly
        if hasattr(image_file, 'read'):
            # im_b for "image binary"
            im_b = image_file.read()
        else:
            im_b = image_file
        tmp_f.write(im_b)
        image_file = tmp_f

    image_file.seek(0)
    sha = hashlib.sha1()
    sha.update(image_file.read())
    sha = sha.hexdigest()

    if not skip_seek:
        image_file.seek(0)
    f = image_file
    from PIL import Image
    im = Image.open(f)
    im.thumbnail((50, 50), Image.ANTIALIAS)

    im.save(full_path, 'JPEG')

    from raggregate.models.sectionpicture import SectionPicture
    sp = SectionPicture(orig_filename, new_filename, sha, 0)
    dbsession.add(sp)
    dbsession.flush()
    return sp.id
