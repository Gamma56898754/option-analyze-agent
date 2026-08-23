from pathlib import Path
from tempfile import TemporaryDirectory

from memory.conversation_store import (
    ConversationStore,
)


def test_conversation_store():

    with TemporaryDirectory() as temp_dir:

        database_path = (
            Path(temp_dir)
            / "conversations.db"
        )

        store = ConversationStore(
            database_path
        )

        store.save_turn(
            thread_id="web-tsla",
            user_message=(
                "分析 TSLA 2026-08-17 的 GEX"
            ),
            assistant_message=(
                "这是 TSLA 的 GEX 分析。"
            ),
        )

        store.save_turn(
            thread_id="web-nvda",
            user_message=(
                "分析 NVDA 2026-08-21 的 DEX"
            ),
            assistant_message=(
                "这是 NVDA 的 DEX 分析。"
            ),
        )

        store.save_turn(
            thread_id="web-tsla",
            user_message="再详细解释一下",
            assistant_message="这是进一步解释。",
        )

        conversations = store.list_recent()

        assert len(conversations) == 2

        assert conversations[0][
            "thread_id"
        ] == "web-tsla"

        messages = store.get_messages(
            "web-tsla"
        )

        assert len(messages) == 4

        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
        assert messages[2]["content"] == (
            "再详细解释一下"
        )

        updated = store.update_title(
            thread_id="web-tsla",
            title="TSLA GEX 深度分析",
        )

        assert updated is True

        conversations = store.list_recent()

        assert conversations[0]["title"] == (
            "TSLA GEX 深度分析"
        )

    print(
        "Conversation store test passed."
    )


if __name__ == "__main__":
    test_conversation_store()