
def soup_find_absolutely(soup, id_):
    """ Finds the element with the given ID, or raise KeyError. """
    e = soup.find(id=id_)
    if e is None:
        msg = 'Cannot find element with ID %r' % id_
        raise KeyError(msg)
    assert e.attrs['id'] == id_
    return e


def copy_contents_into(a, b):
    """ Copy the contents of a into b """
    for e in a.children:
        b.append(e.__copy__())