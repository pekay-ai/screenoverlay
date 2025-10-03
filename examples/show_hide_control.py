#!/usr/bin/env python3
"""
Show/Hide Control Example
Demonstrates instant show/hide toggling with single-process architecture.
Perfect for real-time applications like ScreenStop.
"""

if __name__ == '__main__':
    import time
    from screenoverlay import Overlay

    print("Show/Hide Control Demo")
    print("=" * 50)
    print("This demonstrates instant overlay toggling")
    print("with minimal latency (<1ms per call)")
    print("=" * 50)
    print()

    # Step 1: Initialize overlay (one-time setup)
    print("1. Initializing overlay...")
    overlay = Overlay(mode='blur', blur_strength=4)
    overlay.start()  # Creates Tkinter windows
    print("   ✓ Ready! (hidden by default)")
    print()
    
    overlay.update()  # Process initial events
    time.sleep(1)

    # Step 2: Rapid show/hide cycles
    print("2. Testing rapid show/hide cycles...")
    for i in range(3):
        print(f"   Cycle {i+1}:")
        print("     → show() - overlay appears")
        overlay.show()
        overlay.update()  # Keep overlay responsive
        time.sleep(1.5)
        
        print("     → hide() - overlay disappears")
        overlay.hide()
        overlay.update()  # Keep overlay responsive
        time.sleep(0.5)
    
    print()

    # Step 3: Demonstrate sustained visibility
    print("3. Sustained display test...")
    print("   → Showing for 3 seconds...")
    overlay.show()
    
    # Keep overlay responsive during sustained display
    for _ in range(30):  # 30 iterations of 0.1s = 3 seconds
        overlay.update()
        time.sleep(0.1)
    
    print("   → Hiding...")
    overlay.hide()
    overlay.update()
    time.sleep(1)
    
    print()

    # Step 4: Cleanup
    print("4. Cleaning up...")
    overlay.stop()
    print("   ✓ Done!")
    print()

    # Summary
    print("=" * 50)
    print("PERFORMANCE SUMMARY")
    print("=" * 50)
    print("• start():   Creates windows (one-time)")
    print("• show():    <1ms (instant)")
    print("• hide():    <1ms (instant)")
    print("• update():  <1ms (call regularly in your loop!)")
    print("• stop():    Graceful cleanup")
    print()
    print("Perfect for ScreenStop - no process spawning!")
    print("=" * 50)

