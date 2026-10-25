"""COMM: generate executable data tasks, diagnose how benchmark questions communicate them, and transfer those communication
patterns to generated tasks as controlled question variants.  (docs/PIPELINE.md)

  1. construct   specbridge.comm.construct   ported P (pd's generator output) and database-first P -> frozen tasks with explicit V
  2. diagnose    specbridge.comm.diagnose    benchmark question vs explicit V of its reference -> inspected disagreements -> a library
                                  of reviewed interpretation choices with alternative SQL and communication analyses
  3. transfer    specbridge.comm.transfer    choice points proposed and verified by execution on generated tasks -> precise natural
                                  and open natural questions (plan, write, review) -> evaluation against explicit V
  common         specbridge.comm.common      model calls (sealed, cached), database access and graders, the batched solver

P (the query generator) and V (specbridge.pd.spec.render: explicit specification) live in pd/. This package only uses them."""
