import pytest

from tool_runner import execute_tool, handle_tool_call

def test_days_until_returns_result():
    result = execute_tool(
        "days_until",
        {"target_date": "2027-08-16"},
        lambda text: False,
    )
    assert result.isdigit()


def test_invalid_date_raises_value_error():
    with pytest.raises(ValueError):
        execute_tool(
            "days_until",
            {"target_date": "내일"},
            lambda text: False,
        )


def test_denied_save_does_not_create_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = execute_tool(
        "save_note",
        {"text": "저장하지 않을 기록"},
        lambda text: False,
    )

    assert "거절" in result
    assert not (tmp_path / "notes.txt").exists()



@pytest.mark.parametrize(
    "raw_arguments, expected_success",
    [
        ('{"target_date": "2027-08-16"}', True),
        ("{", False),
        ('{"target_date": "내일"}', False),
    ],
)
def test_handle_tool_call_logs_success_and_failures(
    raw_arguments, expected_success, capsys
):
    result = handle_tool_call(
        "days_until",
        raw_arguments,
        lambda text: False,
    )
    output = capsys.readouterr().out

    assert "name=days_until" in output
    assert f"success={expected_success}" in output
    assert "elapsed_ms=" in output

    if expected_success:
        assert result.isdigit()
    else:
        assert result.startswith("도구 실행 실패:")