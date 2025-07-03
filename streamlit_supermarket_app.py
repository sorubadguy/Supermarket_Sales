import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Supermarket | Sales Analysis", layout="wide")

st.title("🛒 Supermarket Sales Analysis")

# Data Loading
df_sales = pd.read_csv("data/sales.csv")
df_product_loss = pd.read_csv("data/product_loss.csv")
df_products = pd.read_csv("data/products.csv")
df_retail_price = pd.read_csv("data/retail_price.csv")

# Total Sales Analysis
st.header("🔝 Top 15 Best-Selling Products")
df_total_sales = (
    df_sales[df_sales["Sale or Return"] == "sale"]
    .groupby("Item Code", as_index=False)["Quantity Sold (kilo)"]
    .sum()
    .merge(df_products, on="Item Code", how="left")
)

df_ordered = df_total_sales.sort_values(
    by=["Quantity Sold (kilo)", "Item Name"], ascending=[False, True]
).reset_index(drop=True)

fig1 = px.bar(
    df_ordered.head(15),
    x="Item Name",
    y="Quantity Sold (kilo)",
    title="Top 15 Best-Selling Products",
    labels={"Item Name": "Product", "Quantity Sold (kilo)": "Quantity Sold (kilo)"},
    color_discrete_sequence=["skyblue"]
)
fig1.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig1, use_container_width=True)

# Análisis de pérdida de productos
st.header("📉 Sales vs. Loss Rate by Product")
df_loss = df_product_loss.merge(df_sales, on="Item Code", how="left")
df_loss = df_loss.groupby(["Item Name", "Loss Rate (%)"], as_index=False).agg(
    {"Quantity Sold (kilo)": "sum"}
).sort_values(by="Quantity Sold (kilo)", ascending=False)

fig2 = go.Figure()
fig2.add_trace(go.Bar(
    x=df_loss["Item Name"],
    y=df_loss["Quantity Sold (kilo)"] / 1000,
    name="Quantity Sold (tons)",
    marker_color="skyblue",
    yaxis="y1"
))
fig2.add_trace(go.Scatter(
    x=df_loss["Item Name"],
    y=df_loss["Loss Rate (%)"],
    name="Loss Rate (%)",
    mode="lines+markers",
    marker=dict(color="crimson", size=8),
    yaxis="y2"
))
fig2.update_layout(
    title="Sales vs. Losses by Product",
    xaxis=dict(title="Producto"),
    yaxis=dict(title="Quantity Sold (tons)", side="left"),
    yaxis2=dict(title="Loss Rate (%)", overlaying="y", side="right"),
    xaxis_tickangle=-45,
    height=600
)
st.plotly_chart(fig2, use_container_width=True)

# Preparation for profitability analysis
df_profitable = df_sales[df_sales["Sale or Return"] == "sale"].drop(['Time', 'Sale or Return'], axis=1)
df_profitable = df_profitable.groupby(["Date", "Item Code", "Unit Selling Price (RMB/kg)", "Discount (Yes/No)"], as_index=False)['Quantity Sold (kilo)'].sum()
df_profitable = df_profitable.merge(df_products, on="Item Code", how="left").drop(['Category Code', 'Category Name'], axis=1)

# Time Series
st.header("📆 Total Sales per Day")
df_day = df_profitable.groupby("Date")["Quantity Sold (kilo)"].sum().reset_index()
fig3 = px.line(df_day, x="Date", y="Quantity Sold (kilo)", title="Total Sales per Day")
st.plotly_chart(fig3, use_container_width=True)

st.header("💲 Average price per day")
df_price = df_profitable.groupby("Date")["Unit Selling Price (RMB/kg)"].mean().reset_index()
fig4 = px.line(df_price, x="Date", y="Unit Selling Price (RMB/kg)", title="Average price per day")
st.plotly_chart(fig4, use_container_width=True)

# Con/sin descuento
st.header("🎯 Comparación de ventas con y sin descuento")
df_discount = df_profitable.groupby("Discount (Yes/No)")["Quantity Sold (kilo)"].sum().reset_index()
fig5 = px.bar(df_discount, x="Discount (Yes/No)", y="Quantity Sold (kilo)", title="Ventas con y sin descuento")
st.plotly_chart(fig5, use_container_width=True)

# Top productos y series por producto
st.header("📦 Top 10 productos por cantidad vendida")
df_top = df_profitable.groupby("Item Name")["Quantity Sold (kilo)"].sum().reset_index().sort_values(
    by="Quantity Sold (kilo)", ascending=False).head(10)
fig6 = px.bar(df_top, x="Item Name", y="Quantity Sold (kilo)", title="Top 10 productos más vendidos")
st.plotly_chart(fig6, use_container_width=True)

st.header("📈 Ventas por producto a lo largo del tiempo")
df_serie = df_profitable.groupby(["Date", "Item Name"])["Quantity Sold (kilo)"].sum().reset_index()
fig7 = px.line(df_serie, x="Date", y="Quantity Sold (kilo)", color="Item Name", title="Ventas por producto en el tiempo")
st.plotly_chart(fig7, use_container_width=True)

# Recomendaciones automáticas
st.header("🧠 Recomendaciones automáticas")
df_recomendation = df_profitable.merge(df_retail_price, on=["Item Code", "Date"], how="left")
df_recomendation["Margen por kg"] = df_recomendation["Unit Selling Price (RMB/kg)"] - df_recomendation["Wholesale Price (RMB/kg)"]

df_top_rec = df_recomendation.groupby("Item Name", as_index=False).agg({
    "Quantity Sold (kilo)": "sum",
    "Unit Selling Price (RMB/kg)": "mean",
    "Wholesale Price (RMB/kg)": "mean",
    "Margen por kg": "mean",
    "Discount (Yes/No)": lambda x: x.mode()[0] if not x.isna().all() else 'No'
}).sort_values(by="Quantity Sold (kilo)", ascending=False).head(10)

for _, row in df_top_rec.iterrows():
    producto = row["Item Name"]
    ventas = row["Quantity Sold (kilo)"]
    margen = row["Margen por kg"]
    descuento = row["Discount (Yes/No)"]

    if margen > 2 and descuento == "No":
        st.markdown(f"✅ **{producto}** It has a good margin and no discount. You could run a strategic promotion.")
    elif margen < 0:
        st.markdown(f"⚠️ **{producto}** has a negative margin. Review your purchase or sale price.")
    elif ventas < 100:
        st.markdown(f"📉 **{producto}** It has a low turnover. Evaluate whether it's worth keeping in stock.")
    elif ventas > 1000 and descuento == "Yes":
        st.markdown(f"💸 **{producto}** It sells very well, even at a discount. Consider reducing it or adjusting the price.")
