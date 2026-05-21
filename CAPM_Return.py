# import libraries

import datetime
import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import capm_functions

st.set_page_config(page_title="CAPM  Calculator", 
    page_icon="📈",
    layout="wide")

set_title = st.title("Capital Asset Pricing Model")

# getting user input for stock ticker and market index ticker

col1, col2 = st.columns([1,1])
with col1:
    stock_list = st.multiselect("Select 4 stock ", options=["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA","NFLX","MGM", "NVDA"], default=["AAPL","MSFT", "GOOGL", "AMZN"])
with col2:
    year = st.number_input("Number of years", 1,10)

# downloading data for sp500
try: 
    end = datetime.date.today()
    start = datetime.date(datetime.date.today().year - year, datetime.date.today().month, datetime.date.today().day)

    sp500 = web.DataReader(['sp500'],'fred',start,end)
    # print(sp500.tail())

    stocks_df = pd.DataFrame()

    for stock in stock_list:
        data = yf.download(stock, period=f"{year}y")
        stocks_df[f'{stock}'] = data['Close']

        # print(stocks_df.head())

    stocks_df.reset_index(inplace=True)
    sp500.reset_index(inplace=True)
    # print(stocks_df.dtypes)
    # print(sp500.dtypes)

    sp500.columns=['Date','sp500']
    stocks_df['Date'] = stocks_df['Date'].astype('datetime64[ns]')
    stocks_df['Date'] = stocks_df['Date'].apply(lambda x: str(x)[:10])
    stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])
    stocks_df = pd.merge(stocks_df, sp500, on='Date', how='inner')
    print(stocks_df)

    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown("### Dataframe head")
        st.dataframe(stocks_df.head(),use_container_width=True)

    with col2:
        st.markdown("### Dataframe tail")
        st.dataframe(stocks_df.tail(),use_container_width=True)


    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown("### Price of all the Stocks")
        st.plotly_chart(capm_functions.interactive_plot(stocks_df))

    with col2:
        
        st.markdown("### Price of all the Stocks - After Normalizaing")
        st.plotly_chart(capm_functions.interactive_plot(capm_functions.normalize(stocks_df)))

    stocks_daily_return = capm_functions.daily_return(stocks_df)
    print(stocks_daily_return.head())

    beta = {}
    alpha = {}

    for i in stocks_daily_return.columns[1:-1]:
        if i != 'Date' and i != 'sp500':
            b, a = capm_functions.calculate_beta(stocks_daily_return, i)

            beta[i] = b
            alpha[i] = a

    print(beta,alpha)

    beta_df = pd.DataFrame(columns=['Stock', 'Beta Value'])
    beta_df['Stock'] = beta.keys()
    beta_df['Beta Value'] = [str(round(i,2)) for i in beta.values()]

    with col1:
        st.markdown("### calculated Beta Values")
        st.dataframe(beta_df,use_container_width=True)

    rf = 0
    rm = stocks_daily_return['sp500'].mean()*252

    return_df = pd.DataFrame()
    return_value = []
    for stock, value in beta.items():
        return_value.append(str(round(rf + value*(rf - rm),2)))
    return_df['Stock'] = stock_list

    return_df['Return Value'] = return_value

    with col2:
        st.markdown("### calculated Return using CAPM")
        st.dataframe(return_df,use_container_width=True)

except:
    st.write("Please select valid input")