"""specbridge.pd.ask — ONE WAY TO ASK A MODEL ANYTHING. Four modules had their own.

`pd.say`, `pd.solve`, `specbridge.pd.realize.vocab` and `pd.agent` each carried a copy of "POST a prompt to ollama and read
the reply". They were not identical, and the differences were not decisions -- they were whatever the
module happened to need on the day it was written:

    say      cached, stripped, 120s              vocab     uncached, stripped, 120s
    solve    uncached, RAW, 300s, CLI models     agent     cached to its own file, "" on failure

AND ONLY `solve` COULD REACH A CLI MODEL. `haiku` and its kin do not speak the ollama protocol; they go
through `claude -p`, and only the solver knew that. So the DESCRIBER and the NAMER -- the two parts that
write words into the corpus -- physically could not use the model this project names as its validator
default, and nothing said so. A capability gap hiding inside a duplication, which is the argument for
this file: copies do not just drift, they quietly differ in what they can do at all.

Every difference above is now an argument. Caching is per-caller, because a namer asks the same thing
hundreds of times in a build and a solver never repeats a prompt.
"""
from __future__ import annotations
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.request

from specbridge.pd.models import CLI

OLLAMA = "http://localhost:11434/api/generate"
import re
LIMIT = re.compile(r"hit your (session|usage|weekly) limit|usage limit reached|rate limit|credit balance is too low", re.I)

# ONE SEALED DIRECTORY, NOT ONE PER CALL. A temp dir per question left 253 of them behind in a single
# evening and bought nothing: what makes the directory safe is that it is EMPTY, and one empty directory
# is as empty as two hundred. Resolved once, too, so a PATH lookup is not repeated under load.
_SEALED = tempfile.mkdtemp(prefix="sealed-solver-")
_CLAUDE = shutil.which("claude")
_CODEX = shutil.which("codex")

# OPENAI MODELS through `codex exec`, sealed the same two ways as `claude -p` (2026-10-02): every tool feature off (the shell
# and exec tools, browser, computer use, apps, plugins, sub-agents, images, hooks, web search), user config ignored (no
# plugins or MCP servers), read-only sandbox, the same empty working directory, nothing persisted. Probed: asked to list a
# directory, gpt-5.5 answered "NO TOOLS". Reasoning effort is fixed here, not inherited from ~/.codex/config.toml.
CODEX_EFFORT = "medium"
_CODEX_OFF = ["shell_tool", "unified_exec", "browser_use", "computer_use", "apps", "plugins", "multi_agent",
              "image_generation", "in_app_browser", "view_image", "hooks"]


def codex_cmd(model, out):
    cmd = [_CODEX or "codex", "exec", "-m", model, "-c", 'model_reasoning_effort="%s"' % CODEX_EFFORT, "-c", 'web_search="disabled"',
           "--ignore-user-config", "--ephemeral", "--skip-git-repo-check", "-s", "read-only", "-C", _SEALED, "-o", out]
    for f in _CODEX_OFF: cmd += ["--disable", f]
    return cmd + ["-"]


# USAGE OF THE LAST CALL IN THIS THREAD (2026-10-14): resolved model id, tokens, list cost (Claude) or total tokens (Codex),
# seconds. Read by callers that record cost per call; never part of the answer.
USAGE = threading.local()


def ask(prompt, model, n=256, timeout=120, cache=None, strip=True, quiet=False, system=""):
    """One answer from `model`.

    `cache` is a dict the caller owns and persists however it likes; `quiet` returns "" instead of
    raising, for a build that would rather carry on than stop because a server is down.
    """
    if cache is not None and prompt in cache:
        return cache[prompt]
    USAGE.last = {"model": model}; t0 = time.time()
    try:
        if model.startswith("gpt-"):
            for attempt in range(4):
                fd, out_f = tempfile.mkstemp(suffix=".txt"); os.close(fd)
                try:
                    p = subprocess.run(codex_cmd(model, out_f), input=(system + "\n\n" if system else "") + prompt,
                                       capture_output=True, text=True, cwd=_SEALED, timeout=max(timeout, 300))
                    out = open(out_f).read()
                    tu = re.search(r"tokens used\s*\n\s*([\d,]+)", p.stderr or "")
                    if tu: USAGE.last["total_tokens"] = int(tu.group(1).replace(",", ""))
                    if out.strip() or attempt == 3: break
                except (OSError, subprocess.TimeoutExpired):
                    if attempt == 3: raise
                finally:
                    os.remove(out_f)
                time.sleep(1.5 * (attempt + 1))
        elif model in CLI or model.startswith("claude"):
            # A SOLVER MAY NOT READ THE REPOSITORY IT IS BEING MEASURED IN.
            #
            # `claude -p` inherits this process's working directory and runs with its tools enabled, so
            # every CLI-model answer this project has ever recorded was written by a model that could
            # open `out/corpus/*/bench.jsonl` -- the gold SQL and the gold ANSWER for the very question
            # it was being asked -- along with all of `pd/`. Found 2026-09-22 because sonnet refused two
            # questions and cited `specbridge/pd/reads.py:30-32` and `specbridge/pd/english.py:50` BY LINE NUMBER in its reply.
            #
            # Sealed two ways, because either alone is a single point of failure: no tools at all, and a
            # working directory that holds nothing. A solver is given the schema, the notes and the
            # question, and that is the whole of what the measurement claims it had.
            # SAY WHAT THE JOB IS. Sealed -- no tools, empty directory -- a CLI model has no context at
            # all, and reads "write one SQLite query" as a request to EXECUTE one: three of six trivial
            # prompts came back "I can't execute SQL" or "I'm not sure what you're looking for", and in
            # the first sealed run 37 of 60 haiku answers were chat rather than SQL, scored as wrong.
            # The unsealed runs did not show this because the repository was ambient context -- which is
            # to say the leak was also propping the measurement up. `system` states the task and nothing
            # about the answer, so it cannot help a solver be right.
            # 2026-09-30: sealed with NO tools at all (`--tools ""`), stronger than disallowing a list, and the reply
            # read from JSON output; this was a second door in comm/ and is now the only one.
            cmd = [_CLAUDE or "claude", "-p", "--model", model, "--output-format", "json", "--tools", ""]
            if system: cmd += ["--append-system-prompt", system]
            # A SPAWN THAT FAILED IS NOT AN ANSWER. Each call starts a Node process, and under six-wide
            # load the 2026-09-22 panel began failing with `Exec format error: 'claude'` at call 55 and
            # never recovered -- 62 of 180 rows, all of sonnet among them. The binary was present the
            # whole time (`which claude` resolves it); the system could not START it. Retried with a
            # short backoff, because the alternative is recording "the model got it wrong".
            for attempt in range(4):
                try:
                    raw = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                                         cwd=_SEALED, timeout=max(timeout, 300)).stdout
                    d = json.loads(raw); out = d.get("result") or ""
                    u = d.get("usage") or {}
                    USAGE.last.update({"resolved": sorted(d.get("modelUsage") or {}), "cost_usd": d.get("total_cost_usd"),
                                       "input_tokens": sum(u.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
                                       "output_tokens": u.get("output_tokens")})
                    # A LIMIT OR ERROR REPLY IS NOT AN ANSWER (2026-10-03): during a usage limit the CLI returns "You've hit
                    # your session limit ..." as the result text; 448 solver answers and 788 disclosure responses were saved as
                    # if a model had said it. Raised here, so callers see a failed call ("" when quiet) and never store it.
                    if d.get("is_error") or LIMIT.search(out): raise RuntimeError("model call failed: %s" % out[:120])
                    break
                except (OSError, FileNotFoundError, ValueError, subprocess.TimeoutExpired):
                    if attempt == 3: raise
                    time.sleep(1.5 * (attempt + 1))
        else:
            req = urllib.request.Request(
                OLLAMA,
                data=json.dumps({"model": model, "prompt": prompt, "stream": False,
                                 "options": {"temperature": 0, "num_predict": n}}).encode(),
                headers={"Content-Type": "application/json"})
            out = json.loads(urllib.request.urlopen(req, timeout=timeout).read())["response"]
    except Exception:
        if not quiet: raise
        out = ""
    USAGE.last["seconds"] = round(time.time() - t0, 1)
    if strip: out = out.strip()
    if cache is not None: cache[prompt] = out
    return out
