from enum import Enum


class Request(Enum):
    MOVE = 1,
    SELL = 2,
    BUY = 3


class Answer(Enum):
    ACCEPT = 1,
    DECLINE = 2
