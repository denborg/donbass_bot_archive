from discord.utils import get
from discord.ext import commands
from discord import Embed, Colour
from user import User
from asyncio import sleep
from math import ceil
import random


COINFLIP_SIDES = ['sniper' for _ in range(1000)]
COINFLIP_SIDES.extend(['pudge' for _ in range(1000)])
#COINFLIP_SIDES.extend(['boterf' for _ in range(500)])
COINFLIP_SIDES.extend(['stasyan' for _ in range(50)])
random.shuffle(COINFLIP_SIDES)
EMOJIS = {
    'pudge': '<:pudge:750114207797870673>',
    'sniper': '<:sniper:750059784866103347>',
    'stasyan': '<:stas9n:784352078113931275>'
    #'boterf': '<:boterf:832696346564886528>'
}


class Coinflip_double:
    messages = dict()
    results_channel = None
    emojis_channel = None
    info_message_id = None
    numbers = {
        '3️⃣':3,
        '4️⃣':4,
        '5️⃣':5,
        '6️⃣':6,
        '7️⃣':7,
        '8️⃣':8,
        '9️⃣':9,
        '🔟':10
    }

    @staticmethod
    async def execute(user_id, rounds, base_prize):
        cost =  base_prize + ceil((rounds - 1) * (base_prize * 0.8))
        if User.local_user_list[user_id].balance < cost:
            return await Coinflip_double.results_channel.send(f'<@{user_id}>, недостаточно донбасс-коинов')
        win = base_prize
        embed = Embed(color=Colour.dark_gold(), title='Monki Flip')
        embed.set_author(name=get(User.guild_donbass.members, id=user_id).name, icon_url=get(User.guild_donbass.members, id=user_id).avatar_url)
        embed.description = f'''**Rounds:{rounds} 
--**'''
        sent_msg = await Coinflip_double.results_channel.send(embed=embed)
        for round_n in range(rounds):
            await sleep(1)
            ending = ''
            if round_n % 10 == 1:
                ending = 'st'
            elif round_n % 10 == 2:
                ending = 'nd'
            elif round_n % 10 == 3:
                ending = 'rd'
            else:
                ending = 'th'
            number = random.randint(1, 100)
            if number < 50:
                embed.add_field(name='\u200B', value=f'{round_n+1}{ending} toss  -  🔴', inline=False)
                await sent_msg.edit(embed=embed)
                break
            embed.add_field(name='\u200B', value=f'{round_n+1}{ending} toss  -  🟢', inline=False)
            await sent_msg.edit(embed=embed)
            win *= 2
        embed.add_field(name='\nВыигрыш:', value=f'<:donbass:750673857018462319>{win}')
        await sent_msg.edit(embed=embed)
        await User.local_user_list[user_id].decrease_balance(cost)
        await User.local_user_list[user_id].increase_balance(win)
        

    @staticmethod
    async def init(results_channel, emojis_channel, info_message_id):
        Coinflip_double.results_channel = results_channel
        Coinflip_double.emojis_channel = emojis_channel
        Coinflip_double.info_message_id = info_message_id
        msgs = await emojis_channel.history(limit=200).flatten()
        for msg in msgs:
            if not msg.author.bot:
                continue
            Coinflip_double.messages[msg.id] = msg


class Coinflip_solo:
    channel = None
    active_coinflips = dict()
    

    def __init__(self, user_id, bet):
        self.user_id = user_id
        self.bet = bet
        self.executed = False


    async def create(self):
        embed_ts = Embed(color=Colour.dark_gold(), title='Выберите сторону пуджа')
        embed_ts.add_field(name='\u200B', value='<:pudge:750114207797870673>')
        #embed_ts.add_field(name='\u200B', value='\u200B')
        embed_ts.add_field(name='\u200B', value='<:sniper:750059784866103347>')
        #embed_ts.add_field(name='\u200B', value='\u200B')
        #embed_ts.add_field(name='\u200B', value='<:boterf:832696346564886528>')
        sent_message = await Coinflip_solo.channel.send(embed=embed_ts)
        await sent_message.add_reaction('<:pudge:750114207797870673>')
        await sent_message.add_reaction('<:sniper:750059784866103347>')
        #await sent_message.add_reaction('<:boterf:832696346564886528>')
        self.message = sent_message
        Coinflip_solo.active_coinflips[self.message.id] = self


    async def execute(self, picked_side):
        if picked_side not in COINFLIP_SIDES or self.executed:
            return
        self.executed = True
        win_side = random.choice(COINFLIP_SIDES)
        embed_te = Embed(color=Colour.dark_gold(), title='Выберите сторону пуджа')
        if self.bet >= 10000:
            fuck = random.randint(1, 100)
            if fuck <= 13:
                win_side = 'stasyan'
        if self.bet >= 5000:
            fuck = random.randint(1, 100)
            if fuck <= 10:
                win_side = 'stasyan'
        if picked_side == win_side:
            if picked_side == 'boterf':
                await User.local_user_list[self.user_id].increase_balance(self.bet * 4)
            else:
                await User.local_user_list[self.user_id].increase_balance(self.bet)
            embed_te.title = f'Вы выиграли <:donbass:750673857018462319>{self.bet}'
        else:
            await User.local_user_list[self.user_id].decrease_balance(self.bet)
            embed_te.title = f'Вы проиграли <:donbass:750673857018462319>{self.bet}'
        embed_te.description = f' ⠀\n**Вы выбрали {EMOJIS[picked_side]}**\n ⠀\n**Выпал {EMOJIS[win_side]}**'
        await self.message.edit(embed=embed_te)
        Coinflip_solo.active_coinflips.pop(self.message.id)
        


    @staticmethod
    def init(channel):
        Coinflip_solo.channel = channel


class Coinflip_Cog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    
    @commands.command()
    @commands.has_role('admin')
    async def send_double_message(self, ctx, base_prize):
        sent_msg = await ctx.send(f'Выберите кол-во раундов. Базовый приз: <:donbass:750673857018462319>{base_prize}')
        for key in Coinflip_double.numbers.keys():
            await sent_msg.add_reaction(key)
        Coinflip_double.messages[sent_msg.id] = sent_msg


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        message_id = payload.message_id
        if message_id in Coinflip_solo.active_coinflips.keys() and payload.user_id == Coinflip_solo.active_coinflips[message_id].user_id:
            if Coinflip_solo.active_coinflips[message_id].bet <= User.local_user_list[payload.user_id].balance:
                await Coinflip_solo.active_coinflips[message_id].execute(payload.emoji.name)
            else:
                Coinflip_solo.active_coinflips.pop(message_id)
        
        if message_id != Coinflip_double.info_message_id and payload.channel_id == Coinflip_double.emojis_channel.id:
            rounds = Coinflip_double.numbers[payload.emoji.name]
            msg = Coinflip_double.messages[message_id]
            base_prize = int(msg.content.split()[-1].split('>')[1])
            await Coinflip_double.execute(payload.user_id, rounds, base_prize)


