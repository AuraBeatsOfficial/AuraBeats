# Contributing to AuraBeats

Workflow:
1. Fork the repository
2. Create branch: git checkout -b feat/your-feature
3. Fill in the relevant shell file
4. Test locally: python AuraBeats
5. Open a pull request

Code style:
- Python 3.11+
- PEP-8
- Async-first (Pyrogram, Motor, aiohttp)
- Type hints on public functions
- No hard-coded secrets (use config.py)

Commit format:
  scope: short description

Scope examples: core, plugins, utils, database, docs
