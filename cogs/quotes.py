from random import choice
from time import time
from pathlib import Path

import discord
from discord.ext import commands
from tinydb import Query
from databases.databases import get_quotes_db


class Quoter(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.group(pass_context=True, name="J'invoque")
    async def quoter(self, ctx):
        """Fibre muscullaiiiiire"""
        if ctx.invoked_subcommand is None:
            await ctx.send(f'T\'invoque que MarINT bouffon')

    @quoter.command(name="MarINT")
    async def sexe(self, ctx):
        global last_sent
        global channel_id
        db = get_quotes_db()
        _image = Query()
        pickable = db.search(_image.posted == False)
        if not pickable:
            db.update({"posted": False}, _image.posted == True)
            pickable = db.all()
        print(f"{len(pickable) - 1} pics left")
        picked = choice(pickable)
        text = picked["message"]
        await ctx.send(text, file=discord.File(Path("images") / picked["file"]))
        db.update({"posted": True}, _image.file == picked["file"])
        last_sent = int(time())
        with open("databases/last_sent", "w") as f:
            f.write(str(last_sent))
        return


def setup(bot):
    bot.add_cog(Quoter(bot))