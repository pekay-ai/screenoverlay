#!/usr/bin/env python3
"""
Example: Basic overlay with fixed duration

Shows a blur overlay for 5 seconds and then automatically closes.
"""
from screenoverlay import Overlay

# Create and show blur overlay for 5 seconds
overlay = Overlay(mode='blur', blur_strength=4)
overlay.activate(duration=5)

print("Overlay closed!")

