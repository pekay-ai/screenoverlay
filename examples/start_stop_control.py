#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Manual start/stop control

Shows how to manually control overlay lifetime using start() and stop().
Perfect for integration with apps like ScreenStop.

Note: With the new single-process architecture, Tkinter must run on the main thread.
This example shows a typical pattern where you integrate the overlay with your main loop.
"""
from screenoverlay import Overlay
import time

if __name__ == '__main__':
    print("Starting overlay...")
    
    # Initialize overlay
    overlay = Overlay(mode='blur', blur_strength=4)
    overlay.start()
    overlay.show()  # Show immediately
    
    print("Overlay is running. Showing for 5 seconds...")
    
    try:
        # Keep overlay responsive for 5 seconds
        start_time = time.time()
        while time.time() - start_time < 5:
            overlay.update()  # Must call regularly to keep responsive
            time.sleep(0.01)  # Update every 10ms
    except KeyboardInterrupt:
        print("\nInterrupted by user!")
    
    # Stop the overlay
    print("Stopping overlay...")
    overlay.stop()
    
    print("Overlay stopped!")

