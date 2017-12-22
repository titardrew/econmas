from enum import Enum


class State(Enum):
    BUY = 1
    SELL = 2


class AgentType(Enum):
    HARVESTER = 1
    INDUSTRIAL_A = 2
    INDUSTRIAL_B = 3
    CONSUMER = 4


class Agent(object):

    # Several template configuration
    __harvester = {'EndIn': 0, 'EndOut': 1, 'Money': 2, 'AwayBias': 0.1, 'ProdCost': .5, 'Margin': 1, 'Wm': 2, 'Wr': 2}
    __industrial_a = {'EndIn': 5, 'EndOut': 5, 'Money': 20, 'AwayBias': 0.1, 'ProdCost': .4, 'Margin': 2, 'Wm': 2, 'Wr': 2}
    __industrial_b = {'EndIn': 25, 'EndOut': 25, 'Money': 100, 'AwayBias': 0.1, 'ProdCost': .6, 'Margin': 3, 'Wm': 2, 'Wr': 2}
    __consumer = {'EndIn': 50, 'EndOut': 0, 'Money': 180, 'AwayBias': 0.1, 'ProdCost': 0, 'Margin': 4, 'Wm': 2, 'Wr': 2}

    __configs = {AgentType.HARVESTER: __harvester,
                 AgentType.INDUSTRIAL_A: __industrial_a,
                 AgentType.INDUSTRIAL_B: __industrial_b,
                 AgentType.CONSUMER: __consumer}

    def __init__(self, agent_type):
        self.type = agent_type
        self.config = self.__configs[self.type]

    def add_config(self, config, agent_type):
        self.__configs[agent_type] = config

    def decide(self):
        raise NotImplementedError()

    def _send_sell(self):
        raise NotImplementedError()

    def _send_buy(self):
        raise NotImplementedError()

    def _transform(self):
        raise NotImplementedError()
