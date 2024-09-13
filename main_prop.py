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
    df['commissions'] = df['commissions'].fillna(0)
    df['pnl_liq'] = df['pnl'] - df['commissions']
    
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
        try:
            df = load_data(data_file_1)
            df = manipulation_data_frame(df)
        except Exception as e:
            st.sidebar.error(f"Error loading the file: {e}")

        st.sidebar.markdown("### Select the date range for the analysis")
        st.sidebar.markdown(
            "The analyses will be conducted based on the selected date range. "
            "Only trades within this range will be included."
        )
        start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime(df['trade-date']).min().date())
        end_date = st.sidebar.date_input("End Date", value=pd.to_datetime(df['trade-date']).max().date())
        
        start_date = pd.to_datetime(start_date).tz_localize('America/New_York')
        end_date = pd.to_datetime(end_date).tz_localize('America/New_York')
        
        if start_date > end_date:
            st.sidebar.error("The start date must be earlier than the end date.")
        else:
            df = df.loc[(df['trade-date'] >= start_date) & (df['trade-date'] <= end_date)]
        
        with st.sidebar:
            selected_page = option_menu(
                menu_title="Navigation",
                options=["Overview", "General Statistics", "Trade Frequency and Execution", 
                        "Trade Duration", "Simultaneos Open Positions","Regular Intervals", "Gambling Behavior", 
                        "Stop Loss", "Martingale","Consistency","Risk Score","Machine Learning"],
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
                df['cumulative_pnl'] = df['pnl_liq'].cumsum()
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

            average_profit = df.loc[df['pnl_liq']>0,'pnl_liq'].mean()
            average_loss = df.loc[df['pnl_liq']<0,'pnl_liq'].mean()
            risk_return_ratio = (df.loc[df['pnl_liq']>0,'pnl_liq'].mean()) / abs(df.loc[df['pnl_liq']<0,'pnl_liq'].mean()) if (df.loc[df['pnl_liq']<0,'pnl_liq'].mean()) != 0 else float('inf')
            win_percentage = ((df[df['pnl_liq'] > 0].shape[0])/df.shape[0]) * 100
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
                frequency_df = df[['TradeDay','pnl_liq']].groupby('TradeDay').count().rename(columns={"pnl_liq":"Frequency"})
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
            less_1m = df.loc[df['duration']<1,['symbol','pnl_liq','volume','lots','duration','open-price','close-price','TradeDay','ticket']].set_index('TradeDay')
            st.write(less_1m)
            pd.options.display.float_format = '{:.2f}'.format
            st.write("#### Describe")
            st.write(less_1m.drop(columns=['ticket']).describe().T)
            st.markdown('---')
            st.markdown('---')

        elif selected_page == "Simultaneos Open Positions":
            st.markdown("---")
            format_blue("Simultaneos open positions")
            
            df1 = df.sort_values(by='open-time').reset_index(drop=True)

            # Criar um dataframe para armazenar os eventos de abertura e fechamento dos trades
            events = pd.DataFrame({
                'time': pd.concat([df1['open-time'], df1['close-time']]),
                'event': ['open'] * len(df1) + ['close'] * len(df1),
                'ticket': pd.concat([df1['ticket'], df1['ticket']]),
                'symbol': pd.concat([df1['symbol'], df1['symbol']]),
                'pnl_liq': pd.concat([df1['pnl_liq'], df1['pnl_liq']]),
                'TradeDay': pd.concat([df1['TradeDay'], df1['TradeDay']])
            })

            # Ordenar os eventos por tempo
            events = events.sort_values('time').reset_index(drop=True)

            # Variável para rastrear trades abertos simultaneamente
            open_trades = []
            simultaneous_details = []

            # Iterar sobre os eventos para calcular os trades simultâneos
            for _, row in events.iterrows():
                if row['event'] == 'open':
                    if row['ticket'] not in open_trades:  # Evita duplicidade
                        open_trades.append(row['ticket'])  # Adiciona o ticket à lista de abertos
                        if len(open_trades) > 1:  # Verifica se há mais de um trade simultâneo
                            simultaneous_details.append({
                                'time': row['time'],
                                'open_trades': open_trades.copy(),
                                'symbol': row['symbol'],
                                'TradeDay': row['TradeDay']
                            })
                elif row['event'] == 'close':
                    if row['ticket'] in open_trades:
                        open_trades.remove(row['ticket'])  # Remove o ticket da lista de abertos

            # Criar DataFrame com os trades simultâneos
            simultaneous_trades_df = pd.DataFrame(simultaneous_details)

            # Função para gerar o relatório consolidado de trades simultâneos
            def generate_consolidated_report(df, simultaneous_trades):
                report = []
                
                # Agrupar por símbolo e dia
                grouped = simultaneous_trades.groupby(['symbol', 'TradeDay'])
                
                for (symbol, day), group in grouped:
                    tickets_flagged = set()  # Para armazenar tickets únicos
                    total_pnl = 0  # Acumulador de PnL
                    
                    # Iterar sobre os trades simultâneos no grupo
                    for _, row in group.iterrows():
                        for ticket in row['open_trades']:
                            if ticket not in tickets_flagged:  # Evita duplicidade de tickets
                                tickets_flagged.add(ticket)
                                trade_info = df[df['ticket'] == ticket].iloc[0]
                                total_pnl += trade_info['pnl_liq']  # Somar PnL do ticket
                    
                    # Adicionar dados ao relatório
                    report.append({
                        'Symbol': symbol,
                        'TradeDay': day,
                        'Tickets Flagged': list(tickets_flagged),
                        'Total PnL': total_pnl
                    })
                
                # Retornar DataFrame do relatório consolidado
                return pd.DataFrame(report)

            # Gerar relatório consolidado dos trades simultâneos
            consolidated_report = generate_consolidated_report(df1, simultaneous_trades_df)

            # Exibir relatório
            st.write(consolidated_report)
           #------------------------------------------------------------------------- 
            # Certifique-se de que as colunas 'open-time' e 'close-time' estão no formato datetime
            df['open-time'] = pd.to_datetime(df['open-time'])
            df['close-time'] = pd.to_datetime(df['close-time'])

            # Criar colunas naive para horas de abertura e fechamento (remover timezone)
            df['open-time-naive'] = df['open-time'].dt.tz_localize(None)
            df['close-time-naive'] = df['close-time'].dt.tz_localize(None)

            # Calcular a duração do trade em horas
            df['duration_hours'] = (df['close-time-naive'] - df['open-time-naive']).dt.total_seconds() / 3600

            # Criar o gráfico com Plotly
            fig = go.Figure()

            # Adicionar cada trade como uma barra horizontal
            for i, row in df.iterrows():
                fig.add_trace(go.Bar(
                    y=[f'Ticket {row["ticket"]}'],  # Cada barra corresponde ao ticket de um trade
                    x=[row['duration_hours']],  # A duração do trade em horas
                    base=row['open-time-naive'].timestamp() / 3600,  # Converte o timestamp para horas
                    orientation='h',  # Barras horizontais
                    name=f'Trade {i+1}',
                    marker=dict(color=px.colors.sequential.Viridis[i % len(px.colors.sequential.Viridis)]),  # Usar uma cor da paleta Viridis
                    hovertemplate=(
                        f'Ticket: {row["ticket"]}<br>'
                        f'Side: {row["side"]}<br>'
                        f'Symbol: {row["symbol"]}<br>'
                        f'Lots: {row["lots"]}<br>'
                        f'PnL: {row["pnl_liq"]}<br>'
                        f'Duration (Hours): {row["duration_hours"]:.2f}<br>'
                        f'Open Time: {row["open-time-naive"]}<br>'
                        f'Close Time: {row["close-time-naive"]}<br>'
                        '<extra></extra>'
                    )  # Informações adicionais ao passar o mouse sobre cada barra
                ))

            # Atualizar layout do gráfico
            fig.update_layout(
                title='Trade Durations and Overlaps',
                xaxis_title='Trade Duration (Hours)',  # Eixo X mostrando a duração em horas
                yaxis_title='Trades',  # Eixo Y com os tickets dos trades
                yaxis=dict(
                    showticklabels=False  # Ocultar rótulos do eixo Y
                ),
                showlegend=False,  # Não mostrar a legenda
                height=800
            )

            # Exibir o gráfico no Streamlit
            st.plotly_chart(fig)
            #----------------------------------------------
            
            #---------
            # Explicação para o gráfico
            st.write("""
            **How to use this chart:**
            This chart shows the duration of each trade, represented by horizontal bars. The length of each bar indicates how long a trade was open, in hours. Use this to easily identify overlapping trades and analyze the performance of each trade based on its profit/loss (PnL) and other details available in the hover information.
            """)
            
            st.write('---')
            fig1 = px.bar(
                consolidated_report, 
                x='TradeDay', 
                y='Total PnL', 
                color='Symbol',color_continuous_scale='Blues', 
                title='Total PnL by Symbol and Trade Day for Simultaneous Positions',
                labels={
                    'TradeDay': 'Trade Day',
                    'Total PnL': 'Total Profit and Loss (PnL)',
                    'Symbol': 'Symbol'
                },
                hover_data=['Tickets Flagged']
            )

            fig1.update_layout(
                xaxis_title='Trade Day',
                yaxis_title='Total PnL',
                title_x=0.5,  # Center the title
                hovermode="x unified"  # Show all hover info for each x value
            )

            st.plotly_chart(fig1)

            # Explanation for the chart
            st.write("""
            **How to use this chart:**
            This bar chart displays the total Profit and Loss (PnL) for each trade day, segmented by the trading symbol. Hover over any bar to see additional details, including the tickets flagged for simultaneous open trades on that particular day and symbol. 
            This chart helps you quickly assess which trade days and symbols had the highest or lowest PnL from simultaneous positions.
            """)

            heatmap_data = consolidated_report.pivot_table(
                index='Symbol', 
                columns='TradeDay', 
                values='Tickets Flagged', 
                aggfunc='count', 
                fill_value=0
            )

            # Criar o heatmap usando plotly
            fig2 = go.Figure(
                data=go.Heatmap(
                    z=heatmap_data.values, 
                    x=heatmap_data.columns, 
                    y=heatmap_data.index, 
                    colorscale='Blues',
                    hoverongaps=False
                )
            )

            fig2.update_layout(
                title='Frequency of Simultaneous Trades by Symbol and Trade Day',
                xaxis_title='Trade Day',
                yaxis_title='Symbol',
                title_x=0.5,  # Centralizar o título
            )

            st.plotly_chart(fig2)

            # Explicação para o heatmap
            st.write("""
            **How to use this chart:**
            This heatmap represents the number of simultaneous open trades grouped by trading symbol and trade day. Each cell's color indicates the number of flagged simultaneous trades, with darker colors representing more simultaneous positions. Use this chart to identify trading patterns where multiple trades occurred simultaneously for specific symbols on particular days.
            """)
            # Adding the 'time_diff' column to the dataframe
            df['time_diff'] = df['open-time'].diff().dt.total_seconds()

            # Visualization 6: Scatter Plot of Time Difference Between Trades vs. PNL
            st.write("### Scatter Plot of Time Difference Between Trades vs. PNL")
            fig6 = px.scatter(df, x='time_diff', y='pnl_liq', color='symbol', 
                            title='Time Difference Between Trades vs. PNL',
                            labels={'time_diff': 'Time Difference (seconds)', 'pnl_liq': 'PNL'})
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
            fig = px.scatter(df, x='lots', y='pnl_liq', template='simple_white')
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

            intervals_seconds = [0,1, 5, 15, 30, 45, 60, 120, 240, 480, 960, 3600,df['time_diff'].max()]

            results = []

            for interval in intervals_seconds:
                regular_trades = df[df['time_diff'].between(0, interval)]
                
                count_trades = regular_trades.shape[0]
                total_trades = df.shape[0]
                regular_percentage = (count_trades / total_trades) * 100
                average_lots = regular_trades['lots'].mean() if count_trades > 0 else None

                results.append({
                    'Interval (seconds)': f'0 to {interval}',
                    'Total Trades': total_trades,
                    'Regular Trades': count_trades,
                    'Percentage of Regular Trades': regular_percentage,
                    'Average Lots': average_lots
                })
                
            results_df = pd.DataFrame(results)

            st.write("\n### Trades Executed at Regular Intervals")
            st.write(results_df)

            fig1 = px.bar(results_df, x='Interval (seconds)', y='Percentage of Regular Trades', template='simple_white',color_continuous_scale='Blues',
                        title='Percentage of Trades Executed at Regular Intervals',
                        labels={'Interval (seconds)': 'Interval (Seconds)', 'Percentage of Regular Trades': 'Percentage (%)'})
            st.plotly_chart(fig1)

            fig2 = px.bar(results_df, x='Interval (seconds)', y='Average Lots', template='simple_white',color_continuous_scale='Blues',
                        title='Average Lots for Trades Executed at Regular Intervals',
                        labels={'Interval (seconds)': 'Interval (Seconds)', 'Average Lots': 'Average Lots'})
            st.plotly_chart(fig2)
            # Loop para calcular as métricas para cada intervalo
            
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
            df_no_sl = df[df['sl'].isna() | (df['sl'] == '')]

            # Agrupa por dia e calcula o PNL acumulado
            grouped_no_sl = df_no_sl.groupby('TradeDay').agg({
                'ticket': lambda x: ', '.join(map(str, x)),
                'pnl': 'sum'
            }).reset_index()

            # Renomeia as colunas para melhor compreensão
            grouped_no_sl.columns = ['TradeDay', 'Tickets IDs', 'PNL Acumulado']

            # Ordena o DataFrame por dia
            grouped_no_sl = grouped_no_sl.sort_values(by='TradeDay').reset_index(drop=True)

            # Exibe o DataFrame resultante
            st.write(grouped_no_sl)

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
                consistency = df[['TradeDay', 'pnl_liq']].groupby('TradeDay').sum()
                st.write("### Daily Profit and Loss Summary")
                st.dataframe(consistency)
            
            with col2:
                total_profits = round(consistency.loc[consistency['pnl_liq'] > 0].sum(axis=0).tolist()[0], 2)
                cumulative_pnl = consistency.sum(axis=0).tolist()[0]
                most_profitable_day = consistency['pnl_liq'].max()
                most_profitable_day_info = consistency[consistency['pnl_liq'] == most_profitable_day]
                percentage_of_total_profits = round((most_profitable_day / total_profits) * 100, 2)
                
                st.write(f"**Total Profits:** ${total_profits}")
                st.write(f"**Cumulative PnL:** ${cumulative_pnl}")
                st.write(f"**Most Profitable Day:**")
                st.dataframe(most_profitable_day_info)
                st.write(f"**Percentage of Total Profits:** {percentage_of_total_profits}%")
            
            st.subheader("Visualizations of Trading Consistency")

            # Gráfico de linha para mostrar a evolução diária do PnL
            fig_daily_pnl = px.line(consistency, x=consistency.index, y='pnl_liq', title='Daily Profit and Loss Over Time',
                                labels={'TradeDay': 'Date', 'pnl_liq': 'PnL'})
            st.plotly_chart(fig_daily_pnl)
            
            # Gráfico de barras para mostrar a comparação dos lucros diários
            fig_daily_pnl_bar = px.bar(consistency, x=consistency.index, y='pnl_liq', title='Daily PnL Comparison',
                                    labels={'TradeDay': 'Date', 'pnl_liq': 'PnL'})
            st.plotly_chart(fig_daily_pnl_bar)

            # Distribuição do PnL por Dia da Semana
            df['day_of_week'] = df['TradeDay'].dt.day_name()
            weekly_pnl = df.groupby('day_of_week')['pnl_liq'].sum().reset_index()
            fig_weekly_pnl = px.bar(weekly_pnl, x='day_of_week', y='pnl_liq', title='Total PnL by Day of the Week',
                                    labels={'day_of_week': 'Day of the Week', 'pnl_liq': 'Total PnL'})
            st.plotly_chart(fig_weekly_pnl)

            # Histograma do PnL Diário
            fig_histogram_pnl = px.histogram(consistency, x='pnl_liq', nbins=30, title='Distribution of Daily PnL',
                                            labels={'pnl_liq': 'Daily PnL'})
            st.plotly_chart(fig_histogram_pnl)

            # Box Plot do PnL Diário
            fig_box_pnl = px.box(consistency, y='pnl_liq', title='Box Plot of Daily PnL',
                                labels={'pnl_liq': 'Daily PnL'})
            st.plotly_chart(fig_box_pnl)
            st.markdown('---')

        elif selected_page == "Machine Learning":
            st.write('---')
            st.write("### Working...")

        elif selected_page == "Risk Score":
            st.write('---')
            def get_risk_manager_input():
                format_blue("Risk Assessment Input")

                # Categoria: Trading Style Compliance
                st.subheader("Trading Style Compliance (0-10):")
                st.markdown("""- 0-2: Highly consistent and disciplined""")
                st.markdown("- 3-5: Generally consistent, minor irregularities")
                st.markdown('- 6-8: Significant inconsistencies')        
                st.markdown(' - 9-10: Erratic or highly risky')       
                
                trading_style = st.slider("Enter score for Trading Style Compliance:", 0, 10)

                # Categoria: Account Management Adherence
                st.subheader("Account Management Adherence (0-10)")
                st.write("- 0-2: Excellent management\n")
                st.write("- 3-5: Good management, occasional issues\n")
                st.write("- 6-8: Poor management, frequent issues\n")
                st.write("- 9-10: Severe mismanagement")
                account_management = st.slider("Enter score for Account Management Adherence:", 0, 10)

                # Categoria: Prohibited Practices Risk
                st.subheader("Prohibited Practices Risk (0-10)")
                st.write("- 0-2: No evidence of prohibited practices\n")
                st.write("- 3-5: Suspicious activity, no clear violations\n")
                st.write("- 6-8: Clear, infrequent violations\n")
                st.write("- 9-10: Frequent/severe violations")
                prohibited_practices = st.slider("Enter score for Prohibited Practices Risk:", 0, 10)

                # Categoria: Gambling Behavior Indicators
                st.subheader("Gambling Behavior Indicators (0-10)")
                st.write("0-2: No signs of gambling behavior\n")
                st.write("3-5: Occasional high-risk behavior\n")
                st.write("6-8: Frequent high-risk behavior\n")
                st.write("9-10: Consistent gambling-like behavior")
                gambling_behavior = st.slider("Enter score for Gambling Behavior Indicators:", 0, 10)

                return trading_style, account_management, prohibited_practices, gambling_behavior

            # Função para calcular o score de risco
            def calculate_risk_score(trading_style, account_management, prohibited_practices, gambling_behavior):
                # Pesos para cada categoria
                trading_style_weight = 0.3
                account_management_weight = 0.2
                prohibited_practices_weight = 0.3
                gambling_behavior_weight = 0.2

                # Cálculo do score final com base nos pesos
                overall_risk_score = (
                    (trading_style * trading_style_weight) +
                    (account_management * account_management_weight) +
                    (prohibited_practices * prohibited_practices_weight) +
                    (gambling_behavior * gambling_behavior_weight)
                )

                return overall_risk_score

            # Função para determinar a ação com base no score
            def determine_payout_action(risk_score):
                if 0 <= risk_score <= 3:
                    return {
                        "Risk Level": "Low",
                        "Primary Action": "Pay the trader",
                        "Secondary Action": "None",
                        "Notes": "Regular monitoring continues"
                    }
                elif 3.1 <= risk_score <= 4:
                    return {
                        "Risk Level": "Low-Moderate",
                        "Primary Action": "Pay the trader",
                        "Secondary Action": "Issue a warning",
                        "Notes": "Specify areas of concern in the warning"
                    }
                elif 4.1 <= risk_score <= 6:
                    return {
                        "Risk Level": "Moderate",
                        "Primary Action": "Pay with a deduction",
                        "Secondary Action": "Increased monitoring",
                        "Notes": "Deduction percentage based on severity of issues"
                    }
                elif 6.1 <= risk_score <= 7:
                    return {
                        "Risk Level": "High-Moderate",
                        "Primary Action": "Reject payout, allow trading",
                        "Secondary Action": "Implement restrictions",
                        "Notes": "Specify conditions for future payouts"
                    }
                elif 7.1 <= risk_score <= 10:
                    return {
                        "Risk Level": "High",
                        "Primary Action": "Reject and ban",
                        "Secondary Action": "Close account",
                        "Notes": "Document reasons thoroughly"
                    }
                else:
                    return {
                        "Risk Level": "Invalid score",
                        "Primary Action": "None",
                        "Secondary Action": "None",
                        "Notes": "Risk score is out of range"
                    }

            # Função principal para rodar o processo de avaliação de risco
            def run_risk_assessment():
                format_blue("Risk Assessment Dashboard")
                st.write("---")

                # Coletar entradas do gestor de risco
                trading_style_score, account_management_score, prohibited_practices_score, gambling_behavior_score = get_risk_manager_input()

                # Calcular o score geral
                overall_risk_score = calculate_risk_score(trading_style_score, account_management_score, prohibited_practices_score, gambling_behavior_score)

                # Determinar a ação baseada no score
                action_matrix = determine_payout_action(overall_risk_score)

                # Exibir os resultados
                blue("Risk Assessment Results")
                st.write(f"**Overall Risk Score**: {overall_risk_score:.2f}")
                st.write("**Action Matrix**:")

                for key, value in action_matrix.items():
                    st.write(f"**{key}:** {value}")

            # Executar o processo de avaliação de risco

            run_risk_assessment()




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
                df['prev_pnl'] = df.groupby('symbol')['pnl_liq'].shift(1)
                df['prev_lots'] = df.groupby('symbol')['lots'].shift(1)
                df['is_loss'] = df['prev_pnl'] < 0
                df['lots_increase'] = df['lots'] > df['prev_lots']
                
                martingale_candidates = df[df['is_loss'] & df['lots_increase']]
                
                return martingale_candidates

            martingale_candidates = identify_martingale(df)

            st.subheader("Additional Martingale Analysis")
            st.write("""
The Martingale analysis evaluates trading patterns where a trader increases the size of the position after a loss in an attempt to recover losses by making a profitable trade in the opposite direction. This strategy is often used in gambling and, in trading, can indicate riskier behavior. Specifically, it looks for the following conditions:

1. **Loss Followed by Opposite Trade:** The analysis checks if a trade resulting in a loss is immediately followed by another trade in the opposite direction.
2. **Short Time Interval:** The second trade must happen within a short time window (e.g., within 60 seconds) after the losing trade.
3. **Side Reversal:** The direction of the trade (buy/sell) changes, indicating a potential attempt to reverse the initial losing position.            
""")    
            st.write('---')
            # Função para identificar padrões de Martingale
            # Função para identificar padrões de Martingale
            def identificar_martingale(grupo):
                if grupo.empty:
                    return pd.DataFrame()  # Retorna um DataFrame vazio se o grupo estiver vazio

                grupo = grupo.sort_values(by='trade-date')
                resultado = []

                for i in range(1, len(grupo)):
                    trade_anterior = grupo.iloc[i - 1]
                    trade_atual = grupo.iloc[i]

                    # Calcula a diferença de tempo entre as trades
                    tempo_diferenca = (trade_atual['trade-date'] - trade_anterior['trade-date']).total_seconds()

                    # Verifica se há um padrão de Martingale (perda seguida por trade na direção oposta em curto intervalo de tempo)
                    if trade_anterior['pnl_category'] == 'loss' and trade_atual['side'] != trade_anterior['side'] and tempo_diferenca <= 60:
                        resultado.append({
                            'ticket_1': trade_anterior['ticket'],
                            'ticket_2': trade_atual['ticket'],
                            'pnl_1': trade_anterior['pnl'],
                            'pnl_2': trade_atual['pnl'],
                            'lots_1': trade_anterior['lots'],
                            'lots_2': trade_atual['lots'],
                            'pnl_acumulado_dia': grupo['pnl'].sum(),
                            'symbol': trade_anterior['symbol'],
                            'data': trade_anterior['trade-date'],
                            'tempo_diferenca': tempo_diferenca,
                            'side_1': trade_anterior['side'],
                            'side_2': trade_atual['side']
                        })

                # Retorna o DataFrame com os resultados ou um DataFrame vazio, se não houver resultados
                return pd.DataFrame(resultado)

            # Agrupamento por 'TradeDay' e 'symbol' para identificar padrões de Martingale
            martingale_trades = df.groupby(['TradeDay', 'symbol'], group_keys=False).apply(identificar_martingale).reset_index(drop=True)

            # Verificar se o DataFrame 'martingale_trades' contém dados antes de processar
            if not martingale_trades.empty:
                st.dataframe(martingale_trades)
                st.write("### How to Interpret the Results")
                st.write("""
                    1. **Tickets and PnL (Profit and Loss):** O ticket_1 e ticket_2 mostram os IDs das trades, enquanto pnl_1 e pnl_2 mostram o lucro ou perda de cada trade. Uma perda em pnl_1 seguida de uma trade com pnl_2 pode indicar o uso da estratégia de Martingale.
                    2. **Lots:** As colunas lots_1 e lots_2 exibem o tamanho de cada trade. Em muitos padrões de Martingale, a segunda trade (que visa recuperar as perdas) pode envolver posições maiores (lots_2 > lots_1).
                    3. **Time Difference:** A coluna tempo_diferenca mostra a diferença de tempo entre as duas trades. Um curto intervalo de tempo (por exemplo, menos de 60 segundos) pode sugerir que o trader reagiu rapidamente após a perda, o que é característico do comportamento de Martingale.
                    4. **Symbol and Date:** Essas colunas ajudam a rastrear o ativo específico (symbol) e o dia (data) em que as trades ocorreram.
                    5. **Cumulative PnL:** A coluna pnl_acumulado_dia mostra o lucro ou perda total acumulado no dia para aquele símbolo.
                """)
            else:
                # Mensagem caso não haja padrões de Martingale detectados
                st.write("No Martingale Strategies Detected.")



               

if __name__ == '__main__':
    main()
