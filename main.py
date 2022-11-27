# !/usr/bin/env python3
import nest_asyncio
from numpy import int0
from sympy import Q
nest_asyncio.apply()
import argparse
import asyncio
import io
import re
import chat_exporter
import logging
import logging.handlers
import os
from typing import List
import asyncpg
import discord
from aiohttp import ClientSession
from aitextgen.TokenDataset import TokenDataset
from discord.ext import commands
import data.embeds as embeds
import data.helper as helper
import data.lists as lists
from data.helper import (activesettings, opensettings, savesettings,
                         showsettings)

global settingsfile, modelfolder, configname, intents


intents = discord.Intents.all()


def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in {'false', 'f', '0', 'no', 'n', 'html'}:
        return False
    elif value.lower() in {'true', 't', '1', 'yes', 'y'}:
        return True
    raise ValueError(f'{value} is invalid: please use true/false, t/f, 1/0, yes/no, y/n')


def main(cache_name=None):
    """Main function"""
    truedict = {True: 'true', True: 't', True: '1', True: 'yes', True: 'y'}
    falsedict = {False: 'false', False: 'f', False: '0', False: 'no', False: 'n'}
    parser = argparse.ArgumentParser(description="Sam's Dum Chatbot", exit_on_error=False)
    common = parser.add_argument_group('Common Settings', 'Settings that will need to be set everytime if not default')
    aioptions = parser.add_argument_group('AI Options', 'AI Related settings')
    standard = parser.add_argument_group('Standard Options', 'True/False can be set with [true/false, t/f, 1/0, yes/no, y/n] | Non-AI Related settings, will save to specified config after being set once')
    aioptions.add_argument("--test", dest="test", action="store_true", help="Test the currently trained AI model through the terminal prompt without launching the entire bot.")
    aioptions.add_argument("--train", dest="train", action="store_true", help="Trains the model on a file named dataset_cache.tar.gz")
    aioptions.add_argument("--data", dest="cachename", help="set a non default datafile to train on. Default: dataset_cache.tar.gz")
    aioptions.add_argument("--encode", dest="encode", action="store_true", help="encodes dataset.txt into a compressed archive.")
    aioptions.add_argument("--clean", dest="clean", action="store_true", help="clean a rawtext.txt file discord chatlog into something with less junk data | Outputs as dataset.txt")
    aioptions.add_argument("--model", dest="modelfolder", help="Specify a custom folder to use a training model from. Default: trained_model (for ./trained_model)")
    common.add_argument("--config", dest="configfile", default="config", help="Specifies a custom config file | Follow with a config file name (ex.--config main for main.ini)")
    standard.add_argument("--token", dest="token", action="store", help="Follow with a token (--token TOKEN) to set the token for this config (Only needs to be set once, this value will save in the config afterwards)")  
    standard.add_argument("--togpu", type=str_to_bool, nargs='?', const=True, choices={True: dict(truedict), False: dict(falsedict)}, help="Specifies whether or not this config uses a Cuda GPU (Only needs to be set once, this value will save in the config afterwards)")
    standard.add_argument("--debug", type=str_to_bool, nargs='?', const=True, choices={True: dict(truedict), False: dict(falsedict)}, help="Specifies whether or not this config outputs debug logs (Only needs to be set once, this value will save in the config afterwards)")
    try:
        args = parser.parse_args()
    except argparse.ArgumentError:
        print(" ")
        print(f'Arguments are invalid: for --togpu and --debug please use true/false, t/f, 1/0, yes/no, y/n')
        return
    args = parser.parse_args()
    settingsfile = str(f'{args.configfile}.ini')
    helper.configname = args.configfile
    helper.activesettingsvar = settingsfile
    opensettings(settingsfile=settingsfile)
    if args.token:
        savesettings(settingsfile, token=str(args.token))
    if args.togpu is True:
        savesettings(settingsfile, togpu="1")
    if args.togpu is False:
        savesettings(settingsfile, togpu="0")
    if args.debug is True:
        savesettings(settingsfile, debug="1")
    if args.debug is False:
        savesettings(settingsfile, debug="0")
    if args.modelfolder:
        if args.modelfolder != helper.modelfolder:
            savesettings(settingsfile, modelfolder=args.modelfolder)
    if args.cachename:
        if args.cachename != helper.cachename:
            savesettings(settingsfile, cachename=args.cachename)
    opensettings(settingsfile)
    helper.token = helper.token
    helper.activesettingsvar = settingsfile
    global prefix

    if args.test:
        parser.print_help()
        asyncio.run(DiscordClient.testrun())

    elif args.encode:
        from aitextgen.TokenDataset import TokenDataset
        data = TokenDataset("dataset.txt")
        data.save()
        print("Finished encoding the specified file...")
        return

    elif args.clean:

        inputfile = open('rawtext.txt', encoding="utf8")
        outputfile = open('dataset.txt', encoding="utf8", mode="w")
        for line in inputfile.readlines():
            if not line.startswith(lists.badstarts):
                for blocked in lists.badcontains:
                    if (blocked in line):
                        break
                re.sub(lists.replace, " :", line)
                re.sub(lists.replace2, ":", line)
                outputfile.write(line)
        print("Finished cleaning rawtext.txt into dataset.txt file...")

    elif args.train:
        from aitextgen import aitextgen
        ai = aitextgen(model_folder=helper.modelfolder)
        ai.train(f'./{helper.cachename}',
                 line_by_line=False,
                 from_cache=True,
                 num_steps=50000,
                 generate_every=500,
                 save_every=1000,
                 learning_rate=1e-4,
                 fp16=False,  # this setting improves memory efficiency, disable if it causes issues
                 batch_size=1,
                 #restore_from='latest',
                 overwrite=True,
                 num_workers=os.cpu_count()
                 )
    else:
        parser.print_help()
        asyncio.run(mainbot())
        print("Launch with either --test --train --encode --clean or set a token in main.py")
   

class DiscordClient(commands.Bot):
    
    global status, activitylabel, loglevelvar
   
    def __init__(
        self,
        *args,
        initial_extensions: List[str],
        db_pool: asyncpg.Pool,
        web_client: ClientSession,
        **kwargs,
    ):
        self.settingsfile = helper.settingsfile
        super().__init__(*args, **kwargs)
        activesettings()
        self.db_pool = db_pool
        self.web_client = web_client
        self.initial_extensions = initial_extensions
        
    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension("cogs." + extension)

    async def testrun():
        from data.ChatAI import ChatAI
        ai = ChatAI()  # see comment on line 33
        print("Type \"exit!!\" to exit.")
        while True:
            inp = input("> ")
            if (inp == "exit!!"):
                return
            ai.get_bot_response(receivedmessage=inp)
            print("============================+RESPONSE+===========================")
            
    def getactivity():        
        #status conversion stuff
        if helper.activitystatus == 'dnd':
            helper.discstatus = discord.Status.dnd
        if helper.activitystatus == 'online':
            helper.discstatus = discord.Status.online
        if helper.activitystatus == 'idle':
            helper.discstatus = discord.Status.idle
        if helper.activitystatus == 'invisible':
            helper.discstatus = discord.Status.invisible
        if helper.activitytype == 'playing':
            helper.activitylabel = discord.ActivityType.playing
        if helper.activitytype == 'streaming':
            helper.activitylabel = discord.ActivityType.streaming
        if helper.activitytype == 'listening':
            helper.activitylabel = discord.ActivityType.listening
        if helper.activitytype == 'watching':
            helper.activitylabel = discord.ActivityType.watching


async def mainbot() -> object:
    #logger (requires postgresql)
    if helper.debugbool:
        loglevelvar = logging.INFO
    if not helper.debugbool:
        loglevelvar = logging.INFO
    logger = logging.getLogger('discord')
    logger.setLevel(loglevelvar)
    handler = logging.handlers.RotatingFileHandler(
        filename=str(f'botlog_{helper.configname}.log'),
        encoding='utf-8',
        maxBytes=16 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    async with ClientSession() as our_client, asyncpg.create_pool(user='postgres', host='localhost', command_timeout=30) as pool:
        global status, activitylabel
        exts = ['MessageWatcher']
        async with DiscordClient(command_prefix=helper.prefix, db_pool=pool, web_client=our_client, initial_extensions=exts, intents=intents) as bot:
            
            @bot.event
            async def on_ready():
                
                activesettings()
                DiscordClient.getactivity()
                
                activity = discord.Activity(type=helper.activitylabel, name=str(helper.activitytext))
                await bot.change_presence(status=helper.discstatus, activity=activity)
                
                # bot.tree.copy_global_to()
                # await bot.tree.sync()
                
                showsettings()
                print('bot name : ' + bot.user.name)
                print(f'bot ID : {bot.user.id}')
                print('discord version : ' + discord.__version__)
                print("=================================================================")             
            
            @bot.command()
            @commands.is_owner()
            async def save(ctx, channelid: int = None, htmloff: str = 'true'):
                ownerid = int(helper.ownerid)
                owner = bot.get_user(ownerid)
                if htmloff:
                    check = str_to_bool(htmloff)
                if channelid is not None:
                    ogchannel = ctx.channel
                    channel = bot.get_channel(channelid)
                else:
                    channel = ctx.channel
                print(f"Grabbing history for {channel.name}")
                if check:
                    await chat_exporter.quick_text(channel=channel, ogchannel=ogchannel)
                    transcript_file = discord.File(fp=f"./channeltranscripts/transcript-{channel.name}.txt", filename=f"transcript.txt")
                    await ogchannel.send(f"Transcript for {channel}:", file=transcript_file)
                else:
                    await chat_exporter.quick_export(channel=channel)
                    transcript_file = discord.File(fp=f"./channeltranscripts/transcript-{channel.name}.html", filename=f"transcript.html")    
                    finalmessage = await owner.send(f"Transcript for {channel}:", file=transcript_file)
                    url = finalmessage.attachments[0].url
                    embed = discord.Embed(
                        title=(f"Channel Archived!"),
                        description=(
                            f"[Click here to view the transcript of {channel.name}](https://mahto.id/chat-exporter?url={finalmessage.attachments[0].url})"
                        ),
                        colour=discord.Colour.blurple(),
                    )   
                    await ogchannel.send(embed=embed)
                    print(f"Done! grabbing history for {channel.name}")


            @bot.command()
            @commands.is_owner()
            async def savebig(ctx, channelid: int = None, htmloff: str = 'true'):
                await bot.unload_extension("cogs." + 'MessageWatcher')
                if htmloff:
                    check = str_to_bool(htmloff)
                ownerid = int(helper.ownerid)
                owner = bot.get_user(ownerid)
                if channelid is not None:
                    ogchannel = ctx.channel
                    channel = bot.get_channel(channelid)
                else:
                    ogchannel = ctx.channel
                    channel = ctx.channel
                print(f"Grabbing history for {channel.name}.. disabling cogs in the meantime...")
                if check:
                    await chat_exporter.quick_text(channel=channel, ogchannel=ogchannel)
                else:
                    await chat_exporter.quick_export(channel=channel)
                print(f"finished grabbing history for {channel.name}. Re-enabling cogs.")
                await bot.load_extension("cogs." + 'MessageWatcher')
                finalmessage = await owner.send(f"<@{ownerid}> Your transcript for {channel} should be in the bot's directory")
                url = finalmessage.attachments[0].url
                embed = discord.Embed(
                    title=(f"Channel Archived!"),
                    description=(
                        f"[Click here to view the transcript of #{channel.name}](https://mahto.id/chat-exporter?url={url})"
                    ),
                    colour=discord.Colour.blurple(),
                )   
                await owner.send(embed=embed)
                print(f"Done! grabbing history for {channel.name}")
                

                #else:
                #await ogchannel.send(embed=transcript_embed, file=transcript_file)

            # @bot.hybrid_command(with_app_command=True)
            # @discord.ext.commands.is_owner()
            # async def debug(ctx, *, option=None):
            #     ctx.send(content="test", ephemeral=True)
            #     if option == 0:
            #         helper.savesettings(settingsfile, debug="0")
            #         helper.savesettings(settingsfile, listenerdebug="0")
            #         await send_message(content="Disabled all debuggers.", ephemeral=True)
            #     if option == 1:
            #         helper.savesettings(settingsfile, debug="1")
            #         await send_message(content="enabled terminal debugger.", ephemeral=True)
            #     if option == 2:
            #         helper.savesettings(settingsfile, listenerdebug="1")
            #         await send_message(content="enabled listener debugger.", ephemeral=True)
            #     if option == 3:
            #         helper.savesettings(settingsfile, debug="1")
            #         helper.savesettings(settingsfile, listenerdebug="1", ephemeral=True)
            #         await send_message(content="enabled all debuggers.", ephemeral=True)
    

            await bot.start(f"{helper.token}") 


            
            # @debug.autocomplete('option')
            # async def debug_autocomplete(interaction: discord.Interaction, current: int) -> List[app_commands.Choice[int]]:
            #     DebugChoices = ['0', '1', '2', '3']
            #     return [app_commands.Choice(name=DebugChoices, value=option) for option in DebugChoices if current == 0]


if __name__ == "__main__":
    main()