import logging

from autotraders.ship import Ship


class ShipCommand:
    def __init__(self, command, args):
        if type(args) is not dict:
            args = {}
        self.command = command
        self.fail_fast = args.get("fail-fast", True)

    def execute(self, ship: Ship):
        if self.command == "dock":
            ship.dock()
        elif self.command == "orbit":
            ship.orbit()
        elif self.command == "refuel":
            try:
                ship.refuel()
            except IOError as e:
                if self.fail_fast:
                    raise e
                else:
                    logging.warning(self.command + " failed to execute")
        elif self.command == "extract":
            try:
                ship.refuel()
            except IOError as e:
                if self.fail_fast:
                    raise e
                else:
                    logging.warning(self.command + " failed to execute")
