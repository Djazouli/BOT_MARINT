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

        self.authorized_channels = {434724164511727620, 356826903405002752}

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
        if ctx.command is None:
            if not ctx.message.clean_content in self.all_commands:
                return
            ctx.command = self.all_commands[ctx.message.clean_content]
        if ctx.author not in self.custom_users:
            self.custom_users[ctx.author] = User(ctx.author)
        await self.invoke(ctx)

    async def on_message(self, message):
        if message.author.bot or message.channel.id not in self.authorized_channels:
            return
        await self.process_commands(message)



client = MarkovBot()
client.run()