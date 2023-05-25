import time
from threading import Thread

import yaml
from autotraders import session as s
from autotraders.agent import Agent
from autotraders.ship import Ship

import secret
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
            time.sleep(1)


class Trigger:
    def __init__(self, name, data):
        self.name = name  # TODO: Concurrency support
        self.steps = {}
        for group in data:
            self.steps[group] = [Step(d, data[group]["steps"][d]) for d in data[group]["steps"]]

    def run(self, ships, events, session):
        print("[" + self.name + "] Executing")
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
        print("[main] Initializing state ...")  # TODO: Tech Debt on threads (use logging instead)
        agent = Agent(session)
        print("[main] Agent: " + agent.symbol)
        ships = {}
        for group in self.ship_groups:
            ships[group] = [Ship(ship, session) for ship in self.ship_groups[group]]
            time.sleep(0.5)
        contains_onstart = len([trigger for trigger in self.triggers if trigger.name == "on_start"]) == 1
        if contains_onstart:
            on_start = [trigger for trigger in self.triggers if trigger.name == "on_start"][0]
            print("[main] Processing trigger on_start")
            thread = Thread(target=on_start.run, args=(ships, self.events, session))
            thread.start()
        while True:
            print("[main] Checking triggers ...")
            agent.update()
            time.sleep(5)  # TODO: Actually check triggers


def load_text(stream):
    data = yaml.load(stream, Loader=yaml.Loader)
    return data


if __name__ == "__main__":
    File(load_text(open("example.yml"))).run(s.get_session(secret.TOKEN))
