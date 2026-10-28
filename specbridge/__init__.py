"""SpecBridge: separating computation and communication in data-agent evaluation.
  pd/        the trunk: SQL algebra, the grammar of database programs, catalogues and checks, explicit V
  comm/      the methodology: construct, verbal, diagnose, transfer, common
  archive/   superseded code kept as a record (inference experiments, paused tools, old experiment scripts)"""
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))     # the repository root: data folders live here, code under specbridge/
try:                                       # SQL runs on the SQLite 3.42 that sqlean.py bundles, when installed (requirements.txt):
    import sqlean as _sq, sys as _sys       # SQLite 3.43 and later sum floats differently, which changes a few results
    _sys.modules["sqlite3"] = _sq
except ImportError: pass
