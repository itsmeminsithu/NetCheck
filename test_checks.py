# Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
import csv
import io
import socket
import subprocess
from types import SimpleNamespace
from unittest.mock import patch

import dns.resolver
import pytest
from netcheck.checks import addresses, dns_check, normalize_host, ping_check, tcp_check
from netcheck.export import to_csv


@pytest.mark.parametrize('value', ['https://example.com', '-c 99', 'a;b', 'a/b', 'x:443', '', 'bad host', 'a..b', 'fe80::1%eth0'])
def test_reject_invalid_targets(value):
    with pytest.raises(ValueError):
        normalize_host(value)


@pytest.mark.parametrize('value,expected', [(' EXAMPLE.COM. ', 'example.com'), ('::1', '::1'), ('127.0.0.1', '127.0.0.1'), ('münich.de', 'xn--mnich-kva.de')])
def test_normalize(value, expected):
    assert normalize_host(value) == expected


def test_dns_outcomes():
    with patch('dns.resolver.resolve', return_value=['192.0.2.1']):
        assert dns_check('example.com')['status'] == 'Resolved'
    for error, status in [(dns.resolver.NXDOMAIN, 'Not found'), (dns.resolver.NoAnswer, 'No records'), (dns.exception.Timeout, 'Timed out')]:
        with patch('dns.resolver.resolve', side_effect=error):
            assert dns_check('example.com')['status'] == status


def test_ping_missing():
    with patch('shutil.which', return_value=None):
        assert ping_check('127.0.0.1')['status'] == 'Unavailable'


def test_ping_parsing_and_shell_free():
    with patch('shutil.which', return_value='/usr/bin/ping'), patch('platform.system', return_value='Linux'), patch('subprocess.run', return_value=SimpleNamespace(returncode=0, stdout='time=0.42 ms', stderr='')) as run:
        row = ping_check('127.0.0.1')
        assert row['latency_ms'] == 0.42
        assert run.call_args.args[0] == ['/usr/bin/ping', '-n', '-c', '1', '127.0.0.1']
        assert not run.call_args.kwargs.get('shell', False)


def test_ping_timeout():
    with patch('shutil.which', return_value='ping'), patch('subprocess.run', side_effect=subprocess.TimeoutExpired('ping', 4)):
        assert ping_check('127.0.0.1')['status'] == 'No reply'


def test_tcp_local_listener():
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        listener.listen(1)
        row = tcp_check('127.0.0.1', listener.getsockname()[1])
        assert row['status'] == 'Connected'
        assert row['latency_ms'] >= 0


def test_tcp_refused():
    with patch('socket.socket') as factory:
        factory.return_value.__enter__.return_value.connect.side_effect = ConnectionRefusedError()
        assert 'refused' in tcp_check('127.0.0.1')['details']


def test_bad_port():
    with pytest.raises(ValueError):
        tcp_check('localhost', 65536)


def test_resolution_failure():
    with patch('dns.resolver.Resolver') as resolver:
        resolver.return_value.resolve.side_effect = dns.resolver.NXDOMAIN()
        assert tcp_check('missing.example')['status'] == 'Error'


def test_export_escapes_formulas_and_preserves_multiline():
    data = to_csv([{'target': 'example.com', 'details': '=DANGEROUS()\nsecond line'}])
    row = next(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))
    assert row['details'] == "'=DANGEROUS()\nsecond line"
