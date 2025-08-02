# Insider QA Automation Suite

This repository contains a Selenium-based test automation suite for Insider's
Quality Assurance job listings, implemented using the Page Object Model.

## Setup

1. **Create a virtual environment (Optional)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # or `.venv\\Scripts\\activate` on Windows
   ```

2. **Install requirements**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Running Tests

```bash
pytest -v
```

## Extending

- Add new page objects in `pages/`.
- Write new test cases in `tests/`.

---

Note: I kept the delay a little longer to avoid incorrect results from the filter. You should wait a few seconds. And finally, sometimes you might encounter a bug when you adjust the dimensions of the opened test page, so it would be better not to touch it for efficiency reasons.
