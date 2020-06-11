from random import choice
from time import time
from pathlib import Path

import discord
from discord.ext import commands
from tinydb import Query
from databases.databases import get_ranking_db



class Markov(commands.Cog):


    def __init__(self, bot):
        super().__init__()
        self.bot = bot

        for name in self.bot.markov_chains.keys():
            self.bot.add_command(commands.Command(self.get_name_guess_func(name), name=name))
            self.bot.add_command(commands.Command(self.get_line_func(name), name=f"Line {name}",))

    def get_line_func(self, name):
        async def _get_line(ctx):
            sentence, _name = self.get_line(name)
            await ctx.send(f"> {sentence}\n{_name}")
        return _get_line

    def get_name_guess_func(self, name):
        async def _name_guess(ctx):
            await self.try_guess(name, ctx)
        return _name_guess

    def get_line(self, name=None):
        if not name or name not in self.bot.markov_chains:
            name = choice(list(self.bot.markov_chains.keys()))
        markov_chain = self.bot.markov_chains.get(name)
        sentence = markov_chain.generate_sentence()
        if len(sentence.split()) < 5:
            sentence += f". {markov_chain.generate_sentence()}"
        return sentence, name

    @commands.command("Guess")
    async def guess(self, ctx):
        if self.bot.custom_users.get(ctx.author).current_guess is not None:
            await ctx.send("Game already in progress...")
            return
        current_guessing = choice(list(self.bot.markov_chains.keys()))
        sentence, name = self.get_line(current_guessing)
        print(name)
        await ctx.send(f"Guess who could have said:\n*{sentence}*")
        self.bot.custom_users.get(ctx.author).current_guess = name

    @commands.command("Users")
    async def get_guess_list(self, ctx):
        await ctx.send(' - ' + '\n - '.join(self.bot.markov_chains.keys()))

    async def try_guess(self, name: str, ctx):
        user = self.bot.custom_users.get(ctx.author)
        if user.current_guess is None:
            return
        if name == user.current_guess:
            message = f"Congratulations! You guessed {name}!"
            user.set_current_streak(user.current_streak + 1)
            user.increment_won()
        else:
            message = f"You lost! It was {user.current_guess}!"
            user.set_current_streak(0)
        user.increment_played()
        await ctx.send(f"{message}\nCurrent streak is {user.current_streak}")
        user.current_guess = None
        return

    @commands.command("Ladder")
    async def ladder(self, ctx):
        ranking_db = get_ranking_db()
        ranking = sorted(ranking_db.all(), key=lambda x: x["won"]/x["played"] if x["played"] else 0)
        message = ""
        for rank in ranking:
            winrate = (rank['won']*100)//rank['played'] if rank["played"] else 0
            _message = f"{rank['name']} | {rank['best_streak']} | {winrate}"
            message += _message + "\n"
        if message:
            await ctx.send(message)

def setup(bot):
    bot.add_cog(Markov(bot))