import json

from dotenv import load_dotenv
from openai import OpenAI

from tools import get_current_time, days_until, save_note



load_dotenv()
client = OpenAI()

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
            "text": {
                "type": "string",
                "description": "파일에 저장할 한 줄의 학습 기록",
            }
        },
        "required": ["text"],
        "additionalProperties": False,
    },
    "strict": True,
    }
]

response = client.responses.create(
    model="gpt-5-nano",
    input=input("질문> "),
    tools=tools,
)

for step in range(5):  # 무한히 도구를 호출하지 않도록 제한
    calls = [
        item for item in response.output
        if item.type == "function_call"
    ]

    if not calls:
        print("모델의 최종 답변:", response.output_text)
        break

    tool_outputs = []

    for call in calls:
        args = json.loads(call.arguments)
        print("모델의 도구 요청:", call.name, args)

        if call.name == "get_current_time":
            result = get_current_time()
        elif call.name == "days_until":
            result = days_until(args["target_date"])
        elif call.name == "save_note":
            text = args["text"]
            print(f"저장할 내용: {text}")
            approval = input("notes.txt에 저장할까? [y/N] ").strip().lower()

            if approval == "y":
                result = save_note(text)
            else:
                result = "사용자가 저장을 거절함. 파일을 변경하지 않았음."
        else:
            raise ValueError(f"허용하지 않은 도구: {call.name}")

        print("Python 함수 실행 결과:", result)
        tool_outputs.append({
            "type": "function_call_output",
            "call_id": call.call_id,
            "output": str(result),
        })

    response = client.responses.create(
        model="gpt-5-nano",
        previous_response_id=response.id,
        input=tool_outputs,
        tools=tools,
    )
else:
    print("도구 호출 횟수 제한에 도달했어.")


