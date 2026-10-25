# Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from netcheck.checks import result

APP = str(Path(__file__).resolve().parents[0] / 'app.py')


def test_ui_validation():
    app = AppTest.from_file(APP).run()
    assert not app.exception
    app.button[0].click().run()
    assert app.error
    assert not app.exception


def test_run_and_clear():
    row = result('Ping', 'example.com', 'Reply received', 'sample reply', 1.2)
    with patch('netcheck.checks.ping_check', return_value=row), patch('netcheck.checks.dns_check', return_value={**row, 'check': 'DNS A'}), patch('netcheck.checks.tcp_check', return_value={**row, 'check': 'TCP'}):
        app = AppTest.from_file(APP).run()
        app.text_input[0].set_value('example.com')
        app.button[0].click().run()
        assert not app.exception
        assert len(app.session_state['history']) == 3
        assert len(app.metric) == 3
        next(b for b in app.button if b.label == 'Clear history').click().run()
        assert not app.exception
        assert app.session_state['history'] == []
