"""
ScreenOverlay - Cross-platform screen overlay library
Provides blur, black, white, custom color overlays, and a non-covering
persistent corner badge, all with minimal latency
"""

from .overlay import NativeBlurOverlay as Overlay

__version__ = '0.7.0'
__author__ = 'ScreenStop'
__all__ = ['Overlay']

