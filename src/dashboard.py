import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Delivery Operations Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: Inter, system-ui, sans-serif;
}

/* Main Background */
[data-testid="stAppViewContainer"] {
    background-color: #F4F6F9;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #FFFFFF;
    border-right: 1px solid #E5E7EB;
}

/* Main Layout */
.main .block-container {
    padding: 2rem;
}

/* Typography */
h1, h2, h3 {
    color: #111827 !important;
    font-weight: 700 !important;
}

p, label, div {
    color: #6B7280;
}

/* Metric Cards */
[data-testid="metric-container"] {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Metric Values */
[data-testid="stMetricValue"] {
    color: #111827 !important;
    font-size: 30px !important;
    font-weight: 700 !important;
}

/* Metric Labels */
[data-testid="stMetricLabel"] {
    color: #6B7280 !important;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Tables */
.stDataFrame {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 5px;
}

/* Alerts */
.stAlert {
    border-radius: 12px;
}

/* HR */
hr {
    border-color: #E5E7EB;
}

/* Radio Buttons */
div[data-testid="stRadio"] label {
    color: #374151 !important;
    font-weight: 500;
}

</style>
""", unsafe_allow_html=True)
@st.cache_data
def load_data():
    conn = snowflake.connector.connect(
        account   = 'kncgmxf-pz18830',
        user      = 'MESHAL',
        password  =  os.getenv('SNOWFLAKE_PASSWORD'),
        database  = 'DELIVERY_DB',
        schema    = 'PUBLIC',
        warehouse = 'COMPUTE_WH'
    )
    orders = pd.read_sql(
        "SELECT * FROM FACT_ORDERS",
        conn
    )
    captains = pd.read_sql(
        "SELECT * FROM DIM_CAPTAINS",
        conn
    )
    restaurants = pd.read_sql(
        "SELECT * FROM DIM_RESTAURANTS",
        conn
    )
    conn.close()

    orders.columns = orders.columns.str.lower()
    captains.columns = captains.columns.str.lower()
    restaurants.columns = restaurants.columns.str.lower()
    return orders, captains, restaurants
orders, captains, restaurants = load_data()
CHART_THEME = {
    "paper_bgcolor": "#FFFFFF",
    "plot_bgcolor": "#FFFFFF",
    "font_color": "#374151",
    "gridcolor": "#E5E7EB"
}

def style_fig(fig):
    fig.update_layout(
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font_color=CHART_THEME["font_color"],
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            bgcolor="rgba(0,0,0,0)"
        )
    )
    fig.update_xaxes(
        gridcolor=CHART_THEME["gridcolor"],
        showline=False,
        zeroline=False
    )

    fig.update_yaxes(
        gridcolor=CHART_THEME["gridcolor"],
        showline=False,
        zeroline=False
    )

    return fig
st.markdown("""
<div style="
background:white;
padding:22px 28px;
border:1px solid #E5E7EB;
border-radius:18px;
margin-bottom:24px;
display:flex;
justify-content:space-between;
align-items:center;
">
<div>
<div style="
font-size:28px;
font-weight:700;
color:#111827;
">
Delivery Operations Dashboard
</div>
<div style="
font-size:14px;
color:#6B7280;
margin-top:4px;
">
Real-time logistics performance monitoring
</div>
</div>
</div>
""", unsafe_allow_html=True)
with st.sidebar:
    st.markdown("## Navigation")
    page = st.radio(
        "",
        [
            "Executive Overview",
            "Operations Analysis",
            "Captain Performance",
            "Operational Insights"
        ]
    )
    st.markdown("---")
    st.markdown("### System Statistics")
    st.metric(
        "Orders",
        f"{len(orders):,}"
    )
    st.metric(
        "Captains",
        f"{len(captains):,}"
    )
    st.metric(
        "Restaurants",
        f"{len(restaurants):,}"
    )

if page == "Executive Overview":
    st.title("Executive Overview")
    st.caption("Key operational KPIs and business metrics")
    delivered = orders[
        orders['status'] == 'delivered'
    ].shape[0]
    cancelled = orders[
        orders['status'] == 'cancelled'
    ].shape[0]
    revenue = orders[
        'order_value_sar'
    ].sum()
    avg_time = orders[
        'delivery_time_min'
    ].mean()
    delay_rate = (
        orders['is_delayed'].mean() * 100
    )
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Total Orders",
        f"{len(orders):,}"
    )
    c2.metric(
        "Revenue",
        f"{revenue/1_000_000:.2f}M SAR"
    )
    c3.metric(
        "Avg Delivery",
        f"{avg_time:.1f} min"
    )
    c4.metric(
        "Delivered",
        f"{delivered:,}"
    )
    c5.metric(
        "Delay Rate",
        f"{delay_rate:.1f}%"
    )
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Order Status")
        status_counts = (
            orders['status']
            .value_counts()
            .reset_index()
        )
        status_counts.columns = [
            'status',
            'count'
        ]

        fig = px.pie(
            status_counts,
            values='count',
            names='status',
            hole=0.65,
            color_discrete_sequence=[
                "#2563EB",
                "#16A34A",
                "#DC2626"
            ]
        )
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label'
        )
        fig = style_fig(fig)
        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:
        st.subheader("Weather vs Delay Rate")
        weather_stats = orders.groupby(
            'weather'
        ).agg(
            total=('order_id', 'count'),
            delayed=('is_delayed', 'sum')
        ).reset_index()
        weather_stats['delay_rate'] = (
            weather_stats['delayed']
            / weather_stats['total']
            * 100
        ).round(1)
        fig = px.bar(
            weather_stats,
            x='weather',
            y='delay_rate',
            text='delay_rate',
            color='delay_rate',
            color_continuous_scale='Blues'
        )
        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )
        fig = style_fig(fig)
        st.plotly_chart(
            fig,
            use_container_width=True
        )
elif page == "Operations Analysis":
    st.title("Operations Analysis")
    st.caption("Delivery flow and operational bottlenecks")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Orders by District")
        district_stats = orders.groupby(
            'district'
        ).agg(
            total=('order_id', 'count')
        ).reset_index()
        district_stats = district_stats.sort_values(
            'total',
            ascending=False
        )
        fig = px.bar(
            district_stats,
            x='district',
            y='total',
            text='total',
            color='total',
            color_continuous_scale='Blues'
        )
        fig.update_traces(
            textposition='outside'
        )
        fig = style_fig(fig)
        st.plotly_chart(
            fig,
            use_container_width=True
        )
    with col2:
        st.subheader("Hourly Demand")
        hour_stats = orders.groupby(
            'hour_of_day'
        ).agg(
            total=('order_id', 'count')
        ).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hour_stats['hour_of_day'],
            y=hour_stats['total'],
            mode='lines+markers',
            line=dict(width=4),
            fill='tozeroy'
        ))
        fig = style_fig(fig)
        st.plotly_chart(
            fig,
            use_container_width=True
        )
    st.subheader("Traffic Impact Analysis")
    traffic_stats = orders.groupby(
        'traffic_level'
    ).agg(
        total_orders=('order_id', 'count'),
        avg_delivery_min=('delivery_time_min', 'mean'),
        delay_rate_pct=('is_delayed', 'mean')
    ).reset_index()
    traffic_stats['avg_delivery_min'] = (
        traffic_stats['avg_delivery_min']
    ).round(1)
    traffic_stats['delay_rate_pct'] = (
        traffic_stats['delay_rate_pct']
        * 100
    ).round(1)
    st.dataframe(
        traffic_stats,
        use_container_width=True
    )
elif page == "Captain Performance":
    st.title("Captain Performance")
    st.caption("Fleet monitoring and performance tracking")
    captain_stats = orders.merge(
        captains,
        on='captain_id'
    )
    captain_perf = captain_stats.groupby(
        ['captain_id', 'rating']
    ).agg(
        total_orders=('order_id', 'count'),
        avg_time=('delivery_time_min', 'mean'),
        delay_rate=('is_delayed', 'mean')
    ).reset_index()
    captain_perf['avg_time'] = (
        captain_perf['avg_time']
    ).round(1)
    captain_perf['delay_rate'] = (
        captain_perf['delay_rate']
        * 100
    ).round(1)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Performance Distribution")
        fig = px.scatter(
            captain_perf,
            x='rating',
            y='avg_time',
            size='total_orders',
            color='delay_rate',
            hover_data=['captain_id'],
            color_continuous_scale='Blues'
        )

        fig = style_fig(fig)
        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:
        st.subheader("Top Performing Captains")
        top = captain_perf.nsmallest(
            10,
            'delay_rate'
        )[[
            'captain_id',
            'rating',
            'total_orders',
            'delay_rate'
        ]]
        st.dataframe(
            top,
            use_container_width=True
        )
    st.subheader("Captains Requiring Attention")
    worst = captain_perf[
        captain_perf['total_orders'] >= 50
    ].nlargest(
        10,
        'delay_rate'
    )[[
        'captain_id',
        'rating',
        'total_orders',
        'avg_time',
        'delay_rate'
    ]]
    st.dataframe(
        worst,
        use_container_width=True
    )

elif page == "Operational Insights":
    st.title("Operational Insights")
    st.caption("Advanced operational intelligence")
    st.subheader("District Delay Heatmap")
    zone_weather = orders.groupby(
        ['district', 'weather']
    ).agg(
        delay_rate=('is_delayed', 'mean')
    ).reset_index()
    zone_weather['delay_rate'] = (
        zone_weather['delay_rate']
        * 100
    ).round(1)
    fig = px.density_heatmap(
        zone_weather,
        x='district',
        y='weather',
        z='delay_rate',
        color_continuous_scale='Blues'
    )
    fig = style_fig(fig)
    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.subheader("Demand Forecast by District")
    demand = orders.groupby(
        ['hour_of_day', 'district']
    ).size().reset_index(name='orders')
    fig = px.line(
        demand,
        x='hour_of_day',
        y='orders',
        color='district'
    )
    fig = style_fig(fig)
    st.plotly_chart(
        fig,
        use_container_width=True
    )
    st.subheader("Operational Alerts")
    high_risk = orders[
        orders['is_delayed'] == 1
    ].groupby('district').size().reset_index(
        name='delayed_orders'
    )
    high_risk = high_risk.sort_values(
        'delayed_orders',
        ascending=False
    ).head(5)
    for _, row in high_risk.iterrows():
        st.warning(
            f"{row['district']} — "
            f"{row['delayed_orders']:,} delayed orders detected"
        )