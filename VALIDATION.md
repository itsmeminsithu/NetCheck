# Validation

Validated on Linux with Python 3.12, Streamlit 1.66.1 and dnspython 2.9.0.

- 26 pytest tests passed.
- Python source compilation passed.
- Real local TCP listener connection passed.
- Streamlit AppTest covered initial render, invalid input, diagnostic results and history clearing.
- External DNS and ping outcomes were mocked; live external network checks were not validated.
- The included GitHub Actions matrix has not yet run on GitHub.
- macOS and Windows runtime behavior has not been manually tested.

Run `python -m pytest -q` from the project folder to reproduce the tests.
