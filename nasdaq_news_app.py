# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# Replace with your own News API and Financial Modeling Prep API keys
NEWS_API_KEY = 'b6f17f92-f77c-46fc-a277-fdded4d318b7'
FMP_API_KEY = 'zHLUFb49obS6qILBHZOE8rXaxXF3yJt3'

st.set_page_config(page_title="Nasdaq QQQ News", layout="wide")

st.title("📰 Nasdaq QQQ News & Earnings Monitor")

# Nasdaq-100 stock list
nasdaq_100 = [
    "AAPL", "MSFT", "AMZN", "NVDA", "META", "GOOG", "GOOGL", "TSLA", "AVGO", "PEP",
    "COST", "ADBE", "NFLX", "AMD", "CMCSA", "INTC", "CSCO", "TXN", "QCOM", "AMAT",
    "INTU", "BKNG", "ISRG", "MDLZ", "LRCX", "ADI", "VRTX", "MU", "PANW", "REGN",
    "GILD", "ASML", "CRWD", "ZM", "PYPL", "PDD", "SBUX", "NXPI", "CDNS", "MNST",
    "KDP", "ABNB", "ADP", "CHTR", "CTSH", "FTNT", "ROST", "MAR", "MELI", "BIIB",
    "EA", "EXC", "DLTR", "ORLY", "PAYX", "WDAY", "TTD", "PCAR", "ODFL", "MRNA",
    "AEP", "TEAM", "FAST", "CTAS", "XEL", "VRSK", "WBD", "BKR", "ANSS", "CEG",
    "SIRI", "ALGN", "IDXX", "CPRT", "LCID", "ZS", "FANG", "KLAC", "GFS", "CRGY",
    "GEN", "TTWO", "HBAN", "JBHT", "SPLK", "KHC", "DLR", "TECH", "VRTX", "WBA",
    "ILMN", "PEAK", "SIRI"
]

@st.cache_data(show_spinner=False)
def get_earnings_calendar():
    try:
        url = f'https://financialmodelingprep.com/api/v3/earning_calendar?apikey={FMP_API_KEY}&from={datetime.today().date()}&to={(datetime.today() + timedelta(days=7)).date()}'
        response = requests.get(url)
        data = response.json()

        # Make sure we got a list and it's not empty
        if not isinstance(data, list) or len(data) == 0:
            st.warning("No earnings data returned. Please check your FMP API key or try again later.")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df = df[df['symbol'].isin(nasdaq_100)]
        df['date'] = pd.to_datetime(df['date']).dt.date
        df['DaysUntilEarnings'] = (df['date'] - datetime.today().date()).apply(lambda x: x.days)
        return df[['symbol', 'date', 'DaysUntilEarnings']]
    except Exception as e:
        st.error(f"Error fetching earnings data: {e}")
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def get_news_sentiment(ticker):
    try:
        url = f"https://newsapi.org/v2/everything?q={ticker}&sortBy=publishedAt&language=en&pageSize=50&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        articles = response.json().get("articles", [])

        sentiments = []
        for article in articles:
            title = article['title']
            if any(word in title.lower() for word in ['up', 'surge', 'beats', 'soars', 'gains', 'growth']):
                sentiments.append('Positive')
            elif any(word in title.lower() for word in ['down', 'miss', 'falls', 'drops', 'cut', 'warning']):
                sentiments.append('Negative')
            else:
                sentiments.append('Neutral')

        sentiment_counts = pd.Series(sentiments).value_counts().reindex(['Positive', 'Negative', 'Neutral'], fill_value=0)
        return sentiment_counts
    except Exception as e:
        st.error(f"Error fetching news for {ticker}: {e}")
        return pd.Series({'Positive': 0, 'Negative': 0, 'Neutral': 0})

# Sidebar filters
selected_tickers = st.sidebar.multiselect("Select Nasdaq-100 Tickers", options=nasdaq_100, default=["QQQ", "AAPL", "MSFT", "NVDA"])
show_earnings = st.sidebar.checkbox("Show Earnings Calendar", value=True)

# Display earnings
if show_earnings:
    st.subheader("📅 Upcoming Earnings (Next 7 Days)")
    earnings = get_earnings_calendar()
    if not earnings.empty:
        st.dataframe(earnings.sort_values("DaysUntilEarnings"))
    else:
        st.info("No earnings data available.")

# Display sentiment charts
st.subheader("📰 News Sentiment by Ticker")

cols = st.columns(len(selected_tickers))
for i, ticker in enumerate(selected_tickers):
    with cols[i]:
        sentiment = get_news_sentiment(ticker)
        st.metric(label=f"{ticker}", value=f"{sentiment['Positive']} 🟢 / {sentiment['Negative']} 🔴")
