import json
import os
from typing import Any
from urllib import error, request

class TrelloConnector:
    def __init__(self) -> None:
        self.api_key = os.getenv("TRELLO_API_KEY")
        self.token = os.getenv("TRELLO_TOKEN")
        self.list_id = os.getenv("TRELLO_LIST_ID")

    def create_card(self, title: str, description: str = "") -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("TRELLO_API_KEYが .env に設定されていません。")
        
        if not self.token:
            raise RuntimeError("TRELLO が .envに設定されていません。")
        
        if not self.list_id:
            raise RuntimeError("TRELLO_LIST_IDが .env に設定されていません。")
        
        payload = {
            "key": self.api_key,
            "token": self.token,
            "idList": self.list_id,
            "name": title.strip(),
            "desc": description.strip()
        }

        body = json.dumps(payload).encode("utf-8")

        req = request.Request(
            url="https://api.trello.com/1/cards",
            data=body,
            method="POST",
            headers={
                "Accept": "application.json",
                "Content-Type": "application.json",
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