"""Model access for the methods and the benchmark runner. Every method takes a plain callable ask(prompt) -> reply text, so any
model can be plugged in. make_ask(name) returns the callable the paper's runs used: specbridge.pd.ask.ask, which calls Claude
models through the `claude` CLI and OpenAI models through `codex exec`, both sealed (no tools, an empty working directory).
Usage of the last call (resolved model, tokens, list cost, seconds) is in specbridge.pd.ask.USAGE.last."""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def make_ask(model, timeout=1500):
    from specbridge.pd.ask import ask
    return lambda prompt: ask(prompt, model, timeout=timeout, quiet=True)
