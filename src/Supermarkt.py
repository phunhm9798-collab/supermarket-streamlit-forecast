# Import necessary modules
import pandas as pd
import plotly.express as px
import streamlit as st
from forecasting import forecast_sales  # Import the forecasting function


def get_data_from_excel():
    df = pd.read_excel(
        io='data\Supermarket.xlsx',
        engine='openpyxl',
        sheet_name='Sales',
        skiprows=3,
        usecols='B:R',
        nrows=1000,
    )

   # Ensure datetime columns
    if 'Time' in df.columns:
        df["hour"] = pd.to_datetime(
            df["Time"], format="%H:%M:%S", errors='coerce').dt.hour
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    return df


df = get_data_from_excel()

st.set_page_config(page_title='Sales Dashboard',
                   page_icon='📈',
                   layout='wide')

st.dataframe(df)

# Sidebar
st.sidebar.header('Please Filter Here:')
if 'Date' in df.columns:
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    date_range = st.sidebar.date_input("Date range",
                                       value=(min_date, max_date),
                                       min_value=min_date,
                                       max_value=max_date)
else:
    date_range = None
city = st.sidebar.multiselect(
    'Select the City',
    options=df['City'].unique(),
    default=df['City'].unique()
)

customer_type = st.sidebar.multiselect(
    "Select the customer type: ",
    options=df['Customer_type'].unique(),
    default=df['Customer_type'].unique()
)

gender = st.sidebar.multiselect(
    "Select the Gender : ",
    options=df['Gender'].unique(),
    default=df['Gender'].unique()
)

df_selection = df.query(
    'City == @city & Customer_type == @customer_type & Gender == @gender'
)

# apply date filter if present
if date_range and 'Date' in df_selection.columns:
    start_date, end_date = date_range
    df_selection = df_selection[(df_selection['Date'].dt.date >= start_date) &
                                (df_selection['Date'].dt.date <= end_date)]
# Mainpage
st.title('📈Sales Dashboard')
st.markdown('##')

# Top KPI's
total_sales = int(df_selection['Total'].sum())
average_rating = round(df_selection['Rating'].mean(), 1)
star_rating = ':star:' * int(round(average_rating, 0))
average_sales_by_transaction = round(df_selection['Total'].mean(), 2)

left_column, middle_column, right_column = st.columns(3)
with left_column:
    st.subheader('Total Sales: ')
    st.subheader(f'US $ {total_sales:,}')
with middle_column:
    st.subheader('Average Rating:')
    st.subheader(f'{average_rating} {star_rating}')
with right_column:
    st.subheader("Average Sales Per Transaction:")
    st.subheader(f'US $ {average_sales_by_transaction}')

st.markdown('---')

# Sales by product line bar chart
sale_by_product_line = df_selection.groupby(by=["Product line"])[
    ["Total"]].sum().sort_values(by="Total")

fig_product_sales = px.bar(
    sale_by_product_line,
    x='Total',
    y=sale_by_product_line.index,
    orientation='h',
    title='<b> Sales by Product Line</b>',
    color_discrete_sequence=['#0083B8'] * len(sale_by_product_line),
    template='plotly_white'
)

st.plotly_chart(fig_product_sales)

# Sale by hour bar chart
sale_by_hour = df_selection.groupby(by=["hour"])[["Total"]].sum()
fig_hourly_sales = px.bar(
    sale_by_hour,
    x=sale_by_hour.index,
    y='Total',
    title='<b>Sales by Hour</b>',
    color_discrete_sequence=['#0083B8'] * len(sale_by_product_line),
    template='plotly_white'
)
st.plotly_chart(fig_hourly_sales)

# Add a download button for the filtered dataset
csv = df_selection.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name='supermarket_filtered.csv',
    mime='text/csv'
)

# Top products by revenue (new)
st.subheader("Top 10 Product Lines by Revenue")
top_products = (df_selection.groupby('Product line')['Total']
                .sum()
                .sort_values(ascending=False)
                .head(10)
                .reset_index())
fig_top = px.bar(top_products, x='Total', y='Product line', orientation='h',
                 title='Top 10 Product Lines', color='Total', template='plotly_white')
st.plotly_chart(fig_top, use_container_width=True)

# Hour x Weekday heatmap (new)
if 'hour' in df_selection.columns and 'Date' in df_selection.columns:
    df_selection['weekday'] = df_selection['Date'].dt.day_name()
    weekday_order = ['Monday', 'Tuesday', 'Wednesday',
                     'Thursday', 'Friday', 'Saturday', 'Sunday']
    pivot = (df_selection.pivot_table(values='Total', index='hour', columns='weekday',
                                      aggfunc='sum', fill_value=0)
             .reindex(columns=weekday_order, fill_value=0)
             .sort_index())
    st.subheader("Sales heatmap: Hour vs Weekday")
    fig_heat = px.imshow(pivot,
                         labels=dict(x="Weekday", y="Hour of day",
                                     color="Sales"),
                         x=pivot.columns,
                         y=pivot.index,
                         aspect='auto',
                         color_continuous_scale='Blues')
    st.plotly_chart(fig_heat, use_container_width=True)


# Forecasting section
st.markdown('---')
st.header('Sales Forecasting')

# Forecasting input
forecast_period = st.number_input(
    'Enter the number of periods to forecast:', min_value=1, max_value=12, value=3)

if st.button('Forecast Sales'):
    forecasted_sales = forecast_sales(df_selection, forecast_period)
    # Display the forecasted sales as a line chart
    st.line_chart(forecasted_sales)
