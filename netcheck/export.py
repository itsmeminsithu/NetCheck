"""CSV export with spreadsheet formula escaping.
Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
"""
import csv
import io

FIELDS = ('timestamp', 'check', 'target', 'status', 'latency_ms', 'details')


def to_csv(rows):
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=FIELDS)
    writer.writeheader()
    for row in rows:
        safe = {}
        for key in FIELDS:
            value = row.get(key, '')
            if isinstance(value, str) and value.lstrip().startswith(('=', '+', '-', '@')):
                value = "'" + value
            safe[key] = value
        writer.writerow(safe)
    return output.getvalue().encode('utf-8-sig')
