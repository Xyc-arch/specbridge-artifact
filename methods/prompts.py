"""Prompts of the two methods, copied verbatim from the experiment code (tests/test_prompts.py checks the copies).
  DETECT       the disclosure method's first call: list the readings, each rewritten as a request with one reading
  PLAIN        the single-call SQL prompt used for every request text in the rewrite test (schema, documentation, request)
  INSTRUCTION  the explanation call of Finding 1 (main SQL, open assumptions, up to two alternatives)
  TELL         appended to DtP's interpretation prompt to ask for the one interpretation with a given meaning (arm b)
  CONDENSE     LangChain's condense-question prompt (ConversationalRetrievalChain), without "in its original language" (arm d)
The disclosure method answers each reading with DtP's released SQL prompt (third_party/dtp_prompts.py, user_message_sql)."""

DETECT = 'You are given a database and a question about it. Decide whether the question has more than one reasonable reading on THIS\ndatabase -- readings that a careful analyst could each intend and that would give different answers. If it has one reading, return\nit unchanged. If it has several, rewrite the question once per reading, each rewrite fully specified so that it has exactly one\nreading. Do not invent readings the question rules out.\n\nDatabase:\n%s\n\nQuestion:\n%s\n\nAnswer ONLY JSON: {"readings": ["<question rewritten for reading 1>", ...]}'

PLAIN = 'Answer the request with SQL for the database below.\n\nDATABASE SCHEMA:\n%s\n\nDATABASE DOCUMENTATION:\n%s\n\nREQUEST:\n%s\n\nAnswer ONLY JSON: {"sql": "your query"}'

INSTRUCTION = 'Answer the request with SQL for the database below. Briefly state any consequential assumption that the request and\nthe supplied context do not settle. If another interpretation is supported, describe it and give its SQL. Do not invent alternatives\nwhen the context settles the choice.\n\nDATABASE SCHEMA:\n%s\n\nDATABASE DOCUMENTATION:\n%s\n\nREQUEST:\n%s\n\nAnswer ONLY JSON: {"sql": "your primary query", "assumptions": [{"assumption": "what your primary query assumes", "unresolved": true|false}],\n"alternatives": [{"interpretation": "another supported reading, in words", "sql": "..."}]}\nAt most two alternatives; an empty list when the request settles its meaning.'

TELL = '\n\nThe question is meant in this way: {}\nWrite exactly ONE interpretation: the one with this meaning. One line, no explanation.'

CONDENSE = 'Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question.\n\nChat History:\nHuman: {}\nFollow Up Input: {}\nStandalone question:'
