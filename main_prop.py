import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import re
from pytz import timezone
from PIL import Image
import plotly.graph_objects as go
import time
from streamlit_option_menu import option_menu


custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style='ticks', rc=custom_params)

@st.cache_data
def load_data(file_data):
    try:
        return pd.read_csv(file_data)
    except:
        return pd.read_excel(file_data)

def format_blue(text:str):
    st.markdown(
        f"""
        <div style="text-align: center;">
            <h2 style="color: lightblue;">{text}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

def blue(text:str):
    st.markdown(
        f"""
        <div style="text-align: center;">
            <h3 style="color: orange;">{text}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

def manipulation_data_frame(dataframe):
    df = dataframe
    df['trade-date'] = pd.to_datetime(df['trade-date'], format='%d/%m/%Y %I:%M:%S %p').dt.tz_localize('UTC')
    df['open-time'] = pd.to_datetime(df['open-time'], format='%d/%m/%Y %I:%M:%S %p').dt.tz_localize('UTC')
    df['close-time'] = pd.to_datetime(df['close-time'], format='%d/%m/%Y %I:%M:%S %p').dt.tz_localize('UTC')
    def duration_to_minutes(duration):      
        match = re.match(r'(?:(\d+):)?(\d+):(\d+):(\d+)', duration)
        if match:
            days, hours, minutes, seconds = match.groups()
            days = int(days) if days else 0
            hours = int(hours)
            minutes = int(minutes)
            seconds = int(seconds)
            total_minutes = days * 1440 + hours * 60 + minutes + seconds / 60
            return total_minutes
        return None
    df['duration'] = df['duration'].apply(duration_to_minutes)
    df['trade-date'] = df['trade-date'].dt.tz_convert('America/New_York')
    df['open-time'] = df['open-time'].dt.tz_convert('America/New_York')
    df['close-time'] = df['close-time'].dt.tz_convert('America/New_York')
    df['hour_of_day'] = df['trade-date'].dt.hour
    df['day_of_week'] = df['trade-date'].dt.day_name()
    df['pnl_category'] = df['pnl'].apply(lambda x: 'Gain' if x > 0 else 'Loss')
    df['TradeDay'] = df['trade-date'].apply(lambda x: x.strftime("%d-%m-%Y"))
    df['TradeDay'] = pd.to_datetime(df['TradeDay'], errors='coerce', format='%d-%m-%Y')
    df['ticket'] = df['ticket'].astype(str)
    return df

def main():
    st.set_page_config(page_title="Payouts Analysis",
                       page_icon='logo.jpg',
                       layout='wide',
                       initial_sidebar_state='expanded')

    st.markdown(
        """
        <div style="text-align: center;">
            <h1 style="color: lightblue;">Data Analysis to Approve Payouts</h1>
            <h2>Ensuring Payment Accuracy through Data Analysis.</h2>
            <p>This project aims to develop a data analysis tool for approving payments based on 
            rigorous validation and testing criteria. By analyzing trade frequency, trade execution,
            and conducting hypothesis tests, the app ensures the accuracy and reliability of the payments made. Incorporating these methods allows for more informed and secure decision-making in the payment approval process.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.image('logo.jpg')
    st.sidebar.markdown("---")

    # Carregamento do arquivo
    data_file_1 = st.sidebar.file_uploader("Open your file here", type=['csv', 'xlsx'])
    st.sidebar.markdown("---")

    if data_file_1 is not None:
        df = load_data(data_file_1)
        df = manipulation_data_frame(df)

        with st.sidebar:
            selected_page = option_menu(
                menu_title="Navigation",
                options=["Overview", "General Statistics", "Trade Frequency and Execution", 
                        "Trade Duration", "Simultaneos Open Positions","Regular Intervals", "Gambling Behavior", 
                        "Stop Loss", "Martingale","Consistency","Machine Learning"],
                icons=["house", "bar-chart-line", "clock", "hourglass", "calendar", 
                    "play-circle", "stop-circle", "shuffle", "check-circle"],
                menu_icon="cast",
                default_index=0,
                orientation="vertical",
                key="navigation_menu"
            )

        if selected_page == "Overview":
            st.markdown('---')
            format_blue("Overview")
            st.markdown(
                """
                <p>Below are some basic visualizations to provide insights into the data:</p>
                <ul>
                    <li><strong>Cumulative Profit/Loss:</strong> This line chart shows the cumulative profit and loss over time. It helps in understanding the overall financial performance and trend of the trades.</li>
                    <li><strong>Percentage of Trades by Symbols:</strong> This gauge chart displays the distribution of trades by symbols, indicating the proportion of trades associated with each symbol. It provides a quick view of the trading activity across different symbols.</li>
                </ul>
                """,
                unsafe_allow_html=True
            )
            col1, col2 = st.columns(2)
            with col1:
                df['cumulative_pnl'] = df['pnl'].cumsum()
                fig = px.line(df, x='trade-date', y='cumulative_pnl', title='Cumulative Profit/Loss', 
                              labels={'trade-date':'Trade Date', 'cumulative_pnl':'Cumulative PnL'}, 
                              color_discrete_sequence=['#1e87f7'])
                fig.update_layout(width=800, height=500, font=dict(size=16))
                st.plotly_chart(fig, use_container_width=True)

            with col2: 
                df_pair = (df[['symbol','ticket']].groupby('symbol').count().rename(columns={'ticket':'Percentual'})) / df.shape[0] * 100
                fig = go.Figure(data=[go.Pie(labels=df_pair.index, values=df_pair['Percentual'], hoverinfo='label+percent', textinfo='percent', marker=dict(colors=px.colors.sequential.Viridis), hole=.3)])
                fig.update_layout(title_text='Percentage of Trades by Symbols', showlegend=True, width=800, height=500, font=dict(size=16))
                st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df)
            st.write(f"rows: {df.shape[0]} and columns: {df.shape[1]}")
            


        elif selected_page == "General Statistics":
            st.markdown('---')
           
            st.markdown(
        """
        <div style="text-align: center;">
            <h2 style="color: lightblue;">General Statistics</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
            df1 = df.sort_values(by='open-time').reset_index(drop=True)

            events = pd.DataFrame({
                'time': pd.concat([df1['open-time'], df1['close-time']]),
                'event': ['open'] * len(df1) + ['close'] * len(df1)
            })

            events = events.sort_values('time').reset_index(drop=True)
            open_trades = 0
            simultaneous_positions = []
            for index, row in events.iterrows():
                if row['event'] == 'open':
                    open_trades += 1
                else:
                    open_trades -= 1
                simultaneous_positions.append(open_trades)

            df1['simultaneous_positions'] = pd.Series(simultaneous_positions[:len(df1)])
            
            simultaneous_trades_df = df1[df1['simultaneous_positions'] > 1]
            num_simultaneous_trades = len(simultaneous_trades_df)
            total_trades = len(df1)
            proportion_simultaneous = num_simultaneous_trades / total_trades

            average_profit = df.loc[df['pnl']>0,'pnl'].mean()
            average_loss = df.loc[df['pnl']<0,'pnl'].mean()
            risk_return_ratio = (df.loc[df['pnl']>0,'pnl'].mean()) / abs(df.loc[df['pnl']<0,'pnl'].mean()) if (df.loc[df['pnl']<0,'pnl'].mean()) != 0 else float('inf')
            win_percentage = ((df[df['pnl'] > 0].shape[0])/df.shape[0]) * 100
            loss_percentage = (100 - win_percentage)

            st.markdown(f"- Average Trade Duration: {round(df['duration'].mean())} minutes")
            st.markdown(f"- Risk-Return Ratio: {round(risk_return_ratio,2)}")
            st.markdown(f"- Total Trades less than 1 minute: {df.loc[df['duration']<1].shape[0]} Trades")
            st.markdown(f"- Percentage of Trades less than 1 minute: {round(((df.loc[df['duration']<1].shape[0])/df.shape[0])*100,2)}% of the total trades")
            st.markdown(f"- Total Number of Simultaneous Open Positions: {num_simultaneous_trades}")
            st.markdown(f"- Proportion simultaneous: {proportion_simultaneous:.2%}")
            st.markdown(f"- Total trades: {total_trades}")

            st.markdown("#### Basic statistical measures, including mean, median, and standard deviation, for key metrics")
            st.write(df.drop(columns=['ticket','swap','comment','TradeDay']).describe())

        elif selected_page == "Trade Frequency and Execution":
            st.markdown('---')
            st.markdown(
        """
        <div style="text-align: center;">
            <h2 style="color: lightblue;">Trade Frequency and Execution</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
            st.markdown("""
                The analysis of trade frequency and execution is essential to understanding market activity patterns. 
                Trade frequency can indicate the level of engagement and aggressiveness of the trader, while execution 
                analysis provides insights into the efficiency of the strategies employed.
            """)
            
            col1, col2 = st.columns(2)
            
            with col1:
                frequency_df = df[['TradeDay','pnl']].groupby('TradeDay').count().rename(columns={"pnl":"Frequency"})
                st.write(frequency_df)
                st.markdown("""
                    **Description:** The table above shows the daily trade frequency, 
                    indicating how many trades were made on each specific day. 
                    Days with high frequency may suggest increased volatility or market opportunities identified by the trader.
                """)
            
            with col2:
                st.markdown(f"- **Mean:** {round(frequency_df.mean().tolist()[0], 2)} trades per day")
                st.markdown(f"- **Median:** {frequency_df.median().tolist()[0]} trades per day")
                st.markdown(f"- **Upper Quartile:** {frequency_df.describe().loc['75%'].tolist()[0]} trades per day")
                st.markdown(f"- **Lower Quartile:** {frequency_df.describe().loc['25%'].tolist()[0]} trades per day")
                st.markdown(f"- **Minimum:** {frequency_df.min().tolist()[0]} trades per day")
                st.markdown(f"- **Maximum:** {frequency_df.max().tolist()[0]} trades per day")
                st.markdown("""
                    ### Statistical Analysis:
                    - **Mean and Median:** The mean provides an overall view of the number of trades per day, while the median 
                    can be a more robust indicator regarding the data distribution.
                    - **Quartiles:** The upper and lower quartiles help understand data dispersion, 
                    offering insight into variability in trade frequency.
                    - **Minimum and Maximum:** These values highlight the days with the least and most trading activity, 
                    respectively.
                """)
            
            st.markdown("---")
            st.subheader("Histogram of Trade Frequency")
            st.write("A histogram can be used to show the distribution of trading frequency per day. It reveals the density of different frequency intervals, helping to identify patterns in trading activity.")
            fig = px.histogram(frequency_df, x='Frequency', nbins=20,
                               labels={'Frequency': 'Number of Trades'}, template='simple_white')
            st.plotly_chart(fig)

            st.subheader("Frequency of Trades Over Time")
            st.write("A line graph showing the number of trades per day over time. This provides a clear view of daily trends and how trade frequency varies over time.")
            fig = px.line(frequency_df, x=frequency_df.index, y='Frequency',
                          labels={'index': 'Day', 'Frequency': 'Number of Trades'}, template='simple_white')
            st.plotly_chart(fig)

            st.subheader("Distribution of Trade Frequency")
            st.write("A boxplot can be used to visualize the distribution of trade frequency per day, including median, quartiles, and possible outliers. This provides a visual representation of the dispersion of the data.")
            fig = px.box(frequency_df, y='Frequency',
                         labels={'Frequency': 'Number of Trades'}, template='simple_white')
            st.plotly_chart(fig)

            st.subheader("Heatmap of Trade Frequency by Day and Hour")
            st.write("can be used to show the distribution of trading frequency at different times of the day and days of the week. This can reveal seasonal patterns or times of high activity")
            heatmap_data = df.pivot_table(index=df['trade-date'].dt.hour, columns=df['trade-date'].dt.day_name(), 
                                          values='ticket', aggfunc='count')
            fig = px.imshow(heatmap_data, color_continuous_scale='Viridis')
            st.plotly_chart(fig)

            st.write("### Days with Above-Average Frequency")
            st.write(frequency_df[frequency_df['Frequency'] > round(frequency_df.mean().tolist()[0], 2)])
            st.markdown("""
                **Description:** The table above highlights the days where the number of trades exceeded the average. 
                These days can be analyzed further to understand the factors that led to increased trading activity.
            """)

            st.subheader("Days with Above Average Trade Frequency")
            above_average_df = frequency_df[frequency_df['Frequency'] > round(frequency_df.mean().tolist()[0], 2)]
            fig = px.bar(above_average_df, x=above_average_df.index, y='Frequency',
                         labels={'index': 'Day', 'Frequency': 'Number of Trades'}, template='simple_white')
            st.plotly_chart(fig)
            st.markdown('---')
            st.write("**If you prefer to filter the data from a specific date, please select below.**")
            start_date = st.date_input("Start Date", value=pd.to_datetime(df['trade-date']).min().date())
            end_date = st.date_input("End Date", value=pd.to_datetime(df['trade-date']).max().date())
            start_date = pd.to_datetime(start_date).tz_localize('America/New_York')
            end_date = pd.to_datetime(end_date).tz_localize('America/New_York')
            filtered_df = df.loc[(df['trade-date'] >= start_date) & (df['trade-date'] <= end_date)]
            st.dataframe(filtered_df)
            st.markdown('---')

        elif selected_page == "Trade Duration":
            st.markdown('---')
            
            
            st.markdown(
        """
        <div style="text-align: center;">
            <h2 style="color: lightblue;">Trade Duration</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

            col1, col2 = st.columns(2)
            
            with col1:
                st.write("#### Statistics : ")
                st.markdown(f"- **Mean Execution Time:** {round(df.duration.mean())} minutes")
                st.markdown(f"- **Median Execution Time:** {round(df.duration.median())} minutes")
                st.markdown(f"- **Upper Quartile:** {round(df[['duration']].describe().loc['75%'].tolist()[0],2)} minutes")
                st.markdown(f"- **Lower Quartile:** {round(df[['duration']].describe().loc['25%'].tolist()[0],2)} minutes")
                st.markdown(f"- **Maximum Duration:** {round(df.duration.max(),2)} minutes")
                st.markdown(f"- **Minimum Duration:** {round(df.duration.min(),2)} minutes")
                st.markdown("""
                    **Description:** The statistics above summarize the trade duration data:
                    - **Mean and Median Execution Time** provide central tendency measures, indicating the typical duration of trades.
                    - **Quartiles** help understand the distribution of trade durations, showing where 50% of the durations fall within the upper and lower quartiles.
                    - **Maximum and Minimum Durations** highlight the extremes, showing the longest and shortest trade durations observed.
                """)

            with col2:

                st.write("#### Average Trade Duration by Day:")
                avg_duration_by_day = df[['duration', 'TradeDay']].groupby('TradeDay').mean()
                st.write(avg_duration_by_day)
                
                st.markdown("""
                    **Description:** This table shows the average trade duration for each trading day. 
                    Analyzing the average durations can reveal patterns in how long trades tend to last over different days, 
                    which could be linked to market conditions or strategy adjustments.
                """)
            st.markdown('---')
            st.write("### Days with Above-Average Trade Duration")
            st.write(avg_duration_by_day[avg_duration_by_day['duration'] > avg_duration_by_day['duration'].mean()])
            st.markdown("""
                **Description:** This table identifies the days where the average trade duration was longer than usual. 
                These days might indicate times when the market was more challenging, leading to longer decision-making processes, 
                or when strategies required more time to execute fully.
            """)

            # Visualization 1: Histogram of Trade Durations
            st.write("### Distribution of Trade Durations")
            fig1 = px.histogram(df, x='duration', marginal="box", template='simple_white')
            fig1.update_layout(xaxis_title='Duration (minutes)', yaxis_title='Frequency')
            st.plotly_chart(fig1)
            st.markdown("""
                **Description:** This histogram shows the distribution of trade durations. The marginal boxplot highlights the spread and any potential outliers.
                Understanding this distribution can help identify common trade durations and anomalies.
            """)

            # Visualization 2: Boxplot of Trade Durations
            st.write("### Boxplot of Trade Durations")
            fig2 = px.box(df, y='duration')
            fig2.update_layout(yaxis_title='Duration (minutes)')
            st.plotly_chart(fig2)
            st.markdown("""
                **Description:** The boxplot provides a visual summary of trade duration distribution, including the median, quartiles, and outliers.
                It's useful for identifying the range of typical trade durations and any unusually long or short trades.
            """)

            # Visualization 3: Time Series Line Plot of Average Trade Duration by Day
            st.write("### Time Series of Average Trade Duration by Day")
            fig3 = px.bar(df, x='TradeDay', y='duration')
            fig3.update_layout(xaxis_title='Trade Day', yaxis_title='Average Duration (minutes)')
            st.plotly_chart(fig3)
            st.markdown("""
                **Description:** This time series plot shows how the average trade duration changes over different trading days.
                It can reveal trends or patterns related to specific days that might require further investigation.
            """)

            # Visualization 4: Scatter Plot of Trade Duration vs. Trade Day
            st.write("### Scatter Plot of Trade Duration vs. Trade Day")
            fig4 = px.scatter(df, x='TradeDay', y='duration')
            fig4.update_layout(xaxis_title='Trade Day', yaxis_title='Duration (minutes)')
            st.plotly_chart(fig4)
            st.markdown("""
                **Description:** The scatter plot shows individual trade durations across different trading days.
                This visualization helps identify specific days with particularly high or low trade durations.
            """)

            # Visualization 5: Heatmap of Trade Duration vs. Symbol
            st.write("### Heatmap of Trade Duration vs. Symbol")
            pivot_table = df.pivot_table(values='duration', index='symbol', columns='TradeDay', aggfunc='mean').reset_index()
            fig5 = px.imshow(pivot_table.set_index('symbol'))
            fig5.update_layout(xaxis_title='Trade Day', yaxis_title='Symbol')
            st.plotly_chart(fig5)
            st.markdown("""
                **Description:** This heatmap visualizes the average trade duration by symbol across different trading days.
                It helps identify which symbols tend to have longer or shorter trades on specific days.
            """)

            # Visualization 6: Bar Chart of Average Trade Duration by Symbol
            st.write("### Average Trade Duration by Symbol")
            avg_duration_by_symbol = df.groupby('symbol')['duration'].mean().sort_values().reset_index()
            fig6 = px.bar(avg_duration_by_symbol, x='symbol', y='duration')
            fig6.update_layout(xaxis_title='Symbol', yaxis_title='Average Duration (minutes)')
            st.plotly_chart(fig6)
            st.markdown("""
                **Description:** This bar chart shows the average trade duration for each symbol.
                It's useful for identifying which symbols typically involve longer or shorter trades.
            """)

            # Visualization 7: Trade Duration vs. Lots Size Scatter Plot
            st.write("### Scatter Plot of Trade Duration vs. Lots Size")
            fig7 = px.scatter(df, x='lots', y='duration')
            fig7.update_layout(xaxis_title='Lots Size', yaxis_title='Duration (minutes)')
            st.plotly_chart(fig7)
            st.markdown("""
                **Description:** This scatter plot explores the relationship between trade duration and lot size.
                It helps identify whether larger or smaller trades tend to take more or less time.
            """)

            # Visualization 8: Cumulative Distribution Function (CDF) of Trade Durations
            st.write("### CDF of Trade Durations")
            fig8 = px.ecdf(df, x='duration',)
            fig8.update_layout(xaxis_title='Duration (minutes)',title='Cumulative Distribution Function of Trade Durations')
            st.plotly_chart(fig8)
            st.markdown("""
                **Description:** The CDF shows the proportion of trades completed within a certain duration.
                It's useful for understanding how quickly the majority of trades are executed.
            """)

            # Visualization 9: Time Series of Maximum and Minimum Trade Durations by Day
            st.write("### Maximum and Minimum Trade Durations by Day")
            max_min_duration_by_day = df.groupby('TradeDay')['duration'].agg(['max', 'min']).reset_index()
            fig9 = px.line(max_min_duration_by_day, x='TradeDay', y=['max', 'min'], )
            fig9.update_layout(xaxis_title='Trade Day', yaxis_title='Duration (minutes)')
            st.plotly_chart(fig9)
            st.markdown("""
                **Description:** This line plot shows the maximum and minimum trade durations for each day.
                It's helpful for identifying days with extreme trade durations that may indicate unusual market conditions.
            """)

            
            st.write("### Violin Plot of Trade Duration by Symbol")
            fig10 = px.violin(df, y='duration', box=True, points="all",color='symbol',template='simple_white')
            fig10.update_layout(xaxis_title='Symbol', yaxis_title='Duration (minutes)')
            st.plotly_chart(fig10)
            st.markdown("""
                **Description:** The violin plot shows the distribution of trade durations for each symbol, including the density and range of durations.
                It's useful for comparing the spread of trade durations across different symbols.
            """)
            st.markdown('---')
            st.header("Trade that had a duration of less than 1 minute")
            st.write("""
            Now, let’s dive into an interesting subset of trades—those that had a duration of less than one minute. Such quick trades can be indicative of high-frequency trading strategies, potentially automated by trading bots. The purpose of this analysis is to identify patterns that may suggest the presence of manipulative behavior or the use of trading bots, which could undermine market fairness.
            Description: Trades that are executed in under a minute might not follow the typical human decision-making process and are often associated with automated trading systems. These trades could be designed to exploit market inefficiencies or to execute large orders in a rapid manner. By analyzing these trades, we can uncover suspicious activity or identify users who might be employing high-frequency trading algorithms.""")
            
            quick_trades = df[df['duration'] < 1]

            # Visualization 1: Histogram of Quick Trades by Duration
            st.write("### Histogram of Quick Trades by Duration")
            fig1 = px.histogram(quick_trades, x='duration', title='Histogram of Quick Trades by Duration', nbins=30, template='simple_white')
            fig1.update_layout(xaxis_title='Duration (seconds)', yaxis_title='Frequency')
            st.plotly_chart(fig1)

            # Description for Histogram
            st.markdown("""
            **Description:** The histogram above shows the distribution of trades that were completed in under one minute. 
            A higher frequency of trades at the lower end of the duration scale could indicate the use of trading bots that 
            execute orders extremely quickly.
            """)

            # Visualization 2: Scatter Plot of Quick Trades - Duration vs. Lots Size
            st.write("### Scatter Plot of Quick Trades - Duration vs. Lots Size")
            fig2 = px.scatter(quick_trades, x='lots', y='duration', title='Duration vs. Lots Size for Quick Trades',color='symbol')
            fig2.update_layout(xaxis_title='Lots Size', yaxis_title='Duration (seconds)')
            st.plotly_chart(fig2)

            # Description for Scatter Plot
            st.markdown("""
            **Description:** This scatter plot visualizes the relationship between the trade size and the duration for trades 
            under one minute. Observing patterns here might help identify whether large trades are being executed quickly, 
            which could be another sign of automated trading.
            """)

            # Visualization 3: Bar Chart of Average Trade Duration by Symbol for Quick Trades
            st.write("### Average Trade Duration by Symbol for Quick Trades")
            avg_duration_quick_trades = quick_trades.groupby('symbol')['duration'].mean().sort_values().reset_index()
            fig3 = px.bar(avg_duration_quick_trades, x='symbol', y='duration', title='Average Trade Duration by Symbol for Quick Trades')
            fig3.update_layout(xaxis_title='Symbol', yaxis_title='Average Duration (seconds)')
            st.plotly_chart(fig3)

            # Description for Bar Chart
            st.markdown("""
            **Description:** The bar chart shows the average duration of quick trades (less than one minute) for each trading symbol. 
            Symbols with unusually short average durations may warrant further investigation to determine if they are being targeted by 
            high-frequency trading strategies.
            """)

            # Visualization 4: Violin Plot of Trade Duration by Symbol for Quick Trades
            st.write("### Violin Plot of Trade Duration by Symbol for Quick Trades")
            fig4 = px.violin(quick_trades, x='symbol', y='duration', title='Violin Plot of Trade Duration by Symbol for Quick Trades', box=True, points="all")
            fig4.update_layout(xaxis_title='Symbol', yaxis_title='Duration (seconds)')
            st.plotly_chart(fig4)

            # Description for Violin Plot
            st.markdown("""
            **Description:** The violin plot displays the distribution of trade durations for each symbol among trades lasting 
            less than one minute. This visualization can help us understand the spread and density of quick trades for different symbols, 
            potentially indicating patterns of trading activity that may be linked to the use of bots.
            """)

            # Visualization 5: Time Series of Number of Quick Trades by Day
            st.write("### Number of Quick Trades by Day")
            quick_trades_by_day = quick_trades.groupby('TradeDay').size().reset_index(name='count')
            fig5 = px.line(quick_trades_by_day, x='TradeDay', y='count', title='Number of Quick Trades by Day')
            fig5.update_layout(xaxis_title='Trade Day', yaxis_title='Number of Trades')
            st.plotly_chart(fig5)

            # Description for Time Series
            st.markdown("""
            **Description:** This time series plot tracks the number of trades executed in under one minute across different trading days. 
            Anomalies, such as sudden spikes in quick trades, could point to specific days where trading bots were more active, possibly 
            due to market conditions or events.
            """)

            # Conclusion
            st.markdown("""
            **Conclusion:** The analyses above provide a focused view on trades executed in under a minute, highlighting potential indicators 
            of automated or manipulative trading activities. These insights are crucial for identifying and understanding patterns that 
            could suggest unfair trading practices in the market.
            """)
            st.write("#### Detais of the trades that had a duration of less than 1 minute")
            less_1m = df.loc[df['duration']<1,['symbol','pnl','volume','lots','duration','open-price','close-price','TradeDay','ticket']].set_index('TradeDay')
            st.write(less_1m)
            pd.options.display.float_format = '{:.2f}'.format
            st.write("#### Describe")
            st.write(less_1m.drop(columns=['ticket']).describe().T)
            st.markdown('---')
            st.write("**If you prefer to filter the data from a specific date, please select below.**")
            start_date = st.date_input("Start Date", value=pd.to_datetime(df['trade-date']).min().date())
            end_date = st.date_input("End Date", value=pd.to_datetime(df['trade-date']).max().date())
            start_date = pd.to_datetime(start_date).tz_localize('America/New_York')
            end_date = pd.to_datetime(end_date).tz_localize('America/New_York')
            filtered_df = df.loc[(df['trade-date'] >= start_date) & (df['trade-date'] <= end_date)]
            st.dataframe(filtered_df)
            st.markdown('---')

        elif selected_page == "Simultaneos Open Positions":
            st.markdown("---")
            format_blue("Simultaneos open positions")
            
            
            st.write("### Details")
            # Ordenar o dataframe pelas colunas de tempo de abertura dos trades
            df1 = df.sort_values(by='open-time').reset_index(drop=True)

            # Criar um dataframe para armazenar os eventos de abertura e fechamento dos trades
            events = pd.DataFrame({
                'time': pd.concat([df1['open-time'], df1['close-time']]),
                'event': ['open'] * len(df1) + ['close'] * len(df1),
                'ticket': pd.concat([df1['ticket'], df1['ticket']])
            })

            # Ordenar os eventos por tempo
            events = events.sort_values('time').reset_index(drop=True)

            # Variável para rastrear o número de trades simultâneos
            open_trades = 0
            simultaneous_positions = []
            open_tickets = []

            # Contador para armazenar tickets abertos simultaneamente
            simultaneous_details = []

            # Iterar sobre os eventos para calcular os trades simultâneos
            for index, row in events.iterrows():
                if row['event'] == 'open':
                    open_trades += 1
                    open_tickets.append(row['ticket'])  # Adiciona o ticket à lista de abertos
                else:
                    open_tickets.remove(row['ticket'])  # Remove o ticket da lista de abertos
                    open_trades -= 1

                simultaneous_positions.append(open_trades)
                
                # Armazena detalhes se houver trades simultâneos
                if open_trades > 1:
                    simultaneous_details.append({
                        'Ticket': row['ticket'],
                        'Open Trades Tickets': open_tickets.copy(),
                        'Time': row['time']
                    })

            # Adiciona ao dataframe original a contagem de posições simultâneas
            df1['simultaneous_positions'] = pd.Series(simultaneous_positions[:len(df1)])

            # Filtrar trades simultâneos
            simultaneous_trades_df = df1[df1['simultaneous_positions'] > 1]
            st.write(simultaneous_trades_df[['ticket','open-time','close-time','simultaneous_positions']])
            # Gerar relatório detalhado de trades simultâneos
            for index, row in simultaneous_trades_df.iterrows():
                details = [d for d in simultaneous_details if row['ticket'] in d['Open Trades Tickets']]
                
                if details:
                    format_blue(f"\n     {row['TradeDay']}")
                    for i, detail in enumerate(details):
                        ticket_info = df1[df1['ticket'] == detail['Ticket']].iloc[0]
                        previous_ticket = details[i - 1]['Ticket'] if i > 0 else 'None (first in the list)'
                        time_diff = (detail['Time'] - details[i - 1]['Time']).total_seconds() if i > 0 else 'N/A'
                        st.markdown(f"**Ticket:** {ticket_info['ticket']}")
                        st.markdown(f"**Previous Trade Ticket:** {previous_ticket}")
                        st.markdown(f"**Open Time:** {ticket_info['open-time']}")
                        st.markdown(f"**Close Time:** {ticket_info['close-time']}")
                        st.markdown(f"**Open Price:** {ticket_info['open-price']}")
                        st.markdown(f"**Close Price:** {ticket_info['close-price']}")
                        st.markdown(f"**Symbol:** {ticket_info['symbol']}")
                        st.markdown(f"**PNL:** ${ticket_info['pnl']:.2f}")
                        st.markdown(f"Time Difference from Previous Trade: {time_diff} seconds")
                        st.markdown("---")
            # Visualization 1: Line Chart of Simultaneous Positions Over Time
            st.write("### Line Chart of Simultaneous Positions Over Time")
            fig1 = px.line(df1, x='open-time', y='simultaneous_positions', title='Simultaneous Positions Over Time')
            fig1.update_layout(xaxis_title='Time', yaxis_title='Simultaneous Positions', template='plotly_dark')
            st.plotly_chart(fig1)

            # Description for Line Chart
            st.markdown("""
            **Description:** This line chart displays the number of simultaneous positions over time. A significant increase may indicate 
            that multiple trades are being opened simultaneously, possibly signaling the use of a martingale strategy or other multi-trade approaches.
            """)

            # Visualization 2: Heatmap of Simultaneous Positions by Hour and Day of the Week
            st.write("### Heatmap of Simultaneous Positions by Hour and Day of the Week")
            heatmap_data = df1.groupby(['hour_of_day', 'day_of_week'])['simultaneous_positions'].mean().reset_index()

            fig2 = px.density_heatmap(heatmap_data, x='hour_of_day', y='day_of_week', z='simultaneous_positions', 
                                    title='Simultaneous Positions by Hour and Day of the Week',
                                    color_continuous_scale='Blues')
            fig2.update_layout(xaxis_title='Hour of the Day', yaxis_title='Day of the Week', template='plotly_dark')
            st.plotly_chart(fig2)

            # Description for Heatmap
            st.markdown("""
            **Description:** This heatmap reveals the density of simultaneous positions distributed across different hours of the day 
            and days of the week. It highlights critical moments when multiple trades are being executed.
            """)

            # Visualization 3: Scatter Plot of PNL vs. Volume in Simultaneous Trades
            st.write("### Scatter Plot of PNL vs. Volume in Simultaneous Trades")
            fig3 = px.scatter(simultaneous_trades_df, x='volume', y='pnl', color='symbol', 
                            title='PNL vs. Volume in Simultaneous Trades',
                            labels={'volume': 'Volume', 'pnl': 'PNL'},
                            hover_data=['ticket', 'open-time'])
            fig3.update_traces(marker=dict(size=12, line=dict(width=2, color='DarkSlateGrey')))
            st.plotly_chart(fig3)

            # Description for Scatter Plot
            st.markdown("""
            **Description:** This scatter plot visualizes the relationship between profit/loss (PNL) and trade volume for simultaneous trades. 
            Different colors represent different symbols, and larger bubbles may indicate high volatility in these trades.
            """)

            # Visualization 4: Histogram of Trade Duration for Simultaneous Trades
            st.write("### Histogram of Trade Duration for Simultaneous Trades")
            fig4 = px.histogram(simultaneous_trades_df, x='duration', title='Duration of Simultaneous Trades')
            fig4.update_layout(xaxis_title='Duration (minutes)', yaxis_title='Frequency', template='plotly_dark')
            st.plotly_chart(fig4)

            # Description for Histogram
            st.markdown("""
            **Description:** This histogram shows the distribution of trade durations for simultaneous trades. 
            Longer durations could indicate trades held for extended periods, which may be linked to specific trading strategies.
            """)

            # Visualization 5: Histogram of Simultaneous Trades by Symbol
            st.write("### Histogram of Simultaneous Trades by Symbol")
            fig5 = px.histogram(simultaneous_trades_df, x='symbol', title='Distribution of Simultaneous Trades by Symbol')
            fig5.update_layout(xaxis_title='Symbol', yaxis_title='Number of Trades', template='plotly_dark')
            st.plotly_chart(fig5)

            # Description for Symbol Histogram
            st.markdown("""
            **Description:** This histogram illustrates the distribution of simultaneous trades by symbol. 
            If a particular asset is being traded at high volumes, it may indicate manipulation or special strategies.
            """)

            # Adding the 'time_diff' column to the dataframe
            df['time_diff'] = df['open-time'].diff().dt.total_seconds()

            # Visualization 6: Scatter Plot of Time Difference Between Trades vs. PNL
            st.write("### Scatter Plot of Time Difference Between Trades vs. PNL")
            fig6 = px.scatter(df, x='time_diff', y='pnl', color='symbol', 
                            title='Time Difference Between Trades vs. PNL',
                            labels={'time_diff': 'Time Difference (seconds)', 'pnl': 'PNL'})
            st.plotly_chart(fig6)

            # Description for Time Difference Scatter Plot
            st.markdown("""
            **Description:** This scatter plot shows the relationship between the time difference between trades and PNL. 
            Shorter time intervals between trades may indicate high-frequency trading strategies.
            """)

            # Visualization 7: Histogram of Time Difference Between Trades
            st.write("### Histogram of Time Difference Between Trades")
            fig7 = px.histogram(df, x='time_diff', title='Histogram of Time Difference Between Trades')
            fig7.update_layout(xaxis_title='Time Difference (seconds)', yaxis_title='Frequency', template='plotly_dark')
            st.plotly_chart(fig7)

            # Description for Time Difference Histogram
            st.markdown("""
            **Description:** This histogram displays the distribution of time differences between trades. 
            A high frequency of short intervals between trades may indicate rapid market movements or automated trading systems.
            """)

            # Visualization 8: Line Chart of Time Difference Between Trades Over Time
            st.write("### Line Chart of Time Difference Between Trades Over Time")
            fig8 = px.line(df, x='open-time', y='time_diff', title='Evolution of Time Difference Between Trades Over Time')
            fig8.update_layout(xaxis_title='Time', yaxis_title='Time Difference (seconds)', template='plotly_dark')
            st.plotly_chart(fig8)

            # Description for Time Difference Line Chart
            st.markdown("""
            **Description:** This line chart tracks the time difference between trades over time. 
            A decrease in time intervals between trades could suggest periods of heightened trading activity.
            """)
            st.write("**If you prefer to filter the data from a specific date, please select below.**")
            start_date = st.date_input("Start Date", value=pd.to_datetime(df['trade-date']).min().date())
            end_date = st.date_input("End Date", value=pd.to_datetime(df['trade-date']).max().date())
            start_date = pd.to_datetime(start_date).tz_localize('America/New_York')
            end_date = pd.to_datetime(end_date).tz_localize('America/New_York')
            filtered_df = df.loc[(df['trade-date'] >= start_date) & (df['trade-date'] <= end_date)]
            st.dataframe(filtered_df)
            st.markdown('---')

        elif selected_page == "Gambling Behavior":
            st.markdown('---')

            st.markdown(
                """
                <div style="text-align: center;">
                    <h2 style="color: lightblue;">Gambling Behavior Analysis</h2>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.subheader("Analysis of Trade Volumes")

            st.write("""
                This section provides a comprehensive analysis of the trading volumes (lots) used in each transaction. 
                By examining the volume of trades, we aim to identify patterns, potential risk-taking behaviors, 
                and any signs of gambling-like tendencies in trading activity. Understanding trade volumes can offer 
                valuable insights into how aggressive or conservative trading strategies are and how they evolve over time.
            """)

            col1,col2 = st.columns(2)
            with col1:
                st.subheader('Lots per Trade')
                st.write(df[['trade-date','lots']].set_index('trade-date'))
            with col2:
                st.subheader("Descriptive Statistics of Trade Volumes")
                st.write(f"- **Mean Volume:** {round(df['lots'].mean(), 2)} lots")
                st.write(f"- **Median Volume:** {round(df['lots'].median(), 2)} lots")
                st.write(f"- **Maximum Volume:** {round(df['lots'].max(), 2)} lots")
                st.write(f"- **Minimum Volume:** {round(df['lots'].min(), 2)} lots")
                st.markdown(f"- **Lower Quartile:** {df['lots'].describe().to_dict()['25%']}")
                st.markdown(f"- **Upper Quartile:** {df['lots'].describe().to_dict()['75%']}")
                st.write(f"- **Standard Deviation:** {round(df['lots'].std(), 2)}")
                st.write("""
                    **Description:** This analysis provides an overview of the trading volumes (lots), helping identify 
                    common trade sizes and potential outliers.
                """)
            st.markdown('---')
            col1,col2 = st.columns(2)
            with col1:
                st.subheader("Higher than the mean")
                st.write(df.loc[df['lots'] >df['lots'].mean(),['trade-date','lots']])

            with col2:
                st.subheader("Distribution of Trade Volumes")
                fig = px.histogram(df, x='lots', nbins=20, template='simple_white')
                fig.update_layout(xaxis_title='Volume (lots)', yaxis_title='Frequency')
                st.plotly_chart(fig)
                st.write("""
                    **Description:** The histogram displays how frequently different trade volumes (lots) are used, 
                    helping to spot potential overuse of large volumes, which might indicate risky or aggressive behavior.
                """)

            st.subheader("Trade Volumes vs. Trade Outcomes")
            fig = px.scatter(df, x='lots', y='pnl', template='simple_white')
            fig.update_layout(xaxis_title='Volume (lots)', yaxis_title='Profit/Loss')
            st.plotly_chart(fig)
            st.write("""
                **Description:** This scatter plot shows the relationship between the volume of trades and the corresponding outcomes (profit/loss), 
                potentially revealing if larger volume trades tend to be more profitable or riskier.
            """)

            st.subheader("Boxplot of Trade Volumes by Day")
            fig = px.box(df, x='TradeDay', y='lots', template='simple_white')
            fig.update_layout(xaxis_title='Trade Day', yaxis_title='Volume (lots)')
            st.plotly_chart(fig)
            st.write("""
                **Description:** This boxplot shows the distribution of trade volumes for each trading day, 
                helping to understand if certain days are associated with higher or lower volumes.
            """)


            st.subheader("Cumulative Trade Volume Over Time")
            df['cumulative_volume'] = df['lots'].cumsum()
            fig = px.line(df, x='trade-date', y='cumulative_volume', template='simple_white')
            fig.update_layout(xaxis_title='Date', yaxis_title='Cumulative Volume (lots)')
            st.plotly_chart(fig)
            st.write("""
                **Description:** This cumulative plot tracks the total trade volume over time, showing how aggressively trading strategies are applied across the dataset.
            """)

            st.subheader("Comparison of Volumes in Winning vs. Losing Trades")
            fig = px.box(df, x='pnl_category', y='lots', template='simple_white')  # win_or_loss could be a column indicating 1 for win and 0 for loss
            fig.update_layout(xaxis_title='Trade Outcome (Win/Loss)', yaxis_title='Volume (lots)')
            st.plotly_chart(fig)
            st.write("""
                **Description:** This boxplot compares the trade volumes in winning vs. losing trades, 
                revealing if larger volumes are more frequently associated with successful or unsuccessful trades.
            """)
            st.subheader("Boxplot of Trade Volumes by Symbol")
            fig=px.box(data_frame=df,y='lots',color='symbol')
            st.plotly_chart(fig)
            st.write("""
                     **Description:** The boxplot visualizes the distribution
                      of trade volumes (lots) across different trading symbols. 
                     Each box represents the interquartile range (IQR) of trade volumes 
                     for a specific symbol, with the line inside the box indicating the 
                     median volume. The whiskers extend to show the range of the data, 
                     excluding outliers, which are plotted as individual points. This 
                     visualization helps in comparing the spread and central tendency of 
                     trade volumes among various symbols, revealing any significant differences in trading behavior or volume ranges across different symbols. It is particularly useful for identifying which symbols have higher variability in trade volumes and spotting any potential outliers.""")
            st.write("---")
            st.subheader("Detailed Analysis of Trade Volumes by Symbol")
            lista_symbol = df.symbol.unique().tolist()
            for sym in lista_symbol:
                    format_blue(f"{sym.upper()}")
                    
                    # Filter data for the current symbol
                    data_zone = df.loc[df['symbol'] == sym, ['trade-date', 'lots']]
                    data_zone['date'] = data_zone['trade-date'].dt.date  # Extract date only
                    
                    # Display daily data
                    for day, group in data_zone.groupby('date'):
                        blue(f"Date: {day}")
                        st.dataframe(group[['trade-date', 'lots']].set_index('trade-date'))
                        st.write(f"**Average lots for {day}:** {group['lots'].mean():.2f}")
                        st.markdown('---')
                    
                    # Display summary statistics
                    format_blue(f"Total Summary for {sym.upper()}:")
                    st.markdown(f"""
                    - **Mean Lots:** {data_zone['lots'].mean():.2f}
                    - **Median Lots:** {data_zone['lots'].median():.2f}
                    - **Upper Quartile:** {data_zone['lots'].quantile(0.75):.2f}
                    - **Lower Quartile:** {data_zone['lots'].quantile(0.25):.2f}
                    """)
                    st.markdown('---')
                    st.markdown('---')

            st.subheader("Average Trade Volume per Day of the Week")
            df['day_of_week'] = pd.to_datetime(df['trade-date']).dt.day_name()
            avg_volume_per_day = df.groupby('day_of_week')['lots'].mean()
            st.write(avg_volume_per_day)
            st.write("""
                **Description:** This table shows the average volume of trades for each day of the week, revealing patterns of aggressive or cautious behavior on specific days.
            """)
            fig = px.bar(data_frame=avg_volume_per_day,x=avg_volume_per_day.index,y='lots')
            st.plotly_chart(fig)
            st.write("**If you prefer to filter the data from a specific date, please select below.**")
            start_date = st.date_input("Start Date", value=pd.to_datetime(df['trade-date']).min().date())
            end_date = st.date_input("End Date", value=pd.to_datetime(df['trade-date']).max().date())
            start_date = pd.to_datetime(start_date).tz_localize('America/New_York')
            end_date = pd.to_datetime(end_date).tz_localize('America/New_York')
            filtered_df = df.loc[(df['trade-date'] >= start_date) & (df['trade-date'] <= end_date)]
            st.dataframe(filtered_df)
            st.markdown('---')
        
        elif selected_page == "Regular Intervals":
            st.markdown('---')
            format_blue("Analysis of Regular Trade Intervals")
            st.subheader("Overview of Trade Execution at Regular Intervals")
            st.write("""
                In this section, we perform an in-depth analysis of trade execution intervals. 
                We examine the frequency of trades executed at regular time intervals, 
                ranging from seconds to hours. This analysis helps identify if there are 
                any patterns or systematic behaviors in trading activities that occur 
                at specific intervals. 

                The analysis includes:
                - Identification of trades executed at exact intervals (e.g., every 1 second, 5 seconds, etc.).
                - Comparative analysis of trade volume and frequency across different time intervals.
                - Visualization of the percentage of trades executed within each specified interval.
                
                By examining these patterns, we aim to uncover any regular trading behaviors or 
                strategies that operate on set schedules, which could be indicative of algorithmic trading 
                strategies or other systematic trading practices.
            """)
            
            st.subheader("Detailed Breakdown of Trades Executed at Regular Intervals")
            st.write("""
                The following table provides a detailed breakdown of trades executed within specified time intervals.
                The intervals range from very short durations (e.g., 1 second) to longer periods (e.g., 3600 seconds). 
                For each interval, we display:
                - The total number of trades.
                - The number of trades executed within the interval.
                - The percentage of trades that fall within the interval.
            """)
            # Converte a coluna 'trade-date' para datetime se ainda não estiver
            df['trade-date'] = pd.to_datetime(df['trade-date'])
            df['time_diff'] = df['trade-date'].diff().dt.total_seconds()

            # Define os intervalos de tempo em segundos
            intervals_seconds = [1, 5, 15, 30, 45, 60, 120, 240, 480, 960, 3600]

            
            results = []

            # Loop para calcular as métricas para cada intervalo
            for interval in intervals_seconds:
                interval_range = range(0, interval + 1, 1)  # Intervalos de 1 segundo para precisão

                interval_results = []

                for start in interval_range:
                    end = start + 1
                    regular_trades = df[df['time_diff'].between(start, end)]
                    
                    # Calcula as estatísticas
                    count_trades = regular_trades.shape[0]
                    total_trades = df.shape[0]
                    regular_percentage = (count_trades / total_trades) * 100
                    average_lots = regular_trades['lots'].mean() if count_trades > 0 else None
                    
                    interval_results.append({
                        'Interval Start (seconds)': start,
                        'Interval End (seconds)': end,
                        'Total Trades': total_trades,
                        'Regular Trades': count_trades,
                        'Percentage of Regular Trades': regular_percentage,
                        'Average Lots': average_lots
                    })
                
                # Converte resultados em um DataFrame
                results_df = pd.DataFrame(interval_results)
                
                # Exibe a tabela com os resultados para o intervalo atual
                blue(f"\n Interval from 0 to {interval} seconds")
                st.markdown("\n#### Detailed Breakdown of Trades Executed at Regular Intervals:")
                st.dataframe(results_df)
                
                # Plota gráficos comparativos
                fig1 = px.bar(results_df, x='Interval End (seconds)', y='Percentage of Regular Trades',template='plotly_dark',
                            title=f'Percentage of Trades Executed at Regular Intervals (0 to {interval} seconds)',
                            labels={'Interval End (seconds)': 'Interval End (Seconds)', 'Percentage of Regular Trades': 'Percentage (%)'})
                st.plotly_chart(fig1)
                
                fig2 = px.bar(results_df, x='Interval End (seconds)', y='Average Lots',template='plotly_dark',
                            title=f'Average Lots for Trades Executed at Regular Intervals (0 to {interval} seconds)',
                            labels={'Interval End (seconds)': 'Interval End (Seconds)', 'Average Lots': 'Average Lots'})
                st.plotly_chart(fig2)
            st.write("**If you prefer to filter the data from a specific date, please select below.**")
            start_date = st.date_input("Start Date", value=pd.to_datetime(df['trade-date']).min().date())
            end_date = st.date_input("End Date", value=pd.to_datetime(df['trade-date']).max().date())
            start_date = pd.to_datetime(start_date).tz_localize('America/New_York')
            end_date = pd.to_datetime(end_date).tz_localize('America/New_York')
            filtered_df = df.loc[(df['trade-date'] >= start_date) & (df['trade-date'] <= end_date)]
            st.dataframe(filtered_df)
            st.markdown('---')

        elif selected_page == "Stop Loss":
            st.write("---")
            st.header("Analysis of Trades Without Stop Loss")
            
            st.subheader("Overview")
            st.write("""
                This section focuses on analyzing trades that were executed without a Stop Loss (SL) 
                order. Stop Loss orders are critical for managing risk by automatically closing trades 
                when a certain loss threshold is reached. Understanding the characteristics of trades 
                without SL can provide insights into risk management practices and trading strategies.

                The analysis includes:
                - Total number of trades.
                - Number and percentage of trades executed without a Stop Loss.
                - Detailed breakdown of tickets associated with trades that lack a Stop Loss.

                Examining these trades helps to identify any patterns or risks associated with the absence 
                of Stop Loss orders and assess the overall risk exposure in the trading dataset.
            """)
            
            # Exibindo estatísticas gerais
            total_trades = df.shape[0]
            trades_without_sl = df.loc[df['sl'].isna()]
            num_trades_without_sl = trades_without_sl.shape[0]
            percentage_without_sl = round((num_trades_without_sl / total_trades) * 100, 2)

            st.write(f"**Total Number of Trades:** {total_trades}")
            st.write(f"**Trades Without Stop Loss:** {num_trades_without_sl}")
            st.write(f"**Percentage of Trades Without Stop Loss:** {percentage_without_sl}%")
            
            # Mostrar tabela de tickets sem Stop Loss
            st.write("### Ticket Details for Trades Without Stop Loss")
            st.dataframe(trades_without_sl[['ticket']].reset_index(drop=True))
            
            # Visualizações
            st.subheader("Trade Distribution by Symbol for Trades Without Stop Loss")
            
            # Gráfico de barras: Distribuição de Trades por Símbolo
            fig_symbol_dist = px.bar(trades_without_sl, x='symbol', title='Trade Distribution by Symbol (Without Stop Loss)',
                                    labels={'symbol': 'Symbol', 'count': 'Number of Trades'})
            st.plotly_chart(fig_symbol_dist)
            
            st.subheader("Trade Volume Analysis for Trades Without Stop Loss")
            
            # Gráfico de caixa: Volume dos Trades sem Stop Loss
            fig_volume = px.box(trades_without_sl, y='volume', title='Trade Volume Analysis (Without Stop Loss)',
                                labels={'volume': 'Volume'})
            st.plotly_chart(fig_volume)
            
            st.subheader("Trade Duration Analysis for Trades Without Stop Loss")
            
            # Gráfico de caixa: Duração dos Trades sem Stop Loss
            fig_duration = px.box(trades_without_sl, y='duration', title='Trade Duration Analysis (Without Stop Loss)',
                                labels={'duration': 'Duration (seconds)'})
            st.plotly_chart(fig_duration)
            st.write("**If you prefer to filter the data from a specific date, please select below.**")
            start_date = st.date_input("Start Date", value=pd.to_datetime(df['trade-date']).min().date())
            end_date = st.date_input("End Date", value=pd.to_datetime(df['trade-date']).max().date())
            start_date = pd.to_datetime(start_date).tz_localize('America/New_York')
            end_date = pd.to_datetime(end_date).tz_localize('America/New_York')
            filtered_df = df.loc[(df['trade-date'] >= start_date) & (df['trade-date'] <= end_date)]
            st.dataframe(filtered_df)
            st.markdown('---')

        elif selected_page == "Consistency":
            st.write("---")
            st.header("Consistency Analysis of Trading Performance")
            
            st.subheader("Daily Profit and Loss Summary")
            st.write("""
                This section provides an analysis of trading performance based on daily Profit and Loss (PnL). 
                The analysis includes a summary of daily profits and losses, total profits, cumulative PnL, 
                and identifies the most profitable day. Understanding these metrics helps in evaluating 
                trading consistency and identifying patterns in trading performance.

                The analysis includes:
                - A daily summary of total profits and losses.
                - Total profits and cumulative PnL over the trading period.
                - Identification of the most profitable trading day.
                - Percentage contribution of the most profitable day to total profits.
            """)
            
            # Cálculo e visualização das estatísticas
            col1, col2 = st.columns(2)
            
            with col1:
                consistency = df[['TradeDay', 'pnl']].groupby('TradeDay').sum()
                st.write("### Daily Profit and Loss Summary")
                st.dataframe(consistency)
            
            with col2:
                total_profits = round(consistency.loc[consistency['pnl'] > 0].sum(axis=0).tolist()[0], 2)
                cumulative_pnl = consistency.sum(axis=0).tolist()[0]
                most_profitable_day = consistency['pnl'].max()
                most_profitable_day_info = consistency[consistency['pnl'] == most_profitable_day]
                percentage_of_total_profits = round((most_profitable_day / total_profits) * 100, 2)
                
                st.write(f"**Total Profits:** ${total_profits}")
                st.write(f"**Cumulative PnL:** ${cumulative_pnl}")
                st.write(f"**Most Profitable Day:**")
                st.dataframe(most_profitable_day_info)
                st.write(f"**Percentage of Total Profits:** {percentage_of_total_profits}%")
            
            st.subheader("Visualizations of Trading Consistency")

            # Gráfico de linha para mostrar a evolução diária do PnL
            fig_daily_pnl = px.line(consistency, x=consistency.index, y='pnl', title='Daily Profit and Loss Over Time',
                                labels={'TradeDay': 'Date', 'pnl': 'PnL'})
            st.plotly_chart(fig_daily_pnl)
            
            # Gráfico de barras para mostrar a comparação dos lucros diários
            fig_daily_pnl_bar = px.bar(consistency, x=consistency.index, y='pnl', title='Daily PnL Comparison',
                                    labels={'TradeDay': 'Date', 'pnl': 'PnL'})
            st.plotly_chart(fig_daily_pnl_bar)

            # Distribuição do PnL por Dia da Semana
            df['day_of_week'] = df['TradeDay'].dt.day_name()
            weekly_pnl = df.groupby('day_of_week')['pnl'].sum().reset_index()
            fig_weekly_pnl = px.bar(weekly_pnl, x='day_of_week', y='pnl', title='Total PnL by Day of the Week',
                                    labels={'day_of_week': 'Day of the Week', 'pnl': 'Total PnL'})
            st.plotly_chart(fig_weekly_pnl)

            # Histograma do PnL Diário
            fig_histogram_pnl = px.histogram(consistency, x='pnl', nbins=30, title='Distribution of Daily PnL',
                                            labels={'pnl': 'Daily PnL'})
            st.plotly_chart(fig_histogram_pnl)

            # Box Plot do PnL Diário
            fig_box_pnl = px.box(consistency, y='pnl', title='Box Plot of Daily PnL',
                                labels={'pnl': 'Daily PnL'})
            st.plotly_chart(fig_box_pnl)
            st.write("**If you prefer to filter the data from a specific date, please select below.**")
            start_date = st.date_input("Start Date", value=pd.to_datetime(df['trade-date']).min().date())
            end_date = st.date_input("End Date", value=pd.to_datetime(df['trade-date']).max().date())
            start_date = pd.to_datetime(start_date).tz_localize('America/New_York')
            end_date = pd.to_datetime(end_date).tz_localize('America/New_York')
            filtered_df = df.loc[(df['trade-date'] >= start_date) & (df['trade-date'] <= end_date)]
            st.dataframe(filtered_df)
            st.markdown('---')

        elif selected_page == "Machine Learning":
            st.write('---')
            st.write("### Working...")

        elif selected_page == "Martingale":
            st.write('---')
            st.header("Analysis of Martingale Strategies")

            st.subheader("Overview")
            st.write("""
                This section focuses on analyzing potential Martingale strategies within the trading data. 
                Martingale strategies involve increasing the volume of trades after a loss in an attempt to recover previous losses.
                Understanding the presence of such strategies can provide insights into risk management and trading behavior.

                The analysis includes:
                - Identification of simultaneous trades within short time intervals.
                - Detection of patterns where trade volume increases after a loss.
                - Visualizations to illustrate potential Martingale behavior and trading volume patterns.

                By examining these patterns, we aim to uncover any systematic behaviors that suggest the use of Martingale strategies.
            """)
            
            
            possible_martingales = []

            # Por símbolo
            for symbol in df['symbol'].unique():
                symbol_data = df[df['symbol'] == symbol]
                
                # Por dia
                for trade_day in symbol_data['TradeDay'].unique():
                    day_data = symbol_data[symbol_data['TradeDay'] == trade_day]
                    
                    # Por direção
                    for side in day_data['side'].unique():
                        side_data = day_data[day_data['side'] == side].copy()  # Usando .copy() para evitar problemas de slicing
                        
                        # Verifica se há múltiplos trades simultâneos
                        grouped = side_data.groupby('trade-date').filter(lambda x: len(x) > 1)
                        
                        if not grouped.empty:
                            grouped['time_diff'] = grouped['trade-date'].diff().dt.total_seconds()
                            grouped['lots_diff'] = grouped['lots'].diff()
                            
                            possible_martingales.append(grouped[['ticket', 'trade-date', 'symbol', 'side', 'lots', 'time_diff', 'lots_diff']])

            # Concatenando os resultados encontrados
            if possible_martingales:
                martingale_df = pd.concat(possible_martingales).reset_index(drop=True)
                blue(" Possible Martingale Strategies Found:")
                st.dataframe(martingale_df)
            else:
                blue(" No Martingale Strategies Detected.")
            
            # Visualização
            if not martingale_df.empty:
                st.subheader("Visualizations")

                # Gráfico de tempo entre trades e diferença de lots
                st.write("#### Time Between Trades vs Difference in Lots")
                fig_time_lots = px.scatter(martingale_df, x='time_diff', y='lots_diff', 
                                        title='Time Between Trades vs Difference in Lots',
                                        labels={'time_diff': 'Time Between Trades (Seconds)', 'lots_diff': 'Difference in Lots'},
                                        template='plotly_dark')
                st.plotly_chart(fig_time_lots)

                # Gráfico de distribuição de trades por símbolo
                st.write("#### Number of Potential Trades by Symbol")
                symbol_counts = martingale_df['symbol'].value_counts().reset_index()
                symbol_counts.columns = ['Symbol', 'Number of Trades']
                fig_symbol_dist = px.bar(symbol_counts, x='Symbol', y='Number of Trades',
                                        title='Number of Potential Martingale Trades by Symbol',
                                        template='plotly_dark')
                st.plotly_chart(fig_symbol_dist)
            


            st.write('---')
            df['prev_trade_time'] = df.groupby('symbol')['trade-date'].shift(1)
            df['time_diff_seconds'] = (df['trade-date'] - df['prev_trade_time']).dt.total_seconds()
            simultaneous_trades = df[df['time_diff_seconds'] <= 60]  # Trades no intervalo de até 60 segundos

            # Identifica padrões de martingale: Trades com aumento de volume após perdas
            def identify_martingale(df):
                df['prev_pnl'] = df.groupby('symbol')['pnl'].shift(1)
                df['prev_lots'] = df.groupby('symbol')['lots'].shift(1)
                df['is_loss'] = df['prev_pnl'] < 0
                df['lots_increase'] = df['lots'] > df['prev_lots']
                
                martingale_candidates = df[df['is_loss'] & df['lots_increase']]
                
                return martingale_candidates

            martingale_candidates = identify_martingale(df)

            st.subheader("Additional Martingale Analysis")

            # Simultaneous Trades
            st.write("### Simultaneous Trades")
            st.write(f"Total Number of Trades: {df.shape[0]}")
            st.write(f"Number of Simultaneous Trades (within 60 seconds): {simultaneous_trades.shape[0]}")
            st.dataframe(simultaneous_trades[['trade-date', 'symbol', 'lots', 'time_diff_seconds']].reset_index(drop=True))

            # Martingale Patterns
            st.write("### Potential Martingale Patterns")
            st.write(f"Number of Trades Matching Martingale Pattern: {martingale_candidates.shape[0]}")
            st.dataframe(martingale_candidates[['trade-date', 'symbol', 'lots', 'prev_pnl', 'prev_lots']].reset_index(drop=True))

            # Gráficos de visualização

            # Gráfico de volume de trades simultâneos
            st.write("#### Distribution of Time Between Simultaneous Trades")
            fig_simultaneous_trades = px.histogram(simultaneous_trades, x='time_diff_seconds', nbins=60,
                                                title='Distribution of Time Between Simultaneous Trades',
                                                labels={'time_diff_seconds': 'Time Difference (Seconds)'},
                                                template='plotly_dark')
            st.plotly_chart(fig_simultaneous_trades)

            # Gráfico de volume em trades martingale
            st.write("#### Lots vs Previous PnL for Martingale Candidates")
            fig_martingale_patterns = px.scatter(martingale_candidates, x='prev_pnl', y='lots', 
                                                color='symbol', color_continuous_scale='viridis',
                                                title='Lots vs Previous PnL for Martingale Candidates',
                                                labels={'prev_pnl': 'Previous PnL', 'lots': 'Current Lots'},
                                                template='plotly_dark')
            st.plotly_chart(fig_martingale_patterns)

            st.write("**If you prefer to filter the data from a specific date, please select below.**")
            start_date = st.date_input("Start Date", value=pd.to_datetime(df['trade-date']).min().date())
            end_date = st.date_input("End Date", value=pd.to_datetime(df['trade-date']).max().date())
            start_date = pd.to_datetime(start_date).tz_localize('America/New_York')
            end_date = pd.to_datetime(end_date).tz_localize('America/New_York')
            filtered_df = df.loc[(df['trade-date'] >= start_date) & (df['trade-date'] <= end_date)]
            st.dataframe(filtered_df)
            st.markdown('---')
           


if __name__ == '__main__':
    main()