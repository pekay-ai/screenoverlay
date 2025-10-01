# 🖥️ ScreenOverlay

> Cross-platform Python library for creating instant fullscreen overlays with blur, solid colors, or custom effects.

[![PyPI version](https://img.shields.io/pypi/v/screenoverlay.svg)](https://pypi.org/project/screenoverlay/)
[![Python Support](https://img.shields.io/pypi/pyversions/screenoverlay.svg)](https://pypi.org/project/screenoverlay/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform Support](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-blue.svg)](https://github.com/yourusername/screenoverlay)

Perfect for **privacy screens**, **focus modes**, **screen recording**, **presentations**, **visual effects**, and more.

---

## 📖 Our Story

While developing **[ScreenStop](https://github.com/pekay/screenstop)** - our advanced AI-powered phone screenshot detection system - we found ourselves constantly needing to blur or obscure our screens during development, testing, and demos. We needed something **instant**, **lightweight**, and **cross-platform** that didn't require screen recording permissions.

After trying various solutions and finding them too slow (>1 second latency), too complex, or requiring special permissions, we built our own. **ScreenOverlay** was born from this need - a <50ms overlay system that just works.

We're releasing it as **open-source (MIT)** because we believe privacy tools should be accessible to everyone. Whether you're protecting sensitive data during a video call, building focus apps, or just need a quick screen blackout - ScreenOverlay has you covered.

**Want enterprise-grade screen protection?** Check out our flagship product **[ScreenStop](#-interested-in-advanced-screen-protection)** below.

---

## ✨ Features

- 🎭 **4 Overlay Modes** - blur, black, white, custom colors
- ⚡ **Ultra Fast** - <50ms startup, native OS blur effects
- 🔒 **No Permissions** - No screen recording access required
- 🌍 **Cross-Platform** - macOS, Windows, Linux
- 🎯 **Simple API** - One line of code to activate
- 🪶 **Lightweight** - Minimal dependencies

---

## 📦 Installation

```bash
pip install screenoverlay
```

That's it! No additional setup required.

---

## 🚀 Quick Start

### Simple Duration-Based Overlay

```python
from screenoverlay import Overlay

# Privacy blur (great for screen sharing)
Overlay(mode='blur', blur_strength=4).activate(duration=5)

# Full blackout
Overlay(mode='black').activate(duration=3)

# Flash effect
Overlay(mode='white').activate(duration=1)

# Custom colored overlay
Overlay(mode='custom', color_tint=(255, 100, 100), opacity=0.7).activate()
```

Press `ESC` to dismiss the overlay early.

### Manual Start/Stop Control

For apps that need to control overlay lifetime (like ScreenStop):

```python
from screenoverlay import Overlay
from multiprocessing import Process

def run_overlay():
    overlay = Overlay(mode='blur', blur_strength=4)
    overlay.start()  # Runs indefinitely

# Start overlay in separate process
overlay_process = Process(target=run_overlay)
overlay_process.start()

# Later, stop it
overlay_process.terminate()
overlay_process.join()
```

**See [`examples/`](examples/) folder for more use cases!**

---

## 🎨 Overlay Modes

### 1️⃣ Blur Mode

Blurred background with customizable strength - perfect for privacy during screen sharing.

```python
Overlay(
    mode='blur',
    blur_strength=4,        # 1-5: higher = more obscured
    color_tint=(120, 120, 150),  # RGB tint color
    opacity=0.85            # 0.0-1.0
).activate(duration=5)
```

**Use Cases:**
- 🎥 Privacy during screen recording/sharing
- 🧘 Focus mode / distraction blocking
- 📱 Hide sensitive information temporarily

---

### 2️⃣ Black Mode

Full black screen overlay - instant privacy.

```python
Overlay(mode='black').activate(duration=3)
```

**Use Cases:**
- 🔒 Quick privacy/security blackout
- 🎬 Presentation breaks
- ⏸️ Screen pause effect

---

### 3️⃣ White Mode

Full white screen overlay - clean and bright.

```python
Overlay(mode='white').activate(duration=2)
```

**Use Cases:**
- 💡 Flash effects
- 🎞️ Scene transitions
- ✨ Attention grabber

---

### 4️⃣ Custom Mode

Create your own colored overlays with custom transparency.

```python
Overlay(
    mode='custom',
    color_tint=(255, 0, 0),  # Red overlay
    opacity=0.5               # Semi-transparent
).activate(duration=5)
```

**Use Cases:**
- 🎨 Branded overlays
- 🌈 Color filters
- 🎪 Creative effects

---

## 📖 Complete API Reference

### `Overlay` Class

```python
Overlay(
    mode='blur',              # 'blur', 'black', 'white', 'custom'
    blur_strength=3,          # 1-5 (only for mode='blur')
    opacity=0.85,             # 0.0-1.0
    color_tint=(136, 136, 136)  # RGB tuple (0-255)
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | str | `'blur'` | Overlay mode: `'blur'`, `'black'`, `'white'`, `'custom'` |
| `blur_strength` | int | `3` | Blur intensity 1-5 (only for blur mode) |
| `opacity` | float | `0.85` | Window opacity 0.0 (transparent) to 1.0 (opaque) |
| `color_tint` | tuple | `(136, 136, 136)` | RGB color values (0-255) |

### `activate()` Method

Show overlay for a fixed duration.

```python
overlay.activate(duration=5)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `duration` | float | `5` | How long to show overlay (seconds) |

**Note:** Press `ESC` to dismiss early.

### `start()` Method

Start overlay indefinitely (runs until stopped).

```python
overlay.start()
```

**Important:** This is blocking and runs `mainloop()`. For app integration, run in a separate process:

```python
from multiprocessing import Process
p = Process(target=overlay.start)
p.start()
# Later: p.terminate()
```

### `stop()` Method

Stop and close the overlay.

```python
overlay.stop()
```

**Note:** Usually called from within the overlay process, or use `process.terminate()` from parent.

---

## 💡 Real-World Usage Examples

### Privacy Screen During Video Call

```python
from screenoverlay import Overlay

# Activate blur when discussing sensitive info
overlay = Overlay(mode='blur', blur_strength=5)
overlay.activate(duration=10)
```

---

### Focus Timer (Pomodoro Technique)

```python
from screenoverlay import Overlay
import time

def pomodoro_session():
    # 25-minute work session
    print("🍅 Focus time! Work for 25 minutes...")
    time.sleep(25 * 60)
    
    # 5-minute break with screen overlay
    print("☕ Break time!")
    Overlay(mode='black', opacity=0.8).activate(duration=5 * 60)

pomodoro_session()
```

---

### Screen Flash Effect

```python
from screenoverlay import Overlay

# Quick camera flash effect
Overlay(mode='white', opacity=0.9).activate(duration=0.3)
```

---

### Custom Branded Overlay

```python
from screenoverlay import Overlay

# Brand color overlay with transparency
Overlay(
    mode='custom',
    color_tint=(74, 144, 226),  # Brand blue
    opacity=0.6
).activate(duration=3)
```

---

## 🖥️ Platform Support

| Platform | Native Blur | Requirements |
|----------|-------------|--------------|
| **macOS** | ✅ NSVisualEffectView | `pyobjc-framework-Cocoa` (auto-installed) |
| **Windows** | ✅ DWM Acrylic/Mica | Built-in (no extra deps) |
| **Linux** | ⚠️ Compositor-dependent* | Built-in (no extra deps) |

*Linux blur quality depends on your desktop compositor (KDE, GNOME, etc.)

---

## ⚙️ System Requirements

- **Python:** 3.7 or higher
- **Tkinter:** Usually included with Python
- **macOS only:** `pyobjc-framework-Cocoa` (automatically installed)
- **Windows/Linux:** No additional dependencies

---

## ⚡ Performance

- **Startup Latency:** <50ms
- **Method:** Native OS window effects (no screen capture)
- **Permissions:** None required (works without screen recording access)
- **Memory:** Minimal footprint

**Why so fast?** Unlike traditional screen capture approaches (400-1000ms), we use native OS-level window blur effects, eliminating the need to capture, process, and re-render the screen.

---

## 🛡️ Interested in Advanced Screen Protection?

**ScreenOverlay** is great for quick privacy needs, but what if you need **automatic, AI-powered protection**?

### Meet **[ScreenStop](https://github.com/pekay/screenstop)** 📱🔍

Our flagship product, **ScreenStop**, is an enterprise-grade ML-powered system that **automatically detects** when someone is taking a screenshot with their phone and triggers instant screen protection.

#### **Key Features:**
- 🤖 **AI-Powered Detection** - Advanced YOLO + custom ML model
- ⚡ **Real-time Processing** - 216ms detection time
- 🎯 **100% Accuracy** - Zero false positives in production
- 🔄 **Automatic Protection** - No manual activation needed
- 🏢 **Enterprise Ready** - Scalable and production-tested

#### **Perfect For:**
- 📊 Protecting confidential presentations
- 💼 Corporate security compliance
- 🏥 HIPAA/healthcare data protection
- 🏦 Financial services security
- 🔬 Research & IP protection

**ScreenOverlay** provides the instant privacy overlay.  
**ScreenStop** provides the intelligence to trigger it automatically.

**[→ Learn more about ScreenStop](https://github.com/pekay/screenstop)**

---

## 🔧 Development & Testing

### Local Installation

```bash
# Clone the repository
git clone https://github.com/pekay/screenoverlay.git
cd screenoverlay

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .

# Run examples
python examples/basic_duration.py
python examples/start_stop_control.py
```

### Examples

Check out the [`examples/`](examples/) directory for complete working examples:

- **`basic_duration.py`** - Simple blur overlay with fixed duration
- **`black_screen.py`** - Privacy blackout screen
- **`start_stop_control.py`** - Manual control with multiprocessing
- **`custom_color.py`** - Custom colored overlay

Each example is fully documented and ready to run!

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 🎉 Open a Pull Request

### Ideas for Contributions

- 🐛 Bug fixes
- 📝 Documentation improvements
- ✨ New overlay modes or effects
- 🧪 Additional tests
- 🌍 Platform-specific optimizations

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Why MIT?** We believe privacy tools should be freely accessible to everyone. Use it in your personal projects, integrate it into your commercial applications, or fork it to create something entirely new. No restrictions, no complications.

---

## 🙏 Acknowledgments

- Built during the development of **[ScreenStop](https://github.com/pekay/screenstop)**
- Uses Python's `tkinter` for cross-platform GUI
- Leverages native OS APIs for optimal performance
- Inspired by the need for instant, permission-free privacy controls

---

## 📬 Contact & Support

- 🐛 **Issues:** [GitHub Issues](https://github.com/pekay/screenoverlay/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/pekay/screenoverlay/discussions)
- 📧 **Email:** ppnicky@gmail.com
- 🏢 **Enterprise Solutions:** Contact us about **[ScreenStop](https://github.com/pekay/screenstop)** for advanced protection

---

## 🌟 Show Your Support

If you find **ScreenOverlay** useful:
- ⭐ Star the repository
- 🐦 Share on social media
- 📝 Write about your use case
- 🔍 Explore **[ScreenStop](https://github.com/pekay/screenstop)** for advanced features

---

<div align="center">

**Built with ❤️ by Pekay**

[Download](https://pypi.org/project/screenoverlay/) · [Report Bug](https://github.com/pekay/screenoverlay/issues) · [Request Feature](https://github.com/pekay/screenoverlay/issues) · [ScreenStop](https://github.com/pekay/screenstop)

</div>
