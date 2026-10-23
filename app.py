"""NetCheck Dashboard — Min SiThu (devminsithu), https://minsithu.org
Copyright (c) 2026 Min SiThu (devminsithu). SPDX-License-Identifier: MIT
"""
import streamlit as st
from netcheck.checks import RECORD_TYPES, dns_check, normalize_host, ping_check, tcp_check
from netcheck.export import to_csv
from netcheck.insights import explain, compare

st.set_page_config(page_title='NetCheck Fieldnotes · Min SiThu', page_icon='◉', layout='wide')
st.markdown('''<style>
.block-container {max-width:1180px;padding-top:2.8rem;}
h1 {letter-spacing:-.045em;font-weight:750!important;}
[data-testid="stMetric"] {background:#EEE8DC;border:1px solid #CFC5B5;border-radius:14px;padding:18px;}
[data-testid="stSidebar"] {border-right:1px solid #CFC5B5;}
</style>''', unsafe_allow_html=True)
st.session_state.setdefault('history', [])
st.session_state.setdefault('baseline', {})
with st.sidebar:
    st.markdown('### ◉ Fieldnotes')
    st.caption('A NETWORK FIELD JOURNAL')
    st.divider()
    st.markdown('**One target. Clear answers.**')
    st.write('Check connectivity, inspect DNS, and test a TCP service from this machine.')
    timeout = st.slider('Timeout per operation (seconds)', 1, 10, 3)
    st.caption('Address lookup can make two DNS queries before a connection check.')
    st.divider()
    st.markdown('**Min SiThu**  \ndevminsithu')
    st.markdown('[Website](https://minsithu.org/) · [Contact](https://minsithu.org/contact/)')
    st.caption('© 2026 Min SiThu · MIT License')

st.caption('MIN SITHU / NETWORK FIELDNOTES / VOL. 01')
st.title('Follow the signal.')
st.write('Observe a host. Read the evidence. Keep a baseline.')
st.info('Checks run on the machine hosting this app. Use your local computer to test your own network.')
with st.form('diagnostics'):
    host = st.text_input('Hostname or IP address', placeholder='example.com or 192.168.1.1', max_chars=253)
    c1, c2, c3 = st.columns(3)
    with c1:
        do_ping = st.checkbox('Ping', value=True)
        st.caption('One ICMP echo request')
    with c2:
        do_dns = st.checkbox('DNS lookup', value=True)
        record = st.selectbox('Record type', RECORD_TYPES)
    with c3:
        do_tcp = st.checkbox('TCP connection', value=True)
        port = st.number_input('Port', min_value=1, max_value=65535, value=443)
    submitted = st.form_submit_button('Run diagnostics →', type='primary')
if submitted:
    try:
        host = normalize_host(host)
        if not any((do_ping, do_dns, do_tcp)):
            raise ValueError('Select at least one check.')
        with st.spinner('Running diagnostics…'):
            rows = []
            if do_ping:
                rows.append(ping_check(host, timeout))
            if do_dns:
                rows.append(dns_check(host, record, timeout))
            if do_tcp:
                rows.append(tcp_check(host, port, timeout))
        st.session_state['latest'] = rows
        st.session_state['latest_scope'] = (host, do_ping, record if do_dns else None, int(port) if do_tcp else None)
        st.session_state.history = (st.session_state.history + rows)[-500:]
    except ValueError as exc:
        st.error(str(exc))

latest = st.session_state.get('latest', [])
if latest:
    st.subheader('01 / The evidence')
    st.markdown('**Field interpretation**')
    for finding in explain(latest):
        st.write('— ' + finding)
    baseline_key = st.session_state['latest_scope']
    baseline = st.session_state.baseline.get(baseline_key)
    if baseline:
        with st.expander('Compare with pinned baseline', expanded=True):
            for change in compare(baseline, latest):
                st.write(change)
    if st.button('Pin these results as baseline'):
        st.session_state.baseline[baseline_key] = [dict(r) for r in latest]
        st.rerun()
    for col, row in zip(st.columns(len(latest)), latest):
        with col:
            st.metric(row['check'], row['status'])
            if row['latency_ms'] is not None:
                st.caption(f"{row['latency_ms']} ms · {row['target']}")
            else:
                st.caption(row['target'])
            with st.expander('Details'):
                st.code(row['details'], language=None)
else:
    st.caption('READY WHEN YOU ARE · Enter a target above to run your first check.')
st.divider()
st.subheader('02 / The field journal')
history = st.session_state.history
if history:
    st.dataframe(list(reversed(history)), hide_index=True, use_container_width=True)
    left, right = st.columns([1, 3])
    with left:
        st.download_button('↓ Export CSV', to_csv(history), 'netcheck-results.csv', 'text/csv')
    with right:
        if st.button('Clear history'):
            st.session_state.history = []
            st.session_state.pop('latest', None)
            st.session_state.baseline = {}
            st.rerun()
    st.caption('Last 500 checks in this browser session. Export before closing; history is not saved to disk.')
else:
    st.caption('Your diagnostic results will appear here.')
st.caption('Ping silence does not prove a device is offline. A TCP connection does not prove a service is healthy.')
