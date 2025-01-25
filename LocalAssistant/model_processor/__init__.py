"""__init__ of model processor."""

from .chat import ChatExtension
from .download import DownloadExtension
from .relation_extraction import RebelExtension
from .docs import DocsQuestionAnswerExtension

__all__ = [
    'ChatExtension',
    'DownloadExtension',
    'RebelExtension',
    'DocsQuestionAnswerExtension',
]
