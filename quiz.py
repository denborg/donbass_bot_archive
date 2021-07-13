from db import db_handler
from datetime import datetime
from user import User
from discord import Embed, Colour
from logger import Logger, LogType
from discord.utils import get
from time import sleep
from discord.ext import commands, tasks
import asyncio
import requests
import random
import json


class Quiz:
    digits = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣']
    digits_r = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣']
    quizzes = dict()
    revealed = list()
    color = 16766208
    channel = None
    items = dict()
    urls = dict()
    headers = {
        'authority': 'discord.com',
        'accept': 'application/json',
        'accept-language': 'en',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'content-type': 'application/json',
        'origin': 'https://discohook.org',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://discohook.org/',
    }


    def __init__(self, description, message_id, options, right_answer, cost):
        self.message_id = message_id
        self.options = options
        self.right_answer = right_answer
        self.cost = cost
        self.description = description
        self.revealed = False
    

    @staticmethod
    def init(channel):
        Quiz.channel = channel
        Quiz.items = json.loads(open('./quiz/items.json').read())
        Quiz.urls = json.loads(open('./quiz/urls.json').read())



    def set_msg(self, msg):
        self.msg = msg
        Quiz.quizzes[msg.id] = self


    async def reveal(self):
        if self.revealed:
            return
        msg = await Quiz.channel.fetch_message(self.message_id)
        await msg.delete()
        self.revealed = True
        options_embeds = []
        for index, option in enumerate(self.options):
            if option['item_name'] == self.right_answer:
                self.right_answer = Quiz.digits[index]
            cur_embed = dict()
            cur_embed['title'] = f'{Quiz.digits[index]}{option["item_name"]}'
            cur_embed['color'] = Quiz.color
            cur_embed['image'] = {'url':Quiz.urls[option['item_name']]}
            options_embeds.append(cur_embed)
        data = json.dumps({'content':self.description, 'embeds':options_embeds})
        response = requests.post('https://discord.com/api/v8/webhooks/785073484329123891/boHUfwecvf3mvbwlfI-VsfFzs9LYheS5b1kRdC37DxsMYF78Rly1ouWEgxORRXfzrg4l?wait=true', headers=Quiz.headers, data=data)
        message_id = response.json()['id']
        messag = await Quiz.channel.fetch_message(message_id)
        for digit in Quiz.digits:
            await messag.add_reaction(digit)
        return messag
    

    async def check(self, option, user_id):
        if option == self.right_answer:
            await User.local_user_list[user_id].increase_balance(self.cost)
            Quiz.quizzes.pop(self.msg.id)
            Quiz.quizzes.pop(self.message_id)
            await self.msg.delete()
            res_msg = await Quiz.channel.send(f'Верно. Вы получили {self.cost} <:donbass:750673857018462319>донбасс-коинов')
            sleep(5)
            await res_msg.delete()
        else:
            await User.local_user_list[user_id].decrease_balance(self.cost)
            Quiz.quizzes.pop(self.msg.id)
            Quiz.quizzes.pop(self.message_id)
            await self.msg.delete()
            res_msg = await Quiz.channel.send(f'Неверно. Списано {self.cost} <:donbass:750673857018462319>донбасс-коинов')
            sleep(5)
            await res_msg.delete()


class Quiz_Cog(commands.Cog):
    def __init__(self, bot):
        # pylint: disable=no-member
        self.bot = bot
        #self.spawn_quiz.start()

    
    def cog_unload(self):
        # pylint: disable=no-member
        #self.spawn_quiz.cancel()
        pass
 

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return
        message_id = payload.message_id
        if message_id in Quiz.quizzes.keys():
            if payload.emoji.name == '👀':
                revealed_msg = await Quiz.quizzes[message_id].reveal()
                Quiz.quizzes[message_id].set_msg(revealed_msg)
                Quiz.revealed.append(revealed_msg.id)
                def check(reaction, user):
                    return True
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
                except asyncio.TimeoutError:
                    await revealed_msg.delete()
                    Quiz.quizzes.pop(message_id)
                    Quiz.quizzes.pop(revealed_msg.id)
                    Quiz.revealed.remove(revealed_msg.id)
        if message_id in Quiz.revealed:
            await Quiz.quizzes[message_id].check(payload.emoji.name, payload.member.id)
            Quiz.revealed.remove(message_id)


    @commands.command()
    @commands.has_role('admin')
    async def spawn_quizs(self, ctx):
        temp_list = list()
        options = list()
        correct_item = random.choice(list(Quiz.items.keys()))
        temp_list.append(correct_item)
        options.append({'item_name': correct_item, 'url': Quiz.urls[correct_item]})
        desc = Quiz.items[correct_item]
        for _ in range(4):
            item = random.choice(list(Quiz.items.keys()))
            while item in temp_list:
                item = random.choice(list(Quiz.items.keys()))
            options.append({'item_name': item, 'url': Quiz.urls[item]})
        random.shuffle(options)
        sent_msg = await Quiz.channel.send('Unrevealed quiz')
        await sent_msg.add_reaction('👀')
        new_quiz = Quiz(desc, sent_msg.id, options, correct_item, 325)
        Quiz.quizzes[sent_msg.id] = new_quiz


    @tasks.loop(seconds=10800)
    async def spawn_quiz(self):
        temp_list = list()
        options = list()
        correct_item = random.choice(list(Quiz.items.keys()))
        temp_list.append(correct_item)
        options.append({'item_name': correct_item, 'url': Quiz.urls[correct_item]})
        desc = Quiz.items[correct_item]
        for _ in range(4):
            item = random.choice(list(Quiz.items.keys()))
            while item in temp_list:
                item = random.choice(list(Quiz.items.keys()))
            options.append({'item_name': item, 'url': Quiz.urls[item]})
        random.shuffle(options)
        sent_msg = await Quiz.channel.send('Unrevealed quiz')
        await sent_msg.add_reaction('👀')
        new_quiz = Quiz(desc, sent_msg.id, options, correct_item, 325)
        Quiz.quizzes[sent_msg.id] = new_quiz
    

# try:
#                 reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
#             except asyncio.TimeoutError:
#                 await channel.send('👎')
#             else:
#                 await channel.send('👍')