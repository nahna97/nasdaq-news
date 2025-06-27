# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

FMP_API_KEY = 'your_fmp_api_key_here'
NEWS_API_KEY = 'b6f17f92-f77c-46fc-a277-fdded4d318b7'

nasdaq_100 = sorted(list(set([
    'AAPL', 'MSFT', 'AMZN', 'NVDA', 'META', 'GOOGL', 'GOOG', 'AVGO', 'TSLA', 'PEP',
    'ADBE', 'COST', 'CSCO', 'NFLX', 'AMD', 'TMUS', 'INTC', 'QCOM', 'TXN', 'AMAT',
    'SBUX', 'INTU', 'BKNG', 'ISRG', 'MDLZ', 'MU', 'LRCX', 'ADI', 'VRTX', 'REGN',
    'PANW', 'GILD', 'FISV', 'ATVI', 'ADP', 'ZM', 'CHTR', 'MELI', 'KLAC', 'MAR',
    'ASML', 'CTSH', 'AEP', 'CDNS', 'MNST', 'EXC', 'IDXX', 'BIIB', 'CSGP', 'CTAS',
    'DXCM', 'FAST', 'ILMN', 'JD', 'KDP', 'MRNA', 'NXPI', 'ODFL', 'PCAR', 'PAYX',
    'ROST', 'SGEN', 'SIRI', 'SNPS', 'TTD', 'VRSK', 'WBA', 'XEL', 'ZS', 'EBAY',
    'TEAM', 'BIDU', 'NTES', 'ORLY', 'LULU', 'ALGN', 'CRWD', 'CEG', 'DLTR', 'EA',
    'FTNT', 'GEN', 'GEHC', 'HON', 'ROKU', 'SPLK', 'VRSN', 'WBD', 'WDC', 'ANSS',
    'MTCH', 'PDD', 'CDW', 'DDOG', 'OKTA', 'MDB'
])))

@st.cache_data(show_spinner=False)
def get_earnings_calendar():
    url = f'https://financialmodelingprep.com/api/v3/earning_calendar?apikey={FMP_API_KEY}&from={datetime.today().date()}&to={(datetime.today() + timedelta(days=7)).date()}'
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data)
    df = df[df['symbol'].isin(nasdaq_100)]
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['DaysUntilEarnings'] = (df['date'] - datetime.today().date()).apply(lambda x: x.days)
    return df[['symbol', 'date', 'DaysUntilEarnings']]

def get_news_sentiment(ticker):
    url = f'https://newsapi.org/v2/everything?q={ticker}&apiKey={NEWS_API_KEY}&pageSize=100&language=en&sortBy=publishedAt'
    response = requests.get(url)
    articles = response.json().get('articles', [])
    positive, negative, neutral = 0, 0, 0
    for article in articles:
        title = article.get('title', '').lower()
        if any(word in title for word in ['soars', 'beats', 'rises', 'up', 'gains']):
            positive += 1
        elif any(word in title for word in ['falls', 'misses', 'drops', 'down', 'loss']):
            negative += 1
        else:
            neutral += 1
    return {'Ticker': ticker, 'Positive': positive, 'Negative': negative, 'Neutral': neutral}

st.title("📊 Nasdaq-100 Earnings & News Sentiment Dashboard")

st.header("📅 Upcoming Earnings (Next 7 Days)")
earnings = get_earnings_calendar()
earnings_summary = earnings['DaysUntilEarnings'].value_counts().sort_index()
st.bar_chart(earnings_summary)

if st.checkbox("Show full earnings list"):
    st.dataframe(earnings.rename(columns={'symbol': 'Ticker', 'date': 'Earnings Date'}))

st.header("📰 News Sentiment Analysis")
selected_tickers = st.multiselect("Select Ticker(s):", nasdaq_100, default=['AAPL', 'MSFT', 'TSLA'])

if st.button("Analyze News"):
    results = [get_news_sentiment(ticker) for ticker in selected_tickers]
    results_df = pd.DataFrame(results)
    st.dataframe(results_df)
    st.subheader("📈 Sentiment Breakdown")
    st.bar_chart(results_df.set_index('Ticker')[['Positive', 'Negative', 'Neutral']])
