import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="OPS Center — Delivery Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #0A0E1A; }
    [data-testid="stSidebar"] { background: #0D1221; border-right: 1px solid #1E2D4A; }
    .main .block-container { padding: 2rem 2rem 2rem 2rem; }
    h1, h2, h3 { color: #E8EDF5 !important; font-weight: 700 !important; }
    p, label, div { color: #8A96B0; }
    [data-testid="metric-container"] {
        background: #0D1221;
        border: 1px solid #1E2D4A;
        border-radius: 12px;
        padding: 16px;
    }
    [data-testid="stMetricValue"] { color: #E8EDF5 !important; font-size: 28px !important; font-weight: 800 !important; }
    [data-testid="stMetricLabel"] { color: #6B7A99 !important; font-size: 12px !important; letter-spacing: 2px; text-transform: uppercase; }
    .stDataFrame { background: #0D1221; border: 1px solid #1E2D4A; border-radius: 8px; }
    div[data-testid="stRadio"] label { color: #8A96B0 !important; }
    .stAlert { background: #1A0A0A; border: 1px solid #EF4444; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    con = duckdb.connect("data/delivery.db")
    orders      = con.execute("SELECT * FROM fact_orders").df()
    captains    = con.execute("SELECT * FROM dim_captains").df()
    restaurants = con.execute("SELECT * FROM dim_restaurants").df()
    con.close()
    return orders, captains, restaurants

orders, captains, restaurants = load_data()

CHART_THEME = {
    "paper_bgcolor": "#0D1221",
    "plot_bgcolor":  "#0D1221",
    "font_color":    "#8A96B0",
    "gridcolor":     "#1E2D4A",
}

def style_fig(fig):
    fig.update_layout(
        paper_bgcolor = CHART_THEME["paper_bgcolor"],
        plot_bgcolor  = CHART_THEME["plot_bgcolor"],
        font_color    = CHART_THEME["font_color"],
        margin        = dict(l=20, r=20, t=40, b=20),
        legend        = dict(bgcolor="#0D1221", bordercolor="#1E2D4A"),
    )
    fig.update_xaxes(gridcolor=CHART_THEME["gridcolor"], showline=False)
    fig.update_yaxes(gridcolor=CHART_THEME["gridcolor"], showline=False)
    return fig

# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div style='padding: 16px 0;'>
        <div style='font-size:11px; color:#00D4FF; letter-spacing:4px; margin-bottom:4px;'>OPERATIONS CENTER</div>
        <div style='font-size:20px; font-weight:800; color:#E8EDF5;'>Delivery Intelligence</div>
        <div style='font-size:11px; color:#6B7A99; margin-top:4px;'>v1.0 — Live Dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio("", [
        "Executive Overview",
        "Operations Analysis",
        "Captain Performance",
        "AI Insights"
    ])

    st.markdown("---")
    st.markdown(f"<div style='font-size:11px; color:#6B7A99; letter-spacing:2px;'>SYSTEM STATS</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#E8EDF5; margin-top:8px;'>Orders &nbsp;&nbsp;&nbsp; <b style='color:#00D4FF;'>{len(orders):,}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#E8EDF5; margin-top:4px;'>Captains &nbsp;&nbsp; <b style='color:#00D4FF;'>{len(captains):,}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#E8EDF5; margin-top:4px;'>Restaurants <b style='color:#00D4FF;'>{len(restaurants):,}</b></div>", unsafe_allow_html=True)

# PAGE 1
if page == "Executive Overview":
    st.markdown("<div style='font-size:11px; color:#00D4FF; letter-spacing:4px; margin-bottom:8px;'>EXECUTIVE OVERVIEW</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='margin:0; font-size:32px;'>Operational Performance</h1>", unsafe_allow_html=True)
    st.markdown("<p style='margin-bottom:24px;'>Real-time delivery metrics and KPI tracking</p>", unsafe_allow_html=True)
    st.markdown("---")

    delivered = orders[orders['status'] == 'delivered'].shape[0]
    delayed   = orders[orders['status'] == 'delayed'].shape[0]
    cancelled = orders[orders['status'] == 'cancelled'].shape[0]
    revenue   = orders['order_value_sar'].sum()
    avg_time  = orders['delivery_time_min'].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("TOTAL ORDERS",   f"{len(orders):,}")
    c2.metric("REVENUE (SAR)",  f"{revenue/1_000_000:.2f}M")
    c3.metric("AVG DELIVERY",   f"{avg_time:.1f} min")
    c4.metric("DELIVERED",      f"{delivered:,}", f"{delivered/len(orders)*100:.1f}%")
    c5.metric("CANCELLED",      f"{cancelled:,}", f"-{cancelled/len(orders)*100:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3>Order Status Distribution</h3>", unsafe_allow_html=True)
        status_counts = orders['status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        fig = px.pie(
            status_counts, values='count', names='status',
            color='status',
            color_discrete_map={'delivered': '#10B981', 'delayed': '#F59E0B', 'cancelled': '#EF4444'},
            hole=0.6
        )
        fig = style_fig(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<h3>Weather Impact on Delay Rate</h3>", unsafe_allow_html=True)
        weather_stats = orders.groupby('weather').agg(
            total=('order_id', 'count'),
            delayed=('is_delayed', 'sum')
        ).reset_index()
        weather_stats['delay_rate'] = (weather_stats['delayed'] / weather_stats['total'] * 100).round(1)
        weather_stats = weather_stats.sort_values('delay_rate', ascending=True)
        fig = px.bar(
            weather_stats, x='delay_rate', y='weather',
            orientation='h',
            color='delay_rate',
            color_continuous_scale='RdYlGn_r',
        )
        fig = style_fig(fig)
        st.plotly_chart(fig, use_container_width=True)

# PAGE 2
elif page == "Operations Analysis":
    st.markdown("<div style='font-size:11px; color:#00D4FF; letter-spacing:4px; margin-bottom:8px;'>OPERATIONS</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='margin:0; font-size:32px;'>Operations Analysis</h1>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3>Orders by District</h3>", unsafe_allow_html=True)
        district_stats = orders.groupby('district').agg(
            total=('order_id', 'count'),
            delay_rate=('is_delayed', 'mean')
        ).reset_index()
        district_stats['delay_rate'] = (district_stats['delay_rate'] * 100).round(1)
        district_stats = district_stats.sort_values('total', ascending=False)
        fig = px.bar(
            district_stats, x='district', y='total',
            color='delay_rate', color_continuous_scale='RdYlGn_r',
        )
        fig = style_fig(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<h3>Hourly Order Volume</h3>", unsafe_allow_html=True)
        hour_stats = orders.groupby('hour_of_day').agg(
            total=('order_id', 'count'),
        ).reset_index()
        fig = px.line(hour_stats, x='hour_of_day', y='total', markers=True)
        fig.add_vrect(x0=11.5, x1=13.5, fillcolor="#F59E0B", opacity=0.1, annotation_text="Lunch Peak", annotation_font_color="#F59E0B")
        fig.add_vrect(x0=18.5, x1=21.5, fillcolor="#EF4444", opacity=0.1, annotation_text="Dinner Peak", annotation_font_color="#EF4444")
        fig.update_traces(line_color='#00D4FF')
        fig = style_fig(fig)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<h3>Traffic Level Impact</h3>", unsafe_allow_html=True)
    traffic_stats = orders.groupby('traffic_level').agg(
        total_orders=('order_id', 'count'),
        avg_delivery_min=('delivery_time_min', 'mean'),
        delay_rate_pct=('is_delayed', 'mean')
    ).reset_index()
    traffic_stats['avg_delivery_min'] = traffic_stats['avg_delivery_min'].round(1)
    traffic_stats['delay_rate_pct']   = (traffic_stats['delay_rate_pct'] * 100).round(1)
    st.dataframe(traffic_stats, use_container_width=True)

# PAGE 3
elif page == "Captain Performance":
    st.markdown("<div style='font-size:11px; color:#00D4FF; letter-spacing:4px; margin-bottom:8px;'>FLEET MANAGEMENT</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='margin:0; font-size:32px;'>Captain Performance</h1>", unsafe_allow_html=True)
    st.markdown("---")

    captain_stats = orders.merge(captains, on='captain_id')
    captain_perf = captain_stats.groupby(['captain_id', 'rating']).agg(
        total_orders=('order_id', 'count'),
        avg_time=('delivery_time_min', 'mean'),
        delay_rate=('is_delayed', 'mean')
    ).reset_index()
    captain_perf['avg_time']   = captain_perf['avg_time'].round(1)
    captain_perf['delay_rate'] = (captain_perf['delay_rate'] * 100).round(1)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3>Rating vs Delay Rate</h3>", unsafe_allow_html=True)
        fig = px.scatter(
            captain_perf, x='rating', y='delay_rate',
            size='total_orders', color='delay_rate',
            color_continuous_scale='RdYlGn_r',
        )
        fig = style_fig(fig)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<h3>Top 10 Best Captains</h3>", unsafe_allow_html=True)
        top = captain_perf.nsmallest(10, 'delay_rate')[['captain_id', 'rating', 'total_orders', 'delay_rate']]
        st.dataframe(top, use_container_width=True)

    st.markdown("<h3>⚠️ Captains Requiring Attention</h3>", unsafe_allow_html=True)
    worst = captain_perf[captain_perf['total_orders'] >= 50].nlargest(10, 'delay_rate')[['captain_id', 'rating', 'total_orders', 'avg_time', 'delay_rate']]
    st.dataframe(worst, use_container_width=True)

# PAGE 4
elif page == "AI Insights":
    st.markdown("<div style='font-size:11px; color:#00D4FF; letter-spacing:4px; margin-bottom:8px;'>AI INSIGHTS</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='margin:0; font-size:32px;'>Predictive Intelligence</h1>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("<h3>Delay Risk Heatmap — Zone × Weather</h3>", unsafe_allow_html=True)
    zone_weather = orders.groupby(['district', 'weather']).agg(
        delay_rate=('is_delayed', 'mean')
    ).reset_index()
    zone_weather['delay_rate'] = (zone_weather['delay_rate'] * 100).round(1)
    fig = px.density_heatmap(
        zone_weather, x='district', y='weather', z='delay_rate',
        color_continuous_scale='RdYlGn_r',
    )
    fig = style_fig(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<h3>Demand Forecast by Hour & District</h3>", unsafe_allow_html=True)
    demand = orders.groupby(['hour_of_day', 'district']).size().reset_index(name='orders')
    fig = px.line(demand, x='hour_of_day', y='orders', color='district', markers=True)
    fig = style_fig(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<h3>🚨 High Risk Zones — Action Required</h3>", unsafe_allow_html=True)
    high_risk = orders[orders['is_delayed'] == 1].groupby('district').size().reset_index(name='delayed_orders')
    high_risk = high_risk.sort_values('delayed_orders', ascending=False).head(5)
    for _, row in high_risk.iterrows():
        st.error(f"ALERT — {row['district']}  |  {row['delayed_orders']:,} delayed orders detected")