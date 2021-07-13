from discord.ext import commands, tasks
from logger import Logger, LogType
from discord import Embed, Colour
from config import mongodb_url
from discord.utils import get
from user import User
import pymongo
import time
import re


class Role_Expiration:
    def __init__(self, role_id, duration=None, remove_timestamp=None):
        self.role_id = role_id
        if remove_timestamp is None:
            self.remove_timestamp = int(time.time()) + duration * 3600 * 24
            Roles_DB.add_expiration(self.role_id, self.remove_timestamp)
        if duration is None:
            self.remove_timestamp = remove_timestamp
    

    async def remove(self):
        role = get(User.guild_donbass.roles, id=self.role_id)
        await role.delete()
        Roles_DB.remove_expiration(self.role_id)


    @classmethod
    def from_dict(cls, dict):
        return cls(dict['role_id'], remove_timestamp=dict['remove_timestamp'])


class Roles_DB:
    @staticmethod
    def add_expiration(role_id, remove_timestamp):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        role_expirations = db.role_expirations
        role_expirations.insert_one({'role_id': role_id, 'remove_timestamp': remove_timestamp})
        client.close()


    @staticmethod
    def remove_expiration(role_id):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        role_expirations = db.role_expirations
        role_expirations.delete_one({'role_id':role_id})
        client.close()


    @staticmethod
    def get_expirations():
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        role_expirations = db.role_expirations
        expirations = role_expirations.find()
        exp_list = list()
        for expiration in expirations:
            del expiration['_id']
            exp_list.append(expiration)
        return exp_list

        
class Roles_Cog(commands.Cog):
    def __init__(self, bot):
        # pylint: disable=no-member
        self.roles = {
            0:get(User.guild_donbass.roles, id=618485960480522275),
            5:get(User.guild_donbass.roles, id=747025900574605353),
            15:get(User.guild_donbass.roles, id=771507071543672883),
            50:get(User.guild_donbass.roles, id=796414409513369620),
            150:get(User.guild_donbass.roles, id=796415065951305790),
            250:get(User.guild_donbass.roles, id=747026680081678366),
        }
        self.bot = bot
        self.checker.start()


    def cog_unload(self):
        # pylint: disable=no-member
        self.checker.cancel()


    @tasks.loop(seconds=600)
    async def checker(self):
        def normalize_voice_online(online):
            online = online // 3600
            for hour_mark in (250, 150, 50, 15, 5, 0):
                if online >= hour_mark:
                    return hour_mark
        #niger_role = get(User.guild_donbass.roles, id=747025900574605353 )
        #who_role = get(User.guild_donbass.roles, id=618485960480522275)
        roles = self.roles.values()
        for member in User.guild_donbass.members:
            cur_voice_online = normalize_voice_online(User.local_user_list[member.id].voice_online)
            if self.roles[cur_voice_online] in member.roles:
                continue
            await member.remove_roles(*roles)
            await member.add_roles(self.roles[cur_voice_online])
        for exp in Roles_DB.get_expirations():
            curtime = time.time()
            expiration = Role_Expiration.from_dict(exp)
            if curtime >= expiration.remove_timestamp:
                await expiration.remove()



    @commands.command()
    async def buy_role(self, ctx, days, color, *, name):
        if re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', color) is None:
            return await ctx.send('Некорректный код цвета')
        try:
            days = int(days)
        except:
            return await ctx.send(f'<@{ctx.author.id}>, Ошибка. Количество дней должно быть числом')
        if days <= 0:
            return await ctx.send(f'<@{ctx.author.id}>, Ошибка. Некорректное число дней')
        if User.local_user_list[ctx.author.id].balance < days * 100:
            return await ctx.send(f'<@{ctx.author.id}>, Ошибка. Недостаточно средств')
        if name == 'admin':
            return await ctx.send(f'<@{ctx.author.id}>, Ошибка. Некорректное название роли')
        if color == '#000000':
            color = '#000001'
        color = color.replace('#', '')
        color = Colour(value=int(color, 16))
        new_role = await User.guild_donbass.create_role(name=name, colour=color, hoist=False, mentionable=True)
        Role_Expiration(new_role.id, duration=days)
        await Logger.Log(LogType.INFO, f'User {ctx.author.id} bought custom role for {days} days')
        await User.local_user_list[ctx.author.id].decrease_balance(days * 100)
        await User.guild_donbass.edit_role_positions({new_role:len(User.guild_donbass.roles) - 4})
        await ctx.author.add_roles(new_role)
        await ctx.send(f'<@{ctx.author.id}>, вы успешно приобрели роль. С вашего счёта списано {days*100} <:donbass:750673857018462319>донбасс-коинов')