"""PART 1 -- CONSTRUCT TASKS ON A DATABASE. Two sources of P, one freezing step:
  ported   P fitted on source SQL and bound to the target by pd's generator; its accepted queries are frozen   (ported.py)
  dbfirst  database-first structural families instantiated where the catalogue and the data support them  (dbfirst.py)
  freeze   the shared gate: semantic compatibility (lift + spec), execution, a non-trivial answer (1-2,000 rows), a
           grader that can decide the answer (ties at a cut, rounding), and explicit V as the instruction   (freeze.py)
Explicit V states the whole specification, so a task tests implementing a fully specified computation."""
