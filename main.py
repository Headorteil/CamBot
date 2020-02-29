#! /usr/bin/python3

from discord import File, Embed
from discord.ext import commands
from discord.utils import find
from io import BytesIO
from aiohttp_requests import requests
import asyncio
import aiohttp


from config import *
from token_value import token


class CamBot():
    def __init__(self):
        self.prefix = prefix
        self.bot = commands.Bot(command_prefix=self.prefix)

    async def auto_send_occupied(self, occupied):
        chann = find(lambda r: r.name == news_channel,
                     self.bot.get_all_channels())
        if occupied:
            e = Embed(title=occupied_news)
            await chann.send(embed=e)
        else:
            e = Embed(title=empty_news)
            await chann.send(embed=e)

    def catch(self):

        @self.bot.event
        async def on_ready():
            task = asyncio.create_task(check_occupied(self))
            await task

        @self.bot.event
        async def on_command_error(ctx, exc):
            command = ctx.message.content[1:].split(" ")[0]
            if command not in self.bot.commands:
                return
            ctx.message.content = "{pref}help {cmd}".format(pref=self.prefix,
                                                            cmd=command)
            await self.bot.process_commands(ctx.message)

        @self.bot.command()
        async def occupied(ctx):
            """ Tells if there is someone in the room """
            try:
                a = await requests.get(cam_url + occupied_endpoint)
            except aiohttp.client_exceptions.ClientOSError:
                await ctx.send("```{}```".format(error_unreachable))
                return
            a = await a.json()
            if a:
                await ctx.send("```{}```".format(occupied_message))
            else:
                await ctx.send("```{}```".format(empty_message))

        @self.bot.command()
        async def image(ctx):
            """ Send image of the room """
            if find(lambda r: r.name == cam_role, ctx.author.roles) is None:
                await ctx.send("```{}```".format(image_error_role))
                return
            if str(ctx.channel) != cam_channel:
                await ctx.send("```{}```".format(image_error_channel))
                return
            try:
                a = await requests.get(cam_url+image_endpoint)
            except aiohttp.client_exceptions.ClientOSError:
                await ctx.send("```{}```".format(error_unreachable))
                return
            a = await a.content.read()
            with BytesIO(a) as image:
                await ctx.send(file=File(image, "room.png"))

    def start(self):
        self.catch()
        self.bot.run(token)


async def check_occupied(bot):
    test = 2
    while 1:
        try:
            a = await requests.get(cam_url+occupied_endpoint)
        except aiohttp.client_exceptions.ClientOSError:
            await asyncio.sleep(5)
            continue
        a = await a.json()
        if test != a:
            test = a
            await bot.auto_send_occupied(test)
        await asyncio.sleep(1)


if __name__ == "__main__":
    bot = CamBot()
    bot.start()
