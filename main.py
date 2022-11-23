# !/usr/bin/env python3
import argparse
import asyncio
import logging
import logging.handlers
import os

import discord
from aitextgen.TokenDataset import TokenDataset
from discord.ext import commands

import cogs.helper as helper
from cogs.helper import activesettings
from cogs.helper import opensettings
from cogs.helper import savesettings
from cogs.helper import showsettings

global settingsfile, modelfolder


def main(cache_name=None):
    """Main function"""
    parser = argparse.ArgumentParser(description="Sam's Retarded Chatbot")
    parser.add_argument("--test", dest="test", action="store_true",
                        help="Test model by talking to the AI right in the terminal.")
    parser.add_argument("--train", dest="train", action="store_true",
                        help="Trains the model on a file named dataset_cache.tar.gz")
    parser.add_argument("--data", dest="cachename", default="dataset_cache.tar.gz",
                        help="set a non default datafile to train on")
    parser.add_argument("--encode", dest="encode", action="store_true",
                        help="encode a dataset into a compressed archive.")
    parser.add_argument("--clean", dest="clean", action="store_true",
                        help="clean a rawtext.txt file discord chatlog into something with less junk data")
    parser.add_argument("--model", dest="modelfolder", default="trained_model",
                        help="Specify a custom folder to use a training model from.")
    parser.add_argument("--config", dest="configfile", default="config",
                        help="specifies a custom config file")
    parser.add_argument("--togpu", dest="togpu", action="store_true", default=False,
                        help="clean a rawtext.txt file discord chatlog into something with less junk data")
    args = parser.parse_args()

    settingsfile = str(f'{args.configfile}.ini')
    helper.activesettingsvar = settingsfile
    opensettings(settingsfile=settingsfile)
    if args.togpu:
        savesettings(settingsfile, args.modelfolder, togpu="True")
    if not args.togpu:
        savesettings(settingsfile, args.modelfolder, togpu="0")
    if args.modelfolder != helper.modelfolder:
        savesettings(settingsfile, args.modelfolder)
    if args.cachename != helper.cachename:
        savesettings(settingsfile, args.modelfolder)
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
        asyncio.run(DiscordClient.mainbot())
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

# client.load_extension("cogs.examplewatcher")

# client.run(f"{discordtoken}")


# class BotService(commands.Cog):
# async def setup_hook(self) -> None:
#     await self.load_extension('cogs.examplewatcher')

# This would also be a good place to connect to our database and
# load anything that should be in memory prior to handling events.

class DiscordClient(commands.Bot):

    async def setup_hook(self):
        for f in os.listdir("./cogs"):
            if f.endswith(".py"):
                await self.load_extension("cogs." + f[:-3])

    async def testrun():
        from cogs.ChatAI import ChatAI
        ai = ChatAI(int(helper.togpu))  # see comment on line 33
        print("Type \"exit!!\" to exit.")
        while True:
            inp = input("> ")
            if (inp == "exit!!"):
                return
            print(ai.get_bot_response(receivedmessage=inp))
            print("============================+RESPONSE+===========================")

    async def mainbot() -> object:
        activesettingsvar = helper.activesettingsvar
        activesettings()
        discordtoken = helper.token
        intents = discord.Intents.all()
        client = commands.Bot(command_prefix=helper.prefix, intents=intents)
        logger = logging.getLogger('discord')
        logger.setLevel(logging.DEBUG)

        @client.event
        async def on_ready():
            showsettings()
            print('logged in')
            print('bot name : ' + client.user.name)
            print(f'bot ID : {client.user.id}')
            print('discord version : ' + discord.__version__)
            print("=================================================================")

        handler = logging.handlers.RotatingFileHandler(
            filename='discord.log',
            encoding='utf-8',
            maxBytes=32 * 1024 * 1024,  # 32 MiB
            backupCount=5,  # Rotate through 5 files
        )
        discord.utils.setup_logging(handler=handler, root=False)
        async with client:
            await client.load_extension('cogs.MessageWatcher')
            # await client.load_extension('cogs.ChatAI')
            await client.start(f"{discordtoken}")


if __name__ == "__main__":
    main()
