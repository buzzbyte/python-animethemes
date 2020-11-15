from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution('python-animethemes').version
except DistributionNotFound:
    pass

from .animethemes import *
from .schema import *