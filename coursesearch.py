# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# -------------------------
# Page Setup
# -------------------------
st.set_page_config(page_title="Restaurant Inventory Tracker", page_icon="🍔", layout="wide")

st.markdown(
    """
    <style>
    .big-font {font-size:24px !important; font-weight:bold; color:#FF4B4B;}
    .ok-font {font-size:20px !important; font-weight:bold; color:#1F77B4;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🍟 Restaurant Inventory & Order Tracker")

# -------------------------
# Upload Inventory
# -------------------------
st.sidebar.header("📂 Upload Files")

inv_file = st.sidebar.file_uploader("Upload Inventory (CSV)", type=["csv"])
if inv_file:
    st.session_state.inventory_df = pd.read_csv(inv_file, index_col=0)
else:
    if "inventory_df" not in st.session_state:
        st.session_state.inventory_df = pd.DataFrame({
            "Ingredient": ["Buns", "Patties", "Cheese Slices", "Lettuce (g)", "Tomatoes (g)", "Fries (g)", "Soft Drink (ml)"],
            "Available Quantity": [100, 80, 60, 2000, 1500, 5000, 10000]
        }).set_index("Ingredient")

st.sidebar.subheader("📦 Current Inventory")
st.sidebar.dataframe(st.session_state.inventory_df)

# -------------------------
# Upload Menu/Recipes
# -------------------------
menu_file = st.sidebar.file_uploader("Upload Menu (CSV)", type=["csv"])
if menu_file:
    menu_df = pd.read_csv(menu_file)
    st.session_state.menu = {}
    for _, row in menu_df.iterrows():
        dish = row["Dish"]
        st.session_state.menu[dish] = {}
        for col in menu_df.columns[1:]:
            if not pd.isna(row[col]) and row[col] > 0:
                st.session_state.menu[dish][col] = row[col]
else:
    if "menu" not in st.session_state:
        st.session_state.menu = {
            "🍔 Cheeseburger": {"Buns": 1, "Patties": 1, "Cheese Slices": 1, "Lettuce (g)": 30, "Tomatoes (g)": 20},
            "🥗 Veggie Burger": {"Buns": 1, "Cheese Slices": 1, "Lettuce (g)": 40, "Tomatoes (g)": 30},
            "🍟 Fries": {"Fries (g)": 150},
            "🥤 Soft Drink": {"Soft Drink (ml)": 300}
        }

# -------------------------
# Place an Order
# -------------------------
st.header("🛒 Place an Order")
order = {}
cols = st.columns(2)
i = 0
for item in st.session_state.menu.keys():
    with cols[i % 2]:
        order[item] = st.number_input(f"{item}", min_value=0, step=1)
    i += 1

if st.button("✅ Process Order", use_container_width=True):
    order_used = {}
    shortage = []

    # Calculate usage
    for item, qty in order.items():
        if qty > 0:
            for ingredient, amt in st.session_state.menu[item].items():
                total_required = amt * qty
                order_used[ingredient] = order_used.get(ingredient, 0) + total_required

    # Deduct from inventory
    for ingredient, used in order_used.items():
        if ingredient in st.session_state.inventory_df.index:
            if st.session_state.inventory_df.loc[ingredient, "Available Quantity"] >= used:
                st.session_state.inventory_df.loc[ingredient, "Available Quantity"] -= used
            else:
                shortage_amt = used - st.session_state.inventory_df.loc[ingredient, "Available Quantity"]
                shortage.append((ingredient, shortage_amt))
                st.session_state.inventory_df.loc[ingredient, "Available Quantity"] = 0

    st.success("✅ Order processed!")

    # Show usage
    st.subheader("📊 Ingredients Used")
    st.write(pd.DataFrame(list(order_used.items()), columns=["Ingredient", "Quantity Used"]))

    # Show shortages
    if shortage:
        st.markdown('<p class="big-font">⚠️ SHORTAGES!</p>', unsafe_allow_html=True)
        st.write(pd.DataFrame(shortage, columns=["Ingredient", "Shortage Amount"]))

# -------------------------
# Show Updated Inventory
# -------------------------
st.subheader("📦 Updated Inventory")
styled_inv = st.session_state.inventory_df.style.applymap(
    lambda val: "color:red;" if val < 20 else "color:green;", subset=["Available Quantity"]
)
st.write(styled_inv)

# -------------------------
# Charts for Easy View
# -------------------------
st.subheader("📉 Inventory Overview")

fig, ax = plt.subplots(figsize=(8, 4))
st.session_state.inventory_df["Available Quantity"].plot(kind="bar", ax=ax, color="skyblue")
plt.title("Available Inventory")
plt.xticks(rotation=45, ha="right")
st.pyplot(fig)

# -------------------------
# Download Updated Inventory
# -------------------------
def to_csv(df):
    output = BytesIO()
    df.to_csv(output)
    return output.getvalue()

st.download_button(
    label="💾 Download Updated Inventory",
    data=to_csv(st.session_state.inventory_df),
    file_name="updated_inventory.csv",
    mime="text/csv",
    use_container_width=True
)
