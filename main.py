import discord, os, dotenv
from discord.ext import commands

# Read config
dotenv.load_dotenv()

production = False

if os.getenv("PRODUCTION") == "true":
    production = True

bot = commands.Bot(command_prefix="+")

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

print("Running bot")
bot.run(os.getenv("DISCORD_TOKEN"))
