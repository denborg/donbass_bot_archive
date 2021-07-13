import random
import json
from discord import Embed, Colour
from logger import Logger, LogType
from discord.utils import get
from discord.ext import commands
from user import User


CASE_OPENING_MESSAGE_ID = 768155930235502602


class VARS:
    channel = None
    dj_penis_user = None
    denborg_user = None


class coin_case_1:

    name = 'coin_case_1'
    emoji = '<:chest:755800882720800829>'
    display_name = '<:chest:755800882720800829>Coin Case 1'
    cost = 100

    odds = {
        0.644: 100,
        0.0972: 200,
        0.0864: 300,
        0.0756: 400,
        0.0648: 500,
        0.054: 600,
        0.0432: 700,
        0.0324: 800,
        0.0216: 900,
        0.0108: 1000,
    }

    additional_rewards = {
        0.0001: "PUDGE ARCANA"
    }


    @staticmethod
    async def open(user_id, count=1):
        cost = coin_case_1.cost * count
        if User.local_user_list[user_id].balance < cost and User.local_user_list[user_id].inventory.count(coin_case_1.name) < count:
            return await VARS.channel.send(f'<@{user_id}>, в вашем инвентаре нет достаточного кол-ва кейсов или недостаточно донбасс-коинов<:donbass:750673857018462319> для открытия.')
        if User.local_user_list[user_id].inventory.count(coin_case_1.name) >= count:
            User.local_user_list[user_id].remove_from_inventory(coin_case_1.name, count)
        else:
            await User.local_user_list[user_id].decrease_balance(cost) 
        won = 0
        for _ in range(count):
            random_number = random.randint(1,1000000)
            win_amount = 1
            for odd in coin_case_1.odds.keys():
                if random_number <= 1000000 - 1000000*odd:
                    break
                win_amount = coin_case_1.odds[odd]
            win_amount = random.randint(win_amount-99, win_amount)
            if win_amount < 0:
                win_amount *= -1
            won += win_amount
            for item in coin_case_1.additional_rewards.keys():
                if random.random() < item:
                    # await VARS.dj_penis_user.send(f'{user_id} won {coin_case_1.additional_rewards[item]}')
                    await VARS.denborg_user.send(f'{user_id} won {coin_case_1.additional_rewards[item]}')
        await User.local_user_list[user_id].increase_balance(won)
        embed_ts = Embed(color=Colour.from_rgb(255,255,255))
        embed_ts.set_author(name=get(User.guild_donbass.members, id=748892595777962034).name, icon_url=get(User.guild_donbass.members, id=748892595777962034).avatar_url)
        embed_ts.description = f' ⠀\n**{get(User.guild_donbass.members, id=user_id).name} открыл(а)**\n**{count} {coin_case_1.display_name}\n  ⠀\n и получил(а)**\n ⠀\n **<:donbass:750673857018462319>{won}**'
        await Logger.Log(LogType.INFO, f'User {user_id} opened {count} {coin_case_1.name} cases and got {won} coins.')
        await VARS.channel.send(embed=embed_ts)


class Case_openings:
    
    cases = {
        'coin_case_1':coin_case_1
    }

    cases_names = {
        'Coin Case 1': 'coin_case_1'
    }

    @staticmethod
    def init(channel, dj_penis, denborg):
        VARS.channel = channel
        VARS.dj_penis_user = dj_penis
        VARS.denborg_user = denborg


class Cases_Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def open_case(self, ctx, case_name, count=1):
        try:
            count = int(count)
        except:
            return
        if count < 1:
            return
        if case_name not in Case_openings.cases_names.keys():
            return
        await Case_openings.cases[Case_openings.cases_names[case_name]].open(ctx.author.id, int(count))


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        message_id = payload.message_id
        if message_id == CASE_OPENING_MESSAGE_ID:
            if payload.emoji.name == '1️⃣':
                await Case_openings.cases[Case_openings.cases_names['Coin Case 1']].open(payload.user_id, 1)
            if payload.emoji.name == '5️⃣':
                await Case_openings.cases[Case_openings.cases_names['Coin Case 1']].open(payload.user_id, 5)
            if payload.emoji.name == '🔟':
                await Case_openings.cases[Case_openings.cases_names['Coin Case 1']].open(payload.user_id, 10)