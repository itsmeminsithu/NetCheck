# NetCheck Fieldnotes

A network troubleshooting dashboard by **Min SiThu (devminsithu)**.

[Website](https://minsithu.org/) · [Contact](https://minsithu.org/contact/) · [MIT License](LICENSE)

Give it one host. It pings it, reads its DNS records, tests a TCP port, and exports what it found. Python and Streamlit. No API keys, no paid services.

## What it checks

- Ping, one shot, with response time when the system utility reports one
- DNS: A, AAAA, MX, NS, TXT, CNAME and SOA
- One TCP port at a time, against IPv4 and IPv6 targets
- Timeouts you can set, failures shown as failures, and the raw ping output
- History for the session (the 500 most recent checks), CSV export, a clear-history control
- A short summary of what the results point to
- Baselines: pin one, then compare status, details and latency on later runs of the same checks
- Baselines and history are session-only. Clearing history clears baselines too
- Input validation, no shell in the process calls, CSV formula escaping
- Tests (pytest)

## Start it — macOS or Linux

Python 3.11 or newer. In a terminal, in this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://127.0.0.1:8501. Ctrl+C stops it. Next time: activate `.venv`, run the last command again.

On Debian/Ubuntu, if ping is missing, install your distribution's `iputils-ping` package.

## Start it — Windows (Command Prompt)

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Trying it in Codespaces

Streamlit apps cannot run on GitHub Pages, so use Codespaces for a browser preview:

1. On GitHub, click **Code → Codespaces → Create codespace on main** (after this change is merged).
2. The devcontainer installs `requirements.txt` and forwards port **8501**.
3. In the Codespaces terminal: `python -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true`.
4. Open forwarded port **8501** in the Ports panel.

## A first run

Type `example.com`, leave DNS type A and TCP port 443 selected, press **Run diagnostics**.

For your router, use its real LAN IP and a service it actually exposes. Nothing runs until you press the button — there is no background scanning. And a DNS lookup on an IP literal is not a reverse/PTR lookup.

## What the results mean

| Result | Meaning |
| --- | --- |
| Reply received | An ICMP echo reply arrived |
| No reply | ICMP was unanswered or failed; the host may still be online |
| Resolved | DNS returned records of the selected type |
| Not found | DNS returned NXDOMAIN |
| No records | No answer for the selected record type |
| Connected | The selected port accepted a TCP connection |
| Not connected | Refused, timed out or another connection error; inspect details |
| Unavailable | A required system utility is missing |

The three timings are not the same measurement. Ping time comes from system output, DNS time is query duration, TCP time is connection duration. Ping time can also be missing on localized Windows installs, and for Windows `time<1ms` the 1ms shown is an upper bound, not an exact figure.

Resolution uses your configured DNS servers — not hosts-file or mDNS resolution, except for the explicit localhost shortcut. Ping uses the first resolved address. TCP tries addresses inside one total connection budget. Each A/AAAA lookup has its own timeout.

## Privacy and where not to run it

This is built for local use. It binds to 127.0.0.1 by default, and checks run from the machine running Python, not from the browser. Put it on a remote server and you are testing that server's network — and possibly opening up its internal network to whoever can reach the page. Do not expose an unauthenticated instance publicly.

Only test systems you own or are allowed to troubleshoot. Targets go to your configured DNS resolvers and to the hosts you select. There is no database and no telemetry of my own; Streamlit usage telemetry is disabled. History sits in session memory, not on disk, and a new session or a restart can clear it. CSV exports can contain private IPs and diagnostic details, so read them before sharing or committing.

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

DNS and ping are mocked; TCP tests use a local listener. No internet needed.

## Files

- `app.py`: Streamlit interface and session history
- `netcheck/checks.py`: validation, DNS, ping and TCP diagnostics
- `netcheck/insights.py`: result summaries and baseline comparison
- `netcheck/export.py`: safe CSV serialization
- `test_*.py`: unit, local TCP integration and UI tests
- `.devcontainer/devcontainer.json`: Codespaces preview (port 8501)

## Author and license

Copyright © 2026 **Min SiThu (devminsithu)**.
[minsithu.org](https://minsithu.org/) · [Contact](https://minsithu.org/contact/)

Source is distributed under the [MIT License](LICENSE). Third-party packages keep their own licenses.
