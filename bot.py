import discord
from tinydb import TinyDB
import os
import sys
from discord.ext import commands
from discord.ext.commands import context
from markov import generate_markov_chains
from utils.user import User
db = TinyDB("db.json")

extensions = (
    'cogs.quotes',
    'cogs.markov',
    'cogs.soundplay',
)

class MarkovBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="")
        self.token = sys.argv[1]
        self.markov_chains = generate_markov_chains()
        for unwanted_user in ["Discrank"]:
            del self.markov_chains[unwanted_user]

        self.current_guess = None
        self.current_streak = 0

        with open("databases/last_sent") as f:
            last_sent = f.read()
            self.last_sent = int(last_sent) if last_sent else 0

        self.authorized_channels = {434724164511727620, 356826903405002752, 367334912874905601}

        for extension in extensions:
            self.load_extension(extension)

        self.custom_users = {}



    def run(self):
        super().run(self.token, reconnect=True)

    async def on_ready(self):
        game = "Maintenance..." if os.environ.get("DEBUG") else "Ressasser le passé"
        await self.change_presence(activity=discord.Game(name=game))
        print("Bot ready!")

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=context.Context)
        if ctx.author.id == 97674207722213376:
            await ctx.send("Antho ptit bouffon")
        if ctx.command is None:
            ctx.command = self.try_get_commands(ctx.message.clean_content)
        if ctx.command is None:
            return
        if ctx.author not in self.custom_users:
            self.custom_users[ctx.author] = User(ctx.author)
        await self.invoke(ctx)

    def try_get_commands(self, content):
        content = content.casefold()
        for command_name in self.all_commands:
            if command_name.casefold() == content:
                return self.all_commands[command_name]
        return None

    async def on_message(self, message):
        if message.author.bot or (self.authorized_channels and message.channel.id not in self.authorized_channels):
            return
        await self.process_commands(message)



client = MarkovBot()
client.run()