def get_from_post(post, key):
    if key in post and post[key] != '':
        return post[key]
    else:
        return None
