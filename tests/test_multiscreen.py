"""Multi-screen coverage: the overlay must blur every monitor that exists at the
moment show() is called — not the monitors that existed at start() (v0.6.10 fix).

Unit-level: monitors are injected by patching Overlay._get_monitors, and the macOS-26
primary-only clamp is bypassed by patching platform inside the overlay module, so the
test runs identically on any dev machine. mode='black' avoids native blur calls.
Real-screen validation (Win+P duplicate / second-only / docking) is a Windows-machine step.
"""
import sys, os, types

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from screenoverlay import overlay as ov

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail and not ok else ""))


def main():
    # Pretend we're on Windows so the macOS-26 primary-only clamp never engages.
    ov.platform = types.SimpleNamespace(system=lambda: "Windows", mac_ver=lambda: ("", ("", "", ""), ""))

    MON1 = [(0, 0, 800, 600)]
    MON2 = [(0, 0, 800, 600), (800, 0, 800, 600)]
    current = {"monitors": MON1}
    ov.Overlay._get_monitors = lambda self: list(current["monitors"])

    o = ov.Overlay(mode="black", all_screens=True, watermark_enabled=False)
    o.start()
    check("start() with 1 monitor -> 1 window", len(o.windows) == 1, f"got {len(o.windows)}")

    current["monitors"] = MON2                       # a second monitor appears (dock / Win+P)
    o.show()
    check("show() after topology change -> 2 windows", len(o.windows) == 2, f"got {len(o.windows)}")
    geo = o.windows[1].geometry() if len(o.windows) > 1 else "?"
    check("second window positioned on second monitor", geo.startswith("800x600+800"), geo)
    check("overlay visible", o._is_visible)

    o.hide()
    current["monitors"] = MON1                       # back to a single monitor
    o.show()
    check("show() after monitor removed -> 1 window", len(o.windows) == 1, f"got {len(o.windows)}")

    o.hide()
    current["monitors"] = MON2
    o.hide()                                         # hide() must NOT rebuild (only show does)
    check("hide() does not rebuild windows", len(o.windows) == 1, f"got {len(o.windows)}")
    o.show()
    check("next show() picks the change up", len(o.windows) == 2, f"got {len(o.windows)}")

    o.stop()
    print(f"\n  RESULT: {sum(results)}/{len(results)} passed")
    return all(results)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
