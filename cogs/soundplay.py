import asyncio
import os

import discord
import youtube_dl
from discord.ext import commands


class Soundplay(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command(pass_context=True, name="m!list")
    async def listTags(self, ctx):
        tags = [tag.split('.')[0] for tag in os.listdir("sounds")]
        await ctx.send(' - ' + '\n- '.join(tags))

    @commands.command(pass_context=True, name="kctoa")
    async def leave(self, ctx):
        voice = None
        for vc in self.bot.voice_clients:
            if vc.guild == ctx.channel.guild:
                voice = vc
                break
        if voice and voice.is_connected():
            await voice.disconnect()

    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("You are not connected to a voice channel")
            return
        voice = None
        for vc in self.bot.voice_clients:
            if vc.guild == ctx.channel.guild:
                voice = vc
                break
        if voice:
            if voice.channel == channel:
                return voice
            else:
                try:
                    await voice.disconnect(force=True)
                except:
                    pass
                voice = await channel.connect()
                return voice
        else:
            voice = await channel.connect()
            return voice

    @commands.command(pass_context=True, name="m!t")
    async def playsound(self, ctx, tag):
        """Incredible bougadax"""
        matched_file = None

        # find corresponding file
        for file in os.listdir('sounds'):
            if file.split('.')[0] == tag:
                matched_file = file
                break
        if matched_file is None:
            await ctx.send(f'Tag {tag} not found')
            return

        voice = await self.join(ctx)
        if voice.is_playing():
            voice.source = discord.FFmpegPCMAudio("sounds/"+matched_file)
        else:
            def my_after(error):
                coro = self.leave(ctx)
                fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
                try:
                    fut.result()
                except:
                    # an error happened sending the message
                    pass
            voice.play(
                discord.FFmpegPCMAudio("sounds/"+matched_file),
                after=my_after
            )
        # await voice.disconnect()


    @commands.command(pass_context=True, name="m!stc")
    async def createsound(self, ctx, tag, url):
        """WESH LE PIX"""
        for char in ['-', '.', "'", '"', '/']: # would be better with regex
            tag = tag.replace(char, '')

        # check if tag already exists
        for file in os.listdir('sounds'):
            if file.split('.')[0] == tag:
                await ctx.send('Tag déjà existant')
                return

        # check duration
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'sounds/{tag}.%(ext)s'
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            duration = ydl.extract_info(
                url,
                download=False
            ).get('duration')
            if duration > 60:
                await ctx.send('Pas de vidéo de plus de 60 secs ptit bouf')
                return

        # download
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await ctx.send(f'Download complete, tag {tag} created.')


def setup(bot):
    bot.add_cog(Soundplay(bot))