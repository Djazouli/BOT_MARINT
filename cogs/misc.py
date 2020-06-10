from discord.ext import commands

class Markov(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command("Purpose")
    async def purpose(self, ctx):
        ctx.send("Bot utile pour ressasser le passé")