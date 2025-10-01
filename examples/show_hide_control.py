#!/usr/bin/env python3
"""
Show/Hide Control Example
Demonstrates instant show/hide toggling with no subprocess overhead.
Perfect for real-time applications like ScreenStop.
"""

if __name__ == '__main__':
    import time
    from screenoverlay import Overlay

    print("Show/Hide Control Demo")
    print("=" * 50)
    print("This demonstrates instant overlay toggling")
    print("with minimal latency (~0.1ms per call)")
    print("=" * 50)
    print()

    # Step 1: Initialize overlay (one-time setup)
    print("1. Initializing overlay...")
    overlay = Overlay(mode='blur', blur_strength=4)
    overlay.start()  # Creates subprocess, takes ~300ms
    print("   ✓ Ready! (hidden by default)")
    print()
    
    time.sleep(1)

    # Step 2: Rapid show/hide cycles
    print("2. Testing rapid show/hide cycles...")
    for i in range(3):
        print(f"   Cycle {i+1}:")
        print("     → show() - overlay appears")
        overlay.show()
        time.sleep(1.5)
        
        print("     → hide() - overlay disappears")
        overlay.hide()
        time.sleep(0.5)
    
    print()

    # Step 3: Demonstrate sustained visibility
    print("3. Sustained display test...")
    print("   → Showing for 3 seconds...")
    overlay.show()
    time.sleep(3)
    
    print("   → Hiding...")
    overlay.hide()
    time.sleep(1)
    
    print()

    # Step 4: Cleanup
    print("4. Cleaning up...")
    overlay.stop()  # Terminates subprocess
    print("   ✓ Done!")
    print()

    # Summary
    print("=" * 50)
    print("PERFORMANCE SUMMARY")
    print("=" * 50)
    print("• start():  ~300ms (one-time initialization)")
    print("• show():   ~0.1ms (instant)")
    print("• hide():   ~0.1ms (instant)")
    print("• stop():   graceful cleanup")
    print()
    print("Perfect for ScreenStop - no latency on show/hide!")
    print("=" * 50)

