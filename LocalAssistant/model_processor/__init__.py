"""__init__ of model processor."""

from .chat import ChatExtension
from .download import DownloadExtension
from .memory import MemoryExtension

__all__ = [
    'ChatExtension',
    'DownloadExtension',
    'MemoryExtension',
]