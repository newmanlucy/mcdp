# -*- coding: utf-8 -*-
import os
import tempfile
from mcdp_utils_misc.fileutils import get_mcdp_tmp_dir
from mcdp_utils_misc.locate_files_imp import locate_files
from contracts.utils import check_isinstance
import shutil
from mcdp import logger
from contextlib import contextmanager

__all__ = ['create_hierarchy']

def remove_tree_contents(dirname):
    """ Removes all under dirname, but not dirname itself. """
    
    for root, dirs, files in os.walk(dirname):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
            
def create_hierarchy(files0):
    """ 
        Creates a temporary directory with the given files 
    
        files = {
            'lib1.mcdplib/poset1': <contents>
        }
    
    """
    
    mcdp_tmp_dir = get_mcdp_tmp_dir()
    prefix = 'create_hierarchy'
    d = tempfile.mkdtemp(dir=mcdp_tmp_dir, prefix=prefix)
#     
#     if True:
#         warnings.warn('Remove from production')
#         d = '/tmp/create_hierarchy'
#         remove_tree_contents(d)
#         logger.warning("using tmp dir " + d)
#         
    write_hierarchy(d, files0)
    return d

def write_hierarchy(where, files0):
    flattened = mockup_flatten(files0)
    for filename, contents in flattened.items():
        check_isinstance(contents, str)
        fn = os.path.join(where, filename)
        dn = os.path.dirname(fn)
        if not os.path.exists(dn):
            os.makedirs(dn)
        with open(fn, 'w') as f:
            f.write(contents)
            
def read_hierarchy(where):
    # read all files
    res = {}
    for filename in locate_files(where,'*'):
        r = os.path.relpath(filename, where)
        res[r] = open(filename).read()
    return unflatten(res)

def mockup_flatten(d): 
    '''
        from
            a:
                b:
                    x
        to 
            'a/b': x
    '''
    res = {}
    for k, v in d.items():
        if isinstance(v, dict):
#             if not v: # empty directory
#                 v = {'.empty':'# empty'}
            x = mockup_add_prefix(k, mockup_flatten(v))
            res.update(x)
                
        else:
            res[k] = v
    return res

from collections import defaultdict

def unflatten(x):
    def empty():
        return defaultdict(empty)
    res = empty()
    for fn, data in x.items():
        components = fn.split('/')
        assert len(components) >= 1
        w = res
        while len(components) > 1:
            w = w[components.pop(0)]
        last = components[0]
        w[last] = data
        
    # re-convert to dicts
    def conv(dd):
        if isinstance(dd, defaultdict):
            return dict((k, conv(d)) for k,d in dd.items())
        else:
            return dd
        
    return conv(res)
    
def mockup_add_prefix(prefix, d):
    res = {}
    for k, v in d.items():
        res['%s/%s' % (prefix, k)] = v
    return res

@contextmanager
def with_dir_content(data, use_dir=None):
    """
        data = str -> YAML folder structure
        
        d1:
            f1: |
                contents of f1
    """
    import yaml
    files = mockup_flatten(yaml.load(data))
    
    if use_dir is not None:
        remove_tree_contents(use_dir)
        write_hierarchy(use_dir, files)
        d = use_dir
    else:
        d = create_hierarchy(files)
        
    d0 = os.getcwd()
    os.chdir(d)
    try: 
        yield
    finally:
        os.chdir(d0)
        if False:
            shutil.rmtree(d)
        else:
            logger.debug('Not deleting tmp dir %s' % d)
            
        
        
    