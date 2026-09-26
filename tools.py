from datetime import date, datetime
from zoneinfo import ZoneInfo

def get_current_time() -> str:
    """현재 한국 시간을 반환한다."""
    return datetime.now(ZoneInfo("Asia/Seoul")).isoformat()


def days_until(target_date: str) -> int:
    """YYYY-MM-DD 날짜까지 남은 일수를 반환한다."""
    target = date.fromisoformat(target_date)
    today = datetime.now(ZoneInfo("Asia/Seoul")).date()
    return (target - today).days

def save_note(text: str) -> str:
    with open("notes.txt", "a", encoding="utf-8") as file:
        file.write(text + "\n")

    return "저장 완료"
