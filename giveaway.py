import random
import time
import pytz
import json
from logger import Logger, LogType
from db import db_handler
from datetime import datetime
from user import User


class Giveaway:
    active_giveaways = dict()
    json_filename = None
    channel = None


    def __init__(self, amount, duration):
        self.amount = amount
        self.finish_timestamp = int(time.time()) + duration
        self.duration = duration
        self.finish_date = datetime.fromtimestamp(self.finish_timestamp, pytz.timezone('Europe/Moscow')).strftime('%d.%m.%Y, %H:%M:%S (Moscow Standart Time)')
        self.participants = []
    

    async def start(self):
        sent_message = await Giveaway.channel.send(f'Розыгрыш {self.amount} донбасс-коинов<:donbass:750673857018462319>. Принять участие можно до {self.finish_date}. Текущее кол-во участников: {len(self.participants)}')
        await sent_message.add_reaction('📝')
        self.message_id = str(sent_message.id)
        Giveaway.active_giveaways[str(sent_message.id)] = self
        db_handler.add_giveaway(self)


    async def add_participant(self, user_id):
        if int(time.time()) >= self.finish_timestamp:
            return self.finish()
        if user_id not in self.participants:
            self.participants.append(user_id)
            await self.update_participants_count_in_message()
            Giveaway.update_active_giveaway(self.message_id)
        

    async def update_participants_count_in_message(self):
        message = await Giveaway.channel.fetch_message(self.message_id)
        await message.edit(content=f'Розыгрыш {self.amount} донбасс-коинов<:donbass:750673857018462319>. Принять участие можно до {self.finish_date}. Текущее кол-во участников: {len(self.participants)}')


    async def check(self):
        if int(time.time()) >= self.finish_timestamp:
            await self.finish()


    async def finish(self):
        winner = random.choice(self.participants)
        await User.local_user_list[winner].increase_balance(self.amount)
        message = await Giveaway.channel.fetch_message(self.message_id)
        await message.edit(content=f'Розыгрыш {self.amount} донбасс-коинов<:donbass:750673857018462319>. Принять участие можно до {self.finish_date}. Кол-во участников: {len(self.participants)}\n\nРозыгрыш завершен. Победитель: <@{winner}>. Начислено {self.amount} донбасс-коинов<:donbass:750673857018462319>.')
        await Logger.Log(LogType.INFO, f'User {winner} won {self.amount} coins in a giveaway')
        Giveaway.active_giveaways.pop(self.message_id)
        db_handler.remove_giveaway(self)


    def to_dict(self):
        return self.__dict__


    @staticmethod
    def init(channel):
        Giveaway.channel = channel
        Giveaway.load_giveaways()


    @staticmethod
    def update_active_giveaway(message_id):
        db_handler.update_giveaway(Giveaway.active_giveaways[message_id])
    

    @staticmethod
    def load_giveaways():
        giveaways = db_handler.get_giveaways()
        for giveaway in giveaways:
            Giveaway.active_giveaways[giveaway['message_id']] = Giveaway.from_dict(giveaway)
    

    @classmethod
    def from_dict(cls, dict):
        to_return = cls(dict['amount'], dict['duration'])
        to_return.finish_timestamp = dict['finish_timestamp']
        to_return.finish_date = dict['finish_date']
        to_return.participants = dict['participants']
        to_return.message_id = dict['message_id']
        return to_return