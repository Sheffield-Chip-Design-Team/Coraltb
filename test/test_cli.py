import argparse
import logging
import types

import pytest
from coral.cli import coral as coral_cli

@pytest.mark.parametrize(
    "verbosity, quiet, expected_level",
    [
        (0, False, logging.WARNING),
        (1, False, logging.INFO),
        (2, False, logging.DEBUG),
        (1, True, logging.ERROR),
    ],
)
def test_setup_logging_selects_expected_level(monkeypatch, verbosity, quiet, expected_level):
    captured = {}

    def fake_basicConfig(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(logging, "basicConfig", fake_basicConfig)

    coral_cli.setup_logging(verbosity, quiet)

    assert captured["level"] == expected_level
    assert "handlers" in captured
    assert captured["format"] == "[%(name)s] %(message)s"


def test_main_discovers_registers_and_dispatches(monkeypatch):
    calls = {"register_called": False, "func_called": False, "args": None, "logger": None}

    def command_func(args, logger):
        calls["func_called"] = True
        calls["args"] = args
        calls["logger"] = logger

    def register(subparsers):
        calls["register_called"] = True
        parser = subparsers.add_parser("fake")
        parser.add_argument("--value", default="ok")
        parser.set_defaults(func=command_func)

    fake_module = types.SimpleNamespace(register=register)

    # Simulate one discovered command module
    monkeypatch.setattr(
        coral_cli.pkgutil,
        "iter_modules",
        lambda _path: [types.SimpleNamespace(name="fake")],
    )
    monkeypatch.setattr(coral_cli.importlib, "import_module", lambda _name: fake_module)
    monkeypatch.setattr(coral_cli.sys, "argv", ["coral", "fake", "--value", "hello"])

    # Avoid touching real logging config in test
    monkeypatch.setattr(coral_cli, "setup_logging", lambda *_args, **_kwargs: None)

    coral_cli.main()

    assert calls["register_called"] is True
    assert calls["func_called"] is True
    assert calls["args"].command == "fake"
    assert calls["args"].value == "hello"
    assert isinstance(calls["logger"], logging.Logger)


def test_main_passes_quiet_flag_to_setup_logging(monkeypatch):
    captured = {"verbosity": None, "quiet": False}  # Initialize 'quiet' with a boolean value

    def fake_setup_logging(verbosity, quiet=False):
        captured["verbosity"] = verbosity
        captured["quiet"] = quiet

    def command_func(args, logger):
        return None

    def register(subparsers):
        parser = subparsers.add_parser("fake")
        parser.set_defaults(func=command_func)

    fake_module = types.SimpleNamespace(register=register)

    monkeypatch.setattr(
        coral_cli.pkgutil,
        "iter_modules",
        lambda _path: [types.SimpleNamespace(name="fake")],
    )
    monkeypatch.setattr(coral_cli.importlib, "import_module", lambda _name: fake_module)
    monkeypatch.setattr(coral_cli, "setup_logging", fake_setup_logging)
    monkeypatch.setattr(coral_cli.sys, "argv", ["coral", "-q", "fake"])

    coral_cli.main()

    assert captured["verbosity"] is False
    assert captured["quiet"] is True


def test_main_requires_command(monkeypatch):
    # No discovered command modules -> parser still requires a command -> SystemExit
    monkeypatch.setattr(coral_cli.pkgutil, "iter_modules", lambda _path: [])
    monkeypatch.setattr(coral_cli.sys, "argv", ["coral"])
    monkeypatch.setattr(coral_cli, "setup_logging", lambda *_args, **_kwargs: None)

    with pytest.raises(SystemExit):
        coral_cli.main()