#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from threading import Thread
from time import strftime

from rich.console import Console
from rich.live import Live
from rich.table import Table

from api import BrawlS
from config import BUY_BOX_ONE, BUY_BOX_TWO, USER_AGENT, VK_ADMIN_TOKEN


class Bot:
    def __init__(self):
        self.console = Console()
        self.client = BrawlS(self.console, VK_ADMIN_TOKEN, USER_AGENT)
        self.balance = ""
        self.trophies = ""

    def update_account(self, dict_: dict) -> None:
        self.balance = f"{dict_['balance']:,}"
        try:
            self.trophies = f"{dict_['trophies']:,}"
        except KeyError:
            pass

    def get_table(self) -> Table:
        table = Table(title="github.com/monosans/vk-brawls-bot")
        table.add_column("Баланс", style="cyan")
        table.add_column("Трофеи", style="green")
        table.add_row(self.balance, self.trophies)
        return table

    def buy_box_one(self, live: Live) -> None:
        while True:
            self.update_account(self.client.buy_box_one())
            self.console.print(
                f"{strftime('%Y-%m-%d %H:%M:%S')} Купил первый бокс"
            )
            live.update(self.get_table(), refresh=True)

    def buy_box_two(self, live: Live) -> None:
        while True:
            self.update_account(self.client.buy_box_two())
            self.console.print(
                f"{strftime('%Y-%m-%d %H:%M:%S')} Купил второй бокс"
            )
            live.update(self.get_table(), refresh=True)

    def run_bot(self) -> None:
        with Live(
            self.get_table(), console=self.console, auto_refresh=False
        ) as live:
            if BUY_BOX_ONE == 1 and BUY_BOX_TWO == 1:
                threads = (
                    Thread(target=self.buy_box_one, args=(live,)),
                    Thread(target=self.buy_box_two, args=(live,)),
                )
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
            elif BUY_BOX_ONE == 1:
                self.buy_box_one(live)
            elif BUY_BOX_TWO == 1:
                self.buy_box_two(live)
            else:
                self.console.print("Оба вида боксов отключены в config.py.")


if __name__ == "__main__":
    Bot().run_bot()
