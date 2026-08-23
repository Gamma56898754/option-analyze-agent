import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from contextlib import closing


class ConversationStore:
    """
    Store product-level conversation metadata and full display messages.

    LangGraph checkpoints remain responsible for Agent state,
    summaries, and short-term memory.
    """

    def __init__(
        self,
        database_path: str | Path,
    ):

        self.database_path = Path(
            database_path
        )

        self.database_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:

        connection = sqlite3.connect(
            self.database_path
        )

        connection.row_factory = sqlite3.Row

        return connection

    def _initialize_database(self) -> None:

        with closing(self._connect()) as connection, connection:

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    thread_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id TEXT NOT NULL,
                    role TEXT NOT NULL
                        CHECK (
                            role IN (
                                'user',
                                'assistant'
                            )
                        ),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_messages_thread_id_id
                ON messages (
                    thread_id,
                    id
                )
                """
            )

    def create_or_touch(
        self,
        thread_id: str,
        first_message: str | None = None,
    ) -> None:

        now = self._utc_now()

        with closing(self._connect()) as connection, connection:

            existing_conversation = (
                connection.execute(
                    """
                    SELECT thread_id
                    FROM conversations
                    WHERE thread_id = ?
                    """,
                    (thread_id,),
                ).fetchone()
            )

            if existing_conversation is None:

                connection.execute(
                    """
                    INSERT INTO conversations (
                        thread_id,
                        title,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        thread_id,
                        self._make_title(
                            first_message
                        ),
                        now,
                        now,
                    ),
                )

                return

            connection.execute(
                """
                UPDATE conversations
                SET updated_at = ?
                WHERE thread_id = ?
                """,
                (
                    now,
                    thread_id,
                ),
            )

    def save_turn(
        self,
        thread_id: str,
        user_message: str,
        assistant_message: str,
    ) -> None:

        self.create_or_touch(
            thread_id=thread_id,
            first_message=user_message,
        )

        now = self._utc_now()

        with closing(self._connect()) as connection, connection:

            connection.executemany(
                """
                INSERT INTO messages (
                    thread_id,
                    role,
                    content,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        thread_id,
                        "user",
                        user_message,
                        now,
                    ),
                    (
                        thread_id,
                        "assistant",
                        assistant_message,
                        now,
                    ),
                ],
            )

    def list_recent(
        self,
        limit: int = 30,
    ) -> list[dict[str, str]]:

        with closing(self._connect()) as connection, connection:

            rows = connection.execute(
                """
                SELECT
                    thread_id,
                    title,
                    created_at,
                    updated_at
                FROM conversations
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def get_messages(
        self,
        thread_id: str,
    ) -> list[dict[str, str | int]]:

        with closing(self._connect()) as connection, connection:

            rows = connection.execute(
                """
                SELECT
                    id,
                    thread_id,
                    role,
                    content,
                    created_at
                FROM messages
                WHERE thread_id = ?
                ORDER BY id ASC
                """,
                (thread_id,),
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    def update_title(
        self,
        thread_id: str,
        title: str,
    ) -> bool:

        cleaned_title = " ".join(
            title.split()
        )

        with closing(self._connect()) as connection, connection:

            cursor = connection.execute(
                """
                UPDATE conversations
                SET
                    title = ?,
                    updated_at = ?
                WHERE thread_id = ?
                """,
                (
                    cleaned_title,
                    self._utc_now(),
                    thread_id,
                ),
            )

            updated = cursor.rowcount == 1

        return updated

    @staticmethod
    def _make_title(
        first_message: str | None,
    ) -> str:

        if not first_message:
            return "新对话"

        normalized_message = " ".join(
            first_message.split()
        )

        return normalized_message[:40]

    @staticmethod
    def _utc_now() -> str:

        return datetime.now(
            timezone.utc
        ).isoformat()