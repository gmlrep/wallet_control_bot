import pytest

from bot.handlers.keyboard import kb_list_addr, kb_settings


class DummyDatabase:
    async def find_address(self, **filter_by):
        assert filter_by == {"user_id": 42}
        return {
            "EQ1234567890ABCDE": "Main wallet",
            "UQABCDEFGHIJKLMNO": None,
        }

    async def find_user_status(self, **filter_by):
        assert filter_by == {"user_id": 42}
        return True


@pytest.mark.asyncio
async def test_kb_list_addr_builds_named_and_shortened_buttons():
    markup = await kb_list_addr(user_id=42, db=DummyDatabase())

    rows = [[button.text for button in row] for row in markup.inline_keyboard]

    assert rows == [
        ["Main wallet"],
        ["UQABC..KLMNO"],
        ["✏️ Редактировать"],
        ["◀️ Назад"],
    ]


@pytest.mark.asyncio
async def test_kb_settings_reflects_enabled_report_flag():
    markup = await kb_settings(user_id=42, db=DummyDatabase())

    rows = [[button.text for button in row] for row in markup.inline_keyboard]

    assert rows == [["✅ Отчет"], ["◀️ Назад"]]
