"""SpecBridge: separating computation and communication in data-agent evaluation.
  pd/        the trunk: SQL algebra, the grammar of database programs, catalogues and checks, explicit V
  comm/      the methodology: construct, verbal, diagnose, transfer, common
  archive/   superseded code kept as a record (inference experiments, paused tools, old experiment scripts)"""
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))     # the repository root: data folders live here, code under specbridge/
