import logging
import time
from threading import Thread

import yaml
from autotraders.agent import Agent
from autotraders.ship import Ship

from spacelang.step import Step


class Action:
    def __init__(self, name, data):
        self.name = name
        self.actions = []
        for d in data["steps"]:
            if type(d) == str:
                self.actions.append(Step(d, None))
            else:
                self.actions.append(Step(list(d.keys())[0], d[list(d.keys())[0]]))

    def execute(self, ship, events, session):
        for action in self.actions:
            action.execute(ship, events, session)

    def run(self, ships, events, session):
        for ship in ships:
            self.execute(ship, events, session)


class Trigger:
    def __init__(self, name, data):
        self.name = name  # TODO: Concurrency support
        self.steps = {}
        for group in data:
            for d in data[group]["steps"]:
                self.steps[group] = []
                if type(d) == str:
                    self.steps[group].append(Step(d, None))  # TODO: Move to step class
                else:
                    self.steps[group].append(Step(list(d.keys())[0], d[list(d.keys())[0]]))

    def run(self, ships, events, session):
        for group in self.steps:
            ship_group = ships[group]
            for ship in ship_group:
                for step in self.steps[group]:
                    step.execute(ship, events, session)


class File:
    def __init__(self, data):
        self.ship_groups = data["ships"]
        self.events = [Action(d, data["actions"][d]) for d in data["actions"]]
        self.triggers = [Trigger(d, data["triggers"][d]) for d in data["triggers"]]

    def run(self, session):
        logging.info("Initializing state ...")
        agent = Agent(session)
        logging.info("Agent: " + agent.symbol)
        ships = {}
        for group in self.ship_groups:
            ships[group] = [Ship(ship, session) for ship in self.ship_groups[group]]
        contains_onstart = len([trigger for trigger in self.triggers if trigger.name == "on_start"]) == 1
        if contains_onstart:
            on_start = [trigger for trigger in self.triggers if trigger.name == "on_start"][0]
            logging.info("Processing trigger on_start")
            thread = Thread(target=on_start.run, name="OnStart", args=(ships, self.events, session))
            thread.start()
        while True:
            logging.debug("Checking triggers ...")
            agent.update()
            time.sleep(10)  # TODO: Actually check triggers


def load_text(stream):
    data = yaml.load(stream, Loader=yaml.Loader)
    return data


logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("pyrate_limiter").setLevel(logging.WARNING)
logging.basicConfig(format='[%(threadName)s] %(levelname)s: %(message)s', level=logging.DEBUG)
