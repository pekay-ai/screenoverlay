# ScreenOverlay Examples

This directory contains example scripts demonstrating different use cases for the `screenoverlay` library.

## Examples

### 1. Basic Duration (`basic_duration.py`)
Shows a blur overlay for a fixed duration (5 seconds).

```bash
python examples/basic_duration.py
```

### 2. Black Screen (`black_screen.py`)
Privacy mode - full black screen overlay.

```bash
python examples/black_screen.py
```

### 3. Show/Hide Control (`show_hide_control.py`) ⭐ **NEW**
Instant show/hide toggling with minimal latency (~0.1ms). Perfect for real-time applications like ScreenStop.

```bash
python examples/show_hide_control.py
```

### 4. Start/Stop Control (`start_stop_control.py`)
Manual control using multiprocessing - perfect for app integration.

```bash
python examples/start_stop_control.py
```

### 5. Custom Color (`custom_color.py`)
Custom color overlay with transparency.

```bash
python examples/custom_color.py
```

## Running Examples

Make sure you have `screenoverlay` installed:

```bash
pip install screenoverlay
```

Or if running from the repository:

```bash
pip install -e .
```

Then run any example:

```bash
python examples/basic_duration.py
```

