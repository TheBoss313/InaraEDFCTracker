import os
import discord
import json
import pathlib
from discord.ext.commands import has_permissions
import dotenv
from pymongo import MongoClient
from scraper import get_fleet_carrier

dotenv.load_dotenv()
token = str(os.getenv("TOKEN"))
db_name = str(os.getenv("DB_USERNAME"))
db_host = str(os.getenv("DB_HOST"))
db_password = str(os.getenv("DB_PASSWORD"))
db_appname = str(os.getenv("DB_APPNAME"))


def get_database(name, _pass, host, app_name):
    CONNECTION_STRING = f"mongodb+srv://{name}:{_pass}@{host}.xnsguws.mongodb.net/?retryWrites=true&w=majority&appName={app_name}"
    client = MongoClient(CONNECTION_STRING)
    return client['newpBot']


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


@bot.slash_command(name="findfc", description="Returns link to Fleet Carrier from identifier.")
async def info(ctx, identifier: str):
    text = get_fleet_carrier(identifier)
    print(text)
    await ctx.respond(text)

bot.run(token)
