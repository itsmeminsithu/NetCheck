# Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
from netcheck.checks import result
from netcheck.insights import compare, explain


def test_filtered_ping_is_not_offline():
    rows = [result('TCP', 'example.com', 'Connected', ''), result('Ping', 'example.com', 'No reply', '')]
    assert any('do not mark this host offline' in note for note in explain(rows))


def test_baseline_status_change():
    old = [result('TCP', 'example.com', 'Not connected', 'refused')]
    new = [result('TCP', 'example.com', 'Connected', 'accepted', 2)]
    assert 'Not connected → Connected' in compare(old, new)[0]
