#!/usr/bin/env python3
"""
Native Blur Overlay - Uses OS-native blur effects
No screen capture, no permissions needed, instant appearance

Single-process architecture using Tkinter's update() for non-blocking operation.
"""

import tkinter as tk
import platform
import sys
import os

# Try to import screeninfo for multi-monitor support
try:
    from screeninfo import get_monitors
    HAS_SCREENINFO = True
except ImportError:
    HAS_SCREENINFO = False


class NativeBlurOverlay:
    def __init__(self, mode='blur', blur_strength=3, opacity=0.85, color_tint=(136, 136, 136), all_screens=True,
                 watermark_enabled=False, watermark_text="", watermark_position="bottom_right",
                 watermark_font_family="Segoe UI", watermark_font_size=16, watermark_padding=24,
                 watermark_color="#FFFFFF", watermark_shadow=True, watermark_shadow_color="#000000",
                 watermark_shadow_offset=(1, 1)):
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
        - all_screens (bool): If True, blur all monitors. If False, only blur primary monitor (default: True)
        - watermark_enabled (bool): Enable watermark text overlay (default: False)
        - watermark_text (str): Text to display in watermark (default: "")
        - watermark_position (str): Position of watermark - 'bottom_right', 'bottom_left', 'top_right', 'top_left' (default: 'bottom_right')
        - watermark_font_family (str): Font family for watermark (default: 'Segoe UI')
        - watermark_font_size (int): Font size for watermark (default: 16)
        - watermark_padding (int): Padding from edge in pixels (default: 24)
        - watermark_color (str): Text color in hex format (default: '#FFFFFF')
        - watermark_shadow (bool): Enable text shadow (default: True)
        - watermark_shadow_color (str): Shadow color in hex format (default: '#000000')
        - watermark_shadow_offset (tuple): Shadow offset (x, y) in pixels (default: (1, 1))
        """
        self.mode = mode.lower()
        self.blur_strength = max(1, min(5, blur_strength))
        self.all_screens = all_screens
        
        # Watermark settings
        self.watermark_enabled = watermark_enabled
        self.watermark_text = watermark_text
        self.watermark_position = watermark_position
        self.watermark_font_family = watermark_font_family
        self.watermark_font_size = watermark_font_size
        self.watermark_padding = watermark_padding
        self.watermark_color = watermark_color
        self.watermark_shadow = watermark_shadow
        self.watermark_shadow_color = watermark_shadow_color
        self.watermark_shadow_offset = watermark_shadow_offset
        self._watermark_widgets = []  # Store references to prevent garbage collection
        
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
        self.windows = []  # List to hold multiple windows for multi-monitor
        self._monitors = []  # The monitor list the current windows were built for
        self._is_visible = False
        self._last_update_time = 0  # Throttle update() calls
        
    def start(self):
        """
        Initialize the overlay windows.
        Call this once at app startup.
        
        After calling start(), use show() and hide() to control visibility instantly,
        and call update() regularly in your main loop to keep the overlay responsive.
        
        Example:
            overlay = Overlay(mode='blur', blur_strength=4)
            overlay.start()  # Initialize (call once)
            
            while True:
                overlay.show()      # Show overlay (instant)
            time.sleep(2)
                overlay.hide()      # Hide overlay (instant)
                overlay.update()    # Keep overlay responsive (call regularly!)
            
            overlay.stop()   # Cleanup when done
        """
        if self.root is not None:
            return  # Already started
        
        # Create windows for all monitors
        self._create_windows()
        
        # Hide all windows initially
        for win in self.windows:
            win.withdraw()
        
        self._is_visible = False
    
    def show(self):
        """Show the overlay (instant, <1ms)"""
        if self.root is None:
            # Auto-start if not started yet
            self.start()

        # Re-enumerate monitors on EVERY show: the window list was built at start() and
        # display topology changes after that (dock a monitor, Win+P duplicate/extend/
        # second-only). A stale list leaves a live screen uncovered — coverage must match
        # what exists at the moment blur goes up, not at app startup. (v0.6.10)
        self._refresh_windows_if_changed()

        if not self._is_visible:
            print(f"\n🔴 SHOWING overlay windows...")
            for win in self.windows:
                try:
                    win.deiconify()
                    win.attributes('-topmost', True)  # Re-enable topmost when showing
                    win.lift()
                except Exception as e:
                    print(f"Warning: Failed to show window: {e}")
            self._is_visible = True
            print(f"✅ OVERLAY IS NOW VISIBLE\n")
    
    def hide(self):
        """Hide the overlay using withdraw() (lightweight, fast, no resource leaks)"""
        if self.root is None:
            return  # Not started yet
        
        if self._is_visible:
            # LIGHTWEIGHT HIDE - just withdraw windows (don't destroy/recreate)
            print(f"🫥 WITHDRAWING overlay windows (lightweight hide)...")
            for win in self.windows:
                try:
                    win.attributes('-topmost', False)  # Remove topmost before hiding
                    win.withdraw()
                except Exception as e:
                    print(f"Warning: Failed to withdraw window: {e}")
            
            self._is_visible = False
            print(f"✅ OVERLAY HIDDEN (windows withdrawn)\n")
    
    def update(self):
        """
        Keep overlay responsive - call this regularly in your main loop!
        
        This processes Tkinter events and keeps the windows responsive.
        Without calling this, the overlay will freeze.
        
        Example:
            while True:
                detect_something()
                if detected:
                    overlay.show()
                else:
                    overlay.hide()
                overlay.update()  # ← Call this every loop iteration!
                time.sleep(0.1)
        """
        if self.root is not None:
            try:
                import time
                current_time = time.time()
                
                # Throttle: only update every 100ms (10 FPS) to reduce CPU load
                # This prevents excessive event processing while keeping UI responsive
                if current_time - self._last_update_time < 0.1:
                    return  # Skip this update
                
                self._last_update_time = current_time
                
                # Defensive check: verify window state matches _is_visible flag
                for win in self.windows:
                    try:
                        actual_state = win.winfo_viewable()
                        if actual_state and not self._is_visible:
                            print(f"⚠️ BUG DETECTED: Window is visible but _is_visible=False! Force hiding...")
                            win.attributes('-topmost', False)
                            win.withdraw()
                        elif not actual_state and self._is_visible:
                            print(f"⚠️ BUG DETECTED: Window is hidden but _is_visible=True! Syncing flag...")
                            self._is_visible = False
                    except Exception as e:
                        pass  # Ignore errors in defensive check
                
                # Process Tkinter events
                self.root.update()
            except Exception as e:
                print(f"Warning: Update failed: {e}")
    
    def stop(self):
        """Stop and cleanup the overlay completely"""
        if self.root is not None:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
            self.root = None
            self.windows = []
            self._is_visible = False
    
    def _get_monitors(self):
        """Get information about all monitors"""
        if HAS_SCREENINFO:
            try:
                monitors = get_monitors()
                return [(m.x, m.y, m.width, m.height) for m in monitors]
            except:
                pass
        
        # Fallback: assume single primary monitor
        root = tk.Tk()
        root.withdraw()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return [(0, 0, width, height)]
    
    def _create_windows(self):
        """Create overlay windows for all monitors (or just primary if all_screens=False)"""
        monitors = self._active_monitors()
        self._monitors = monitors

        # Create primary root window
        self.root = tk.Tk()
        
        # Hide from dock immediately after creating Tk window
        # This prevents dock icon from appearing even though we create GUI windows
        try:
            import AppKit
            AppKit.NSApp.setActivationPolicy_(AppKit.NSApplicationActivationPolicyProhibited)
            print("✅ Screenoverlay: Dock icon hidden")
        except Exception as e:
            print(f"⚠️  Screenoverlay: Could not hide dock icon: {e}")
        
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        
        # Configure primary window for first monitor
        if monitors:
            x, y, width, height = monitors[0]
            self._configure_window(self.root, x, y, width, height)
            self.windows.append(self.root)
        
        # Create additional windows for other monitors (only if all_screens=True)
        for x, y, width, height in monitors[1:]:
            win = tk.Toplevel(self.root)
            win.overrideredirect(True)
            win.attributes('-topmost', True)
            self._configure_window(win, x, y, width, height)
            self.windows.append(win)
    
    def _active_monitors(self):
        """The monitors the overlay must cover RIGHT NOW, after policy clamps.

        Primary-only when the caller asked (all_screens=False) OR on macOS 26+, where
        multi-monitor native blur is broken: the dock-hide activation policy empties
        NSApp.windows() and the Cocoa/Tk Y-origin differs, leaving second screens
        partially covered. Primary-only there until multi-monitor is fixed."""
        monitors = self._get_monitors()
        _force_single = False
        if platform.system() == "Darwin":
            try:
                _force_single = int(platform.mac_ver()[0].split(".")[0]) >= 26
            except (ValueError, IndexError):
                _force_single = False
        if not self.all_screens or _force_single:
            monitors = monitors[:1]  # Only keep first monitor
        return monitors

    def _refresh_windows_if_changed(self):
        """Rebuild the window set if the display topology changed since the windows
        were built (monitor docked/undocked, Win+P duplicate/extend/second-only).
        Cheap no-op when nothing changed; called from show() so coverage always
        matches the screens that exist at the moment blur goes up. (v0.6.10)"""
        try:
            current = self._active_monitors()
        except Exception:
            return
        if current == self._monitors or not current or self.root is None:
            return
        print(f"🖥️  Display topology changed: {len(self._monitors)} -> {len(current)} monitor(s); rebuilding overlay windows")
        # Root window is reused: move/resize it to the new primary. (Destroying the Tk
        # root would tear down Tcl itself; geometry alone keeps blur+watermark intact.)
        x, y, width, height = current[0]
        try:
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            print(f"Warning: could not re-position primary overlay window: {e}")
        # Secondary windows are cheap Toplevels: drop and recreate for the new list.
        for win in self.windows[1:]:
            try:
                win.destroy()
            except Exception:
                pass
        self.windows = [self.root]
        for x, y, width, height in current[1:]:
            win = tk.Toplevel(self.root)
            win.overrideredirect(True)
            win.attributes('-topmost', True)
            self._configure_window(win, x, y, width, height)
            if not self._is_visible:
                win.withdraw()   # keep new windows hidden until show() reveals the set
            self.windows.append(win)
        self._monitors = current

    def _configure_window(self, window, x, y, width, height):
        """Configure a window with overlay settings"""
        # Set background color (tint)
        bg_color = f'#{self.color_tint[0]:02x}{self.color_tint[1]:02x}{self.color_tint[2]:02x}'
        window.configure(bg=bg_color)
        
        # Set opacity
        window.attributes('-alpha', self.opacity)
        
        # Position and size
        window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Apply native blur effect based on OS (only if mode is 'blur')
        if self.apply_blur:
            self._apply_native_blur_to_window(window)
        
        # Add watermark if enabled
        self._add_watermark(window)
        
        # Bind escape key to hide (only on primary window)
        if window == self.root:
            window.bind('<Escape>', lambda e: self.hide())
    
    def _add_watermark(self, window):
        """Add watermark text overlay to a window"""
        if not self.watermark_enabled or not self.watermark_text:
            return
        
        # Font configuration
        font = (self.watermark_font_family, self.watermark_font_size, "bold")
        
        # Determine placement based on position
        pos = self.watermark_position.lower()
        xpad = self.watermark_padding
        ypad = self.watermark_padding
        
        if pos == "bottom_right":
            relx, rely, anchor = 1.0, 1.0, "se"
            x_offset = -xpad
            y_offset = -ypad
        elif pos == "bottom_left":
            relx, rely, anchor = 0.0, 1.0, "sw"
            x_offset = xpad
            y_offset = -ypad
        elif pos == "top_right":
            relx, rely, anchor = 1.0, 0.0, "ne"
            x_offset = -xpad
            y_offset = ypad
        else:  # "top_left"
            relx, rely, anchor = 0.0, 0.0, "nw"
            x_offset = xpad
            y_offset = ypad
        
        # Get window background color for transparent label background
        bg_color = window.cget("bg")
        
        # Add shadow if enabled
        if self.watermark_shadow:
            sx, sy = self.watermark_shadow_offset
            shadow = tk.Label(
                window,
                text=self.watermark_text,
                fg=self.watermark_shadow_color,
                bg=bg_color,
                font=font
            )
            shadow.place(
                relx=relx,
                rely=rely,
                x=x_offset + sx,
                y=y_offset + sy,
                anchor=anchor
            )
            self._watermark_widgets.append(shadow)
        
        # Add main text
        main = tk.Label(
            window,
            text=self.watermark_text,
            fg=self.watermark_color,
            bg=bg_color,
            font=font
        )
        main.place(
            relx=relx,
            rely=rely,
            x=x_offset,
            y=y_offset,
            anchor=anchor
        )
        self._watermark_widgets.append(main)
    
    def _apply_native_blur_to_window(self, window):
        """Apply OS-native backdrop blur effect to a specific window"""
        system = platform.system()
        
        if system == 'Darwin':  # macOS
            self._apply_macos_blur_to_window(window)
        elif system == 'Windows':
            self._apply_windows_blur_to_window(window)
        elif system == 'Linux':
            self._apply_linux_blur_to_window(window)
    
    def _apply_macos_blur_to_window(self, window):
        """Apply macOS NSVisualEffectView blur to a specific window"""
        try:
            from Cocoa import NSView, NSVisualEffectView
            from Cocoa import NSVisualEffectBlendingModeBehindWindow, NSVisualEffectMaterialDark
            import objc
            
            # Get the Tk window's NSWindow
            window_id = window.winfo_id()
            
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
                for ns_window in NSApp.windows():
                    if ns_window.isVisible():
                        # Create visual effect view
                        frame = ns_window.contentView().frame()
                        effect_view = NSVisualEffectView.alloc().initWithFrame_(frame)
                        effect_view.setBlendingMode_(NSVisualEffectBlendingModeBehindWindow)
                        effect_view.setMaterial_(NSVisualEffectMaterialDark)
                        effect_view.setState_(1)  # Active state
                        
                        # Add as subview
                        ns_window.contentView().addSubview_positioned_relativeTo_(
                            effect_view, 0, None
                        )
                        break
            except Exception as e:
                print(f"AppKit blur failed: {e}")
                
        except ImportError:
            print("pyobjc not available, install with: pip install pyobjc-framework-Cocoa")
        except Exception as e:
            print(f"macOS blur effect failed: {e}")
    
    def _apply_windows_blur_to_window(self, window):
        """Apply Windows Acrylic/Blur effect to a specific window"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Get window handle - try multiple methods
            try:
                # Method 1: Direct window ID
                hwnd = window.winfo_id()
            except:
                # Method 2: Get parent window
                hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
            
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
    
    def _apply_linux_blur_to_window(self, window):
        """Apply Linux compositor blur (X11/Wayland) to a specific window"""
        try:
            # Linux blur depends on compositor (KWin, Mutter, etc.)
            # Most compositors respect window transparency and apply blur automatically
            # For KDE Plasma, we can hint the compositor
            
            # Try to set _KDE_NET_WM_BLUR_BEHIND_REGION property
            # This requires X11 access
            pass  # Most Linux compositors auto-blur transparent windows
            
        except Exception as e:
            print(f"Linux blur effect hint failed: {e}")
    
    # Backward compatibility methods
    def activate(self, duration=5):
        """
        Show overlay for a fixed duration and then exit (blocking).
        
        This is the legacy API for backward compatibility.
        For new code, use start() + show()/hide() + update() instead.
        """
        self.start()
        self.show()
        
        # Schedule hide and cleanup
        self.root.after(int(duration * 1000), self._deactivate_and_exit)
        
        # Run mainloop (blocking)
        self.root.mainloop()
    
    def _deactivate_and_exit(self):
        """Helper for activate() - hide and exit"""
        self.hide()
        self.stop()


# Alias for convenience
Overlay = NativeBlurOverlay


if __name__ == "__main__":
    # Quick test - try different modes
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = 'blur'
    
    print(f"Testing mode='{mode}' for 3 seconds...")
    print("Available modes: blur, black, white, custom")
    print("Usage: python overlay.py [mode]")
    print()
    
    if mode == 'blur':
        overlay = Overlay(mode='blur', blur_strength=4)
    elif mode == 'black':
        overlay = Overlay(mode='black')
    elif mode == 'white':
        overlay = Overlay(mode='white')
    elif mode == 'custom':
        overlay = Overlay(mode='custom', opacity=0.7, color_tint=(255, 0, 0))  # Red example
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)
    
    overlay.activate(duration=3)
