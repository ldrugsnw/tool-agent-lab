import json
import logging

import pytest

import tool_runner


def test_success_records_name_arguments_and_elapsed(monkeypatch, caplog):
    monkeypatch.setattr(tool_runner, "days_until", lambda date: 12)
    with caplog.at_level(logging.INFO, logger="tool_runner"):
        result = tool_runner.execute_tool(
            "days_until", '{"target_date":"2027-08-16"}', lambda _: False
        )

    event = json.loads(caplog.records[-1].message)
    assert result == "12"
    assert event["tool"] == "days_until"
    assert event["arguments"] == {"target_date": "2027-08-16"}
    assert event["success"] is True
    assert event["elapsed_ms"] >= 0


@pytest.mark.parametrize(
    "arguments,tool_failure",
    [
        ('{"target_date":', False),
        ('{"target_date":"bad"}', False),
        ('{"target_date":"2027-08-16"}', True),
    ],
)
def test_bad_arguments_or_tool_exception_return_error(
    arguments, tool_failure, monkeypatch, caplog
):
    if tool_failure:
        def fail(_):
            raise OSError("temporary disk failure")

        monkeypatch.setattr(tool_runner, "days_until", fail)
    with caplog.at_level(logging.INFO, logger="tool_runner"):
        result = tool_runner.execute_tool("days_until", arguments, lambda _: False)

    assert result.startswith("도구 실행 실패:")
    assert json.loads(caplog.records[-1].message)["status"] == "error"


def test_denied_write_does_not_touch_file(tmp_path, monkeypatch, caplog):
    monkeypatch.chdir(tmp_path)
    with caplog.at_level(logging.INFO, logger="tool_runner"):
        result = tool_runner.execute_tool(
            "save_note", '{"text":"비공개 메모"}', lambda _: False
        )

    assert "거절" in result
    assert not (tmp_path / "notes.txt").exists()
    assert json.loads(caplog.records[-1].message)["status"] == "denied"
