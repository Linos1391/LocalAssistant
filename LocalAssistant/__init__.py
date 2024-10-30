from utils import LocalAssistantException

# check for PyTorch
try:
    import torch
except ImportError:
    raise LocalAssistantException("Could not find torch installed. Please visit https://pytorch.org/ and download the version for your device.")
    
__all__ = [
    'models',
    'parser',
    'utils',
]

__version__ = '0.1.dev2'
