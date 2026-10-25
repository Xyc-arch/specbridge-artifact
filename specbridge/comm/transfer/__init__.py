"""PART 3 -- TRANSFER COMMUNICATION PATTERNS TO GENERATED TASKS.
  choice_points  per task, every interpretation choice: proposed with data facts, B as exact edits of the task's SQL,
                 decided by code (edits apply, B runs, B changes the answer under the task's own grader = load-bearing,
                 B renders in explicit V, pairs combine), one batched repair round, then reviewed        choice_points.py
  render         one choice point per task: a plan (shared requirements, choice A/B, evidence, readings without outcomes),
                 precise A, precise B as exact edits of precise A, and the open question; fidelity and interpretation
                 (interp-v7) reviewed separately; one revision                                           render.py
  evaluate       one hidden intention per task (balanced); the solver on explicit V, precise natural and open natural;
                 intended match | either recorded reading | neither                                        evaluate.py
The open questions reproduce recorded communication patterns, not the full distribution of how people ask."""
