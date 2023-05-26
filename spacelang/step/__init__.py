import logging
import time
from autotraders.ship import Ship

from spacelang.step.navigate import Navigate
from spacelang.step.ship_command import ShipCommand


class Step:
    def __init__(self, command, data):
        self.command = command
        self.args = data
        if self.command == "navigate":
            self.inner = Navigate(self.args)
        elif self.command in ["dock", "orbit", "refuel", "extract"]:
            self.inner = ShipCommand(self.command, self.args)

    def event(self, ship, events, session):
        repeat_interval = -1
        if type(self.args) is str:
            name = self.args
            repeat = False
        else:
            name = self.args["name"]
            repeat = "repeat" in self.args
            if repeat and "interval" in self.args["repeat"]:
                repeat_interval = self.args["repeat"]["interval"]
        for event in events:
            if event.name == name:
                if repeat:
                    if repeat_interval != -1:
                        while True:
                            event.execute(ship, events, session)
                            time.sleep(repeat_interval)
                else:
                    event.execute(ship, events, session)

    def execute(self, ship: Ship, events, session):
        logging.debug(self.command)
        if self.command == "navigate":
            self.inner.execute(ship, session)
        elif self.command in ["dock", "orbit", "refuel", "extract"]:
            self.inner.execute(ship)
        elif self.command == "action" or self.command == "event":
            self.event(ship, events, session)
        elif self.command == "refine":
            ship.refine(self.args)
        elif self.command == "sell":
            assert type(self.args) is dict
            ship.sell(self.args["symbol"], self.args.get("quantity", 1))
        elif self.command == "buy":
            assert type(self.args) is dict
            ship.buy(self.args["symbol"], self.args.get("quantity", 1))
        elif self.command == "sellall":
            exclude = []
            if type(self.args) is dict and "exclude" in self.args:
                exclude = self.args["exclude"]
            for i in ship.cargo.inventory:
                if i not in exclude:
                    ship.sell(i, ship.cargo.inventory[i])
                    time.sleep(0.1)
        elif self.command == "sleep":
            if type(self.args) is int:
                time.sleep(self.args)
            else:
                raise NotImplementedError("TODO")
        else:
            raise NotImplementedError("TODO")
        time.sleep(1)
