from __future__ import print_function
import copy
import time
from datetime import date, timedelta

from qsforex.event.event import SignalEvent


class TestStrategy(object):
    def __init__(self, pairs, events):
        self.pairs = pairs
        self.events = events
        self.ticks = 0
        self.invested = False

    def calculate_signals(self, event):
        if event.type == 'TICK' and event.instrument == self.pairs[0]:
            if self.ticks % 5 == 0:
                if self.invested == False:
                    signal = SignalEvent(self.pairs[0], "market", "buy", event.time)
                    self.events.put(signal)
                    self.invested = True
                else:
                    signal = SignalEvent(self.pairs[0], "market", "sell", event.time)
                    self.events.put(signal)
                    self.invested = False
            self.ticks += 1


class MovingAverageCrossStrategy(object):
    def __init__(
        self, pairs, events,
        short_window=500, long_window=2000
    ):
        self.pairs = pairs
        self.pairs_dict = self.create_pairs_dict()
        self.events = events
        self.short_window = short_window
        self.long_window = long_window

    def create_pairs_dict(self):
        attr_dict = {
            "ticks": 0,
            "invested": False,
            "short_sma": None,
            "long_sma": None
        }
        pairs_dict = {}
        for p in self.pairs:
            pairs_dict[p] = copy.deepcopy(attr_dict)
        return pairs_dict

    def calc_rolling_sma(self, sma_m_1, window, price):
        return ((sma_m_1 * (window - 1)) + price) / window

    def calculate_signals(self, event):
        if event.type == 'TICK':
            pair = event.instrument
            price = event.bid
            pd = self.pairs_dict[pair]
            if pd["ticks"] == 0:
                pd["short_sma"] = price
                pd["long_sma"] = price
            else:
                pd["short_sma"] = self.calc_rolling_sma(
                    pd["short_sma"], self.short_window, price
                )
                pd["long_sma"] = self.calc_rolling_sma(
                    pd["long_sma"], self.long_window, price
                )
            # Only start the strategy when we have created an accurate short window
            if pd["ticks"] > self.short_window:
                if pd["short_sma"] > pd["long_sma"] and not pd["invested"]:
                    signal = SignalEvent(pair, "market", "buy", event.time)
                    self.events.put(signal)
                    pd["invested"] = True
                if pd["short_sma"] < pd["long_sma"] and pd["invested"]:
                    signal = SignalEvent(pair, "market", "sell", event.time)
                    self.events.put(signal)
                    pd["invested"] = False
            pd["ticks"] += 1

class DailySupportResistanceTrading(object):
    def __init__(self, pairs, events):
        self.pairs = pairs
        self.pairs_dict = self.create_pairs_dict()
        self.events = events
        self.tick_data = self.create_tick_data_dict()

    def create_tick_data_dict(self):
        today = time.strftime("%Y-%m-%d")
        tick_data = { today: { '0': { 'bid': [], 'ask': [] }}}
        return tick_data

    def create_pairs_dict(self):
        attr_dict = {
            "ticks": 0,
            "invested": False,
        }
        pairs_dict = {}
        for p in self.pairs:
            pairs_dict[p] = copy.deepcopy(attr_dict)
        return pairs_dict

    def get_support_resistance(self, tick_data):
        high = None
        low = None
        for hour in tick_data:
            for array in tick_data[hour]:
                if not tick_data[hour][array]:
                    continue
                else:
                    if array == "ask":
                        high_value = max(tick_data[hour][array])
                        print(high_value)
                        if high == None:
                            high = high_value
                        elif high_value > high:
                            high = high_value
                    elif array == "bid":
                        low_value = min(tick_data[hour][array])
                        if low == None:
                            low = low_value
                        elif low_value < low:
                            low = low_value
        return (low, high)

    def get_previous_day_high_low(self):
        support = 0
        resistance = 0
        d = date.today() - timedelta(days = 0)
        day = d.strftime('%Y-%m-%d')
        if day in self.tick_data:
            support, resistance = self.get_support_resistance(self.tick_data[day])
        return (support, resistance)


    def group_tick_data(self, event):
        if event.type == 'TICK':
            oanda_time = event.time.split('T')
            day = str(oanda_time[0])
            h_m_s = oanda_time[1].split(':')
            hour = str(h_m_s[0])
            bid = str(event.bid)
            ask = str(event.ask)
            if day in self.tick_data:
                if hour in self.tick_data[day]:
                    self.tick_data[day][hour]["bid"].append(bid)
                    self.tick_data[day][hour]["ask"].append(ask)
                else:
                    self.tick_data[day][hour] = { "bid": [], "ask": [] }
                    self.tick_data[day][hour]["bid"].append(bid)
                    self.tick_data[day][hour]["ask"].append(ask)
            else:
                self.tick_data[day] = { hour: { "bid": [], "ask": [] }}
                self.tick_data[day][hour]["bid"].append(bid)
                self.tick_data[day][hour]["ask"].append(ask)
            previous_low, previous_high = self.get_previous_day_high_low()
            print("High: %s, Low: %s" % (previous_high, previous_low))
        return




