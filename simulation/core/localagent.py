import numpy as np
import operator

from .agent import Agent, AgentType, State
from .core import Core, Request, Answer
from ..parameters import SEED


np.random.seed(SEED)


class LocalAgent(Agent):

    neighbourhood = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    def __init__(self, agent_type, world, pos, transform_rate):
        super(LocalAgent, self).__init__(agent_type)

        self.pos = pos
        self.type = agent_type
        self.world = world
        self.phase = State.SELL
        self.state_machine = {
            State.BUY: self._send_buy,
            State.SELL: self._send_sell
        }

        self.end_in = self.config['EndIn']
        self.end_out = self.config['EndOut']
        self.money = self.config['Money']
        self.fat = 0.1 * self.config['Margin']
        self.transform_rate = transform_rate

    def decide(self):
        self.state_machine[self.phase]()

    def _send_sell(self):

        # Transform resources first to sell
        self._transform()

        # Compute Marginal Rate of Substitution:
        if self.end_out <= 1e-5:
            return

        MRS_seller = np.float(self.money / self.config['Wm']) / np.float(self.end_out / self.config['Wr'])
        max_gain = 0
        trade = ()
        # Shuffle buyers list
        request_list = Core.request_list[Request.BUY]
        np.random.shuffle(request_list)

        for buyer, args in request_list:
            # Compare q_for_sell * price ---> gain, which seller will get
            # Buyer with best (by seller's gain) offer gets the deal
            # Filter valid buyers
            if buyer.type.value != self.type.value + 1:
                continue

            pos, MRS_buyer = args
            transport_cost = Core.TRANSPORT_COST * self.world.dist(self.pos, pos)
            price = np.sqrt(MRS_seller * MRS_buyer)

            available_money = buyer.money - buyer.config['Margin'] - self.config['Margin']
            wanted_q = available_money / (price + buyer.config['ProdCost'] * .75)
            real_q = min(self.end_out, wanted_q)

            # Check out weak conditions
            if available_money <= 0 or real_q <= 1e-5:
                continue

            price += self.config['ProdCost'] / real_q
            gain = real_q * (price - transport_cost)
            if gain >= max_gain:
                max_gain = gain
                trade = (real_q, price, transport_cost, (buyer, args))

        if max_gain > 0:
            # Send SELL request
            Core.send_request(self, Request.SELL, *trade)

            # Change phase
            self.phase = State.BUY

    def _send_buy(self):

        # Compute buyer's MRS
        MRS_buyer = np.float(self.money / self.config['Wm']) / np.float(self.end_in / self.config['Wr'])

        # Sending BUY request
        Core.send_request(self, Request.BUY, self.pos, MRS_buyer)

        # Change phase
        self.phase = State.SELL

    def _transform(self):
        raise NotImplementedError()

    @classmethod
    def get_neighbours(cls, pos):
        return [tuple(map(operator.add, pos, index))
                for index in cls.neighbourhood]

    def __str__(self):
        return "<{}, in : {}, out : {}, {} >".format(self.type.name, self.end_in, self.end_out, self.money)


class Harvester(LocalAgent):
    """     State machine:
            ->(Harvest/Move) <--> (Sell)
    """

    def __init__(self, agent_type, world, pos):
        super(Harvester, self).__init__(AgentType.HARVESTER, world, pos, transform_rate=1)
        self.phase = State.BUY

    def _send_buy(self):
        # BUY = HARVEST
        self._transform()

    def _send_move(self):
        # getting neighbourhood
        nb = LocalAgent.get_neighbours(self.pos)
        np.random.shuffle(nb)
        # Getting indexes and values of free elements of nb
        keys = [nb_ for nb_ in nb if self.world.available_item(nb_)]

        if keys:
            values = map(self.world.tor_item, keys)

            # Searching maximum nb value's index (choosing next position)
            d = dict(zip(keys, values))
            next_pos = max(d, key=d.get)

            # Send move request
            Core.send_request(self, Request.MOVE, next_pos)

    def _transform(self):
        """ References harvest() method """
        amount = np.float((self.money - self.config['Margin'])) / self.config['ProdCost']
        not_mined, rest, amount = self.world.harvest(amount, self.pos)
        self.money -= (amount - not_mined) * self.config['ProdCost']
        self.end_out += amount - not_mined

        # Move, if running out of resource:
        if rest <= self.config['AwayBias']:
            self._send_move()

        self.phase = State.SELL


class Industrial(LocalAgent):
    """     State machine:
            ->(Transform + Sell) <--> (Buy)
    """

    def __init__(self, agent_type, world, pos):
        super(Industrial, self).__init__(agent_type, world, pos, transform_rate=.75)

    def _transform(self):
        """ References harvest() method """
        amount = np.float((self.money - self.config['Margin'])) / self.config['ProdCost']
        amount = min(amount / self.transform_rate, self.end_in)

        # Check weak conditions
        if amount < 1e-5:
            return

        self.money -= amount * self.transform_rate * self.config['ProdCost']
        self.end_out += amount * 1/2
        self.end_in -= amount * self.transform_rate


class Consumer(LocalAgent):
    """     State machine:
            ->(Buy + Transform + Consume)--+
                    ^                      |
                    |                      |
                    +----------------------+
    """
    def __init__(self, agent_type, world, pos, income):
        super(Consumer, self).__init__(agent_type, world, pos, transform_rate=0)
        self.income = income

    def _send_sell(self):
        """ Implements SELL = CONSUME """

        # Transform resource (~consume)
        self._transform()

        # Get discrete-time income
        self.money += self.income

        # Change phase
        self.phase = State.BUY

    def _send_buy(self):

        # Compute buyer's MRS
        MRS_buyer = 1

        # Sending BUY request
        Core.send_request(self, Request.BUY, self.pos, MRS_buyer)

        # Change phase
        self.phase = State.SELL

    def _transform(self):
        self.end_in = 0


def new_local_agent(agent_type, *args):

    if agent_type == 1 or agent_type == AgentType.HARVESTER:
        return Harvester(AgentType.HARVESTER, *args)

    elif agent_type == 2 or agent_type == AgentType.INDUSTRIAL_A:
        return Industrial(AgentType.INDUSTRIAL_A, *args)

    elif agent_type == 3 or agent_type == AgentType.INDUSTRIAL_B:
        return Industrial(AgentType.INDUSTRIAL_B, *args)

    elif agent_type == 4 or agent_type == AgentType.CONSUMER:
        return Consumer(AgentType.CONSUMER, *args)
