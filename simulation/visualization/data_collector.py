from matplotlib import use
from enum import Enum

from ..core import AgentType
use("WebAgg")
from ..data import save_sim_data, save_fig
from matplotlib import pyplot as plt


class Bundle(Enum):
    PRICE = 1
    PRIVATE = 2
    WORLD = 3


class DataCollector:
    prices = {AgentType.HARVESTER: [],
              AgentType.INDUSTRIAL_A: [],
              AgentType.INDUSTRIAL_B: []
              }
    end_ins = {AgentType.HARVESTER: {},
               AgentType.INDUSTRIAL_A: {},
               AgentType.INDUSTRIAL_B: {},
               AgentType.CONSUMER: {}
               }
    end_outs = {AgentType.HARVESTER: {},
                AgentType.INDUSTRIAL_A: {},
                AgentType.INDUSTRIAL_B: {},
                AgentType.CONSUMER: {}
                }
    moneys = {AgentType.HARVESTER: {},
              AgentType.INDUSTRIAL_A: {},
              AgentType.INDUSTRIAL_B: {},
              AgentType.CONSUMER: {}
              }
    w_state = []

    @classmethod
    def send_bundle(cls, bundle_type, *args):
        inst = {Bundle.MARKET: cls.add_price,
                Bundle.PRIVATE: cls.add_private,
                Bundle.WORLD: cls.add_world}
        inst[bundle_type](*args)

    @classmethod
    def add_price(cls, source, price):
        cls.prices[source.type].append(price)

    @classmethod
    def add_private(cls, source):
        if source in cls.end_ins[source.type].keys():
            cls.end_ins[source.type][source].append(source.end_in)
            cls.end_outs[source.type][source].append(source.end_out)
            cls.moneys[source.type][source].append(source.money)
        else:
            cls.end_ins[source.type][source] = [source.end_in]
            cls.end_outs[source.type][source] = [source.end_out]
            cls.moneys[source.type][source] = [source.money]

    @classmethod
    def add_world(cls, source):
        cls.w_state.append(source.remain - source.g_capacity * source.quota)

    @classmethod
    def plot_em_all(cls):
        for a_type in AgentType:
            fig = plt.figure(a_type.name, figsize=(6,6))
            fig1 = plt.subplot(221)
            fig2 = plt.subplot(222)
            fig3 = plt.subplot(223)
            fig4 = plt.subplot(224)
            for end_in, end_out, money in zip(cls.end_ins[a_type].values(),
                                              cls.end_outs[a_type].values(),
                                              cls.moneys[a_type].values()):
                fig1.plot(range(len(end_in)), end_in)
                fig2.plot(range(len(end_out)), end_out)
                fig3.plot(range(len(money)), money)

            if a_type != AgentType.CONSUMER:
                fig4.plot(range(len(cls.prices[a_type])), cls.prices[a_type])

            fig1.set_title('End_in')
            fig2.set_title('End_out')
            fig3.set_title('Money')
            fig4.set_title('Price')
            save_fig(fig, a_type.name)
        fig = plt.figure('WORLD', figsize=(6,6))
        plt.plot(range(len(cls.w_state)), cls.w_state)
        plt.title('In-time capacity of resource that could be gathered')
        save_fig(fig, 'WORLD')
        plt.show()

    @classmethod
    def pickle_em_all(cls):
        save_sim_data(cls)
