from tinydb import Query

Team = Query()

def get_role_map(prod):
    if prod:
        # TODO
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
                "TeamUpperSpacer": 58603750080865899,
                "TeamLowerSpacer": 586037540071538688,
        }

def sync_roles_db(teams_db, roles):
    meta_roles = get_role_map(True)
    upper_spacer_position = [role.position for role in roles if role.id == meta_roles["TeamUpperSpacer"]][0]
    lower_spacer_position = [role.position for role in roles if role.id == meta_roles["TeamLowerSpacer"]][0]

    for role in roles:
        if role.position > lower_spacer_position and role.position < upper_spacer_position and role.name != "Team Captain":
            teams_db.upsert({ "name": role.name, "color": str(role.color), "id": role.id }, Team.name == role.name)
