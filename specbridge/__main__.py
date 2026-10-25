"""python -m specbridge <stage> ... -- the pipeline door (specbridge.comm.__main__)."""
import runpy, sys
sys.argv[0] = "specbridge.comm"
runpy.run_module("specbridge.comm", run_name="__main__")
