import os
from dotenv import load_dotenv

from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool
from agents.run import RunConfig

import chainlit as cl

# ✅ Tool definition
@function_tool
def add_emojis_to_summary(text: str) -> str:
    emojis = {
        "success": "✅", "important": "❗", "note": "📝",
        "error": "❌", "fun": "🎉", "text": "📜",
        "summary": "🧾", "user": "👤", "agent": "🤖",
        "information": "ℹ️", "help": "🆘", "clear": "🔍",
        "concise": "✏️", "short": "📎"
    }
    for word, emoji in emojis.items():
        if word in text.lower():
            text += f" {emoji}"
    return text

# Load env & setup model
load_dotenv()
external_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model = OpenAIChatCompletionsModel("gemini-2.0-flash", openai_client=external_client)
config = RunConfig(model=model, model_provider=external_client, tracing_disabled=True)

# Agent with tool
summarizer_agent = Agent(
    name="summarizer",
    instructions=(
        "You are a helpful assistant. Summarize clearly, "
        "then use add_emojis_to_summary tool for fun emojis."
    ),
    tools=[add_emojis_to_summary]
)

@cl.on_chat_start
async def start():
    await cl.Message(content="""
👋 Welcome to the Summarizer Agent!
Paste your long text — summary with emojis is coming! 📝🎉
""").send()

@cl.on_message
async def on_message(msg: cl.Message):
    # Start output container
    stream = cl.Message(content="🧾 **Summary:**\n\n")
    await stream.send()

    # Run streamed agent and iterate events
    run_result = Runner.run_streamed(summarizer_agent, msg.content, run_config=config)
    async for event in run_result.stream_events():
        # We only care about model-generated text deltas
        if event.type == "raw_response_event" and hasattr(event.data, "delta"):
            await stream.stream_token(event.data.delta)

    # Finalize
    await stream.update()




# *******using sync method*******

# import os
# from dotenv import load_dotenv

# from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool
# from agents.run import RunConfig

# import chainlit as cl

# # ✅ Emoji Tool Function with decorator
# @function_tool
# def add_emojis_to_summary(text: str) -> str:
#     """
#     Adds relevant emojis to the given text based on keywords.
#     """
#     emojis = {
#         "success": "✅",
#         "important": "❗",
#         "note": "📝",
#         "error": "❌",
#         "fun": "🎉",
#         "text": "📜",
#         "summary": "🧾",
#         "user": "👤",
#         "agent": "🤖",
#         "information": "ℹ️",
#         "help": "🆘",
#         "clear": "🔍",
#         "concise": "✏️",
#         "short": "📎"
#     }

#     for word, emoji in emojis.items():
#         if word in text.lower():
#             text += f" {emoji}"
#     return text

# # ✅ Load environment variables
# load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")

# # ✅ Set up external client and model
# external_client = AsyncOpenAI(
#     api_key=api_key,
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
# )

# model = OpenAIChatCompletionsModel(
#     model="gemini-2.0-flash",
#     openai_client=external_client
# )

# config = RunConfig(
#     model=model,
#     model_provider=external_client,
#     tracing_disabled=True
# )

# # ✅ Define the summarizer agent with emoji tool
# summarizer_agent: Agent = Agent(
#     name="summarizer",
#     instructions=(
#         "You are a helpful assistant. Summarize the input text in a clear and concise way. "
#         "Use the 'add_emojis_to_summary' tool to make your response fun and expressive."
#     ),
#     tools=[add_emojis_to_summary]  # Register the tool directly
# )

# # ✅ Show welcome message when app starts
# @cl.on_chat_start
# async def start():
#     await cl.Message(
#         content="""
# 👋 **Welcome to Text Summarizer Agent!**

# Just paste any long paragraph and I’ll give you a short, clear summary! 📝
# Emojis will be added automatically to make it more fun! 🎉

# Start typing your content below to begin. ⬇️
# """
#     ).send()

# # ✅ Handle user message
# @cl.on_message
# async def on_message(message: cl.Message):
#     input_text = message.content

#     # Let the agent handle summarizing AND calling the emoji tool
#     result = Runner.run_sync(summarizer_agent, input_text, run_config=config)

#     await cl.Message(
#         content=f"✅🧾🎉 **Here’s your summarized text:**\n\n{result.final_output}"
#     ).send()






