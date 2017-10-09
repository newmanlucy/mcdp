# -*- coding: utf-8 -*-
from .logs import logger
from .branch_info import *
from .constants import *
from .dependencies import *
from .development import *

from .branch_info import __version__


import resource
rsrc = resource.RLIMIT_AS
# rsrc = resource.RLIMIT_DATA
# rsrc = resource.RLIMIT_RSS
# rsrc = resource.RLIMIT_STACK

soft, hard = resource.getrlimit(rsrc)
logger.debug("%s Limit starts as: %s %s" % (rsrc, soft, hard))

resource.setrlimit(rsrc, (1e9, 1e9))
soft, hard = resource.getrlimit(rsrc)
logger.debug("%s Limit starts as: %s %s" % (rsrc, soft, hard))