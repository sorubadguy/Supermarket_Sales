#!/usr/bin/env python
# coding: utf-8

# # Libraries/Packages

# In[52]:


import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# # Basic Analysis

# ### Sales

# In[3]:


sales_path = "data/sales.csv"
df_sales = pd.read_csv(sales_path)
df_sales.info()


# ### Product Loss

# In[4]:


product_loss_path = "data/product_loss.csv"
df_product_loss = pd.read_csv(product_loss_path)
df_product_loss.info()


# ### Products

# In[5]:


products_path = "data/products.csv"
df_products = pd.read_csv(products_path)
df_products.info()


# ### Retail Price

# In[6]:


retail_price_path = "data/retail_price.csv"
df_retail_price = pd.read_csv(retail_price_path)
df_retail_price.info()


# # Top 10 Sales

# In[7]:


df_total_sales = (
    df_sales[df_sales["Sale or Return"] == "sale"]  # Filtrar ventas reales
    .groupby("Item Code", as_index=False)["Quantity Sold (kilo)"]
    .sum()
    .merge(df_products, on="Item Code", how="left")  # Combinar con datos del producto
)
df_total_sales.head()


# In[8]:


df_ordered = df_total_sales.sort_values(by=["Quantity Sold (kilo)", "Item Name"], ascending=[False, True]).reset_index(drop=True)
df_ordered.head()


# In[9]:


fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(df_ordered['Item Name'].head(15), df_ordered['Quantity Sold (kilo)'].head(15), color='skyblue')
plt.xticks(rotation=45)
plt.title('Top 10 Products sales')
plt.xlabel('Product Name')
plt.ylabel('Quantity Sold (kilo)')
plt.show()


# In[10]:


fig = px.bar(
    df_ordered.head(15),
    x='Item Name',
    y='Quantity Sold (kilo)',
    title='Top 15 Product Sales',
    labels={
        'Item Name': 'Product Name',
        'Quantity Sold (kilo)': 'Quantity Sold (kg)'
    },
    color_discrete_sequence=['skyblue']
)

fig.update_layout(xaxis_tickangle=-45)
fig.show()


# # Top loss

# In[11]:


df_loss = df_product_loss.merge(df_sales, on = "Item Code", how = "left").sort_values(
    by=["Quantity Sold (kilo)"], ascending=False)

df_loss = df_loss.groupby(['Item Name', 'Loss Rate (%)'], as_index=False).agg(
    {'Quantity Sold (kilo)': 'sum'}).sort_values(by='Quantity Sold (kilo)', ascending=False)

fig = go.Figure()

# Barras
fig.add_trace(go.Bar(
    x=df_loss['Item Name'],
    y=df_loss['Quantity Sold (kilo)'] / 1000,
    name='Cantidad Vendida (mil kg)',
    marker_color='skyblue',
    yaxis='y1'
))

# Scatter
fig.add_trace(go.Scatter(
    x=df_loss['Item Name'],
    y=df_loss['Loss Rate (%)'],
    name='Tasa de pérdida (%)',
    mode='lines+markers',
    marker=dict(color='crimson', size=8),
    yaxis='y2'
))

# Ejes
fig.update_layout(
    title='Ventas vs Pérdidas por Producto',
    xaxis=dict(title='Producto'),
    yaxis=dict(title='Cantidad Vendida (mil kg)', side='left'),
    yaxis2=dict(title='Tasa de pérdida (%)', overlaying='y', side='right'),
    xaxis_tickangle=-45,
    legend=dict(x=0.01, y=0.99),
    height=500
)

fig.show()


# ## 📊 Sales vs. Loss Rate Analysis by Product
# 
# This chart combines the **total quantity sold (in thousands of kilograms)** with the **loss rate (%)** per product, allowing a clear visualization and assessment of each product's performance.
# 
# ### ✅ Key Findings:
# 
# 1. **No direct correlation between sales and loss**
#    - Many high-demand products show low loss rates.
#    - Others, with low sales, exhibit high loss rates.
#    - 👉 This suggests that product popularity does not necessarily lead to higher spoilage.
# 
# 2. **Low-selling, high-loss products**
#    - Some products have low rotation and high spoilage rates.
#    - 🎯 These are optimization opportunities, as they may generate more loss than revenue.
# 
# 3. **Efficient products**
#    - Some products have large sales volumes and very low loss rates.
#    - 🟢 These are ideal for maintaining in stock, promoting, or using as benchmarks for efficient inventory management.
# 
# 4. **Extreme loss values**
#    - There are peaks in loss rates above 20–30%.
#    - 🔍 These products should be reviewed: they might be perishable, poorly stored, or in low demand.
# 
# ---
# 
# ### 💡 Recommendations:
# - Review products with extremely high loss rates individually.
# - Focus promotions and campaigns on top-performing products.
# - Consider discontinuing low-selling, high-loss products.
# 
# 

# # Most profitable products

# In[41]:


df_profitable = df_sales[df_sales["Sale or Return"] == "sale"].drop(['Time', 'Sale or Return'], axis=1).reset_index()
df_profitable = df_profitable.drop('index', axis = 1)
df_profitable = df_profitable.groupby(["Date", "Item Code", "Unit Selling Price (RMB/kg)", "Discount (Yes/No)"], as_index=False)['Quantity Sold (kilo)'].sum().reset_index()
df_profitable.drop('index', axis=1, inplace=True)
df_profitable = df_profitable.merge(df_products, on="Item Code", how="left").drop(['Category Code', 'Category Name'], axis=1)
df_profitable


# ### Sales per day

# In[42]:


df_day = df_profitable.groupby('Date')['Quantity Sold (kilo)'].sum().reset_index()

fig = px.line(df_day, x='Date', y='Quantity Sold (kilo)', title='Ventas totales por día')
fig.show()


# ### Average price per day

# In[33]:


df_price = df_profitable.groupby('Date')['Unit Selling Price (RMB/kg)'].mean().reset_index()

fig = px.line(df_price, x='Date', y='Unit Selling Price (RMB/kg)', title='Precio promedio por día')
fig.show()


# ### Comparison: with and without discount

# In[43]:


df_discount = df_profitable.groupby('Discount (Yes/No)')['Quantity Sold (kilo)'].sum().reset_index()

fig = px.bar(df_discount, x='Discount (Yes/No)', y='Quantity Sold (kilo)', title='Ventas con y sin descuento')
fig.show()


# ### Top selling products

# In[45]:


df_top = df_profitable.groupby('Item Name')['Quantity Sold (kilo)'].sum().reset_index().sort_values(by='Quantity Sold (kilo)', ascending=False).head(10)

fig = px.bar(df_top, x='Item Name', y='Quantity Sold (kilo)', title='Top 10 productos más vendidos')
fig.show()


# ### Time series by product

# In[47]:


df_serie = df_profitable.groupby(['Date', 'Item Name'])['Quantity Sold (kilo)'].sum().reset_index()

fig = px.line(df_serie, x='Date', y='Quantity Sold (kilo)', color='Item Name', title='Ventas por producto en el tiempo')
fig.show()


# In[49]:


df_recomendation = df_profitable.merge(df_retail_price, on=['Item Code', 'Date'], how='left')
df_recomendation


# In[53]:


def generar_recomendaciones(df, top_n=10):
    st.subheader("🧠 Recomendaciones automáticas")

    # Calcular margen por kg si no existe
    if 'Margen por kg' not in df.columns:
        df['Margen por kg'] = df['Unit Selling Price (RMB/kg)'] - df['Wholesale Price (RMB/kg)']

    # Tomar los top productos más vendidos
    df_top = df.groupby('Item Name', as_index=False).agg({
        'Quantity Sold (kilo)': 'sum',
        'Unit Selling Price (RMB/kg)': 'mean',
        'Wholesale Price (RMB/kg)': 'mean',
        'Margen por kg': 'mean',
        'Discount (Yes/No)': lambda x: x.mode()[0] if not x.isna().all() else 'No'
    }).sort_values(by='Quantity Sold (kilo)', ascending=False).head(top_n)

    # Generar recomendaciones
    for i, row in df_top.iterrows():
        producto = row['Item Name']
        ventas = row['Quantity Sold (kilo)']
        margen = row['Margen por kg']
        descuento = row['Discount (Yes/No)']

        if margen > 2 and descuento == 'No':
            st.markdown(f"✅ **{producto}** tiene buen margen y no tiene descuento. Podrías aplicar una promoción estratégica.")
        elif margen < 0:
            st.markdown(f"⚠️ **{producto}** tiene margen negativo. Revisá su precio de compra o venta.")
        elif ventas < 100:
            st.markdown(f"📉 **{producto}** tiene baja rotación. Evaluá si vale la pena mantenerlo en stock.")
        elif ventas > 1000 and descuento == 'Yes':
            st.markdown(f"💸 **{producto}** vende muy bien, incluso con descuento. Considerá reducirlo o ajustar el precio.")


# In[54]:


generar_recomendaciones(df_recomendation)


# In[ ]:




