import json
import os
from typing import Any
from urllib import error, parse, request


class TrelloConnector:
    def __init__(self) -> None:
        self.api_key = os.getenv("TRELLO_API_KEY")
        self.token = os.getenv("TRELLO_TOKEN")
        self.list_id = os.getenv("TRELLO_LIST_ID")

        self.todo_list_id = os.getenv("TRELLO_TODO_LIST_ID")
        self.doing_list_id = os.getenv("TRELLO_DOING_LIST_ID")
        self.done_list_id = os.getenv("TRELLO_DONE_LIST_ID")

    def create_card(self, title: str, description: str = "") -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("TRELLO_API_KEY が .env に設定されていません。")

        if not self.token:
            raise RuntimeError("TRELLO_TOKEN が .env に設定されていません。")

        if not self.list_id:
            raise RuntimeError("TRELLO_LIST_ID が .env に設定されていません。")

        payload = {
            "key": self.api_key,
            "token": self.token,
            "idList": self.list_id,
            "name": title.strip(),
            "desc": description.strip(),
        }

        body = json.dumps(payload).encode("utf-8")

        req = request.Request(
            url="https://api.trello.com/1/cards",
            data=body,
            method="POST",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        try:
            with request.urlopen(req) as response:
                response_body = response.read().decode("utf-8")
                return json.loads(response_body)
        except error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(
                f"Trello API エラー: status={exc.code}, body={error_body}"
            ) from exc

    def move_card(self, card_id: str, target_status: str) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("TRELLO_API_KEY が .env に設定されていません。")

        if not self.token:
            raise RuntimeError("TRELLO_TOKEN が .env に設定されていません。")

        target_list_id = self._get_target_list_id(target_status)
        if not target_list_id:
            raise RuntimeError(
                "移動先のリストIDが .env に設定されていません。"
            )

        params = parse.urlencode(
            {
                "key": self.api_key,
                "token": self.token,
                "idList": target_list_id,
            }
        )

        req = request.Request(
            url=f"https://api.trello.com/1/cards/{card_id}?{params}",
            method="PUT",
            headers={
                "Accept": "application/json",
            },
        )

        try:
            with request.urlopen(req) as response:
                response_body = response.read().decode("utf-8")
                return json.loads(response_body)
        except error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(
                f"Trello API エラー: status={exc.code}, body={error_body}"
            ) from exc

    def _get_target_list_id(self, target_status: str) -> str | None:
        value = target_status.strip().lower()

        if value == "todo":
            return self.todo_list_id
        if value == "doing":
            return self.doing_list_id
        if value == "done":
            return self.done_list_id

        raise RuntimeError(
            "target_status は todo / doing / done のいずれかで指定してください。"
        )