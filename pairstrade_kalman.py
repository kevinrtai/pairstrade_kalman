from zipline.api import order, record, symbol

def initialize(context):
    pass


def handle_data(context, data):
    order(symbol('COKE'), 10)
    order(symbol('PEP'), 10)
    record(COKE=data.current(symbol('COKE'), 'price'))
    record(PEP=data.current(symbol('PEP'), 'price'))

