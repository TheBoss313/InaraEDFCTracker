import os
from pprint import pprint
import discord
import json
import pathlib
from discord.ext.commands import has_permissions
import dotenv
from scraper import get_fleet_carrier, find_carrier_by_name, get_cmdr, MongoClient, get_database, insert_new_value, find_value, delete_value, update_value

dotenv.load_dotenv()
token = str(os.getenv("TOKEN"))

db_name = str(os.getenv("DB_USERNAME"))
db_host = str(os.getenv("DB_HOST"))
db_password = str(os.getenv("DB_PASSWORD"))
db_appname = str(os.getenv("DB_APPNAME"))

app_name = str(os.getenv("API_APPNAME"))
api_key = str(os.getenv("API_KEY"))
cmdr_name = str(os.getenv("API_CMDR_NAME"))
cmdr_id = str(os.getenv("API_FDEV_ID"))


bot = discord.Bot()
db = get_database(db_name, db_password, db_host, db_appname)
fleet_carriers = db['fleet_carriers']
commanders = db['cmdrs']
tips = db['tips']


@bot.event
async def on_ready():
    game = discord.Game("Tracking N.S.C. Chicky Nuggies")
    await bot.change_presence(status=discord.Status.online, activity=game)
    print('Ready')


@bot.event
async def on_command_error(ctx, error):
    print(error)
    print(ctx)
    if error == discord.errors.Forbidden:
        await ctx.send('I do not have permission to do that.')
    else:
        await ctx.send("Some error occurred.")


@bot.slash_command(name="findfc", description="Searches for Fleet Carriers by identifier.")
async def fc_by_id(ctx, identifier: str):
    text = get_fleet_carrier(identifier, fleet_carriers)
    await ctx.respond(text)


@bot.slash_command(name="findfcname", description="Looks up Fleet Carriers by name. Limited to 30 results.")
async def fc_by_name(ctx, name: str):
    text = find_carrier_by_name(name, fleet_carriers)
    await ctx.respond(text)


@bot.slash_command(name="findcmdr", description="Searches for CMDRs by name.")
async def cmdr_by_name(ctx, name: str):
    text = get_cmdr(name, app_name, api_key, cmdr_name, cmdr_id, commanders)
    await ctx.respond(text)

bot.run(token)
