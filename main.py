# import os
# from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel,function_tool, set_tracing_disabled
# from agents.run import RunConfig
# from dotenv import load_dotenv
# import asyncio
# import streamlit
# import requests

# load_dotenv()
# set_tracing_disabled(True)

# gemini_api_key = os.getenv("GEMINI_API_KEY")

# if not gemini_api_key:
#     raise ValueError("GEMINI_API_KEY is not present in .env file.")

# external_client = AsyncOpenAI(
#     api_key=gemini_api_key,
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai"
# )

# model = OpenAIChatCompletionsModel(
#     model="gemini-2.0-flash",
#     openai_client=external_client
# )

# config = RunConfig(
#     model_provider=external_client,
#     model=model,
#     tracing_disabled=True
# )

# @function_tool
# async def get_crypto_price(crypto_id:str) -> str:
#     """Get the current market rate of cryptocurrency by its ID."""
    
#     url= f"https://api.coinlore.net/api/ticker/?id={crypto_id}"
#     response = requests.get(url)
    
#     if response.status_code == 200:
#         data = response.json()
        
#         if len(data) > 0:
#             name = data[0]['name']
#             price_usd = data[0]['price_usd']
#             return f"The current price of {name} is ${price_usd} USD."
#         else:
#             return "No data found. Invalid Crypto ID."
#     else:
#         return f"Error fetching data: {response.status_code}"

# crypto_data_agent = Agent(
#     name="CryptoDataAgent",
#     instructions=(
#         "You are a Crypto Market Data Agent. "
#         "Your job is to fetch the current price of cryptocurrencies using the `get_crypto_price` tool. "
#         "When a user asks about a crypto price, call the tool with the correct ID."
#     ),
#     tools=[get_crypto_price],
#     model=model
# )

# async def main():
#     result = await Runner.run(
#         starting_agent=crypto_data_agent,
#         input="What is the current price of Bitcoin ID:90?",
#         run_config=config
#     )
#     print(result.final_output)

# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# response = loop.run_until_complete(main())


import os
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel,function_tool, set_tracing_disabled
from agents.run import RunConfig
import asyncio
import streamlit as st
from dotenv import load_dotenv
import requests
import re

set_tracing_disabled(True)

try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
except:
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not present in .env file.")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model_provider=external_client,
    model=model,
    tracing_disabled=True
)

@function_tool
async def get_crypto_price(user_query: str) -> str:
    """
    Extract crypto name from user query and fetch its price.
    Example: "What is the price of Bitcoin?" -> Extract "Bitcoin"
    """
    query = user_query.lower()

    url = "https://api.coinlore.net/api/tickers/"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Error fetching crypto list: {response.status_code}"

    data = response.json().get("data", [])

    for coin in data:
        if coin["name"].lower() in query or coin["symbol"].lower() in query:
            name = coin["name"]
            price_usd = coin["price_usd"]
            return f"The current price of {name} is ${price_usd} USD."

    return "Sorry, I couldn't find any cryptocurrency in your question. Try using the coin name or symbol (e.g., Bitcoin, BTC)."

crypto_data_agent = Agent(
    name="CryptoDataAgent",
    instructions=(
        "You are a Crypto Market Data Agent. "
        "Your job is to fetch the current price of cryptocurrencies using the `get_crypto_price` tool. "
        "When a user asks about a crypto price, call the tool with the correct ID."
    ),
    tools=[get_crypto_price],
    model=model
)

st.set_page_config(page_title="Crypto Data Agent 💰", page_icon="💰", layout="centered")
st.title("Crypto Data Agent 💰")
st.write("This agent fetches the current price of cryptocurrencies by providing its ID.")

if "history" not in st.session_state:
    st.session_state.history = []
    
user_input = st.text_input("Enter your question or crypto ID:", "")

if st.button("Send"):
    if user_input:
        async def main():
            result = await Runner.run(
                starting_agent=crypto_data_agent,
                input=user_input,
                run_config=config
            )
            return result.final_output

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(main())
        
        st.session_state.history.append({"user": user_input, "agent": response})
        
for chat in st.session_state.history:
    st.markdown(f"**User:** {chat['user']}")
    st.markdown(f"**Agent:** {chat['agent']}")
