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


# BACKEND (2026-10-25). The paper's runs used the two CLIs above, which stay the default. SPECBRIDGE_BACKEND=api sends the same
# prompt and system text over HTTP instead: Claude models to the Anthropic Messages API (ANTHROPIC_API_KEY), every other model to
# an OpenAI-compatible chat endpoint (OPENAI_API_KEY; OPENAI_BASE_URL points it at another provider or a local server, so any
# model can be plugged in by name). The CLIs add their own system prompt, so API answers can differ slightly from the saved runs.
BACKEND = os.environ.get("SPECBRIDGE_BACKEND", "cli")
# PINNED MODEL IDS (2026-10-26). The CLI resolves a short name ("haiku") to its newest model: "haiku" was
# claude-haiku-4-5-20251001 up to 2026-10-03 and claude-haiku-5-5 from 2026-10-11 (Claude CLI session logs), so one name
# covered two models. Every call now names the full ID; the short names stay the labels in file paths and reports.
MODEL_ID = {"haiku": "claude-haiku-4-5-20251001", "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}
API_ID = MODEL_ID


def _post(url, body, headers, timeout):
    import urllib.error
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=dict(headers, **{"Content-Type": "application/json"}))
            return json.loads(urllib.request.urlopen(req, timeout=timeout).read())
        except urllib.error.HTTPError as e:                           # retry overload and rate limits, not bad requests
            if e.code not in (408, 429, 500, 502, 503, 504, 529) or attempt == 4: raise
        except OSError:
            if attempt == 4: raise
        time.sleep(5 * (attempt + 1))


def _api(prompt, model, system, timeout):
    if model in CLI or model.startswith("claude"):
        body = {"model": API_ID.get(model, model), "max_tokens": int(os.environ.get("SPECBRIDGE_MAX_TOKENS", 16000)),
                "messages": [{"role": "user", "content": prompt}]}
        if system: body["system"] = system
        d = _post(os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/") + "/v1/messages", body,
                  {"x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""), "anthropic-version": "2023-06-01"}, timeout)
        u = d.get("usage") or {}
        USAGE.last.update({"resolved": [d.get("model")], "input_tokens": u.get("input_tokens"), "output_tokens": u.get("output_tokens")})
        return "".join(b.get("text", "") for b in d.get("content") or [] if b.get("type") == "text")
    body = {"model": model, "messages": ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]}
    if model.startswith("gpt-") and not os.environ.get("OPENAI_BASE_URL"): body["reasoning_effort"] = CODEX_EFFORT
    d = _post(os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/") + "/chat/completions", body,
              {"Authorization": "Bearer " + os.environ.get("OPENAI_API_KEY", "")}, timeout)
    u = d.get("usage") or {}
    USAGE.last.update({"resolved": [d.get("model")], "total_tokens": u.get("total_tokens")})
    return (d.get("choices") or [{}])[0].get("message", {}).get("content") or ""


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
        if BACKEND == "api" and (model.startswith(("gpt-", "claude")) or model in CLI or os.environ.get("OPENAI_BASE_URL")):
            out = _api(prompt, model, system, max(timeout, 300))
            if LIMIT.search(out): raise RuntimeError("model call failed: %s" % out[:120])
        elif model.startswith("gpt-"):
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
            cmd = [_CLAUDE or "claude", "-p", "--model", MODEL_ID.get(model, model), "--output-format", "json", "--tools", ""]
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
