#!/usr/bin/env python3
"""
Example usage of screenoverlay package
Run this after: pip install screenoverlay
"""

from screenoverlay import Overlay
import time

print("=== ScreenOverlay Examples ===\n")

# Example 1: Blur mode
print("1. Blur overlay (3 seconds)...")
Overlay(mode='blur', blur_strength=4).activate(duration=3)
time.sleep(0.5)

# Example 2: Black screen
print("2. Black screen (2 seconds)...")
Overlay(mode='black').activate(duration=2)
time.sleep(0.5)

# Example 3: White screen
print("3. White screen (2 seconds)...")
Overlay(mode='white').activate(duration=2)
time.sleep(0.5)

# Example 4: Custom color
print("4. Custom red overlay (2 seconds)...")
Overlay(mode='custom', color_tint=(255, 100, 100), opacity=0.6).activate(duration=2)

print("\nAll examples completed!")

