
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Análisis de Ventas Supermercado", layout="wide")

st.title("📊 Análisis de Ventas y Pérdidas en Supermercado")

# Cargar datasets
df_sales = pd.read_csv("data/sales.csv")
df_product_loss = pd.read_csv("data/product_loss.csv")
df_products = pd.read_csv("data/products.csv")

# -----------------------------
# 🔝 Top 15 Productos más vendidos
# -----------------------------
st.header("🔝 Top 15 Productos más vendidos")

df_total_sales = (
    df_sales[df_sales["Sale or Return"] == "sale"]
    .groupby("Item Code", as_index=False)["Quantity Sold (kilo)"]
    .sum()
    .merge(df_products, on="Item Code", how="left")
)

df_ordered = df_total_sales.sort_values(
    by=["Quantity Sold (kilo)", "Item Name"],
    ascending=[False, True]
).reset_index(drop=True)

fig1 = px.bar(
    df_ordered.head(15),
    x='Item Name',
    y='Quantity Sold (kilo)',
    title='Top 15 Productos más vendidos',
    labels={'Item Name': 'Producto', 'Quantity Sold (kilo)': 'Cantidad (kg)'},
    color_discrete_sequence=['skyblue']
)
fig1.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig1, use_container_width=True)

# -----------------------------
# 📉 Productos con más pérdida
# -----------------------------
st.header("📉 Pérdidas por Producto")

df_loss = df_product_loss.merge(df_sales, on="Item Code", how="left")
df_loss = df_loss.groupby(['Item Name', 'Loss Rate (%)'], as_index=False).agg(
    {'Quantity Sold (kilo)': 'sum'}
).sort_values(by='Quantity Sold (kilo)', ascending=False)

fig2 = go.Figure()

fig2.add_trace(go.Bar(
    x=df_loss['Item Name'],
    y=df_loss['Quantity Sold (kilo)'] / 1000,
    name='Cantidad Vendida (mil kg)',
    marker_color='skyblue',
    yaxis='y1'
))

fig2.add_trace(go.Scatter(
    x=df_loss['Item Name'],
    y=df_loss['Loss Rate (%)'],
    name='Tasa de pérdida (%)',
    mode='lines+markers',
    marker=dict(color='crimson', size=8),
    yaxis='y2'
))

fig2.update_layout(
    title='Ventas vs Pérdidas por Producto',
    xaxis=dict(title='Producto'),
    yaxis=dict(title='Cantidad Vendida (mil kg)', side='left'),
    yaxis2=dict(title='Tasa de pérdida (%)', overlaying='y', side='right'),
    xaxis_tickangle=-45,
    legend=dict(x=0.01, y=0.99),
    height=600
)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 📦 Productos más rentables (estructura inicial)
# -----------------------------
st.header("📦 Estructura para Análisis de Rentabilidad")
st.info("Aquí podrías agregar ingreso por producto, precio promedio, y márgenes para evaluar rentabilidad.")
