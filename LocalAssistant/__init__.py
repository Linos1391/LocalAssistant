"""__init__ of the package."""

from .utils import UtilsExtension, ConfigManager, LocalAssistantException
from .model_processor import ChatExtension, DownloadExtension,\
    MemoryExtension, DocsQuestionAnswerExtension

# check for PyTorch
try:
    import torch
except ImportError as err:
    raise LocalAssistantException\
        ("Could not find torch installed. Please visit https://pytorch.org/ \
and download the version for your device.") from err

__all__ = [
    'UtilsExtension',
    'ChatExtension',
    'DownloadExtension',
    'MemoryExtension',
    'DocsQuestionAnswerExtension',
    'ConfigManager',
    'LocalAssistantException',
]

__version__ = '1.1.0'
