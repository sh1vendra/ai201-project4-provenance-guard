# Setup

## Prerequisites

- Python 3.10+
- pip

## Create and activate a virtual environment

### Mac / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Configure environment

```bash
cp .env.example .env
# Edit .env and set your GROQ_API_KEY
```
