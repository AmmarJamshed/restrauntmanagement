# app.py
import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Restaurant Inventory Tracker", page_icon="🍔", layout="wide")
st.title("🍟 Restaurant Raw Material & Inventory Tracker")

# -------------------------
# Upload Inventory CSV
# -------------------------
st.sidebar.header("📂 Upload Inventory File")

inv_file = st.sidebar.file_uploader("Upload Inventory (CSV)", type=["csv"])
if inv_file:
    st.session_state.inventory_df = pd.read_csv(inv_file, index_col=0)
    st.sidebar.success("✅ Inventory loaded successfully!")
else:
    if "inventory_df" not in st.session_state:
        st.session_state.inventory_df = pd.DataFrame({
            "Ingredient": ["Buns", "Patties", "Cheese Slices", "Lettuce (g)", "Tomatoes (g)", "Fries (g)", "Soft Drink (ml)"],
            "Available Quantity": [100, 80, 60, 2000, 1500, 5000, 10000]
        }).set_index("Ingredient")

st.sidebar.subheader("📦 Current Inventory")
st.sidebar.dataframe(st.session_state.inventory_df)

# -------------------------
# Upload Menu/Recipe CSV
# -------------------------
st.sidebar.header("📂 Upload Menu File")
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
    st.sidebar.success("✅ Menu loaded successfully!")
else:
    if "menu" not in st.session_state:
        st.session_state.menu = {
            "Cheeseburger": {"Buns": 1, "Patties": 1, "Cheese Slices": 1, "Lettuce (g)": 30, "Tomatoes (g)": 20},
            "Veggie Burger": {"Buns": 1, "Cheese Slices": 1, "Lettuce (g)": 40, "Tomatoes (g)": 30},
            "Fries": {"Fries (g)": 150},
            "Soft Drink": {"Soft Drink (ml)": 300}
        }

# -------------------------
# Place an Order
# -------------------------
st.header("🍴 Place an Order")
order = {}
for item in st.session_state.menu.keys():
    order[item] = st.number_input(f"{item}", min_value=0, step=1)

if st.button("✅ Process Order"):
    order_used = {}
    shortage = []

    # Calculate usage
    for item, qty in order.items():
        if qty > 0:
            for ingredient, amt in st.session_state.menu[item].items():
                total_required = amt * qty
                order_used[ingredient] = order_used.get(ingredient, 0) + total_required

    # Check inventory
    for ingredient, used in order_used.items():
        if ingredient in st.session_state.inventory_df.index:
            if st.session_state.inventory_df.loc[ingredient, "Available Quantity"] >= used:
                st.session_state.inventory_df.loc[ingredient, "Available Quantity"] -= used
            else:
                shortage_amt = used - st.session_state.inventory_df.loc[ingredient, "Available Quantity"]
                shortage.append((ingredient, shortage_amt))
                st.session_state.inventory_df.loc[ingredient, "Available Quantity"] = 0

    st.success("Order processed!")

    # Show usage summary
    st.subheader("📊 Raw Materials Used in this Order")
    st.write(pd.DataFrame(list(order_used.items()), columns=["Ingredient", "Quantity Used"]))

    # Show shortages if any
    if shortage:
        st.error("⚠️ Shortages detected!")
        st.write(pd.DataFrame(shortage, columns=["Ingredient", "Shortage Amount"]))

# -------------------------
# Show Updated Inventory
# -------------------------
st.subheader("📦 Updated Inventory")
st.dataframe(st.session_state.inventory_df)

# -------------------------
# Export Updated Inventory
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
)
