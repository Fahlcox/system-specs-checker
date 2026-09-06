"""
System Specs Checker — a lightweight Streamlit app for inspecting
CPU, memory, disk, network and overall system health in real time.

Author: Super Z
License: MIT
"""

from __future__ import annotations

import datetime as _dt
import os
import platform
import socket
import time
from collections import defaultdict

import psutil
import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:  # pragma: no cover - optional dependency
    st_autorefresh = None


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="System Specs Checker",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Sidebar — controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🖥️ System Specs Checker")
    st.caption("A thin, real-time monitor for CPU, RAM, disk & network.")

    refresh_enabled = st.toggle("Auto-refresh", value=True, help="Poll the system every few seconds.")
    refresh_interval = st.slider(
        "Refresh interval (seconds)",
        min_value=2,
        max_value=30,
        value=5,
        step=1,
        disabled=not refresh_enabled,
    )

    st.divider()
    st.markdown("### Sections")
    show_overview = st.checkbox("System Overview", value=True)
    show_cpu = st.checkbox("CPU", value=True)
    show_memory = st.checkbox("Memory", value=True)
    show_disk = st.checkbox("Disk", value=True)
    show_network = st.checkbox("Network", value=True)
    show_processes = st.checkbox("Top Processes", value=True)
    show_sensors = st.checkbox("Sensors / Battery", value=True)

    st.divider()
    st.caption(f"Built with Streamlit & psutil\n\nRefreshed: {_dt.datetime.now():%H:%M:%S}")

if refresh_enabled and st_autorefresh is not None:
    st_autorefresh(interval=refresh_interval * 1000, key="specs_autorefresh")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def fmt_bytes(num: float) -> str:
    """Human-readable byte formatting."""
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if abs(num) < 1024.0:
            return f"{num:,.1f} {unit}"
        num /= 1024.0
    return f"{num:,.1f} EB"


def fmt_uptime(seconds: float) -> str:
    seconds = int(seconds)
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours or days:
        parts.append(f"{hours}h")
    if minutes or hours or days:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)


def usage_color(pct: float) -> str:
    if pct >= 90:
        return "🔴"
    if pct >= 70:
        return "🟠"
    if pct >= 40:
        return "🟡"
    return "🟢"


def metric_card(label, value, help_text=None):
    return st.metric(label=label, value=value, help=help_text)


# ---------------------------------------------------------------------------
# Title
# ---------------------------------------------------------------------------
st.title("🖥️ System Specs Checker")
st.caption(
    f"Live snapshot of `{socket.gethostname()}` — "
    f"updated {_dt.datetime.now():%Y-%m-%d %H:%M:%S}"
)
st.divider()


# ---------------------------------------------------------------------------
# System Overview
# ---------------------------------------------------------------------------
if show_overview:
    st.subheader("📋 System Overview")

    boot_time = _dt.datetime.fromtimestamp(psutil.boot_time())
    uptime_s = time.time() - psutil.boot_time()

    ov_col1, ov_col2, ov_col3, ov_col4 = st.columns(4)
    with ov_col1:
        st.metric("OS", f"{platform.system()} {platform.release()}")
        st.caption(platform.platform())
    with ov_col2:
        st.metric("Hostname", socket.gethostname())
        st.caption(f"Machine: {platform.machine()}")
    with ov_col3:
        st.metric("Booted at", boot_time.strftime("%Y-%m-%d %H:%M:%S"))
        st.caption(f"Uptime: {fmt_uptime(uptime_s)}")
    with ov_col4:
        py_impl = platform.python_implementation()
        st.metric("Python", platform.python_version())
        st.caption(f"{py_impl} on {platform.processor() or 'unknown CPU'}")

    try:
        users = psutil.users()
        if users:
            who = ", ".join(sorted({u.name for u in users}))
            st.info(f"👥 Logged-in users: **{who}**")
    except Exception:
        pass
    st.divider()


# ---------------------------------------------------------------------------
# CPU
# ---------------------------------------------------------------------------
if show_cpu:
    st.subheader("🧠 CPU")

    try:
        freq = psutil.cpu_freq()
    except Exception:
        freq = None

    cpu_percent = psutil.cpu_percent(interval=0.1)
    per_core = psutil.cpu_percent(interval=0.1, percpu=True)
    physical = psutil.cpu_count(logical=False) or 0
    logical = psutil.cpu_count(logical=True) or 0
    load_avg = getattr(os, "getloadavg", lambda: None)()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Logical Cores", logical, help="Total threads visible to the OS")
    c2.metric("Physical Cores", physical, help="Physical CPU packages × cores")
    c3.metric("Overall Usage", f"{cpu_percent:.1f} %")
    if freq:
        c4.metric("Current Frequency", f"{freq.current / 1000:.2f} GHz",
                  help=f"Min {freq.min / 1000:.2f} GHz · Max {freq.max / 1000:.2f} GHz")
    else:
        c4.metric("Current Frequency", "n/a")

    # Overall usage bar
    st.write(f"{usage_color(cpu_percent)} **Total CPU usage**")
    st.progress(min(cpu_percent / 100.0, 1.0))

    # Per-core breakdown
    if per_core:
        st.markdown("**Per-core usage**")
        cols = st.columns(min(len(per_core), 8))
        for idx, pct in enumerate(per_core):
            with cols[idx % len(cols)]:
                st.write(f"Core {idx}")
                st.progress(min(pct / 100.0, 1.0))
                st.caption(f"{pct:.0f}%")

    if load_avg:
        st.caption(
            f"Load average (1/5/15 min): "
            f"{load_avg[0]:.2f} · {load_avg[1]:.2f} · {load_avg[2]:.2f}"
        )
    st.divider()


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------
if show_memory:
    st.subheader("💾 Memory")

    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total RAM", fmt_bytes(vm.total))
    m2.metric("Available", fmt_bytes(vm.available))
    m3.metric("Used", fmt_bytes(vm.used))
    m4.metric("RAM Usage", f"{vm.percent:.1f} %")

    st.write(f"{usage_color(vm.percent)} **RAM in use**")
    st.progress(min(vm.percent / 100.0, 1.0))

    if sm.total > 0:
        sm1, sm2, sm3 = st.columns(3)
        sm1.metric("Swap Total", fmt_bytes(sm.total))
        sm2.metric("Swap Used", fmt_bytes(sm.used))
        sm3.metric("Swap Usage", f"{sm.percent:.1f} %")
        st.progress(min(sm.percent / 100.0, 1.0))
    else:
        st.caption("Swap: disabled / not configured")
    st.divider()


# ---------------------------------------------------------------------------
# Disk
# ---------------------------------------------------------------------------
if show_disk:
    st.subheader("💿 Disk")

    du = psutil.disk_usage("/")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Total", fmt_bytes(du.total))
    d2.metric("Used", fmt_bytes(du.used))
    d3.metric("Free", fmt_bytes(du.free))
    d4.metric("Usage", f"{du.percent:.1f} %")
    st.write(f"{usage_color(du.percent)} **Root filesystem (`/`) usage**")
    st.progress(min(du.percent / 100.0, 1.0))

    st.markdown("**All mounted partitions**")
    parts = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except PermissionError:
            continue
        except Exception:
            continue
        parts.append({
            "Mount": part.mountpoint,
            "Device": part.device,
            "FS": part.fstype,
            "Total": fmt_bytes(usage.total),
            "Used": fmt_bytes(usage.used),
            "Free": fmt_bytes(usage.free),
            "Usage %": usage.percent,
        })
    if parts:
        st.dataframe(parts, use_container_width=True, hide_index=True)
    else:
        st.caption("No readable partitions found.")

    # Disk I/O
    try:
        io = psutil.disk_io_counters()
        if io:
            io1, io2, io3, io4 = st.columns(4)
            io1.metric("Read (total)", fmt_bytes(io.read_bytes))
            io2.metric("Written (total)", fmt_bytes(io.write_bytes))
            io3.metric("Read ops", f"{io.read_count:,}")
            io4.metric("Write ops", f"{io.write_count:,}")
    except Exception:
        pass
    st.divider()


# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------
if show_network:
    st.subheader("🌐 Network")

    addrs = psutil.net_if_addrs()
    io_net = psutil.net_io_counters()

    n1, n2, n3, n4 = st.columns(4)
    n1.metric("Bytes Sent", fmt_bytes(io_net.bytes_sent))
    n2.metric("Bytes Recv", fmt_bytes(io_net.bytes_recv))
    n3.metric("Packets Sent", f"{io_net.packets_sent:,}")
    n4.metric("Packets Recv", f"{io_net.packets_recv:,}")

    st.markdown("**Network interfaces**")
    iface_rows = []
    for name, addr_list in addrs.items():
        for addr in addr_list:
            if addr.family == socket.AF_INET:
                iface_rows.append({
                    "Interface": name,
                    "Family": "IPv4",
                    "Address": addr.address,
                    "Netmask": addr.netmask,
                    "Broadcast": addr.broadcast or "-",
                })
            elif addr.family == socket.AF_INET6:
                iface_rows.append({
                    "Interface": name,
                    "Family": "IPv6",
                    "Address": addr.address,
                    "Netmask": addr.netmask or "-",
                    "Broadcast": "-",
                })
    if iface_rows:
        st.dataframe(iface_rows, use_container_width=True, hide_index=True)
    else:
        st.caption("No network interfaces detected.")
    st.divider()


# ---------------------------------------------------------------------------
# Top Processes
# ---------------------------------------------------------------------------
if show_processes:
    st.subheader("⚙️ Top Processes")
    sort_by = st.radio(
        "Sort by",
        options=["CPU %", "Memory %"],
        horizontal=True,
        key="proc_sort",
    )

    procs = []
    for p in psutil.process_iter(attrs=["pid", "name", "username", "cpu_percent", "memory_percent"]):
        try:
            info = p.info
            info["cpu_percent"] = info.get("cpu_percent") or 0.0
            info["memory_percent"] = info.get("memory_percent") or 0.0
            procs.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # prime cpu_percent on first run (needs two samples)
    if all(p["cpu_percent"] == 0.0 for p in procs):
        _ = psutil.cpu_percent(interval=0.1, percpu=False)
        for p in psutil.process_iter(attrs=["pid", "name", "username", "cpu_percent", "memory_percent"]):
            try:
                procs = [
                    {**p.info, "cpu_percent": p.info.get("cpu_percent") or 0.0,
                     "memory_percent": p.info.get("memory_percent") or 0.0}
                    for p in psutil.process_iter(
                        attrs=["pid", "name", "username", "cpu_percent", "memory_percent"]
                    )
                ]
            except Exception:
                break

    key = "cpu_percent" if sort_by == "CPU %" else "memory_percent"
    procs.sort(key=lambda x: x.get(key) or 0.0, reverse=True)
    top = procs[:15]

    rows = [
        {
            "PID": p.get("pid"),
            "Name": p.get("name") or "-",
            "User": p.get("username") or "-",
            "CPU %": f"{(p.get('cpu_percent') or 0.0):.1f}",
            "Memory %": f"{(p.get('memory_percent') or 0.0):.1f}",
        }
        for p in top
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.divider()


# ---------------------------------------------------------------------------
# Sensors / Battery
# ---------------------------------------------------------------------------
if show_sensors:
    st.subheader("🌡️ Sensors & Battery")
    sen_col, bat_col = st.columns(2)

    with sen_col:
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                rows = []
                for name, entries in temps.items():
                    for e in entries:
                        rows.append({
                            "Sensor": name,
                            "Label": e.label or "-",
                            "Current (°C)": f"{e.current:.1f}",
                            "High (°C)": f"{e.high:.1f}" if e.high else "-",
                            "Critical (°C)": f"{e.critical:.1f}" if e.critical else "-",
                        })
                st.dataframe(rows, use_container_width=True, hide_index=True)
            else:
                st.caption("No temperature sensors available on this platform.")
        except AttributeError:
            st.caption("Temperature sensors not supported on this OS.")

    with bat_col:
        try:
            bat = psutil.sensors_battery()
            if bat:
                plugged = "yes 🔌" if bat.power_plugged else "no 🔋"
                st.metric("Battery", f"{bat.percent:.0f}%")
                if bat.secsleft not in (psutil.POWER_TIME_UNLIMITED, psutil.POWER_TIME_UNKNOWN):
                    st.caption(f"Time left: {fmt_uptime(bat.secsleft)} · Plugged in: {plugged}")
                else:
                    st.caption(f"Plugged in: {plugged}")
            else:
                st.caption("No battery detected.")
        except AttributeError:
            st.caption("Battery sensor not supported on this OS.")
    st.divider()


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.caption(
    "Tip: deploy this on [Streamlit Community Cloud](https://streamlit.io/cloud) — "
    "include `requirements.txt` with `streamlit`, `psutil` and `streamlit-autorefresh`."
)
