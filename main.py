# !/usr/bin/env python3
import argparse
import asyncio
import asyncpg
import logging
import logging.handlers
import os
import discord
from aitextgen.TokenDataset import TokenDataset
from discord.ext import commands
import data.helper as helper
from data.helper import activesettings
from data.helper import opensettings
from data.helper import savesettings
from data.helper import showsettings
from aiohttp import ClientSession
from typing import List, Generator

global settingsfile, modelfolder, configname


def main(cache_name=None):
    """Main function"""
    def str_to_bool(value):
        if isinstance(value, bool):
            return value
        if value.lower() in {'false', 'f', '0', 'no', 'n'}:
            return False
        elif value.lower() in {'true', 't', '1', 'yes', 'y'}:
            return True
        raise ValueError(f'{value} is invalid: please use true/false, t/f, 1/0, yes/no, y/n')
    truedict = {True: 'true', True: 't', True: '1', True: 'yes', True: 'y'}
    falsedict = {False: 'false', False: 'f', False: '0', False: 'no', False: 'n'}
    parser = argparse.ArgumentParser(description="Sam's Dum Chatbot", exit_on_error=False)
    common = parser.add_argument_group('Common Settings', 'Settings that will need to be set everytime if not default')
    aioptions = parser.add_argument_group('AI Options', 'AI Related settings')
    standard = parser.add_argument_group('Standard Options', 'True/False can be set with [true/false, t/f, 1/0, yes/no, y/n] | Non-AI Related settings, will save to specified config after being set once')
    aioptions.add_argument("--test", dest="test", action="store_true",
                        help="Test the currently trained AI model through the terminal prompt without launching the entire bot.")
    aioptions.add_argument("--train", dest="train", action="store_true",
                        help="Trains the model on a file named dataset_cache.tar.gz")
    aioptions.add_argument("--data", dest="cachename", default="dataset_cache.tar.gz",
                        help="set a non default datafile to train on. Default: dataset_cache.tar.gz")
    aioptions.add_argument("--encode", dest="encode", action="store_true",
                        help="encodes dataset.txt into a compressed archive.")
    aioptions.add_argument("--clean", dest="clean", action="store_true",
                        help="clean a rawtext.txt file discord chatlog into something with less junk data | Outputs as dataset.txt")
    aioptions.add_argument("--model", dest="modelfolder", default="trained_model",
                        help="Specify a custom folder to use a training model from. Default: trained_model (for ./trained_model)")
    common.add_argument("--config", dest="configfile", default="config",
                        help="Specifies a custom config file | Follow with a config file name (ex.--config main for main.ini)")
    standard.add_argument("--token", dest="token", action="store",
                        help="Follow with a token (--token TOKEN) to set the token for this config (Only needs to be set once, this value will save in the config afterwards)")  
    standard.add_argument("--togpu", type=str_to_bool, nargs='?', const=True, choices={True: dict(truedict), False: dict(falsedict)},
                        help="Specifies whether or not this config uses a Cuda GPU (Only needs to be set once, this value will save in the config afterwards)")
    standard.add_argument("--debug", type=str_to_bool, nargs='?', const=True, choices={True: dict(truedict), False: dict(falsedict)},
                        help="Specifies whether or not this config outputs debug logs (Only needs to be set once, this value will save in the config afterwards)")
    parser.print_help()
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
    if args.togpu == True:
        savesettings(settingsfile, togpu="1")
    if args.togpu == False:
        savesettings(settingsfile, togpu="0")
    if args.debug == True:
        savesettings(settingsfile, debug="1")
    if args.debug == False:
        savesettings(settingsfile, debug="0")
    if args.modelfolder != helper.modelfolder:
        savesettings(settingsfile, modelfolder=args.modelfolder)
    if args.cachename != helper.cachename:
        savesettings(settingsfile, cachename=args.cachename)
    opensettings(settingsfile)
    helper.token = helper.token
    helper.activesettingsvar = settingsfile

    if args.test:
        asyncio.run(DiscordClient.testrun())

    elif args.encode:
        TokenDataset("dataset.txt", save_cache=True)

    elif args.clean:
        inputfile = open('rawtext.txt', encoding="utf8")
        outputfile = open('dataset.txt', encoding="utf8", mode="x")
        for line in inputfile.readlines():
            if not line.startswith(("[", "\n", "{", "=====", "Guild:", "Channel:", "Topic:", "{Attachments}",
                                    "https://images-ext-1.discordapp.net/external/", "e!", "{Reactions}",)):
                outputfile.write(line)
        # for line in inputfile.readlines():
        # if not line.contains(( "{Attachments}", "https://images-ext-1.discordapp.net/external/", )):
        # outputfile.write(line)

    elif args.train:
        from aitextgen import aitextgen  # lazily import aitextgen. idk if this matters, but i thought it might speed up start times for when you're not training the AI as opposed to having this at the top
        ai = aitextgen(tf_gpt2="355M", to_gpu=helper.togpu)
        ai.train(helper.cachename,
                 line_by_line=False,
                 from_cache=True,
                 # num_steps=30000,
                 # Takes less than an hour on my RTX 3060. Increase if you want, but remember that training can pick up where it left off after this finishes.
                 generate_every=500,
                 save_every=1000,
                 learning_rate=1e-4,
                 fp16=True,  # this setting improves memory efficiency, disable if it causes issues
                 batch_size=1,
                 restore_from='latest',
                 overwrite=True,
                 )
    else:
        asyncio.run(mainbot())
        print("Launch with either --test --train --encode --clean or set a token in main.py")


# def mainbot():
# intents = discord.Intents.all()
# client = commands.Bot(command_prefix=prefix, intents=intents)

# @client.event
# async def on_ready():
# print('logged in')
# print('bot name : ' + client.user.name)
# print(f'bot ID : {client.user.id}')
# print('discord version : ' + discord.__version__)
# global chat_ai
# chat_ai = ChatAI(maxlines, togpu)

# client.load_extension("data.examplewatcher")

# client.run(f"{discordtoken}")


# class BotService(commands.Cog):
# async def setup_hook(self) -> None:
#     await self.load_extension('data.examplewatcher')

# This would also be a good place to connect to our database and
# load anything that should be in memory prior to handling events.

class DiscordClient(commands.Bot):
    def __init__(
        self,
        *args,
        initial_extensions: List[str],
        db_pool: asyncpg.Pool,
        web_client: ClientSession,
        **kwargs,
    ):
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
        ai = ChatAI(int(helper.togpu))  # see comment on line 33
        print("Type \"exit!!\" to exit.")
        while True:
            inp = input("> ")
            if (inp == "exit!!"):
                return
            ai.get_bot_response(receivedmessage=inp)
            print("============================+RESPONSE+===========================")


async def mainbot() -> object:
    logger = logging.getLogger('discord')
    if helper.debug == 1:
        logger.setLevel(logging.DEBUG)
    if helper.debug == 0:
        logger.setLevel(logging.INFO)
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
    #discord.utils.setup_logging(handler=handler, root=False)
    async with ClientSession() as our_client, asyncpg.create_pool(user='postgres', command_timeout=30) as pool:
        exts = ['MessageWatcher']
        async with DiscordClient(command_prefix=helper.prefix, db_pool=pool, web_client=our_client, initial_extensions=exts, intents=discord.Intents.all()) as client:
            @client.event
            async def on_ready():
                showsettings()
                print('logged in')
                print('bot name : ' + client.user.name)
                print(f'bot ID : {client.user.id}')
                print('discord version : ' + discord.__version__)
                print("=================================================================")
            await client.start(f"{helper.token}")



if __name__ == "__main__":
    main()
