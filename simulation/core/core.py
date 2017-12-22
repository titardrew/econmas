import numpy as np

from .request import Request, Answer
from ..parameters import SEED
from ..visualization import Bundle, DataCollector as dc

np.random.seed(SEED)


class Core(object):
    request_list = {Request.MOVE: [], Request.BUY: [], Request.SELL: []}
    TRANSPORT_COST = 0.1

    @classmethod
    def send_request(cls, source, request: Request, *args):
        cls.request_list[request].append((source, args))

    @classmethod
    def process_requests(cls):

        # processing MOVE requests:
        move_list = cls.request_list[Request.MOVE].copy()
        np.random.shuffle(move_list)

        for move_ in move_list:
            cls._process_move(*move_)
            cls.request_list[Request.MOVE].remove(move_)

        # pairing Buyers with Sellers: (Buyer are initiative)
        sell_list = cls.request_list[Request.SELL].copy()
        np.random.shuffle(sell_list)
        # Each seller looks for a pair-buyer and sells.
        # If he founds its pair, core pairs them and deletes them from requests list.
        # That is for avoiding collisions: several buyers may request common seller.
        for sell_ in sell_list:
            cls.request_list[Request.SELL].remove(sell_)
            cls._process_sell(*sell_)

        # Then rest of buyers should be deleted from request list.
        buy_list = cls.request_list[Request.BUY].copy()

        for buy_ in buy_list:
            cls.request_list[Request.BUY].remove(buy_)

    @classmethod
    def _process_move(cls, source, *args):
        next_pos, = args[0]
        # remove request from list
        if source.world.available_item(next_pos):  # not busy
            source.world.free_spot(source.pos, next_pos)
            source.pos = next_pos
            return Answer.ACCEPT
        else:
            return Answer.DECLINE

    @classmethod
    def _process_sell(cls, source, *args):
        quantity, price, transport_costs, _buy = args[0]
        gain = quantity * (price - transport_costs)
        buyer, _ = _buy

        if gain < 0 or buyer.money < buyer.config['Margin'] + price * quantity:
            return Answer.DECLINE

        print(quantity, price, transport_costs, buyer, source)

        # Remove requests from list
        # If someone sold to this buyer his product,
        # than this request won't be accepted
        try:
            cls.request_list[Request.BUY].remove(_buy)
            # Gain is computed with transport_cost yet.
            source.money += gain
            source.end_out -= quantity

            # Price is payed by buying side.
            buyer.money -= price * quantity
            buyer.end_in += quantity

            dc.add_price(source, price)

            return Answer.ACCEPT
        except ValueError:
            return Answer.DECLINE

