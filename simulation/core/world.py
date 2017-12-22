import numpy as np
from ..parameters import *
from ..visualization import DataCollector as dc

np.random.seed(SEED)


class World(object):

    def __init__(self, size, quota, capacity=RESOURCE_CAPACITY,
                 amount=None, growth_rate=GROWTH_RATE):

        if amount is None:
            amount = np.ones(size) * capacity

        self.map = amount.copy()
        self.available = np.ones(shape=amount.shape, dtype=np.bool)
        self.changed = True
        self.capacity = capacity
        self.growth_rate = growth_rate
        self.remain = np.sum(self.map)
        self.g_capacity = np.prod(size) * capacity
        self.quota = quota

    def _tor(self, index):
        return tuple(map(lambda a_, b_: a_ % b_, index, self.map.shape))

    def tor_item(self, index):
        return self.map.item(self._tor(index))

    def available_item(self, index):
        return self.available.item(self._tor(index))

    def tor_itemset(self, index, value):
        self.map.itemset(self._tor(index), value)

    def harvest(self, amount, index):
        amount = min(self.remain - self.g_capacity * self.quota, amount)  # <-- Quota rule
        dc.add_world(self)
        self.remain -= max(amount, 0)
        value = self.tor_item(index) - max(amount, 0)
        self.tor_itemset(index, value)

        if self.tor_item(index) <= 0:
            not_mined = -self.tor_item(index)
            rest = 0
            self.tor_itemset(index, 0)
        else:
            not_mined = 0
            rest = self.tor_item(index)

        return not_mined, rest, max(amount, 0)

    def renew(self):
        self.changed = False
        for index, amount in np.ndenumerate(self.map):
            new_val = np.min([amount + self.growth_rate, self.capacity])
            fresh = amount != new_val <= self.capacity
            if fresh:
                self.map.itemset(index, new_val)

        self.remain = np.sum(self.map)

    def free_spot(self, last_pos, new_pos):
        self.available.itemset(self._tor(last_pos), True)
        self.available.itemset(self._tor(new_pos), False)

    def dist(self, pos1, pos2):
        """ L1 distance on toroid map """
        pos1 = self._tor(pos1)
        pos2 = self._tor(pos2)
        dist = 0
        for coord1, coord2, c_size in zip(pos1, pos2, self.map.shape):
            dist += min(abs(coord1 - coord2),
                        abs(coord1 - (coord2 - c_size)),
                        abs(coord1 - (coord2 + c_size)))
        return dist

    def __mul__(self, other):
        return World(self.map.shape, self.quota, self.capacity, self.map * other, self.growth_rate)

    def __add__(self, other):
        return World(self.map.shape, self.quota, self.capacity, self.map + other, self.growth_rate)

    def __str__(self):
        return str(self.map)

    def __repr__(self):
        return self.__str__()