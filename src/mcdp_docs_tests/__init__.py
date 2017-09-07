import os

if 'raise_if_test_included' in os.environ:
    raise Exception()

from .book_toc import *
from .element_abbrevs_test import *
from .transformations import *
from .github_link import *
from .github_ref_subs import *
from .split_test import *
from .tags_in_titles import *
from .task_markers_test import *
from .make_console_pre_tests import *