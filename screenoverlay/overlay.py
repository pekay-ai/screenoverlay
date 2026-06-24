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
                 watermark_shadow_offset=(1, 1),
                 learn_more_url="", learn_more_text="Learn more",
                 badge_link_color="#7FB3FF", badge_inner_padding=10):
        """
        Initialize native overlay

        Parameters:
        - mode (str): Overlay mode - 'blur', 'black', 'white', 'custom', 'badge'
                      'blur'   - Blurred background with tint (default)
                      'black'  - Full black screen (privacy mode)
                      'white'  - Full white screen (flash/fade effect)
                      'custom' - Custom color with transparency
                      'badge'  - Small, non-covering, always-on-top corner watermark.
                                 Covers nothing and dims nothing — a persistent
                                 deterrent that floats text in a screen corner.
        - blur_strength (int): How blurred/obscured (1-5, only for mode='blur')
        - opacity (float): Window opacity (0.0 to 1.0)
        - color_tint (tuple): RGB color tint (0-255)
        - all_screens (bool): If True, blur all monitors. If False, only blur primary monitor (default: True)
        - watermark_enabled (bool): Enable watermark text overlay (default: False)
        - watermark_text (str): Text to display in watermark / badge (default: "")
        - watermark_position (str): Position of watermark - 'bottom_right', 'bottom_left', 'top_right', 'top_left' (default: 'bottom_right')
        - watermark_font_family (str): Font family for watermark (default: 'Segoe UI')
        - watermark_font_size (int): Font size for watermark (default: 16)
        - watermark_padding (int): Padding from screen edge in pixels (default: 24)
        - watermark_color (str): Text color in hex format (default: '#FFFFFF')
        - watermark_shadow (bool): Enable text shadow (default: True)
        - watermark_shadow_color (str): Shadow color in hex format (default: '#000000')
        - watermark_shadow_offset (tuple): Shadow offset (x, y) in pixels (default: (1, 1))
        - learn_more_url (str): If set (mode='badge'), clicking the badge opens this URL (default: "")
        - learn_more_text (str): Clickable link text shown after the badge text (default: "Learn more")
        - badge_link_color (str): Link text color in hex format (default: '#7FB3FF')
        - badge_inner_padding (int): Padding around text inside the badge in pixels (default: 10)
        """
        self.mode = mode.lower()
        self.blur_strength = max(1, min(5, blur_strength))
        self.all_screens = all_screens

        # Badge settings (mode='badge')
        self.learn_more_url = learn_more_url
        self.learn_more_text = learn_more_text
        self.badge_link_color = badge_link_color
        self.badge_inner_padding = badge_inner_padding
        self._badge_main_label = None  # ref for live set_text()
        
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
        elif self.mode == 'badge':
            # Non-covering corner badge: no tint, no blur, no screen dimming.
            self.opacity = opacity if opacity != 0.85 else 0.9
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

        # A badge is a persistent deterrent — it stays visible after start().
        if self.mode == 'badge':
            self._is_visible = True
            return

        # Hide all windows initially
        for win in self.windows:
            win.withdraw()

        self._is_visible = False
    
    def show(self):
        """Show the overlay (instant, <1ms)"""
        if self.root is None:
            # Auto-start if not started yet
            self.start()
        
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
        # Badge mode uses a single small corner window, not full-screen coverage.
        if self.mode == 'badge':
            self._create_badge_window()
            return

        monitors = self._get_monitors()
        
        # If all_screens is False, only use primary monitor
        if not self.all_screens:
            monitors = monitors[:1]  # Only keep first monitor
        
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

    # ------------------------------------------------------------------
    # Badge mode (mode='badge') — small, non-covering corner watermark
    # ------------------------------------------------------------------
    def _create_badge_window(self):
        """
        Create a small, always-on-top badge window that covers nothing.

        Unlike the full-screen overlay modes, this dims/blurs nothing — it just
        floats the watermark text (plus an optional clickable 'Learn more' link)
        in a screen corner as a persistent deterrent.
        """
        monitors = self._get_monitors()
        mx, my, mw, mh = monitors[0]  # primary monitor

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)

        # Hide from macOS dock (same approach as the full-screen overlay path)
        try:
            import AppKit
            AppKit.NSApp.setActivationPolicy_(AppKit.NSApplicationActivationPolicyProhibited)
        except Exception:
            pass

        bg_color = self._configure_badge_transparency()
        self._build_badge_content(self.root, bg_color)
        self.windows.append(self.root)

        # Size the window to its content, then place it in the chosen corner.
        self.root.update_idletasks()
        self._place_badge(self.root, mx, my, mw, mh)

    def _configure_badge_transparency(self):
        """
        Make the badge background disappear so only the text floats.

        Returns the background color the labels should use.
        On Windows, '-transparentcolor' makes matching pixels fully transparent
        AND click-through, leaving crisp text. Elsewhere we fall back to a
        semi-transparent badge via window '-alpha'.
        """
        # A near-black key unlikely to collide with the text/shadow colors.
        transparent_key = '#010203'
        if platform.system() == 'Windows':
            try:
                self.root.configure(bg=transparent_key)
                self.root.attributes('-transparentcolor', transparent_key)
                return transparent_key
            except tk.TclError:
                pass  # Fall through to alpha-based badge

        bg_color = f'#{self.color_tint[0]:02x}{self.color_tint[1]:02x}{self.color_tint[2]:02x}'
        self.root.configure(bg=bg_color)
        try:
            self.root.attributes('-alpha', self.opacity)
        except tk.TclError:
            pass
        return bg_color

    def _build_badge_content(self, window, bg_color):
        """Build the badge text + optional clickable 'Learn more' link."""
        font = (self.watermark_font_family, self.watermark_font_size, "bold")
        pad = self.badge_inner_padding

        container = tk.Frame(window, bg=bg_color)
        container.pack(padx=pad, pady=pad)

        self._badge_main_label = tk.Label(
            container, text=self.watermark_text,
            fg=self.watermark_color, bg=bg_color, font=font
        )
        self._badge_main_label.pack(side='left')
        self._watermark_widgets.append(self._badge_main_label)

        if self.learn_more_url:
            link_font = (self.watermark_font_family, self.watermark_font_size, "underline")
            link = tk.Label(
                container, text="  " + self.learn_more_text,
                fg=self.badge_link_color, bg=bg_color, font=link_font, cursor="hand2"
            )
            link.pack(side='left')
            self._watermark_widgets.append(link)

        # The whole badge is clickable (not just the link) for a generous target.
        for widget in (window, container, self._badge_main_label, *self._watermark_widgets):
            widget.bind("<Button-1>", self._open_learn_more)

    def _place_badge(self, window, mx, my, mw, mh):
        """Position the (already sized) badge window in the chosen screen corner."""
        w = window.winfo_reqwidth()
        h = window.winfo_reqheight()
        pad = self.watermark_padding
        pos = self.watermark_position.lower()

        if pos == 'bottom_right':
            x, y = mx + mw - w - pad, my + mh - h - pad
        elif pos == 'bottom_left':
            x, y = mx + pad, my + mh - h - pad
        elif pos == 'top_right':
            x, y = mx + mw - w - pad, my + pad
        else:  # 'top_left'
            x, y = mx + pad, my + pad

        window.geometry(f"+{int(x)}+{int(y)}")

    def _open_learn_more(self, event=None):
        """Open the configured learn-more URL when the badge is clicked."""
        if not self.learn_more_url:
            return
        try:
            import webbrowser
            webbrowser.open(self.learn_more_url)
        except Exception as e:
            print(f"Could not open learn-more URL: {e}")

    def set_text(self, text):
        """Update the badge text live (no window recreate) and reposition."""
        self.watermark_text = text
        if self._badge_main_label is None or self.root is None:
            return
        try:
            self._badge_main_label.config(text=text)
            self.root.update_idletasks()
            mx, my, mw, mh = self._get_monitors()[0]
            self._place_badge(self.root, mx, my, mw, mh)
        except Exception as e:
            print(f"Could not update badge text: {e}")

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
