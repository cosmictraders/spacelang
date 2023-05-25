import logging
import math
import time
from datetime import datetime, timezone

from autotraders.map.waypoint import Waypoint
from autotraders.ship import Ship


class Step:
    def __init__(self, command, data):
        self.command = command
        self.args = data

    def navigate(self, ship, session):
        if type(self.args["destination"]) is str:
            ship.navigate(self.command)
        else:
            choices, _ = Waypoint.all(ship.nav.location.system, session)
            ship_current_waypoint = [choice for choice in choices if choice.symbol == ship.nav.location][0]
            tmp = []
            for choice in choices:
                if "trait" in self.args["destination"]:
                    if len([trait for trait in choice.traits if
                            trait.symbol == self.args["destination"]["trait"]]) != 0:
                        tmp.append(choice)
                if "type" in self.args["destination"]:
                    if choice.waypoint_type == self.args["destination"]["type"]:
                        tmp.append(choice)
            choices = tmp
            if len(choices) == 0:
                raise Exception("0 possible waypoints")
            if "selection" not in self.args["destination"] or self.args["destination"][
                "selection"] == "NEAREST":
                accepted = choices[0]
                best = 1000000
                for choice in choices:
                    if choice.symbol == ship.nav.location:
                        accepted = choice
                        best = -1
                    distance = math.sqrt(
                        ((choice.x - ship_current_waypoint.x) ** 2) + ((choice.y - ship_current_waypoint.y) ** 2))
                    if distance < best:
                        best = distance
                        accepted = choice
            else:
                accepted = choices[0]
            if str(accepted.symbol) != str(ship.nav.location):
                ship.navigate(str(accepted.symbol))
            time.sleep(1)
            ship.update()
            if ship.nav.status == "IN_TRANSIT":
                time.sleep((ship.nav.route.arrival - datetime.now(timezone.utc)).seconds)

    def action(self, ship, events, session):
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
            self.navigate(ship, session)
        elif self.command == "action":
            self.action(ship, events, session)
        elif self.command == "orbit":
            ship.orbit()
        elif self.command == "dock":
            ship.dock()
        elif self.command == "refuel":
            ship.refuel()
        elif self.command == "extract":
            ship.extract()
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
