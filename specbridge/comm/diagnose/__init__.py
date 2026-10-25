"""PART 2 -- DIAGNOSE COMMUNICATION IN A REAL BENCHMARK (BIRD). For a batch of benchmark questions:
  1 tasks     the original question + evidence and the reference SQL; explicit V of the reference (refusals recorded)  tasks.py
  2 compare   the same solver on both wordings, same database, documentation and grading (BIRD set match; tolerance
              0.005 reported beside it)                                                                                 compare.py
  3 inspect   every task whose arms disagree: the concrete difference, and the element of explicit V that supplied it   inspect.py
  4 record    separate agent mistakes, interpretation choices, reference defects and tool defects; for a supported
              choice: alternative SQL, executed difference, two blind reviewers (mutually recognized | disputed), and
              the communication analysis (how the real question carries each requirement)                              record.py
  5 gate      an independent judgment per record: confidence and category (meaning choice | output form | reference
              defect | uncertain)                                                                                        gate.py
  6 repair    a record whose alternative mixes several decisions: isolate the choice, re-execute, re-review           repair.py
  7 library   the collections: meaning retrieval, output-form retrieval, review pool                                   library.py
Solver disagreements prioritise cases; they do not reveal every ambiguity. The held-out split is never run or inspected.
    python -m specbridge.comm.diagnose.<stage> ...   (each module's docstring gives its command)"""
LIB = "out/comm_library"
