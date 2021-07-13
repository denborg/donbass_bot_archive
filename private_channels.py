from discord.ext import commands
from discord import member as ds_member
from discord.ext.commands.core import command


private_channels = dict()


class Private_Channels_Cog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    
    @commands.command()
    @commands.has_role('admin')
    async def private(self, ctx, *ms):
        members = ctx.message.mentions
        if ctx.author.voice:
            voice_channel = ctx.author.voice.channel
            if not voice_channel.id in private_channels.keys():
                private_channels[voice_channel.id] = [m.id for m in members]
                private_channels[voice_channel.id].append(ctx.author.id)
                for m in voice_channel.members:
                    if not m.id in private_channels[voice_channel.id]:
                        await m.edit(mute=True)
                await ctx.send('The channel you\'re in is now private')
            else:
                await ctx.send('The channel you\'re in is already private')
        else:
            await ctx.send('You must be in a voice channel to use this command')
    

    @commands.command()
    @commands.has_role('admin')
    async def unprivate(self, ctx):
        if ctx.author.voice:
            if ctx.author.voice.channel.id in private_channels.keys():
                del private_channels[ctx.author.voice.channel.id]
                for m in ctx.author.voice.channel.members:
                    await m.edit(mute=False)
            else:
                await ctx.send(f'The channel you\'re in is not private')
        else:
            await ctx.send('You must be in a voice channel to use this command')


    @commands.command()
    @commands.has_role('admin')
    async def allow_speak(self, ctx, *ms):
        members = ctx.message.mentions
        if ctx.author.voice:
            if ctx.author.voice.channel.id in private_channels.keys():
                for member in members:
                    if not member.id in private_channels[ctx.author.voice.channel.id]:
                        private_channels[ctx.author.voice.channel.id].append(member.id)
                        await member.edit(mute=False)
                        await ctx.send(f'{member.name} can now speak in your channel')
                    else:
                        await ctx.send(f'{member.name} can already speak in your channel')
            else:
                await ctx.send(f'The channel you\'re in is not private')
        else:
            await ctx.send(f'You must be in a voice channel to use this command')
    
    
    @commands.command()
    @commands.has_role('admin')
    async def deny_speak(self, ctx, *ms):
        members = ctx.message.mentions
        if ctx.author.voice:
            if ctx.author.voice.channel.id in private_channels.keys():
                for member in members:
                    if member.id in private_channels[ctx.author.voice.channel.id]:
                        private_channels[ctx.author.voice.channel.id].remove(member.id)
                        await member.edit(mute=True)
                        await ctx.send(f'{member.name} can no longer speak in your channel')
                    else:
                        await ctx.send(f'{member.name} wasn\'t allowed to speak in your channel')
            else:
                await ctx.send(f'The channel you\'re in is not private')
        else:
            await ctx.send(f'You must be in a voice channel to use this command')


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and after.channel.id in private_channels.keys() and not after.mute:
            if not member.id in private_channels[after.channel.id]:
                await member.edit(mute=True)
        if ((not after.channel) or (not after.channel.id in private_channels.keys())) and after.mute:
            await member.edit(mute=False)

        # if before.channel and before.channel.id in private_channels.keys() and before.mute:
        #     if after.channel and before.channel == after.channel:
        #         if not member.id in private_channels[after.channel.id] and not after.mute:
        #             await member.edit(mute=True)
        #         return
        #     await member.edit(mute=False)