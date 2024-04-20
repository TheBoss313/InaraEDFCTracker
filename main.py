import os
import discord
import json
import pathlib
from discord.ext.commands import has_permissions
import dotenv

dotenv.load_dotenv()
token = str(os.getenv("TOKEN"))

bot = discord.Bot()


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


bot.run(token)
