import nest_asyncio
nest_asyncio.apply()

import asyncio
import datetime
import random
from discord.ext import commands, tasks
from discord.ext.commands import Context
import data.helper as helper
from data.ChatAI import ChatAI, gpt2
from data.helper import activesettings
global processed_input


class MessageWatcher(commands.Cog):
    def __init__(self, bot):
        nest_asyncio.apply()
        notowner = 0
        customstr = 0
        has_mentioned = 0
        response_chance = 0
        activesettings()
        self.count = 0
        self.debug = helper.debug
        self.prefix = helper.prefix
        self.botid = helper.botid
        self.response_chance = helper.responsechance
        self.togpu = helper.togpubool
        self.maxlines = helper.maxlines
        self.channelid = helper.channelid
        self.chat_ai = gpt2
        self.ownerid = int(helper.ownerid)
        self.channelid = helper.channelid
        self.notowner = 'test'
        self.bot = bot
        self.customstr = customstr
        self.notowner = notowner
        self.has_mentioned = has_mentioned
        self.response_chance = helper.responsechance

        @commands.command()
        async def gen(ctx=Context, *, sentence: str = None):
            ctxmessage = ctx.message
            self.ctxmessage = ctxmessage
            self.ctxmessagechannel = ctxmessage.channel
            self.has_mentioned = True
            if ctxmessage.author == self.bot.user:
                return
            if int(ctxmessage.author.id) != int(helper.ownerid):
                self.notowner = True
            else:
                self.notowner = False
            if sentence is not None:
                self.customstr = str(sentence)
                if self.notowner:
                    if int(ctxmessage.channel.id) != int(helper.channelid):
                        return
                    else:
                        customauthorid = int(ctxmessage.author.id)
                        helper.customauthorid = customauthorid
                        asyncio.run(messagecustom(self, ctx=ctxmessage))
                        return
                else:                
                    customauthorid = int(ctxmessage.author.id)
                    helper.customauthorid = customauthorid
                    asyncio.run(messagecustom(self, ctx=ctxmessage))
                    return
            else:
                if self.notowner:
                    if int(ctxmessage.channel.id) != int(helper.channelid):
                        return
                else:
                    try:
                        await ctxmessage.delete()
                    except:
                        print("No permissions to delete the sam's message", flush=True)
                    asyncio.run(messagegen(self, ctx=ctxmessage))
                    return
        self.bot.add_command(gen)

        @commands.command()
        @commands.is_owner()
        async def gentest(ctx=Context, *, number: int = 0):
            print(helper.channelid)
            print(ctx.channel.id)
            print(ctx.author)
            print(self.has_mentioned)
            print(self.bot.user.name)
            print(self.bot.user.discriminator)
            ctxmessage = ctx.message
            if number == 1:
                publictest = True
            else:
                publictest = False
            asyncio.run(messagetest(
                self, ctx=ctxmessage, publictest=publictest))
            try:
                await ctx.message.delete()
            except:
                print("failed to delete message")
        self.bot.add_command(gentest)
        

    @commands.Cog.listener()
    async def on_message(self, ctx: Context) -> None:
        Owner = None
        global settingsfile
        self.has_mentioned = False
        if ctx.author == self.bot.user:
            return
        authorid = ctx.author.id
        ownerid = helper.ownerid
        ctxmessage = ctx
        if helper.listenerdebug == 1:
            print("==========================Bot Triggered at {0:%Y-%m-%d %H:%M:%S}+=========================".format(datetime.datetime.now()), flush=True)
            print(f'MESSAGE AUTHOR: {ctxmessage.author}')
            print(f'MESSAGE CHANNEL: {self.ctxmessagechannel}')
            print(f'{self.response_chance} | {random.random()}')
            if int(ctx.channel.id) != int(helper.channelid):
                print(
                    f'CHANNEL ID:{ctx.channel.id} | BLOCKED CHANNEL: {helper.channelid}')
            else:
                print('CHANNEL ID: PASSED')
            print(f'Mentioned: {self.has_mentioned}')
            print()
        for mention in ctx.mentions:
            if str(mention) == self.bot.user.name + "#" + self.bot.user.discriminator:
                self.has_mentioned = True
                break
        
        if int(authorid) == int(ownerid):
            Owner = True
        self.ctxmessagechannel = ctxmessage.channel
        if Owner and self.has_mentioned:
            asyncio.run(messagegen(self, ctx=ctxmessage))
        else:
            if int(ctxmessage.channel.id) != int(helper.channelid):
                return
            elif float(random.random()) > float(self.response_chance) and self.has_mentioned is False:
                return
            else:
                asyncio.run(messagegen(self, ctx=ctxmessage))
                return
        # Check to see if bot has been mentioned
        # Only respond randomly (or when mentioned), not to every message

  

        


@tasks.loop(count=1)
async def clientsess(self, processed_input):
    ai = ChatAI()
    response = ai.get_bot_response(receivedmessage=processed_input)
    print("============================+RESPONSE+===========================")
    return response


@tasks.loop(count=1)
async def clientcustom(self, processed_input):
    ai = ChatAI()
    response = ai.get_bot_custom(receivedmessage=processed_input)
    print("============================+RESPONSE+===========================")
    return response


@tasks.loop(count=1)
async def messagetest(self, ctx, publictest=False):
    ai = ChatAI()
    channelname = str(ctx.channel.name)
    guildname = str(ctx.guild.name)
    owner = self.bot.get_user(self.ownerid)
    context = ""
    response = ""
    history = ""
    history = [message async for message in ctx.channel.history(limit=6)]
    history.reverse()  # put in right order
    for msg in history:
        if msg.content.startswith(f'{helper.prefix}gentest'):
            continue
        if msg.content.startswith('```'):
            continue
        context += msg.content + "\r\n"
    processed_input = await process_input(context, helper.botid)
    response = ai.get_bot_response(receivedmessage=processed_input)
    testmessage1 = str('```CSS\rGPT2 generation test: {:%m-%d %H:%M:%S}\r'.format(datetime.datetime.now()))
    testmessage2 = str(f'GUILD:   "{guildname}"\rCHANNEL: "#{channelname}"\r```')
    testmessage3 = str(f'```diff\r- Context\r{context[:750]}\r')
    testmessage4 = str(f'- Response\r{response[:750]}\r```')
    report1 = [testmessage1, testmessage2] 
    report2 = [testmessage3, testmessage4]
    message1 = ""
    message2 = ""
    message1 = message1.join(report1)
    message2 = message2.join(report2)
    if publictest:
        await ctx.channel.send(message1)
        await ctx.channel.send(message2)
    await owner.send(message1)
    await owner.send(message2)


@tasks.loop(count=1)
async def messagegen(self, ctx):
    ctxstore = ctx
    final = ""
    context = ""
    response = ""
    history = ""
    history = [message async for message in ctx.channel.history(limit=9)]
    history.reverse()  # put in right order
    for msg in history:
        if msg.content.startswith(f'{helper.prefix}'):
            continue
        if msg.content.startswith('```'):
            continue
        context += msg.content + "\r\n"
    print("==========================Bot Triggered at {0:%Y-%m-%d %H:%M:%S}+=========================".format(
        datetime.datetime.now()), flush=True)
    print(" ", flush=True)
    processed_input = await process_input(context, helper.botid)
    response = await clientsess(self, processed_input)
    postprocess.start(self, response=response, ctx=ctxstore)


@tasks.loop(count=1)
async def messagecustom(self, ctx):
    ctxstore = ctx
    tempstr = self.customstr
    final = ""
    context = ""
    response = ""
    history = ""
    cmdauthor = ctx.author
    history = [message async for message in ctx.channel.history(limit=15)]
    history.reverse()  # put in right order
    for msg in history:
        if int(msg.author.id) == int(cmdauthor.id):
            if msg.content.startswith(self.prefix + "gen"):
                continue
            if msg.content.startswith('```'):
                continue
            context += msg.content + "\r\n"
        if int(msg.author.id) == int(self.botid):
            context += msg.content + "\r\n"
    context += tempstr + "\r\n"
    # Get last n messages, save them to a string to be used as prefix
    print("==========================Bot Triggered at {0:%Y-%m-%d %H:%M:%S}+=========================".format(
        datetime.datetime.now()), flush=True)
    print(" ", flush=True)
    # Process input and generate output@
    processed_input = context
    response = await clientcustom(self, processed_input)
    postprocess.start(self, response=response, ctx=ctxstore)


@tasks.loop(count=1)
async def postprocess(self, response: str, ctx):
    final = response[:2000]
    if self.has_mentioned:
        try:
            await ctx.reply(final)  # sends the response
            self.has_mentioned = False
            return
        except:
            print("failed to reply, sending message normally to user ")
            await self.ctxmessagechannel.send(final)  # sends the response
            self.has_mentioned = False
            return
    else:
        await self.ctxmessagechannel.send(final)  # sends the response
        return


async def process_input(message: str, botid=None) -> str:
    processed_input = message
    return processed_input.replace(("<@!" + str(botid) + ">"), "")


async def setup(bot):
    await bot.add_cog(MessageWatcher(bot))
