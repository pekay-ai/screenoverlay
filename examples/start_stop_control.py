#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Manual start/stop control with multiprocessing

Shows how to manually control overlay lifetime using start() and stop().
Perfect for integration with apps like ScreenStop.
"""
from screenoverlay import Overlay
from multiprocessing import Process
import time

def run_overlay():
    """Run overlay in subprocess"""
    overlay = Overlay(mode='blur', blur_strength=4)
    overlay.start()  # Runs indefinitely

if __name__ == '__main__':
    print("Starting overlay...")
    
    # Start overlay in separate process
    overlay_process = Process(target=run_overlay)
    overlay_process.start()
    
    print("Overlay is running. Press Ctrl+C to stop, or waiting 5 seconds...")
    
    try:
        time.sleep(5)
    except KeyboardInterrupt:
        print("\nInterrupted by user!")
    
    # Stop the overlay
    print("Stopping overlay...")
    overlay_process.terminate()
    overlay_process.join()
    
    print("Overlay stopped!")

