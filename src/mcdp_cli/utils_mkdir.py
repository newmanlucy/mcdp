# -*- coding: utf-8 -*-
import os

def mkdirs_thread_safe(dst):
    """Make directories leading to 'dst' if they don't exist yet"""
    if dst == '' or os.path.exists(dst):
        return
    head, _ = os.path.split(dst)
    if os.sep == ':' and not ':' in head:
        head = head + ':'
    mkdirs_thread_safe(head)
    try:
        os.mkdir(dst, 0777)
    except OSError as err:
        if err.errno != 17:  # file exists
            raise

#
# def make_sure_dir_exists(filename):
#     ''' Makes sure that the path to file exists, but creating directories. '''
#     dirname = os.path.dirname(filename)
#     # dir == '' for current dir
#     if dirname != '' and not os.path.exists(dirname):
#         mkdirs_thread_safe(dirname)

