from zipline.api import order, record, symbol
import numpy as np
from math import floor

def initialize(context):
  context.tickers = ['TLT', 'IEI']
  # context.tickers = ['EWA', 'EWC']
  # context.tickers = ['COKE', 'PEP']
  context.time = None
  context.latest_prices = np.array([-1.0, -1.0])
  context.invested = None

  context.delta = 1e-4
  context.wt = context.delta / (1 - context.delta) * np.eye(2)
  context.vt = 1e-3
  context.theta = np.zeros(2)
  context.P = np.zeros((2, 2))
  context.R = None

  context.days = 0
  context.qty = 40000
  context.cur_hedge_qty = context.qty 


def update_latest(context, data):
  hist_0 = data.history(symbol(context.tickers[0]), 'price', 1, '1d')
  hist_1 = data.history(symbol(context.tickers[1]), 'price', 1, '1d')
  context.latest_prices[0] = hist_0[0]
  context.latest_prices[1] = hist_1[0]


def handle_data(context, data):
  update_latest(context, data)
  context.days = context.days + 1

  F = np.asarray([context.latest_prices[0], 1.0]).reshape((1, 2))
  y = context.latest_prices[1]

  if context.R is not None:
    context.R = context.C + context.wt
  else:
    context.R = np.zeros((2, 2))

  yhat = F.dot(context.theta)
  et = y - yhat

  Qt = F.dot(context.R).dot(F.T) + context.vt
  sqrt_Qt = np.sqrt(Qt)

  At = context.R.dot(F.T) / Qt
  context.theta = context.theta + At.flatten() * et
  context.C = context.R - At * F.dot(context.R)

  if context.days > 1:
    if context.invested == None:
      if et < -sqrt_Qt:
        # Long Entry
        context.cur_hedge_qty = int(floor(context.qty * context.theta[0]))
        order(symbol(context.tickers[1]), context.qty)
        order(symbol(context.tickers[0]), -context.cur_hedge_qty)
        context.invested = "long"
      elif et > sqrt_Qt:
        # Short Entry
        context.cur_hedge_qty = int(floor(context.qty * context.theta[0]))
        order(symbol(context.tickers[1]), -context.qty)
        order(symbol(context.tickers[0]), context.cur_hedge_qty)
        context.invested = "short"
    if context.invested is not None:
      if context.invested == "long" and et > -sqrt_Qt:
        # Close long
        order(symbol(context.tickers[1]), 0)
        order(symbol(context.tickers[0]), 0)
        context.invested = None
      if context.invested == "short" and et < sqrt_Qt:
        # Close short
        order(symbol(context.tickers[1]), 0)
        order(symbol(context.tickers[0]), 0)
        context.invested = None



