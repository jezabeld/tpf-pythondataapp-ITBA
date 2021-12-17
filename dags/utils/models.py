"""Data model definition."""

import utils.db_connections as db
from sqlalchemy import Column, Integer, String, Float, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData

Base = declarative_base()

class StockValue(Base):
    """Stock value data model."""

    __tablename__ = "stock_value" #nombre de la tabla en la db 
    #id = Column(Integer, primary_key=True)
    symbol = Column(String, primary_key=True)
    date = Column(String, primary_key=True) # date o string??
    open = Column(Float)
    close = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(BigInteger)

    def __init__(self, symbol, date, open, close, high, low, volume):
        self.symbol = symbol
        self.date = date
        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = volume

    def __repr__(self):
        return f"<StockValue(symbol='{self.symbol}', date='{self.date}', ...)>"

    def __str__(self):
        return f"{self.symbol} {self.date}: ${round(self.close,2)}"

    def get_keys(self):
        return {'symbol': self.symbol, 'date': self.date}