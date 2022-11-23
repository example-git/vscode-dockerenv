import datetime
import random

import discord
from discord.ext import commands, tasks

import cogs.helper as helper
from cogs.ChatAI import ChatAI
from cogs.helper import activesettings

activesettings()
count = 0
ctx = 0
intents = discord.Intents.all()
client = commands.Bot(command_prefix=helper.prefix, intents=intents)


class MessageWatcher(commands.Cog):
    notsam = 0
    customstr = 0
    testflag = 0
    has_mentioned = 0

    def __init__(self, client2: client):
        model_name = "355M"  # Overwrite with set_model_name()
        super().__init__()
        self.client = client2
        global processed_input
        processed_input = ''
        self.settingsfile = helper.settingsfile
        activesettings()
        self.debug = int(helper.debug)
        self.prefix = helper.prefix
        self.botid = helper.botid
        self.response_chance = helper.responsechance
        self.togpu = helper.togpu
        self.maxlines = helper.maxlines
        self.channelid = helper.channelid
        self.chat_ai = ChatAI()
        self.ownerid = int(helper.ownerid)
        self.count = count
        self.channelid = helper.channelid
        self.processed_input = processed_input

    @tasks.loop(count=1)
    async def clientsess(self, processed_input=None, togpu=None):
        response = self.chat_ai.get_bot_response(receivedmessage=processed_input)
        print("============================+RESPONSE+===========================")
        return response
    
    @tasks.loop(count=1)
    async def clientcustom(self, processed_input=None, togpu=None):
        response = self.chat_ai.get_bot_custom(receivedmessage=processed_input)
        print("============================+RESPONSE+===========================")
        return response

    @tasks.loop(count=1)
    async def postprocess(self, response: str, ctx):
        final = response[:2000]
        if self.has_mentioned:
            try:
                await ctx.reply(final)  # sends the response
                self.has_mentioned = False
                return
            except:
                print("failed to reply, sending message normally to user " + str(ctx.author.id), flush=True)
                await ctx.channel.send(final)  # sends the response
                self.has_mentioned = False
                return
        else:
            await ctx.channel.send(final)  # sends the response
            return

    @tasks.loop(count=1)
    async def messagegen(self, ctx: discord.Message):
        final = ""
        context = ""
        response = ""
        history = ""
        history = [message async for message in ctx.channel.history(limit=9)]
        history.reverse()  # put in right order
        #if self.debug == 1:
            #print(history)
        for msg in history:
            # "context" now becomes a big string containing the content only of the last n messages, line-by-line
            if msg.content.startswith("!gen") or msg.content.startswith("e!gen") or msg.content.startswith("$"):
                continue
            context += msg.content + "\r\n"
        # if not msg.startswith("!gen") or msg.startswith("e!gen") or msg.startswith("$"):
        # Print status to console
        print("==========================Bot Triggered at {0:%Y-%m-%d %H:%M:%S}+=========================".format(
            datetime.datetime.now()), flush=True)
        print(" ", flush=True)
        # Process input and generate output
        processed_input = await process_input(context, helper.botid)
        response = await self.clientsess(processed_input)
        self.postprocess.start(response, ctx)

    @tasks.loop(count=1)
    async def messagecustom(self, ctx: discord.Message):
        tempstr = self.customstr
        final = ""
        context = ""
        response = ""
        history = ""
        cmdauthor = self.customauthor
        history = [message async for message in ctx.channel.history(limit=15)]
        history.reverse()  # put in right order
        #if self.debug == 1:
            #print(cmdauthor.id)
            #print(self.botid)
            #print(history)
        for msg in history:
            #print(msg.author.id)
            if msg.author.id == cmdauthor.id:
                if msg.content.startswith(self.prefix + "gen"):
                    continue
                context += msg.content + "\r\n"
            if int(msg.author.id) == int(self.botid):
                context += msg.content + "\r\n"
        context += tempstr + "\r\n"
        # Get last n messages, save them to a string to be used as prefix
        print("==========================Bot Triggered at {0:%Y-%m-%d %H:%M:%S}+=========================".format(
            datetime.datetime.now()), flush=True)
        print(" ", flush=True)
        # Process input and generate output
        processed_input = context
        response = await self.clientcustom(processed_input)
        self.postprocess.start(response, ctx)

    @commands.command()
    async def gen(self, ctx, *, sentence: str = None):
        ctx = ctx.message
        if ctx.author == self.client.user:
            return
        if ctx.author.id != self.ownerid:
            self.notsam = True
        else:
            self.notsam = False
        if sentence is not None:
            self.customstr = str(sentence)
            if self.notsam:
                if ctx.channel.id != helper.channelid:
                    return
                else:
                    self.has_mentioned = True
                    self.customauthor = ctx.author.id
                    self.messagecustom.start(ctx)
                    return
            else:
                self.has_mentioned = True
                self.customauthor = ctx.author
                self.messagecustom.start(ctx)
                return
        else:
            if self.notsam:
                if ctx.channel.id != helper.channelid:
                    return
                    # else:
                    #     self.messagegen.start(ctx)
                    return
            else:
                try:
                    await ctx.delete()
                except:
                    print("No permissions to delete the sam's message", flush=True)
                self.messagegen.start(ctx)
                return

    client.add_command(gen)

    @commands.command()
    async def gentest(self, ctx):
        ctx = ctx.message
        if ctx.author == self.client.user:
            return
        if ctx.author.id != self.ownerid:
            return
        await ctx.delete()
        self.messagegen.start(ctx)
        return

    client.add_command(gentest)

    @commands.Cog.listener()
    async def on_message(self, ctx: discord.Message) -> None:
        global settingsfile
        if ctx.channel.id != int(self.channelid):
            return
        if ctx.author == self.client.user:
            # Skip any messages sent by ourselves so that we don't get stuck in any loops
            return
        # Check to see if bot has been mentioned
        self.has_mentioned = False
        for mention in ctx.mentions:
            if str(mention) == self.client.user.name + "#" + self.client.user.discriminator:
                self.has_mentioned = True
                break
        # Only respond randomly (or when mentioned), not to every message
        if random.random() > float(self.response_chance) and self.has_mentioned is False:
            return
        #    ctx = await self.get_context(message)
        self.messagegen.start(ctx)


async def process_input(message: str, botid=None) -> str:
    processed_input = message
    # Remove bot's @s from input
    return processed_input.replace(("<@!" + str(botid) + ">"), "")


async def setup(client):
    await client.add_cog(MessageWatcher(client))
