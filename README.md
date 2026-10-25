# ◉ NetCheck Fieldnotes

A network troubleshooting dashboard by **Min SiThu (devminsithu)**.

[Website](https://minsithu.org/) · [Contact](https://minsithu.org/contact/) · [MIT License](LICENSE)

Check one host, understand its DNS records, test a TCP service, and export your results.
Built with Python and Streamlit. No API keys or paid services required.

## Features

- One-shot ping with response time when the system utility reports it
- DNS queries: A, AAAA, MX, NS, TXT, CNAME and SOA
- Single TCP port connectivity test, including IPv4 and IPv6 targets
- Configurable timeouts, explicit failure states and raw ping output
- Session history (500 most recent checks), CSV export and clear-history control
- Diagnostic summaries based on check results
- Pin a baseline and compare status, details and latency for the same checks
- Baselines and history are session-only; clearing history also clears baselines
- Input validation, shell-free process execution and CSV formula escaping
- Automated tests (pytest)

## Start on macOS or Linux

Install Python 3.11 or newer, then open a terminal in this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://127.0.0.1:8501. Stop with Ctrl+C. Next time, activate `.venv` and run the last command again.
On Debian/Ubuntu, if ping is missing, install your distribution's `iputils-ping` package.

## Live preview (GitHub Codespaces)

This is a Streamlit app, so it cannot run on GitHub Pages. Preview it in Codespaces instead:

1. On GitHub, click **Code → Codespaces → Create codespace on main** (after this change is merged).
2. The devcontainer installs `requirements.txt` automatically and forwards port **8501**.
3. In the Codespaces terminal, run `python -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true`.
4. Open the forwarded port **8501** from the Ports panel.

## Start on Windows (Command Prompt)

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Try it

Enter `example.com`, leave DNS type A and TCP port 443 selected, then press **Run diagnostics**.
For your router, enter its actual LAN IP and select a service it exposes.
Queries run only after you press the button; there is no background scanning.
DNS lookup on an IP literal is not a reverse/PTR lookup.

## Reading results

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

Ping time comes from system output and can be absent on localized Windows installations.
DNS time is query duration; TCP time is connection duration. They measure different things.
For Windows `time<1ms`, the displayed 1ms is an upper bound, not an exact measurement.
Address resolution uses your configured DNS servers (not hosts-file or mDNS resolution,
except the explicit localhost shortcut). Ping uses the first resolved address. TCP tries
addresses within one total connection budget. Each A/AAAA lookup has its own timeout.

## Privacy and deployment

Designed for local use; the default bind address is 127.0.0.1. Checks originate from
the machine running Python, not from the browser. Hosting this on a remote server
will test that server's network and may expose its internal network to users.
Do not expose an unauthenticated instance publicly. Only test systems you own or
are authorized to troubleshoot. Targets are sent to configured DNS resolvers and
selected hosts. There is no application database or custom telemetry. Streamlit
usage telemetry is disabled. History lives in session memory, not durable storage.
A new session or server restart may clear it. CSV exports can contain private IPs
and diagnostic details; review before sharing or committing.

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests mock external DNS and ping and use a local TCP listener. No Internet access required.

## Project structure

- `app.py`: Streamlit interface and session history
- `netcheck/checks.py`: validation, DNS, ping and TCP diagnostics
- `netcheck/insights.py`: result summaries and baseline comparison
- `netcheck/export.py`: safe CSV serialization
- `test_*.py`: unit, local TCP integration and UI tests
- `.devcontainer/devcontainer.json`: Codespaces preview (port 8501)

## Author and license

Copyright © 2026 **Min SiThu (devminsithu)**.
[minsithu.org](https://minsithu.org/) · [Contact](https://minsithu.org/contact/)

Project source is distributed under the [MIT License](LICENSE). Third-party
packages retain their own licenses.
