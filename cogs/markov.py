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
        self.bot.add_command(commands.Command(self.get_skip(), name="Je passe"))

    def get_line_func(self, name):
        async def _get_line(ctx):
            sentence, _name = self.get_line(name)
            await ctx.send(f"> {sentence}\n{_name}")
        return _get_line

    def get_skip(self):
        async def _skip(ctx):
            await self.skip(ctx)
            return
        return _skip

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
            sentence += f"\n{markov_chain.generate_sentence()}"
        return sentence, name

    @commands.command("Guess")
    async def guess(self, ctx):
        if self.bot.custom_users.get(ctx.author).current_guess is not None:
            await ctx.send("Game already in progress...")
        else:
            current_guessing = choice(list(self.bot.markov_chains.keys()))
            sentence, name = self.get_line(current_guessing)
            self.bot.custom_users.get(ctx.author).current_guess = name
            self.bot.custom_users.get(ctx.author).current_sentence = sentence

        sentence = self.bot.custom_users.get(ctx.author).current_sentence
        name = self.bot.custom_users.get(ctx.author).current_guess
        embed = discord.Embed(color=0x670097)
        print(name)
        embed.add_field(name="Guess who could have said", value=f"*{sentence}*")
        await ctx.send(embed=embed)

    @commands.command("Users")
    async def get_guess_list(self, ctx):
        await ctx.send(' - ' + '\n- '.join(self.bot.markov_chains.keys()))

    async def try_guess(self, name: str, ctx):
        user = self.bot.custom_users.get(ctx.author)
        if name.casefold() != ctx.message.content.strip().casefold():
            # Avoid false positive
            return
        if user.current_guess is None:
            return
        embed = discord.Embed()
        if name == user.current_guess:
            embed.add_field(name="Congratulations!", value=f"You guessed {name}!", inline=False)
            embed.colour = 0x00d300
            user.set_current_streak(user.current_streak + 1)
            user.increment_won()
        else:
            embed.add_field(name="You lost!", value=f"It was {user.current_guess}!", inline=False)
            embed.colour = 0xe30000
            user.set_current_streak(0)
        user.increment_played()
        embed.add_field(name="Current streak", value=str(user.current_streak), inline=False)
        await ctx.send(embed=embed)
        user.current_guess = None
        user.current_sentence = None
        return

    @commands.command("Ladder")
    async def ladder(self, ctx):
        ranking_db = get_ranking_db()
        ranking = sorted(ranking_db.all(), key=lambda x: x["won"]/x["played"] if x["played"] else 0, reverse=True)
        if not ranking:
            return
        embed = discord.Embed(title="Ladder", description="Ranking: best streak, winrate, played", color=0x00b4d4)
        for rank in ranking:
            winrate = (rank['won']*100)//rank['played'] if rank["played"] else 0
            embed.add_field(name=rank['name'], value=f"{rank['best_streak']} | {winrate}% | {rank['played']}", inline=False)
        await ctx.send(embed=embed)

    @commands.command("Skip")
    async def skip(self, ctx):
        user = self.bot.custom_users.get(ctx.author)
        if user.current_guess is None:
            return
        embed = discord.Embed()
        embed.add_field(name="You lost!", value=f"It was {user.current_guess}!", inline=False)
        embed.colour = 0xe30000
        user.set_current_streak(0)
        user.increment_played()
        embed.add_field(name="Current streak", value=str(user.current_streak), inline=False)
        await ctx.send(embed=embed)
        user.current_guess = None
        user.current_sentence = None





def setup(bot):
    bot.add_cog(Markov(bot))