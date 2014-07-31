import sys
import logging

logger = logging.getLogger(__name__)

platform = sys.platform.lower()
logger.info('Platform %s' % platform)
if platform == 'win32':
    from eggbot_scanwin32 import *
elif platform == 'win64':
    from eggbot_scanwin32 import *
elif platform == 'darwin':
	from eggbot_scanosx import *
elif platform == 'linux2':
	from eggbot_scanlinux import *
else:
	from eggbot_scanposix import *
