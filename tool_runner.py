import json
import logging
from time import perf_counter
from typing import Callable

from tools import days_until, get_current_time, save_note


logger = logging.getLogger(__name__)


def execute_tool(
    name: str,
    raw_arguments: str,
    approve_save: Callable[[str], bool],
) -> str:
    """Execute one requested tool and return a safe result for the model."""
    started = perf_counter()
    status = "success"
    arguments = None

    try:
        arguments = json.loads(raw_arguments)
        if not isinstance(arguments, dict):
            raise ValueError("도구 인자는 JSON 객체여야 함")

        if name == "get_current_time":
            if arguments:
                raise ValueError("get_current_time은 인자를 받지 않음")
            result = get_current_time()
        elif name == "days_until":
            if set(arguments) != {"target_date"} or not isinstance(arguments["target_date"], str):
                raise ValueError("target_date는 YYYY-MM-DD 문자열이어야 함")
            result = days_until(arguments["target_date"])
        elif name == "save_note":
            if set(arguments) != {"text"} or not isinstance(arguments["text"], str):
                raise ValueError("text는 문자열이어야 함")
            if approve_save(arguments["text"]):
                result = save_note(arguments["text"])
            else:
                status = "denied"
                result = "사용자가 저장을 거절함. 파일을 변경하지 않았음."
        else:
            raise ValueError("허용하지 않은 도구")

        return str(result)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError, OSError) as exc:
        status = "error"
        return f"도구 실행 실패: {type(exc).__name__}. 입력을 확인하거나 다른 방법으로 답해줘."
    finally:
        logger.info(
            json.dumps(
                {
                    "tool": name,
                    "arguments": arguments if arguments is not None else raw_arguments,
                    "status": status,
                    "success": status == "success",
                    "elapsed_ms": round((perf_counter() - started) * 1000, 2),
                },
                ensure_ascii=False,
            )
        )
