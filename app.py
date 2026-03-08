import streamlit as st
import pandas as pd
import anthropic

st.set_page_config(page_title="Logistics AI Copilot", page_icon="📦", layout="wide")
st.title("📦 Supply Chain & Weather Copilot")
st.markdown("Ask questions about shipping delays and weather impacts.")

api_key = st.sidebar.text_input("Enter Anthropic API Key", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("Loaded Datasets")

# --- THE SPEED UPGRADE (CACHING) ---
# This tells Streamlit to only load the data once and store it in RAM!
@st.cache_data
def get_dataframe(file_name):
    if file_name.endswith('.csv'):
        return pd.read_csv(file_name)
    return None

def load_and_display(file_name, display_name):
    try:
        df = get_dataframe(file_name)
        st.sidebar.success(f"✅ {display_name}: {len(df)} rows")
        return df
    except Exception:
        st.sidebar.error(f"❌ Missing {file_name}")
        return None

# Load the data via the high-speed cache
weather_df = load_and_display("FULL_ENRICHED_WEATHER.csv", "Weather Data")
orders_daily_df = load_and_display("Orders_Daily.csv", "Daily Orders")
orders_monthly_df = load_and_display("Orders_Monthly.csv", "Monthly Orders")
oil_df = load_and_display("historical_oil_prices.csv", "Oil Prices")
eur_usd_df = load_and_display("historical_eur_usd.csv", "Exchange Rates")

# --- THE CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# This line was missing in your screenshot!
user_query = st.chat_input("Ask a question about your supply chain...")

if user_query:
    st.chat_message("user").markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    if not api_key:
        st.error("Please enter your Anthropic API Key in the sidebar to chat!")
    else:
        client = anthropic.Anthropic(api_key=api_key)
        
        # Injecting the data schemas into Claude's brain
        data_context = f"""
        You are an expert Supply Chain AI Copilot. The user has loaded 5 datasets into your memory.
        Here is the schema for each table:
        1. Weather Data ({len(weather_df) if weather_df is not None else 0} rows): {list(weather_df.columns) if weather_df is not None else 'None'}
        2. Daily Orders ({len(orders_daily_df) if orders_daily_df is not None else 0} rows): {list(orders_daily_df.columns) if orders_daily_df is not None else 'None'}
        3. Monthly Orders ({len(orders_monthly_df) if orders_monthly_df is not None else 0} rows): {list(orders_monthly_df.columns) if orders_monthly_df is not None else 'None'}
        4. Oil Prices ({len(oil_df) if oil_df is not None else 0} rows): {list(oil_df.columns) if oil_df is not None else 'None'}
        5. Exchange Rates ({len(eur_usd_df) if eur_usd_df is not None else 0} rows): {list(eur_usd_df.columns) if eur_usd_df is not None else 'None'}
        
        Answer confidently based on your knowledge of supply chain analytics and these specific data structures. 
        """
        
        with st.spinner("Claude is analyzing the data schemas..."):
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4000,
                system=data_context,
                messages=[{"role": "user", "content": user_query}]
            )
            
            answer = response.content[0].text
            st.chat_message("assistant").markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})