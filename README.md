# 🖥️ ScreenOverlay

> Cross-platform Python library for creating instant fullscreen overlays with blur, solid colors, or custom effects.

[![PyPI version](https://img.shields.io/pypi/v/screenoverlay.svg)](https://pypi.org/project/screenoverlay/)
[![Python Support](https://img.shields.io/pypi/pyversions/screenoverlay.svg)](https://pypi.org/project/screenoverlay/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform Support](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-blue.svg)](https://github.com/yourusername/screenoverlay)

Perfect for **privacy screens**, **focus modes**, **screen recording**, **presentations**, **visual effects**, and more.

---

## 📖 Our Story

While developing **[ScreenStop](https://screenstop.co)** - our advanced AI-powered phone screenshot detection system - we found ourselves constantly needing to blur or obscure our screens during development, testing, and demos. We needed something **instant**, **lightweight**, and **cross-platform** that didn't require screen recording permissions.

After trying various solutions and finding them too slow (>1 second latency), too complex, or requiring special permissions, we built our own. **ScreenOverlay** was born from this need - a <50ms overlay system that just works.

We're releasing it as **open-source (MIT)** because we believe privacy tools should be accessible to everyone. Whether you're protecting sensitive data during a video call, building focus apps, or just need a quick screen blackout - ScreenOverlay has you covered.

**Want enterprise-grade screen protection?** Check out our flagship product **[ScreenStop](#-interested-in-advanced-screen-protection)** below.

---

## ✨ Features

- 🎭 **4 Overlay Modes** - blur, black, white, custom colors
- ⚡ **Ultra Fast** - <50ms startup, native OS blur effects
- 🖥️ **Multi-Monitor Support** - Automatically blurs ALL screens simultaneously
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

# Multi-monitor control
Overlay(mode='blur', all_screens=True).activate(duration=5)   # Blur all monitors (default)
Overlay(mode='blur', all_screens=False).activate(duration=5)  # Blur only primary monitor
```

Press `ESC` to dismiss the overlay early.

### Instant Show/Hide Control ⭐ **NEW**

For real-time applications that need instant toggling with **zero latency** (like ScreenStop):

```python
from screenoverlay import Overlay
import time

# Initialize once (one-time ~300ms setup)
overlay = Overlay(mode='blur', blur_strength=4)
overlay.start()

# Then show/hide instantly (~0.1ms each)
overlay.show()  # Overlay appears instantly
time.sleep(2)
overlay.hide()  # Overlay disappears instantly

overlay.show()  # Show again - still instant!
time.sleep(2)
overlay.hide()

# Cleanup when done
overlay.stop()
```

**Performance:** `show()` and `hide()` take **~0.1ms** - virtually instant! Perfect for real-time control.

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
    color_tint=(136, 136, 136),  # RGB tuple (0-255)
    all_screens=True          # True = all monitors, False = primary only
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | str | `'blur'` | Overlay mode: `'blur'`, `'black'`, `'white'`, `'custom'` |
| `blur_strength` | int | `3` | Blur intensity 1-5 (only for blur mode) |
| `opacity` | float | `0.85` | Window opacity 0.0 (transparent) to 1.0 (opaque) |
| `color_tint` | tuple | `(136, 136, 136)` | RGB color values (0-255) |
| `all_screens` | bool | `True` | If `True`, blur all monitors. If `False`, blur only primary monitor |

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

### `start()` Method ⭐ **NEW**

Initialize the overlay process for instant show/hide control.

```python
overlay.start()
```

**Important:** Call this once at app startup. It creates a background process (~300ms). After initialization, use `show()` and `hide()` for instant toggling.

### `show()` Method ⭐ **NEW**

Show the overlay instantly (~0.1ms).

```python
overlay.show()
```

**Performance:** Virtually instant - no subprocess creation, just a queue message.

### `hide()` Method ⭐ **NEW**

Hide the overlay instantly (~0.1ms).

```python
overlay.hide()
```

**Performance:** Even faster than `show()` - typically <0.1ms.

### `stop()` Method

Stop and cleanup the overlay process.

```python
overlay.stop()
```

**Note:** Call this when your application exits to gracefully terminate the overlay process.

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

### Latency Benchmarks ⭐ **UPDATED**

- **activate() (duration-based):** <50ms startup
- **start() (one-time init):** ~300ms (creates subprocess)
- **show() / hide():** **~0.1ms** (virtually instant!)

### How It Works

- **Method:** Native OS window effects (no screen capture)
- **Permissions:** None required (works without screen recording access)
- **Memory:** Minimal footprint (~10 MB per screen)
- **Process Model:** Separate process with queue-based messaging
- **Multi-Monitor:** Automatically detects and covers all screens

**Why so fast?** Unlike traditional screen capture approaches (400-1000ms), we use:
1. Native OS-level window blur effects (no image processing)
2. Persistent subprocess with `withdraw()`/`deiconify()` toggling
3. Queue-based messaging for instant communication
4. One window per monitor (all controlled simultaneously)

This makes `show()` and `hide()` nearly **10,000x faster** than recreating the overlay each time!

---

## 🛡️ Interested in Advanced Screen Protection?

**ScreenOverlay** is great for quick privacy needs, but what if you need **automatic, AI-powered protection**?

### Meet **[ScreenStop](https://screenstop.co)** 📱🔍

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

**[→ Learn more about ScreenStop](https://screenstop.co)**

---

## 🔧 Development & Testing

### Local Installation

```bash
# Clone the repository
git clone https://github.com/pekay-ai/screenoverlay.git
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
- **`show_hide_control.py`** ⭐ **NEW** - Instant show/hide toggling (~0.1ms)
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

## 📄 Licensing

ScreenOverlay uses a **dual-license model** similar to xlwings:

### 🆓 Non-Commercial Use (Free)

Free for individuals and non-commercial purposes:

✅ Personal projects  
✅ Educational use  
✅ Academic research  
✅ Open source projects (OSI-approved licenses)  
✅ Non-profit organizations  
✅ Evaluation and testing

**No license key needed** - just `pip install screenoverlay` and start using it!

### 💼 Commercial Use (License Required)

A commercial license is required if you use ScreenOverlay:

💼 At a company or for commercial purposes  
🏢 In a commercial product or service  
💰 For client work or revenue-generating activities  
🔧 In any business context

#### Pricing:

| License Type | Price | Use Case |
|--------------|-------|----------|
| 👨‍💻 **Developer** | $149/year | Single developer |
| 👥 **Team** | $699/year | Up to 5 developers |
| 🏢 **Enterprise** | Custom | Unlimited developers + priority support |

**All commercial licenses include:**

✅ Commercial use rights  
✅ Priority email support  
✅ Perpetual license for purchased version  
✅ 1 year of updates

**[Purchase License](mailto:ppnicky@gmail.com?subject=ScreenOverlay%20Commercial%20License) | [Contact Sales](mailto:ppnicky@gmail.com?subject=ScreenOverlay%20Enterprise%20Inquiry)**

### ❓ Which License Do I Need?

**Simple rule:** If you're using it in a business/commercial context, you need a commercial license.

| Scenario | License Needed |
|----------|----------------|
| Personal side project (no revenue) | 🆓 Non-Commercial |
| Learning Python at home | 🆓 Non-Commercial |
| University research project | 🆓 Non-Commercial |
| Open source project (MIT, GPL, etc.) | 🆓 Non-Commercial |
| Using at your company/job | 💼 Commercial |
| Building a SaaS product | 💼 Commercial |
| Freelance client work | 💼 Commercial |
| Integrating into commercial software | 💼 Commercial |

---

## 🙏 Acknowledgments

- Built during the development of **[ScreenStop](https://screenstop.co)**
- Uses Python's `tkinter` for cross-platform GUI
- Leverages native OS APIs for optimal performance
- Inspired by the need for instant, permission-free privacy controls

---

## 📬 Contact & Support

- 🐛 **Issues:** [GitHub Issues](https://github.com/pekay-ai/screenoverlay/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/pekay-ai/screenoverlay/discussions)
- 📧 **Email:** ppnicky@gmail.com
- 🏢 **Enterprise Solutions:** Contact us about **[ScreenStop](https://screenstop.co)** for advanced protection

---

## 🌟 Show Your Support

If you find **ScreenOverlay** useful:
- ⭐ Star the repository
- 🐦 Share on social media
- 📝 Write about your use case
- 🔍 Explore **[ScreenStop](https://screenstop.co)** for advanced features

---

<div align="center">

**Built with ❤️ by [ScreenStop](https://screenstop.co)**

[Download](https://pypi.org/project/screenoverlay/) · [Report Bug](https://github.com/pekay-ai/screenoverlay/issues) · [Request Feature](https://github.com/pekay-ai/screenoverlay/issues) · [ScreenStop](https://screenstop.co)

</div>
