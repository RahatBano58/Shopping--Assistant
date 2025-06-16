from agents import Agent, Runner, RunConfig, OpenAIChatCompletionsModel, AsyncOpenAI
import streamlit as st
from dotenv import load_dotenv
import os
import asyncio

# Load environment
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please check your .env file.")

# Gemini Client Setup
external_client = AsyncOpenAI(
    api_key=API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

ShoppingAgent = Agent(
    name="Shopping Advisor",
    instructions="You're a helpful shopping assistant that suggests or explains products based on the user's query. Be concise, clear, and helpful."
)

async def get_product_suggestion(prompt):
    try:
        response = await Runner.run(ShoppingAgent, input=prompt, run_config=config)
        return response.final_output
    except Exception as e:
        return f"❌ Error: {e}"

# Streamlit UI
st.set_page_config(page_title="ShopWise AI 🛍️", page_icon="🛒")

if "shopping_history" not in st.session_state:
    st.session_state.shopping_history = []

st.sidebar.title("🛒 ShopWise AI")
st.sidebar.markdown("## 🛍️ Past Searches")

for i, item in enumerate(reversed(st.session_state.shopping_history), 1):
    st.sidebar.markdown(f"**{i}.** {item['query'][:25]}...")
    if st.sidebar.button(f"View {i}", key=f"view_{i}"):
        st.session_state["viewed_search"] = item

# Display viewed search
if "viewed_search" in st.session_state:
    viewed = st.session_state["viewed_search"]
    st.markdown("## 🔍 Search Result")
    st.markdown(f"**Query:** {viewed['query']}")
    st.markdown("**Gemini Response:**")
    st.success(viewed['response'])

# Main UI
st.title("🛍️ ShopWise AI - Your Smart Shopping Assistant")

query = st.text_input("🔎 What product are you looking for?", placeholder="e.g. best phone under 50k")

if st.button("Search Product"):
    if not query.strip():
        st.warning("Please enter a product or category.")
    else:
        with st.spinner("Searching..."):
            full_prompt = f"Suggest or explain the best options for: {query}"
            answer = asyncio.run(get_product_suggestion(full_prompt))

            st.session_state.shopping_history.append({
                "query": query,
                "response": answer
            })

            st.subheader("✅ Gemini Response:")
            st.success(answer)

# Sample Product Showcase (Optional)
st.markdown("---")
st.markdown("### 🧺 Featured Products")
cols = st.columns(3)
products = [
    {"name": "Samsung Galaxy A15", "price": "Rs 48,999", "emoji": "📱"},
    {"name": "HP Laptop 14s", "price": "Rs 99,999", "emoji": "💻"},
    {"name": "AirPods Pro 2", "price": "Rs 54,000", "emoji": "🎧"},

]
for col, p in zip(cols, products):
    col.markdown(f"**{p['emoji']} {p['name']}**\n\n💰 {p['price']}")

# Footer
st.markdown("---")
st.markdown("🛒 **ShopWise AI** &copy; 2025 | Created by Rahat Bano")
st.markdown("📧 Contact: `rahatbano142@gmail.com` | 🔗 [GitHub](https://github.com/RahatBano58)")
