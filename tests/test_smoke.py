import importlib


def test_package_is_importable() -> None:
    module = importlib.import_module("ja_guard")
    assert module.__doc__
