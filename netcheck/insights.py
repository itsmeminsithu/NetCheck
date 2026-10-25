"""Evidence-based field notes, without overclaiming root causes.
Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
"""


def explain(rows):
    statuses = {row['check']: row['status'] for row in rows}
    notes = []
    if statuses.get('TCP') == 'Connected':
        notes.append('The selected TCP service accepted a connection from this machine.')
        if statuses.get('Ping') == 'No reply':
            notes.append('TCP responded despite ping silence. ICMP may be filtered; do not mark this host offline.')
    elif statuses.get('TCP') == 'Not connected':
        notes.append('The TCP connection failed. Inspect its details for refusal, timeout or routing errors.')
    if statuses.get('Ping') == 'Reply received' and statuses.get('TCP') == 'Not connected':
        notes.append('The host answered ICMP, but the selected service did not connect. Check the port, service and firewall.')
    for row in rows:
        if row['check'].startswith('DNS') and row['status'] == 'Resolved':
            notes.append('The requested DNS records were returned. DNS success alone does not verify the service.')
        elif row['check'].startswith('DNS') and row['status'] != 'Resolved':
            notes.append('The DNS query did not return records. Inspect its status before drawing a connectivity conclusion.')
    if not notes:
        notes.append('Read the individual results below; these checks do not establish a root cause by themselves.')
    return notes


def compare(baseline, current):
    previous = {(r['check'], r['target']): r for r in baseline}
    changes = []
    for row in current:
        old = previous.get((row['check'], row['target']))
        if not old:
            continue
        label = row['check']
        if old['status'] != row['status']:
            changes.append(f"{label}: {old['status']} → {row['status']}")
        if old['details'] != row['details']:
            changes.append(f'{label}: diagnostic details changed; inspect the latest evidence.')
        if old['latency_ms'] is not None and row['latency_ms'] is not None:
            delta = row['latency_ms'] - old['latency_ms']
            changes.append(f'{label}: {delta:+.2f} ms versus baseline (single measurement).')
    return changes or ['No status or diagnostic detail changes detected.']
