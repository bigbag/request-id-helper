import runpy
from pathlib import Path


def test_basic_usage_example_runs() -> None:
    runpy.run_path(Path("examples/basic_usage.py"), run_name="__main__")


def test_async_propagation_example_runs() -> None:
    runpy.run_path(Path("examples/async_propagation.py"), run_name="__main__")
