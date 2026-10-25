"""MODEL CALLS through specbridge.pd.ask (the one door: sealed, no tools, an empty working directory), plus a JSON reader. Pass `cache=<dir>` to store every reply under the hash of (model, prompt) as soon as it returns, so a
stage rerun reuses finished calls."""
import collections, hashlib, json, os, re, threading

CALLS = collections.Counter()      # model calls actually made in this process (cache hits excluded), by model
_LOCK = threading.Lock()


def call(prompt, model):
    """One sealed model call (specbridge.pd.ask: no tools, empty working directory). "" when the call fails."""
    from specbridge.pd.ask import ask
    return ask(prompt, model, timeout=1500, quiet=True)


def parse(txt, brace="{"):
    m = re.search(r"\{.*\}" if brace == "{" else r"\[.*\]", txt or "", re.S)
    try: return json.loads(m.group(0))
    except Exception: return None


def ask_json(prompt, model, brace="{", cache=None):
    """The reply parsed as a JSON object (brace "{") or list (brace "["); None when it does not parse."""
    if cache:
        os.makedirs(cache, exist_ok=True)
        f = "%s/%s.json" % (cache, hashlib.sha256((model + "\0" + brace + "\0" + prompt).encode()).hexdigest()[:24])
        if os.path.exists(f): return json.load(open(f))["reply"]
    with _LOCK: CALLS[model] += 1
    r = parse(call(prompt, model), brace)
    if cache and r is not None: json.dump({"model": model, "reply": r}, open(f, "w"))
    return r
