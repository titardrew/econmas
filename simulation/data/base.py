import pickle as pkl
from matplotlib import pyplot as plt

__location__ = __file__[:-len('base.py')]


def get_last_sim_data():
    with open(__location__ + 'data.pkl', 'rb') as file:
        dc = pkl.load(file)
    return dc


def save_sim_data(dc):
    with open(__location__ + 'data.pkl', 'wb') as file:
        pkl.dump([dc.moneys, dc.prices, dc.w_state, dc.end_ins, dc.end_outs], file, protocol=pkl.HIGHEST_PROTOCOL)


def save_fig(fig, name):
    fig.savefig(__location__ + 'graphs/' + name + '.png')