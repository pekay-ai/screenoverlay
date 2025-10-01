#!/usr/bin/env python3
"""
Example: Black screen overlay

Privacy mode - shows a full black screen for 3 seconds.
"""
from screenoverlay import Overlay

# Full black screen for privacy
overlay = Overlay(mode='black')
overlay.activate(duration=3)

print("Privacy screen closed!")

