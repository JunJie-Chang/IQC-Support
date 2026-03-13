"""Discord bot for IQC Support Agent — runs as a background service."""

import os
import asyncio

import discord
from dotenv import load_dotenv
load_dotenv()

from agent import run_agent

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_connect():
    print("Connected to Discord gateway...")

@bot.event
async def on_disconnect():
    print("Disconnected from Discord.")


@bot.event
async def on_ready():
    print(f"IQC Support is online as {bot.user} (ID: {bot.user.id})")
    print(f"Listening to all channels.")


@bot.event
async def on_message(message: discord.Message):
    print(f"Message received: {message.author} in #{message.channel} (id={message.channel.id}): {message.content[:80]}")
    if message.author == bot.user:
        print("  -> Ignored: own message"); return
    if bot.user not in message.mentions:
        print(f"  -> Ignored: bot not mentioned"); return
    print("  -> Passing to agent...")

    # Strip the mention from the message
    user_text = message.content.replace(f"<@{bot.user.id}>", "").strip()
    if not user_text:
        await message.reply("Hi! How can I help with IQC? Ask me to take notes or schedule a meeting.")
        return

    # Show typing indicator while agent processes
    async with message.channel.typing():
        try:
            reply = await asyncio.get_event_loop().run_in_executor(
                None, run_agent, user_text
            )
        except Exception as e:
            reply = f"Sorry, I ran into an error: {e}"

    # Discord messages have a 2000 char limit — split if needed
    if len(reply) <= 2000:
        await message.reply(reply)
    else:
        chunks = [reply[i:i+1990] for i in range(0, len(reply), 1990)]
        for chunk in chunks:
            await message.channel.send(chunk)


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
