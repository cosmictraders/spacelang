import math
import time
from datetime import datetime, timezone

from autotraders.map.waypoint import Waypoint


class WaypointQuery:
    def __init__(self, args):
        self.data = args

    def query(self, ship, session):
        if type(self.data["destination"]) is str:
            return self.data["destination"]
        else:
            choices, _ = Waypoint.all(ship.nav.location.system, session)
            ship_current_waypoint = [
                choice for choice in choices if choice.symbol == ship.nav.location
            ][0]
            tmp = []
            for choice in choices:
                if "trait" in self.data["destination"]:
                    if (
                        len(
                            [
                                trait
                                for trait in choice.traits
                                if trait.symbol == self.data["destination"]["trait"]
                            ]
                        )
                        != 0
                    ):
                        tmp.append(choice)
                if "type" in self.data["destination"]:
                    if choice.waypoint_type == self.data["destination"]["type"]:
                        tmp.append(choice)
            choices = tmp
            if len(choices) == 0:
                raise Exception("0 possible waypoints")
            if (
                "selection" not in self.data["destination"]
                or self.data["destination"]["selection"] == "NEAREST"
            ):
                accepted = choices[0]
                best = 1000000
                for choice in choices:
                    if choice.symbol == ship.nav.location:
                        accepted = choice
                        best = -1
                    distance = math.sqrt(
                        ((choice.x - ship_current_waypoint.x) ** 2)
                        + ((choice.y - ship_current_waypoint.y) ** 2)
                    )
                    if distance < best:
                        best = distance
                        accepted = choice
            else:
                accepted = choices[0]
            return accepted


class Navigate:
    def __init__(self, args):
        self.data = args
        self.query = WaypointQuery(args)

    def execute(self, ship, session):
        accepted = self.query.query(ship, session)
        if str(accepted.symbol) != str(ship.nav.location):
            ship.navigate(str(accepted.symbol))
        ship.update()
        if ship.nav.moving:
            time.sleep((ship.nav.route.arrival - datetime.now(timezone.utc)).seconds)
