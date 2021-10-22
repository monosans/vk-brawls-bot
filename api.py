# -*- coding: utf-8 -*-
from re import findall
from time import sleep

from requests import Session
from rich.console import Console


class IncorrectToken(Exception):
    pass


class IncorrectTokenType(Exception):
    pass


class BrawlS:
    def __init__(
        self, console: Console, vk_admin_token: str, user_agent: str
    ) -> None:
        """
        vk_admin_token (str): VK Admin токен с vkhost.github.io.
        user_agent (str): User agent браузера.
        """
        self._console = console
        self._s = Session()
        self._s.headers.update({"User-Agent": user_agent.strip()})
        r = self._s.get(
            f"https://api.vk.com/method/apps.get?access_token={vk_admin_token.split('access_token=')[-1].split('&expires_in')[0].strip()}&v=5.131&app_id=7949771&platform=web"
        ).json()
        response = r.get("response")
        if not response:
            raise IncorrectToken("Неверный токен.")
        item = response["items"][0]
        webview_url = item.get("webview_url")
        if not webview_url:
            raise IncorrectTokenType(
                "Токен неверного типа. Нужен VK Admin токен."
            )
        origin, params = webview_url.split("/index.html?")
        self._PARAMS = params
        self.MY_ID = int(findall(r".*vk_user_id=(\d+)*", params)[0])
        self._s.headers.update({"Origin": origin, "Referer": f"{origin}/"})

    def get_profile(self, user_id: int = None) -> dict:
        return self._req(
            "2008", "", {"id": user_id or self.MY_ID, "params": self._PARAMS}
        )

    def buy_box_one(self) -> dict:
        return self._req(
            "2010", "buyBoxOne", {"id": self.MY_ID, "params": self._PARAMS}
        )

    def buy_box_two(self) -> dict:
        return self._req(
            "2015", "buyBoxTwo", {"id": self.MY_ID, "params": self._PARAMS}
        )

    def buy_box_three(self, hash_: str) -> dict:
        return self._req(
            "2003",
            "buyBoxThree",
            {"id": self.MY_ID, "hash": hash_, "params": self._PARAMS},
        )

    def get_top_100(self) -> dict:
        return self._req("2001", "getTop100")

    def get_brawlers(self) -> dict:
        return self._req(
            "2007", "getBrawlers", {"id": self.MY_ID, "params": self._PARAMS}
        )

    def buy_boost_2(self) -> dict:
        return self._req(
            "2004", "buyBoost2", {"id": self.MY_ID, "params": self._PARAMS}
        )

    def buy_boost_3(self) -> dict:
        return self._req(
            "2005", "buyBoost3", {"id": self.MY_ID, "params": self._PARAMS}
        )

    def buy_boost_5(self) -> dict:
        return self._req(
            "2006", "buyBoost5", {"id": self.MY_ID, "params": self._PARAMS}
        )

    def reg_ref(self, user_id: int) -> dict:
        return self._req(
            "2009",
            "regRef",
            {"id": user_id, "refid": self.MY_ID, "params": self._PARAMS},
        )

    def transfer(self, recipient_id: str, amount: int, type_: int) -> dict:
        return self._req(
            "2002",
            "transfer",
            {
                "id": self.MY_ID,
                "recipient_id": recipient_id,
                "amount": amount,
                "type": type_,
                "params": self._PARAMS,
            },
        )

    def _req(self, port: str, endpoint: str, json: dict = None) -> dict:
        """Метод для отправки запросов серверу игры."""
        try:
            r = self._s.post(
                f"https://baguette-game.com:{port}/{endpoint}", json=json
            )
        except Exception as e:
            self._console.print(f"{endpoint}: {e}")
            sleep(1)
            return self._req(port, endpoint, json)
        if r.status_code == 429:
            sleep(0.1)
            return self._req(port, endpoint, json)
        return r.json()
