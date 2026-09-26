import json
import logging

from dotenv import load_dotenv
from openai import OpenAI

from tool_runner import execute_tool


tools = [
    {
        "type": "function",
        "name": "get_current_time",
        "description": "현재 한국 시간을 확인한다.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "days_until",
        "description": "특정 날짜까지 남은 일수를 계산한다. 날짜는 YYYY-MM-DD 형식으로 받는다.",
        "parameters": {
            "type": "object",
            "properties": {
                "target_date": {
                    "type": "string",
                    "description": "목표 날짜, 예: 2027-08-16",
                }
            },
            "required": ["target_date"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "save_note",
        "description": "사용자가 명시적으로 기록해 달라고 요청한 내용을 notes.txt에 저장한다.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "파일에 저장할 한 줄의 학습 기록"}
            },
            "required": ["text"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def approve_save(text: str) -> bool:
    print(f"저장할 내용: {text}")
    return input("notes.txt에 저장할까? [y/N] ").strip().lower() == "y"


def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    client = OpenAI()
    response = client.responses.create(
        model="gpt-5-nano",
        input=input("질문> "),
        tools=tools,
    )
    failures = 0

    for _ in range(5):
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            print("모델의 최종 답변:", response.output_text)
            return

        tool_outputs = []
        for call in calls:
            result = execute_tool(call.name, call.arguments, approve_save)
            print(f"도구 결과 ({call.name}): {result}")
            if result.startswith("도구 실행 실패:"):
                failures += 1
            tool_outputs.append(
                {"type": "function_call_output", "call_id": call.call_id, "output": result}
            )

        response = client.responses.create(
            model="gpt-5-nano",
            previous_response_id=response.id,
            input=tool_outputs,
            tools=tools,
            tool_choice="none" if failures >= 2 else "auto",
        )

    print("도구 호출 횟수 제한에 도달했어.")


if __name__ == "__main__":
    main()
