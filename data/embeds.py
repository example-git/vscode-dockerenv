import discord
import discord.ext
#https://cog-creators.github.io/discord-embed-sandbox/


debugembed = discord.Embed(title="Debugger Info", color=0x000000)
debugembed.set_thumbnail(url="https://i.imgur.com/WUymNPF.png")
debugembed.add_field(name="0 - No debugging", value="disables all debuggers", inline=False)
debugembed.add_field(name="1 - Command Debugging", value="only enables console debuggers for certain commands and gpt2 gens", inline=False)
debugembed.add_field(name="2 - Listener Debugging", value="enables listener debugging (annoying)", inline=False)
debugembed.add_field(name="3 - All debugging", value="Enables BOTH", inline=False)
#await ctx.send(embed=debugembed)