* DOCME: refer github contribution guide
* DOCME: our requirements

## Testing

### Create Environment

Run these commands just the first time:

```bash
# Ensure python3 is installed
python3 -m venv .venv
source .venv/bin/activate
pip install nox
```

### Enter Environment

Run this command once you open a new shell:

```bash
source .venv/bin/activate
```

### Test Your Changes

```bash
# test
nox -R
```

## Project Structure

The project contains these files and directories:

| File/Directory | Description |
|---|---|
| `src/` | Python Package Sources - the files this is all about. |
| `pyproject.toml` | Python Package Meta File. Also contains all tool settings. |
| `.gitignore` | Lists of files and directories ignored by version control system. |
| `.github/` | Github Settings. |
| `.readthedocs.yaml` | Documentation Server Configuration. |
| `.pre-commit-config.yaml` | Pre-Commit Check Configuration. |

Next to that, there are some temporary files ignored by version control system.

| File/Directory | Description |
|---|---|
| `pdm.lock` | File with resolved python package dependencies |
| `htmlcov/` | Test Execution Code Coverage Report in HTML format. |
| `report.xml` | Test Execution Report. |
| `.*_cache/` | Cache Directory. |
| `.nox/` | [NOX][nox] directory. |
| `.venv*` | Virtual Environments |
