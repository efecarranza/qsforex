from __future__ import print_function

import datetime
from decimal import Decimal, getcontext, ROUND_HALF_DOWN
import os
import os.path
import re
import time

import numpy as np
import pandas as pd

from qsforex import settings
from qsforex.event.event import TickEvent

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class PriceHandler(object):
    def __init__(self, pair):
        self.pair = pair

    def start_engine(self):
        engine = create_engine('sqlite:///../data/eurusd.sqlite')
        connection = engine.connect()
        short_ema_query = connection.execute("SELECT * FROM eurusd ORDER BY Date DESC LIMIT 9;")
        long_ema_query = connection.execute("SELECT * FROM eurusd ORDER BY Date DESC LIMIT 18;")
        short_ema_array = []
        long_ema_array = []
        for row in short_ema_query:
            short_ema_array.append(row[1])
        for row in long_ema_query:
            long_ema_array.append(row[1])
        short_ema = self.calculate_initial_short_ema(short_ema_array)
        long_ema = self.calculate_initial_long_ema(long_ema_array)
        return (short_ema, long_ema)

    def calculate_initial_short_ema(self, short_ema_array):
        ema_periods = 9
        sma = sum(short_ema_array) / ema_periods
        mutiplier = (2 / (ema_periods + 1))
        ema = (short_ema_array[0] - sma) * mutiplier + sma
        ema_string = "{:.5f}".format(ema)
        print(ema_string)
        ema = Decimal(ema_string)
        print("short ema: %s" % ema)
        return ema

    def calculate_initial_long_ema(self, long_ema_array):
        ema_periods = 18
        sma = sum(long_ema_array) / ema_periods
        mutiplier = (2 / (ema_periods + 1))
        ema = (long_ema_array[0] - sma) * mutiplier + sma
        ema_string = "{:.5f}".format(ema)
        ema = Decimal(ema_string)
        print("long ema %s" % ema)
        return ema

connection = PriceHandler('eurusd')
connection.start_engine()
