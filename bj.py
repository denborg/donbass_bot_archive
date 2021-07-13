from discord.ext import commands, tasks
from discord import PermissionOverwrite, Embed, channel, player
from discord.utils import get
from enum import Enum
from user import User
import asyncio
import random
import time
# '\u200B'
deck = ['club_10', 'club_2', 'club_3', 'club_4', 'club_5', 'club_6', 'club_7', 'club_8', 'club_9', 'club_A', 'club_J', 'club_K', 'club_Q', 
        'diamond_10', 'diamond_2', 'diamond_3', 'diamond_4', 'diamond_5', 'diamond_6', 'diamond_7', 'diamond_8', 'diamond_9', 'diamond_A', 'diamond_J', 'diamond_K', 'diamond_Q', 
        'heart_10', 'heart_2', 'heart_3', 'heart_4', 'heart_5', 'heart_6', 'heart_7', 'heart_8', 'heart_9', 'heart_A', 'heart_J', 'heart_K', 'heart_Q', 
        'spade_10', 'spade_2', 'spade_3', 'spade_4', 'spade_5', 'spade_6', 'spade_7', 'spade_8', 'spade_9', 'spade_A', 'spade_J', 'spade_K', 'spade_Q']


_CARD_VALUES = {
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J':10, 'Q':10, 'K':10
}

_CARD_BACK = '<:card_back:861620756813971456>'
_CHARS = 'ACDEFGHIJKLMOPQRSTUVWXYZ1234567890'


_CARD_TO_EMOJI = {
    'diamond_4': '<:diamond_4:858643555018997772>', 'club_3': '<:club_3:858643555240902687>', 'diamond_2': '<:diamond_2:858643555312336906>', 'heart_2': '<:heart_2:858643555328589825>', 
    'club_4': '<:club_4:858643555353231432>', 'diamond_A': '<:diamond_A:858643555357818920>', 'diamond_3': '<:diamond_3:858643555358343168>', 'spade_A': '<:spade_A:858643555370795009>', 
    'club_2': '<:club_2:858643555392159744>', 'heart_A': '<:heart_A:858643555400679454>', 'spade_8': '<:spade_8:858643555417194527>', 'spade_2': '<:spade_2:858643555420602368>', 'club_A': '<:club_A:858643555442098186>', 
    'diamond_5': '<:diamond_5:858643555463331870>', 'heart_3': '<:heart_3:858643555501342730>', 'heart_4': '<:heart_4:858643555538305044>', 'spade_4': '<:spade_4:858643555550494720>', 
    'club_5': '<:club_5:858643555550494750>', 'spade_5': '<:spade_5:858643555568582676>', 'club_7': '<:club_7:858643555601874954>', 'diamond_7': '<:diamond_7:858643555622060052>', 
    'spade_6': '<:spade_6:858643555642638346>', 'spade_3': '<:spade_3:858643555672129536>', 'diamond_10': '<:diamond_10:858643555694018600>', 'heart_10': '<:heart_10:858643555706339378>', 
    'diamond_9': '<:diamond_9:858643555747889162>', 'heart_6': '<:heart_6:858643555752083456>', 'heart_5': '<:heart_5:858643555765190667>', 'heart_8': '<:heart_8:858643555769909298>', 
    'club_8': '<:club_8:858643555772530708>', 'diamond_8': '<:diamond_8:858643555811590154>', 'spade_9': '<:spade_9:858643555816177704>', 'heart_7': '<:heart_7:858643555877781544>', 
    'club_6': '<:club_6:858643555919593532>', 'diamond_6': '<:diamond_6:858643555945152523>', 'spade_7': '<:spade_7:858643556058398730>', 'club_9': '<:club_9:858643556168368148>', 
    'club_10': '<:club_10:858643556179902464>', 'diamond_J': '<:diamond_J:858643556239015956>', 'club_J': '<:club_J:858643556242292736>', 'spade_10': '<:spade_10:858643556259725332>', 
    'club_Q': '<:club_Q:858643556263395378>', 'diamond_K': '<:diamond_K:858643556280565780>', 'heart_9': '<:heart_9:858643556309401601>', 'club_K': '<:club_K:858643556343873536>', 
    'diamond_Q': '<:diamond_Q:858643556431429672>', 'heart_Q': '<:heart_Q:858643556449386526>', 'heart_J': '<:heart_J:858643556578230272>', 'spade_J': '<:spade_J:858643556590813204>', 
    'heart_K': '<:heart_K:858647462490013697>', 'spade_Q':'<:spade_Q:858647563187912715>','spade_K':'<:spade_K:858647563078074368>'
}


class Bj_Player():
    def __init__(self, discord=None):
        self.discord = discord
        self.cards = []
        self.score = 0


class _GAME_STATES(Enum):
    INITIATING = 0
    WAITING_FOR_BET = 1
    GIVING_A_CARD = 2
    WAITING_FOR_ACTION = 3
    DEALER_PLAY = 4
    GAME_ENDED = 5


_CURRENT_GAMES = dict()


class Black_Jack_Game:
    @staticmethod
    def in_game(user_id):
        for game in _CURRENT_GAMES.values():
            if user_id == game.player.discord.id:
                return True
        return False


    @staticmethod
    def get_hand_value(hand):
        score = 0
        for card in hand:
            card_v = card.split('_')[1]
            if card_v == 'A':
                if score + 11 <= 21:
                    score += 11
                else:
                    score += 1
            else:
                score += _CARD_VALUES[card_v]
        return score


    def __init__(self, player_ds, id):
        self.player = Bj_Player(discord=player_ds)
        self.dealer = Bj_Player()
        self.deck = list(deck)
        self.id = id
        self.bet = None
        self.channel = None
        self.message = None
        last_action = int(time.time())
        random.shuffle(self.deck)
        self.game_state = _GAME_STATES.INITIATING


    async def create(self):
        overwrites = {
            User.guild_donbass.default_role: PermissionOverwrite(read_messages=False, send_messages=False),
            self.player.discord:PermissionOverwrite(read_messages=True, send_messages=True)
        }
        g_channel = await User.guild_donbass.create_text_channel(name=f'Black Jack - {self.id}', overwrites=overwrites, category=get(User.guild_donbass.categories, id=752060919584129064), position=5)
        self.channel = g_channel
        g_message = await self.channel.send(f'<@!{self.player.discord.id}>\nЧтобы начать игру, отправьте следующим сообщением количество <:donbass:750673857018462319>донбасс-коинов для ставки. Минимальная ставка: <:donbass:750673857018462319>250\nВ сообщении должно быть только число.')
        self.message = g_message
        _CURRENT_GAMES[self.channel.id] = self
        self.last_action = int(time.time())
        self.game_state = _GAME_STATES.WAITING_FOR_BET


    async def start(self, bet):
        self.bet = bet
        self.game_state = _GAME_STATES.GIVING_A_CARD
        self.outcome = None
        self.player.cards.append(self.deck.pop())
        self.player.cards.append(self.deck.pop())
        self.player.score = Black_Jack_Game.get_hand_value(self.player.cards)
        self.dealer.cards.append(self.deck.pop())
        self.dealer.cards.append(self.deck.pop())
        self.dealer.score = Black_Jack_Game.get_hand_value(self.dealer.cards[:1])
        if self.player.score == 21:
            self.game_state = _GAME_STATES.DEALER_PLAY
            await self.play_the_dealer()
        else:
            self.game_state = _GAME_STATES.WAITING_FOR_ACTION
        await self.message.edit(embed=self.get_embed(), content='✅ — Взять ещё карту\n⛔ — Остаться при своих картах')
        await self.message.add_reaction('✅')
        await self.message.add_reaction('⛔')

    
    async def give_card_to_player(self):
        self.game_state = _GAME_STATES.GIVING_A_CARD
        self.player.cards.append(self.deck.pop())
        self.player.score = Black_Jack_Game.get_hand_value(self.player.cards)
        self.game_state = _GAME_STATES.WAITING_FOR_ACTION
        if self.player.score == 21:
            self.game_state = _GAME_STATES.DEALER_PLAY
            await self.play_the_dealer()
        if self.player.score > 21:
            self.dealer.score = Black_Jack_Game.get_hand_value(self.dealer.cards)
            self.game_state = _GAME_STATES.GAME_ENDED
            self.outcome = 'player_lost'
            await self.end_the_game()
            return
        await self.message.edit(embed=self.get_embed())
            

    def give_card_to_dealer(self):
        self.dealer.cards.append(self.deck.pop())
        self.dealer.score = Black_Jack_Game.get_hand_value(self.dealer.cards)


    async def play_the_dealer(self):
        self.game_state = _GAME_STATES.DEALER_PLAY
        self.dealer.score = Black_Jack_Game.get_hand_value(self.dealer.cards)
        await self.message.edit(embed=self.get_embed(), content=None)
        await asyncio.sleep(0.5)
        if self.dealer.score < 21:
            while self.dealer.score < self.player.score:
                self.give_card_to_dealer()
                await asyncio.sleep(0.5)
                await self.message.edit(embed=self.get_embed())
            if self.dealer.score > 21:
                self.outcome = 'player_won'
                await self.end_the_game()
                return
            if self.dealer.score == self.player.score:
                self.outcome = 'draw'
                await self.end_the_game()
                return
            else:
                self.outcome = 'player_lost'
                await self.end_the_game()
                return
        else:
            if self.player.score == 21:
                self.outcome = 'draw'
                await self.end_the_game()
                return
            else:
                self.outcome = 'player_lost'
                await self.end_the_game()
                return


                


    async def end_the_game(self,game_expired=False):
        self.game_state = _GAME_STATES.GAME_ENDED
        if not game_expired:
            try:
                await self.message.edit(embed=self.get_embed(), content=None)
            except:
                pass
            if self.outcome == 'player_won':
                await User.local_user_list[self.player.discord.id].increase_balance(self.bet)
            elif self.outcome == 'player_lost':
                await User.local_user_list[self.player.discord.id].decrease_balance(self.bet)
            await asyncio.sleep(5)
        try:
            await self.channel.delete()
        except:
            pass
        del _CURRENT_GAMES[self.channel.id]
        


    def get_embed(self):
        embed_ts = Embed(title=f'Black Jack {self.id}')
        dealer_cards = [_CARD_TO_EMOJI[card] for card in self.dealer.cards]
        player_cards = [_CARD_TO_EMOJI[card] for card in self.player.cards]
        embed_ts.add_field(name='\u200B',value='\u200B',inline=True)
        if self.game_state == _GAME_STATES.WAITING_FOR_ACTION:
            embed_ts.add_field(name='Dealer cards',value=f'{" ".join(dealer_cards[:1])} {_CARD_BACK} — {self.dealer.score}',inline=True)
        else:
            embed_ts.add_field(name='Dealer cards',value=f'{" ".join(dealer_cards)} — {self.dealer.score}',inline=True)
        embed_ts.add_field(name='\u200B',value='\u200B',inline=False)
        embed_ts.add_field(name='Player cards',value=f'{" ".join(player_cards)} — {self.player.score}',inline=True)
        embed_ts.add_field(name='\u200B',value='\u200B',inline=True)
        if self.game_state == _GAME_STATES.WAITING_FOR_ACTION:
            return embed_ts
        if self.game_state == _GAME_STATES.DEALER_PLAY:
            embed_ts.description = 'Дилер берёт карты'
            return embed_ts
        if self.game_state == _GAME_STATES.GAME_ENDED:
            if self.outcome == 'player_won':
                embed_ts.description = f'Вы выиграли <:donbass:750673857018462319>{self.bet}'
            elif self.outcome == 'player_lost':
                embed_ts.description = f'Вы проиграли <:donbass:750673857018462319>{self.bet}'
            elif self.outcome == 'draw':
                embed_ts.description = 'Ставка возвращена'
            #embed_ts.description = 'Игра закончена'
            return embed_ts

        
        

class Black_Jack_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.expired_checker.start()


    def cog_unload(self):
            self.expired_checker.cancel()


    @tasks.loop(seconds=10.0)
    async def expired_checker(self):
        games_copy = _CURRENT_GAMES.copy()
        for game in games_copy.values():
            current_tstamp = int(time.time())
            if current_tstamp - game.last_action >= 300:
                await game.end_the_game(game_expired=True)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        channel_id = message.channel.id
        if channel_id in _CURRENT_GAMES.keys():
            if _CURRENT_GAMES[channel_id].game_state == _GAME_STATES.WAITING_FOR_BET:
                player = _CURRENT_GAMES[channel_id].player
                try:
                    player_bet = int(message.content)
                    if player_bet < 250 or player_bet > User.local_user_list[player.discord.id].balance:
                        raise ArithmeticError
                except:
                    await message.delete()
                    return
                await message.delete()
                _CURRENT_GAMES[channel_id].bet == _GAME_STATES.INITIATING
                await _CURRENT_GAMES[channel_id].start(player_bet)
    

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        if payload.message_id == 861579386834124820:
            if payload.emoji.name == '🆕' and not Black_Jack_Game.in_game(payload.member.id):
                game_id = ''
                while game_id == '' or game_id in _CURRENT_GAMES:
                    game_id = ''.join([random.choice(_CHARS) for _ in range(4)])
                game = Black_Jack_Game(payload.member, game_id)
                await game.create()
        if payload.channel_id in _CURRENT_GAMES:
            c_game = _CURRENT_GAMES[payload.channel_id]
            if payload.member.id == c_game.player.discord.id and payload.message_id == c_game.message.id and c_game.game_state == _GAME_STATES.WAITING_FOR_ACTION:
                if payload.emoji.name == '✅':
                    await c_game.give_card_to_player()
                elif payload.emoji.name == '⛔':
                    await c_game.play_the_dealer()