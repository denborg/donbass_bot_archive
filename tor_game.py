from enum import Enum
from jb_games import Participant
from jb_games import Spectator
from discord.utils import get
from discord.ext import commands
from discord import PermissionOverwrite
from discord import Embed
from random import choice
from random import shuffle
from user import User
import time


class Player:
    def __init__(self, ds_obj, ):
        self.ds_obj = ds_obj
        self.score = 0
        self.round_1_truth = None
        self.round_1_current_lie = None
        self.round_2_truth = None
        self.round_2_lie = None


class Game:
    def __init__(self, host):
        self.players = [Player(host)]
        self.spectators = list()
        
        



        
class TOR_Cog(commands.Cog):
    def __init__(self, bot, games_channel):
        self.bot = bot
        self.channel = games_channel


    @commands.Cog.listener()
    async def on_message(self, message):
        print(message.content)
        game_info = is_in_game(message.author.id)
        if game_info[0]:
            game = game_info[1]
            if game.game_stage == TOR_Game._GAME_STAGES.ROUND_1:
                if game.game_state == TOR_Game._GAME_STATES.WAITING_FOR_TRUTH_INPUT:
                    if not game.participants[message.author.id].r1_a:
                        game.participants[message.author.id].set_r1_true_answer(message.content)
                        new_emb = game.round_1_embed()
                        await game.game_message.edit(embed=new_emb)
                        if game.all_truths_sent():
                            await game.start_lying_phase()
                if game.game_state == TOR_Game._GAME_STATES.WAITING_FOR_LIE_INPUT:
                    if not game.participants[message.author.id].r1_lie:
                        game.participants[message.author.id].set_r1_lie(message.content)
                        game.round_1_lies.append(Lie(message.author.id, message.content))
                        new_emb = game.round_1_embed()
                        await game.game_message.edit(embed=new_emb)


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            user_id = payload.member.id
            if payload.member.bot:
                return
        except:
            return
        #GAME CREATION
        if payload.emoji.name == '🆕' and not is_in_game(user_id)[0] and payload.channel_id == self.channel.id:
            g_id = ''
            while g_id == '' or g_id in _ACTIVE_GAMES:
                g_id = ''.join([chr(choice(_ASCII_CODES)) for _ in range(4)])
            overwrites = {
                User.guild_donbass.default_role: PermissionOverwrite(read_messages=False, send_messages=False),
                payload.member:PermissionOverwrite(read_messages=True)
            }
            g_channel = await User.guild_donbass.create_text_channel(name=f'Truth Or Lie - {g_id}', overwrites=overwrites, category=get(User.guild_donbass.categories, id=832191407459794954))
            join_embed = Embed(title=f'Игра {g_id}', description='Нажмите на эможу чтобы присоединиться', colour=14607435)
            join_embed.set_author(name='Jackbox discord clone', icon_url='http://denborg.ru/tor_logo.png')
            join_embed.set_footer(text='\\/ \\/ \\/ \\/')
            j_message = await self.channel.send(embed=join_embed)
            await j_message.add_reaction('🚪')
            game_embed = TOR_Game.lobby_embed(g_id, None, 0, payload.member.name)
            g_message = await g_channel.send(embed=game_embed)
            await g_message.add_reaction('✅')
            game = TOR_Game(user_id, g_message, g_channel, j_message, g_id, payload.member.name)
            _ACTIVE_GAMES[g_id] = game
        #JOINING GAME
        if payload.emoji.name == '🚪' and not is_in_game(user_id)[0] and payload.channel_id == self.channel.id:
            j_msg = await self.channel.fetch_message(payload.message_id)
            g_id = j_msg.embeds[0].title.split()[1]
            await _ACTIVE_GAMES[g_id].add_player(user_id, payload.member.name)
        #STARTING GAME
        if payload.emoji.name == '✅' and get(User.guild_donbass.channels, id=payload.channel_id).category_id == 832191407459794954 and payload.channel_id != self.channel.id:
            g_id = get(User.guild_donbass.channels, id=payload.channel_id).name.split('-')[3].upper()
            if _ACTIVE_GAMES[g_id].game_stage == TOR_Game._GAME_STAGES.LOBBY and _ACTIVE_GAMES[g_id].game_leader.discord_id == user_id:
                await _ACTIVE_GAMES[g_id].start_the_game()

