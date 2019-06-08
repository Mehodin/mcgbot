import discord
import os
import roles
import state
import logging
from discord.ext import commands

state = state.State()

bot = commands.Bot(command_prefix="/")

logger = logging.getLogger(__name__)


async def is_moderator(ctx):
    return discord.utils.get(ctx.author.roles, id=state.role_map["Moderator"]) is not None


@bot.command()
@commands.check(is_moderator)
async def sync_roles(ctx):
    roles.sync_roles_db(state, ctx.guild)
    await ctx.message.add_reaction("\U0001f440")  # Eyes emoji


@sync_roles.error
async def sync_roles_error(ctx, error):
    if not isinstance(error, commands.CheckFailure):
        return logger.warning(error)
    await ctx.send(f"{ctx.author.mention}: Unauthorized")


@bot.command()
async def source(ctx):
    await ctx.send("https://github.com/64/mcgbot")


@bot.command()
async def assign(ctx, member: discord.Member):
    # Check that the author is a captain
    # TODO: Use commands.check(is_captain) as per above
    author_team = roles.get_user_team(state, ctx.author)
    if author_team is None or not roles.is_captain(state, author_team, ctx.author):
        return await ctx.send(f"{ctx.author.mention}: You are not a team captain")

    # Check if the target is already in a team
    target_user_team = roles.get_user_team(state, member)
    if target_user_team is not None:
        return await ctx.send(f"{ctx.author.mention}: That user is already in '{target_user_team['name']}'")

    # Apply the new role
    target_role = discord.utils.get(ctx.guild.roles, id=author_team["id"])
    if target_role is None:
        return logger.warning(f"No role found for team '{author_team['name']}'")

    await member.add_roles(target_role, reason=f"Assigned by {ctx.author}")
    await ctx.message.add_reaction("\U0001f440")


@assign.error
async def assign_error(ctx, error):
    if not isinstance(error, commands.BadArgument):
        return logger.warning(error)

    await ctx.send("{ctx.author.mention}: unknown user")


@bot.command()
async def unassign(ctx, member: discord.Member = None):
    author_team = roles.get_user_team(state, ctx.author)
    if author_team is None:
        return await ctx.send(f"{ctx.author.mention}: You are not in a team")

    target_role = discord.utils.get(ctx.guild.roles, id=author_team["id"])
    if target_role is None:
        logger.warning(f"No role found for team '{author_team['name']}'")
        return

    if member is None or member == ctx.author:
        # Trying to unassign themselves
        if roles.is_captain(state, author_team, ctx.author):
            return await ctx.send(f"{ctx.author.mention}: You can't unassign yourself if you're a captain (ask a moderator)")

        await member.remove_roles(target_role, reason="Self-unassigned")
        await ctx.message.add_reaction("\U0001f440")
    else:
        # Trying to assign someone else
        if not roles.is_captain(state, author_team, ctx.author):
            return await ctx.send(f"{ctx.author.mention}: You are not a captain")

        target_user_team = roles.get_user_team(state, member)
        if target_user_team is None:
            return await ctx.send(f"{ctx.author.mention}: That user is not in a team")

        # Are they in the same team?
        if target_user_team["id"] != author_team["id"]:
            return await ctx.send(f"{ctx.author.mention}: That user is in a different team")

        await member.remove_roles(target_role, reason=f"Unassigned by {ctx.author}")
        await ctx.message.add_reaction("\U0001f440")


@assign.error
async def unassign_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("{ctx.author.mention}: unknown user")
    else:
        logger.warning(error)

print("Starting bot...")
bot.run(os.getenv("DISCORD_TOKEN"))
