"""
Integration tests for PHYFlow CLI subcommands.
"""

import sys
from phyflow.cli import cmd_check_tools, cmd_version, build_parser


def test_cli_check_tools(capsys):
    parser = build_parser()
    args = parser.parse_args(["check-tools"])
    exit_code = cmd_check_tools(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "PHYFlow EDA & System Environment Tool Audit" in captured.out


def test_cli_version(capsys):
    parser = build_parser()
    args = parser.parse_args(["version"])
    exit_code = cmd_version(args)
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "1.0.0" in captured.out
