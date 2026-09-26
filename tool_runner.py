import json
from time import perf_counter

from tools import days_until, get_current_time, save_note


def execute_tool(name: str, args: dict, approve_save) -> str:
    if name == "get_current_time":
        return get_current_time()

    if name == "days_until":
        return str(days_until(args["target_date"]))

    if name == "save_note":
        text = args["text"]
        if approve_save(text):
            return save_note(text)
        return "사용자가 저장을 거절함. 파일을 변경하지 않았음."

    raise ValueError(f"허용하지 않은 도구: {name}")



def handle_tool_call(name: str, raw_arguments: str, approve_save) -> str:
    started = perf_counter()
    success = True

    try:
        args = json.loads(raw_arguments)
        if not isinstance(args, dict):
            raise ValueError("도구 인자는 JSON 객체여야 함")

        result = execute_tool(name, args, approve_save)
    except (json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
        success = False
        result = f"도구 실행 실패: {exc}"

    elapsed_ms = (perf_counter() - started) * 1000
    print(
        f"도구 기록: name={name}, args={raw_arguments}, "
        f"success={success}, elapsed_ms={elapsed_ms:.2f}"
    )
    return str(result)