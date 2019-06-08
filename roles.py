import logging
import discord
from tinydb import Query

Team = Query()
logger = logging.getLogger(__name__)


def get_role_map(prod):
    if prod:
        return {
            "Team Captain": 585478468569923611,
            "Moderator": 572950198243033088,
            "TeamUpperSpacer": 578912788903362560,
            "TeamLowerSpacer": 578912719265333270,
        }
    else:
        # Valid for the bot testing server only
        return {
            "Team Captain": 585918031339847680,
            "Moderator": 585918102009675776,
            "TeamUpperSpacer": 586037500808658991,
            "TeamLowerSpacer": 586037540071538688,
        }


def get_user_team(state, member):
    for role in member.roles:
        items = state.teams_db.search(Team.id == role.id)
        if len(items) != 1:
            continue
        return items[0]


def is_captain(state, team, member):
    # Are they a captain according to the local DB?
    captains = [member.id for captain in team["captains"]]

    # Are they a captain according to the roles on the discord server?
    is_remote_captain = discord.utils.get(
        member.roles, id=state.role_map["Team Captain"])

    if is_remote_captain and member.id not in captains:
        # Need to update local copy
        sync_roles_db(state, member.guild)

    return is_remote_captain


def sync_roles_db(state, guild):
    upper_spacer_position = discord.utils.get(
        guild.roles, id=state.role_map["TeamUpperSpacer"])  # or ....
    lower_spacer_position = discord.utils.get(
        guild.roles, id=state.role_map["TeamLowerSpacer"])  # or ....

    # Update team list
    for role in guild.roles:
        if role.position <= lower_spacer_position:
            continue
        if role.position >= upper_spacer_position:
            continue
        if role.name == "Team Captain":
            continue
        state.teams_db.upsert({"name": role.name, "color": str(
            role.color), "id": role.id, "captains": []}, Team.name == role.name)

    # Get all team captains
    for member in guild.get_role(state.role_map["Team Captain"]).members:
        team = get_user_team(state, member)
        if team is None:
            continue

        # Add them as a captain on the team list
        captains = team["captains"]
        captains.append({"id": member.id, "name": member.name})
        state.teams_db.update({"captains": captains}, Team.id == team["id"])
