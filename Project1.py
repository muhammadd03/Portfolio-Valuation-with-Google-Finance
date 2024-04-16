import requests as r
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List
from tabulate import tabulate
# https://www.google.com/finance/quote/MSFT:NASDAQ?hl=en


@dataclass
class Stock:
    ticker: str
    exchange: str
    price: float = 0
    currency: str = 'USD'
    usd_price: float = 0

    def __post_init__(self):
        price_info = get_price_information(self.ticker, self.exchange)

        if price_info['Ticker'] == self.ticker:
            self.price = price_info['Price']
            self.currency = price_info['Currency']
            self.usd_price = price_info['USD-price']
        # else:
        #     print(f"Error: Ticker '{self.ticker}' not found in price information")

@dataclass
class Position:
    stock: Stock
    quantity: int

@dataclass
class Portfolio:
    positions: List[Position]

    def get_total_value(self):
        total_value = 0

        for position in self.positions:
            total_value+= position.quantity * position.stock.usd_price

            return total_value

def get_fx_to_usd(currency):
    fx_url = f'https://www.google.com/finance/quote/{currency}-USD?hl=en'
    response = r.get(fx_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    fx_rate = soup.find('div', attrs={'data-last-price': True})
    fx = float(fx_rate['data-last-price'])

    return fx


def get_price_information(ticker, exchange):
    url = f'https://www.google.com/finance/quote/{ticker}:{exchange}?hl=en'
    response = r.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    price_div = soup.find('div', attrs={'data-last-price': True})
    price = float(price_div['data-last-price'])
    currency = price_div['data-currency-code']

    usd_price = price
    if currency != 'USD':
        fx = get_fx_to_usd(currency)
        usd_price = round(price*fx, 2)
    return {
        'Ticker': ticker,
        'Exchange': exchange,
        'Price': price,
        'Currency': currency,
        'USD-price': usd_price
    }
def display_portfolio_summary(portfolio):
    if not isinstance(portfolio, Portfolio):
        raise TypeError('Please provide an instance if the portfolio type')
    portfolio_value = portfolio.get_total_value()

    portfolio_data = []

    for position in sorted(portfolio.positions,
                           key=lambda x: x.quantity * x.stock.usd_price,
                           reverse=True):
        portfolio_data.append([
            position.stock.ticker,
            position.stock.exchange,
            position.quantity,
            position.stock.usd_price,
            position.quantity * position.stock.usd_price,
            position.quantity * position.stock.usd_price / portfolio_value * 100
        ])

        print(tabulate(portfolio_data,
                       headers=['Ticker', 'Exchange', 'Quantity', 'Price', 'Market_Value', '% Allocation'],
                       tablefmt='psql',
                       floatfmt='.2f'))
        print(f'Total portfolio value: ${portfolio_value:,.2f}.')
if __name__ == '__main__':
    shop = Stock('SHOP', 'TSE')
    msft = Stock('MSFT', 'NASDAQ')
    nvda = Stock('NVDA', 'NASDAQ')
    bns = Stock('BNS', 'TSE')
    googl = Stock('GOOGL', 'NASDAQ')
    portfolio = Portfolio([Position(nvda, 10),
                           Position(bns, 1000),
                           Position(googl, 100),
                           Position(msft,2),
                           Position(shop,30)])
    print(portfolio.get_total_value())
    display_portfolio_summary(portfolio)
