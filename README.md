# 🖥️ System Specs Checker

A thin, real-time **Streamlit** app for inspecting your machine's
**CPU, RAM, disk, network, processes and sensors** — all in a clean browser UI.

It uses [`psutil`](https://github.com/giampaolo/psutil) for the heavy lifting
and [`streamlit-autorefresh`](https://github.com/khalido/streamlit-autorefresh)
for live polling.

![Python](https://img.shields.io/badge/python-3.9+-blue) ![Streamlit](https://img.shields.io/badge/streamlit-1.30+-red) ![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- **System Overview** — OS, hostname, uptime, boot time, Python version, logged-in users.
- **CPU** — logical & physical cores, frequency, total & per-core usage, load average.
- **Memory** — total / available / used RAM, swap stats.
- **Disk** — root filesystem usage, every mounted partition, disk I/O counters.
- **Network** — bytes/packets sent & received, per-interface IPv4 / IPv6 addresses.
- **Top Processes** — sortable by CPU % or memory %, top 15.
- **Sensors / Battery** — temperatures and battery state (where supported by the OS).
- **Auto-refresh** toggle with adjustable interval (2–30 s).
- Color-coded usage indicators (🟢🟡🟠🔴) for quick health checks.

## 🚀 Run locally

```bash
git clone https://github.com/<your-user>/<this-repo>.git
cd <this-repo>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the printed local URL (usually `http://localhost:8501`).

## ☁️ Deploy on Streamlit Community Cloud

1. Push this repository to GitHub (public or private).
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Pick this repo, set the main file to `app.py`, and the Python environment will
   install from `requirements.txt` automatically.
4. Click **Deploy**. Your monitor will be live in ~1–2 minutes.

## 🗂️ Project layout

```
.
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml        # Streamlit theme / server config
└── README.md
```

## ⚠️ Notes

- Some sections (sensors, battery) are OS-dependent and may show "not supported"
  on certain platforms or inside containers — that's expected.
- Running as a non-root user may hide a few partitions/processes; this is
  normal OS-level access control, not a bug.
- `streamlit-autorefresh` is optional: if unavailable, the app still works with
  manual `R`-key refreshes.

## 📜 License

MIT — do whatever you like, no warranty.
