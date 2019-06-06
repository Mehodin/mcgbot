import discord, os, dotenv, tinydb
import roles
from discord.ext import commands

# Read config
dotenv.load_dotenv()
db = tinydb.TinyDB("db.json")
teams_db = db.table("teams")

production = False

if os.getenv("PRODUCTION") == "true":
    production = True

role_map = roles.get_role_map(production)

bot = commands.Bot(command_prefix="+")

@bot.command()
async def ping(ctx):
    roles.sync_roles_db(teams_db, ctx.guild.roles)
    await ctx.send("pong")


print("Running bot")
bot.run(os.getenv("DISCORD_TOKEN"))
