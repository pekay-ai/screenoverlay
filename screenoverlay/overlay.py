#!/usr/bin/env python3
"""
Native Blur Overlay - Uses OS-native blur effects
No screen capture, no permissions needed, instant appearance
"""

import tkinter as tk
import platform
import sys
import os


class NativeBlurOverlay:
    def __init__(self, mode='blur', blur_strength=3, opacity=0.85, color_tint=(136, 136, 136)):
        """
        Initialize native overlay
        
        Parameters:
        - mode (str): Overlay mode - 'blur', 'black', 'white', 'custom'
                      'blur'   - Blurred background with tint (default)
                      'black'  - Full black screen (privacy mode)
                      'white'  - Full white screen (flash/fade effect)
                      'custom' - Custom color with transparency
        - blur_strength (int): How blurred/obscured (1-5, only for mode='blur')
        - opacity (float): Window opacity (0.0 to 1.0)
        - color_tint (tuple): RGB color tint (0-255)
        """
        self.mode = mode.lower()
        self.blur_strength = max(1, min(5, blur_strength))
        
        # Apply mode-specific settings
        if self.mode == 'black':
            self.opacity = opacity if opacity != 0.85 else 1.0  # Default full opacity for black
            self.color_tint = (0, 0, 0)
            self.apply_blur = False
        elif self.mode == 'white':
            self.opacity = opacity if opacity != 0.85 else 1.0  # Default full opacity for white
            self.color_tint = (255, 255, 255)
            self.apply_blur = False
        elif self.mode == 'custom':
            self.opacity = opacity
            self.color_tint = color_tint
            self.apply_blur = False
        else:  # mode == 'blur'
            # Adjust opacity based on blur strength
            self.opacity = min(1.0, opacity + (self.blur_strength - 3) * 0.05)
            # Adjust tint intensity based on blur strength
            tint_factor = 1.0 + (self.blur_strength - 3) * 0.15
            self.color_tint = tuple(min(255, int(c * tint_factor)) for c in color_tint)
            self.apply_blur = True
        
        self.root = None
        self._timer_id = None
        
    def start(self):
        """
        Start the overlay indefinitely (non-blocking, runs until stop() is called)
        
        For ScreenStop integration, run this in a separate process:
            from multiprocessing import Process
            p = Process(target=overlay.start)
            p.start()
            # Later: p.terminate()
        """
        self._create_window()
        self.root.mainloop()
    
    def stop(self):
        """Stop and close the overlay"""
        if self._timer_id is not None:
            try:
                self.root.after_cancel(self._timer_id)
                self._timer_id = None
            except:
                pass
        if self.root is not None:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
            self.root = None
        # Exit the process cleanly
        os._exit(0)
    
    def _create_window(self):
        """Internal method to create and configure the Tkinter window"""
        self.root = tk.Tk()
        
        # Remove window decorations
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        
        # Set background color (tint)
        bg_color = f'#{self.color_tint[0]:02x}{self.color_tint[1]:02x}{self.color_tint[2]:02x}'
        self.root.configure(bg=bg_color)
        
        # Set opacity
        self.root.attributes('-alpha', self.opacity)
        
        # Full screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Apply native blur effect based on OS (only if mode is 'blur')
        if self.apply_blur:
            self._apply_native_blur()
        
        # Bind escape key to exit
        self.root.bind('<Escape>', lambda e: self.kill_completely())
        self.root.focus_set()
    
    def activate(self, duration=5):
        """Show native blur overlay and exit after duration"""
        self._create_window()
        
        # Auto-exit timer
        self._timer_id = self.root.after(int(duration * 1000), self.kill_completely)
        
        # Show window
        self.root.mainloop()
        
    def _apply_native_blur(self):
        """Apply OS-native backdrop blur effect"""
        system = platform.system()
        
        if system == 'Darwin':  # macOS
            self._apply_macos_blur()
        elif system == 'Windows':
            self._apply_windows_blur()
        elif system == 'Linux':
            self._apply_linux_blur()
            
    def _apply_macos_blur(self):
        """Apply macOS NSVisualEffectView blur"""
        try:
            from Cocoa import NSView, NSVisualEffectView
            from Cocoa import NSVisualEffectBlendingModeBehindWindow, NSVisualEffectMaterialDark
            import objc
            
            # Get the Tk window's NSWindow
            window_id = self.root.winfo_id()
            
            # Create NSVisualEffectView
            # Note: This requires pyobjc-framework-Cocoa
            # The blur will be applied to the window background
            
            # Try to get NSWindow from Tk
            from tkinter import _tkinter
            
            # Alternative: Use AppKit directly
            try:
                from AppKit import NSApp, NSWindow
                from Cocoa import NSMakeRect
                
                # Get all windows and find ours
                for window in NSApp.windows():
                    if window.isVisible():
                        # Create visual effect view
                        frame = window.contentView().frame()
                        effect_view = NSVisualEffectView.alloc().initWithFrame_(frame)
                        effect_view.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
                        effect_view.setMaterial_(NSVisualEffectMaterialDark)
                        effect_view.setState_(1)  # Active state
                        
                        # Add as subview
                        window.contentView().addSubview_positioned_relativeTo_(
                            effect_view, 0, None
                        )
                        break
            except Exception as e:
                print(f"AppKit blur failed: {e}")
                
        except ImportError:
            print("pyobjc not available, install with: pip install pyobjc-framework-Cocoa")
        except Exception as e:
            print(f"macOS blur effect failed: {e}")
            
    def _apply_windows_blur(self):
        """Apply Windows Acrylic/Blur effect"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Get window handle - try multiple methods
            try:
                # Method 1: Direct window ID
                hwnd = self.root.winfo_id()
            except:
                # Method 2: Get parent window
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            
            if not hwnd:
                print("Could not get window handle for blur effect")
                return
            
            # Windows 10+ blur effect using DWM (Desktop Window Manager)
            DWM_BB_ENABLE = 0x00000001
            DWM_BB_BLURREGION = 0x00000002
            
            class DWM_BLURBEHIND(ctypes.Structure):
                _fields_ = [
                    ("dwFlags", wintypes.DWORD),
                    ("fEnable", wintypes.BOOL),
                    ("hRgnBlur", wintypes.HANDLE),
                    ("fTransitionOnMaximized", wintypes.BOOL),
                ]
            
            # Enable blur behind window
            bb = DWM_BLURBEHIND()
            bb.dwFlags = DWM_BB_ENABLE
            bb.fEnable = True
            bb.hRgnBlur = None
            bb.fTransitionOnMaximized = False
            
            result = ctypes.windll.dwmapi.DwmEnableBlurBehindWindow(hwnd, ctypes.byref(bb))
            
            # Try Windows 11 Acrylic/Mica effect (newer, better-looking blur)
            try:
                DWMWA_SYSTEMBACKDROP_TYPE = 38
                DWMSBT_TRANSIENTWINDOW = 3  # Acrylic effect (best for overlays)
                DWMSBT_MAINWINDOW = 2       # Mica effect (alternative)
                
                # Use Acrylic for stronger blur effect
                value = ctypes.c_int(DWMSBT_TRANSIENTWINDOW)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, 
                    DWMWA_SYSTEMBACKDROP_TYPE,
                    ctypes.byref(value),
                    ctypes.sizeof(value)
                )
            except Exception as e:
                # Windows 10 fallback - DwmEnableBlurBehindWindow is enough
                pass
                
        except Exception as e:
            # Blur effect failed, but window will still work (just without blur)
            print(f"Note: Windows blur effect unavailable: {e}")
            print("Overlay will work but without native blur effect")
            
    def _apply_linux_blur(self):
        """Apply Linux compositor blur (X11/Wayland)"""
        try:
            # Linux blur depends on compositor (KWin, Mutter, etc.)
            # Most compositors respect window transparency and apply blur automatically
            # For KDE Plasma, we can hint the compositor
            
            # Try to set _KDE_NET_WM_BLUR_BEHIND_REGION property
            # This requires X11 access
            pass  # Most Linux compositors auto-blur transparent windows
            
        except Exception as e:
            print(f"Linux blur effect hint failed: {e}")
    
    def kill_completely(self):
        """Exit the overlay completely"""
        try:
            if self.root:
                self.root.quit()
                self.root.destroy()
        except:
            pass
        
        os._exit(0)


if __name__ == "__main__":
    # Quick test - try different modes
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = 'blur'
    
    print(f"Testing mode='{mode}' for 3 seconds...")
    print("Available modes: blur, black, white, custom")
    print("Usage: python NativeBlurOverlay.py [mode]")
    print()
    
    if mode == 'blur':
        overlay = NativeBlurOverlay(mode='blur', blur_strength=4)
    elif mode == 'black':
        overlay = NativeBlurOverlay(mode='black')
    elif mode == 'white':
        overlay = NativeBlurOverlay(mode='white')
    elif mode == 'custom':
        overlay = NativeBlurOverlay(mode='custom', opacity=0.7, color_tint=(255, 0, 0))  # Red example
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
    
    overlay.activate(duration=3)

