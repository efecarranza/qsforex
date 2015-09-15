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
        engine = create_engine('sqlite:///eurusd.sqlite')
        connection = engine.connect()
        result = connection.execute("select * from eurusd;")
        row = result.first()
        print(row)
        # Session = sessionmaker(bind = engine)
        # session = Session()
        # for instance in session.query(eurusd).order_by(eurusd.Date):
        #     print(instance.open)

connection = PriceHandler('eurusd')
connection.start_engine()
