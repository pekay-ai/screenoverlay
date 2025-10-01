#!/usr/bin/env python3
"""
Example: Custom color overlay

Shows a semi-transparent red overlay for 3 seconds.
"""
from screenoverlay import Overlay

# Custom color overlay (red with 70% opacity)
overlay = Overlay(mode='custom', opacity=0.7, color_tint=(255, 0, 0))
overlay.activate(duration=3)

print("Custom overlay closed!")

