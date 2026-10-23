"""Bounded, single-target diagnostics. No shell interpolation or port scanning.
Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
"""
import ipaddress
import os
import platform
import re
import shutil
import socket
import subprocess
import time
from datetime import datetime, timezone

import dns.exception
import dns.resolver

RECORD_TYPES = ('A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA')


def normalize_host(value):
    host = value.strip()
    if not host or len(host) > 253 or '%' in host:
        raise ValueError('Enter a hostname or IP address, without a URL, path or port.')
    try:
        return str(ipaddress.ip_address(host))
    except ValueError:
        pass
    try:
        host = host.rstrip('.').encode('idna').decode('ascii').lower()
    except UnicodeError as exc:
        raise ValueError('Invalid hostname.') from exc
    if not all(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', part)
               for part in host.split('.')):
        raise ValueError('Enter a hostname or IP address, without a URL, path or port.')
    return host


def result(check, target, status, details, latency_ms=None):
    return dict(timestamp=datetime.now(timezone.utc).isoformat(timespec='seconds'),
                check=check, target=target, status=status,
                latency_ms=latency_ms, details=details)


def addresses(host, timeout=3):
    """Use bounded DNS queries; avoid unbounded system getaddrinfo calls."""
    try:
        return [str(ipaddress.ip_address(host))]
    except ValueError:
        pass
    if host == 'localhost':
        return ['127.0.0.1', '::1']
    resolver = dns.resolver.Resolver()
    found = []
    errors = []
    for kind in ('A', 'AAAA'):
        try:
            found.extend(str(record) for record in resolver.resolve(host, kind, lifetime=timeout))
        except dns.exception.DNSException as exc:
            errors.append(type(exc).__name__)
    if not found:
        raise ValueError('Address resolution failed: ' + ', '.join(errors))
    return found


def ping_check(host, timeout=3):
    host = normalize_host(host)
    executable = shutil.which('ping')
    if not executable:
        return result('Ping', host, 'Unavailable', 'The system ping utility is not installed.')
    try:
        address = addresses(host, timeout)[0]
    except (ValueError, dns.exception.DNSException) as exc:
        return result('Ping', host, 'Error', str(exc))
    system = platform.system()
    args = [executable]
    if ':' in address:
        if system == 'Darwin':
            executable6 = shutil.which('ping6')
            if not executable6:
                return result('Ping', host, 'Unavailable', 'IPv6 requires ping6 on macOS.')
            args = [executable6]
        else:
            args.append('-6')
    args += ['-n', '1', '-w', str(timeout * 1000)] if system == 'Windows' else ['-n', '-c', '1']
    args.append(address)
    try:
        completed = subprocess.run(args, capture_output=True, text=True, errors='replace',
                                   timeout=timeout + 1, env={**os.environ, 'LC_ALL': 'C'})
    except subprocess.TimeoutExpired:
        return result('Ping', host, 'No reply', 'Timed out. ICMP may be filtered; this does not prove the host is offline.')
    except OSError as exc:
        return result('Ping', host, 'Error', str(exc))
    output = (completed.stdout + completed.stderr).strip()
    match = re.search(r'time[=<]\s*([\d.]+)\s*ms', output, re.I)
    latency = float(match.group(1)) if match else None
    if completed.returncode == 0:
        return result('Ping', host, 'Reply received', output, latency)
    return result('Ping', host, 'No reply', output + '\nNo reply is not proof that the host is offline.')


def dns_check(host, record_type='A', timeout=3):
    host = normalize_host(host)
    if record_type not in RECORD_TYPES:
        raise ValueError('Unsupported DNS record type.')
    start = time.perf_counter()
    try:
        answer = dns.resolver.resolve(host, record_type, lifetime=timeout, search=False)
        return result('DNS ' + record_type, host, 'Resolved', '\n'.join(str(r) for r in answer),
                      round((time.perf_counter() - start) * 1000, 2))
    except dns.resolver.NXDOMAIN:
        return result('DNS ' + record_type, host, 'Not found', 'DNS returned NXDOMAIN.')
    except dns.resolver.NoAnswer:
        return result('DNS ' + record_type, host, 'No records', 'No records of this type were returned.')
    except dns.exception.Timeout:
        return result('DNS ' + record_type, host, 'Timed out', 'The DNS resolver did not respond in time.')
    except dns.exception.DNSException as exc:
        return result('DNS ' + record_type, host, 'Error', str(exc))


def tcp_check(host, port=443, timeout=3):
    host = normalize_host(host)
    port = int(port)
    if not 1 <= port <= 65535:
        raise ValueError('Port must be between 1 and 65535.')
    try:
        ips = addresses(host, timeout)
    except (ValueError, dns.exception.DNSException) as exc:
        return result('TCP', host, 'Error', str(exc))
    # One selected service, with a total connect budget across resolved addresses.
    deadline = time.monotonic() + timeout
    failures = []
    for address in ips:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            failures.append('Connection budget exhausted')
            break
        family = socket.AF_INET6 if ':' in address else socket.AF_INET
        try:
            with socket.socket(family, socket.SOCK_STREAM) as sock:
                sock.settimeout(remaining)
                start = time.perf_counter()
                sock.connect((address, port))
                latency = round((time.perf_counter() - start) * 1000, 2)
            return result('TCP', host, 'Connected', f'{address}:{port} accepted a TCP connection. This does not verify application health.', latency)
        except ConnectionRefusedError:
            failures.append(f'{address}:{port}: connection refused')
        except (TimeoutError, socket.timeout):
            failures.append(f'{address}:{port}: timed out (possibly filtered)')
        except OSError as exc:
            failures.append(f'{address}:{port}: {exc}')
    return result('TCP', host, 'Not connected', '\n'.join(failures))
