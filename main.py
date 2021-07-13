#pylint: disable=unused-variable
from discord import File, Embed, Colour, AuditLogAction
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound, MissingRole
from discord.utils import get
from coinflip import Coinflip_solo, Coinflip_double, Coinflip_Cog
from roles import Roles_Cog
from logger import Logger
from logger import LogType
from case import Case_openings, Cases_Cog
from quiz import Quiz, Quiz_Cog
#from tor_game import TOR_Cog
from giveaway import Giveaway
#from private_channels import Private_Channels_Cog
from threading import Timer
from config import bot_token
from user import User
#from rmt import RMT_Cog
from bj import Black_Jack_Cog
from io import BytesIO
import aiohttp
import asyncio
import time
import random
import json
import re
import requests
from bs4 import BeautifulSoup


YANDEX_OAUTH_TOKEN = 'AQAAAABRitudAATuwSBIR9uWVUBFrCaTUh7dA9c'
UKRAINIAN_DAY = False


class donbass:
    guild = None
    free_coins_interval = 100.0
    free_coins_channel = None


class giveaway_checking(commands.Cog):
    # pylint: disable=no-member
    def __init__(self):
        self.update_local_list.start()
        self.checker.start()
        self.give_cases.start()


    def cog_unload(self):
        self.checker.cancel()
        self.give_cases.cancel()
        self.update_local_list.cancel()

    @tasks.loop(seconds=10.0)
    async def checker(self):
        dict_copy = dict(Giveaway.active_giveaways)
        for giveaway in dict_copy.values():
            await giveaway.check()

    
    @tasks.loop(seconds=3600)
    async def give_cases(self):
        await give_free_cases()

    
    @tasks.loop(seconds=30)
    async def update_local_list(self):
        await User.load_users_to_local_list(donbass.guild)


def get_nickname(language):
    if language == 'r':
        pril_url = 'https://inflectonline.ru/'
        headers = {'Origin':'http://sklonenie-slova.ru/', 'Referer':'http://sklonenie-slova.ru/servis/rod', 'X-Requested-With':'XMLHttpRequest'}
        susch_url='http://sklonenie-slova.ru/service/getRodSlova'
        russian_nouns = json.load(open('russian_nouns.json', encoding='utf-8'))
        russian_adjs = json.load(open('russian_adjs.json', encoding='utf-8'))
        noun = random.choice(russian_nouns)
        adj = random.choice(russian_adjs)
        rod_noun = requests.post(susch_url, data={'v':noun}, headers=headers).json()['result']
        adj_page = requests.post('https://inflectonline.ru/search', data={'q':adj})
        soup = BeautifulSoup(adj_page.content, features='lxml')
        try:
            table_contents = list(soup.tbody.children)
        except:
            return get_nickname(language)
        list(table_contents[3].children)[1]
        if 'мужского' in rod_noun:
            adj = str(list(table_contents[3].children)[1])
        elif 'женского' in rod_noun:
            adj = str(list(table_contents[3].children)[3])
        elif 'среднего' in rod_noun:
            adj = str(list(table_contents[3].children)[5])
        else:
            return get_nickname(language)
        return adj[4:-5] + ' ' + noun
    else:
        english_nouns = json.load(open('english_nouns.json', encoding='utf-8'))
        english_adjs = json.load(open('english_adjs.json', encoding='utf-8'))
        return random.choice(english_adjs) + ' ' + random.choice(english_nouns)


async def give_free_cases():
    try:
        last_day = int(open('lastcased', encoding='utf-8').read())
    except:
        open('lastcased','w',encoding='utf-8').write(str(time.localtime()[-2]))
        last_day = time.localtime()[-2]
    curtime = time.localtime()
    cur_day = curtime[-2]
    if cur_day != last_day:
        await regenerate_nicknames_for_everyone()
        User.add_to_everyones_inventory('coin_case_1')
    open('lastcased','w', encoding='utf-8').write(str(cur_day))


async def fuck_up_nicknames():
    for member in donbass.guild.members:
        try:
            await member.edit(nick="﷽"*32)
        except Exception as e:
            await Logger.Log(LogType.ERROR, '\n'.join(('Failed to change nickname', str(e), str(member.id))))


async def regenerate_nicknames_for_everyone():
    yandex_iam_token = ''
    if UKRAINIAN_DAY:
        t_url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
        t_data = {'yandexPassportOauthToken': YANDEX_OAUTH_TOKEN}
        b = requests.post(t_url, json=t_data)
        yandex_iam_token = b.json()['iamToken']
    for member in donbass.guild.members:
        if member.bot:
            await member.edit(nick=None)
            continue
        language = random.choice(['r', 'e'])
        result = ''
        while len(result) == 0 or len(result) >= 32:
            result = get_nickname(language)
        if UKRAINIAN_DAY:
            tr_url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {yandex_iam_token}"}
            tr_data = {"folder_id":"b1g1jjv3vseqbtnrm4gr", "texts":[result], "targetLanguageCode":"uk"}
            tr_req = requests.post(tr_url, json=tr_data, headers=headers)
            result = tr_req.json()['translations'][0]['text']
            time.sleep(0.3)
        try:
            await member.edit(nick=result.title())
        except Exception as e:
            await Logger.Log(LogType.ERROR, '\n'.join(('Failed to change nickname', str(e), str(member.id))))


#

async def spawn_free_coins():
    return
    await asyncio.sleep(random.randint(3600, 10800))
    money_amount = random.randint(50, 150)
    sent_message = await donbass.free_coins_channel.send(f'free {money_amount} money')
    await sent_message.add_reaction(get(donbass.guild.emojis, id=750673857018462319))
    await Logger.Log(LogType.INFO, f'spawned {money_amount} free coins')
    #await spawn_free_coins()


GAME_ROLES = {
        'dota2': 746823927896080447,
        'minecraft': 747024509176905737,
        'custom': '1111',
        'hearthstone': 747033049551732748,
        'csgo': 751010688415170581,
        'donbass': 751401881561071677
    }
bot = commands.Bot(command_prefix='/')
admin_members = (229632740083892226, 204797248452821002)
MEME_ROLE_MESSAGE_ID = 750425714909773964
ROLES_MESSAGE_ID = 751152625830854836
FREE_COINS_CHANNEL_ID = 750771034877198426
GIVEAWAYS_CHANNEL_ID = 751012017816731658
COINFLIP_SOLO_CHANNEL_ID = 752057645547913247
CASES_CHANNEL_ID = 755725903883010129
CASE_OPENING_MESSAGE_ID = 768155930235502602
GIVEAWAYS_JSON_FILENAME = 'giveaways.json'
admin_role = 'admin'
guild_donbass = None
bot_name = None
bot_ava_url = None
logger = None


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    if isinstance(error, MissingRole):
        return
    raise error


@bot.event
async def on_message(message):
    if not message.author.bot:
        User.local_user_list[message.author.id].increment_msg_count()
        if UKRAINIAN_DAY and not '!$' in message.content:
            t_url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
            t_data = {'yandexPassportOauthToken': YANDEX_OAUTH_TOKEN}
            b = requests.post(t_url, json=t_data)
            yandex_iam_token = b.json()['iamToken']
            tr_url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {yandex_iam_token}"}
            tr_data = {"folder_id":"b1g1jjv3vseqbtnrm4gr", "texts":[message.content], "targetLanguageCode":"uk"}
            tr_req = requests.post(tr_url, json=tr_data, headers=headers)
            result = tr_req.json()['translations'][0]['text']
            embed_ts = Embed(color=Colour.from_rgb(255,255,255))
            embed_ts.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
            embed_ts.description = result
            await message.channel.send(embed=embed_ts)
            await message.delete()
        await bot.process_commands(message)


@bot.event
async def on_ready():
    guild_donbass = bot.guilds[0]
    logger = Logger(get(guild_donbass.channels, id=780746879910674442))
    donbass.guild = bot.guilds[0]
    await User.load_users_to_local_list(guild_donbass)
    await Coinflip_double.init(get(donbass.guild.channels, id=772710434582691869), get(donbass.guild.channels, id=772706125240860683), 772746703882420234)
    bot.add_cog(Coinflip_Cog(bot))
    #bot.add_cog(TOR_Cog(bot, get(guild_donbass.channels, id=832191522840510504)))
    bot.add_cog(Cases_Cog(bot))
    bot.add_cog(Roles_Cog(bot))
    #bot.add_cog(RMT_Cog(bot))
    bot.add_cog(Black_Jack_Cog(bot))
    #bot.add_cog(Private_Channels_Cog(bot))
    check_func = lambda m:True
    channel = get(User.guild_donbass.channels, id=784755307619549204)
    await channel.purge(limit=100, check=check_func)
    bot.add_cog(Quiz_Cog(bot))
    donbass.free_coins_channel = get(guild_donbass.channels, id=FREE_COINS_CHANNEL_ID)
    Giveaway.init(get(donbass.guild.channels, id=GIVEAWAYS_CHANNEL_ID))
    Coinflip_solo.init(get(donbass.guild.channels, id=COINFLIP_SOLO_CHANNEL_ID))
    Quiz.init(get(guild_donbass.channels, id=784755307619549204))
    Case_openings.init(get(donbass.guild.channels, id=CASES_CHANNEL_ID), get(donbass.guild.members, id=229632740083892226), get(donbass.guild.members, id=204797248452821002))
    bot_name = get(donbass.guild.members, id=748892595777962034).name
    bot_ava_url = get(donbass.guild.members, id=748892595777962034).avatar_url
    giveaway_checking()
    #loop = asyncio.get_running_loop()
    #loop.run_until_complete(play_music())
    #asyncio.run(play_music())
    await Logger.Log(LogType.INFO, f'Logged in as {bot.user}')
    await spawn_free_coins()


@bot.event
async def on_member_join(member):
    await User.new_user(member.id)
    role = get(donbass.guild.roles, id=618485960480522275)
    role1 = get(donbass.guild.roles, id=853339781038604298)
    await member.add_roles(role)
    if member.id != 391213014189080576:
        await member.add_roles(role1)
    if member.id == 204797248452821002:
        await member.add_roles(get(User.guild_donbass.roles, id=748638191933849640))
    result = get_nickname(random.choice(('russian', 'english')))
    await member.edit(nick=result.title())


@bot.event
async def on_member_remove(member):
    user_id = member.id
    if user_id != 204797248452821002:
        return
    print(user_id, 'removed from guild')
    entries = await User.guild_donbass.audit_logs(limit=10).flatten()
    for entry in entries:
        if entry.action == AuditLogAction.ban and entry.target.id == 204797248452821002:
            try:
                await get(User.guild_donbass.members, id=entry.user.id).ban()
            except:
                pass
            await User.guild_donbass.unban(entry.target)
            invites = await User.guild_donbass.invites()
            print(invites[0].code, 'INVITE CODE')
            await entry.target.send(invites[0].code)
            return


@bot.event
async def on_member_update(before, after):
    for activity in after.activities:
        if activity.name == 'Dota 2':
            role = get(donbass.guild.roles, id=761201701533122580)
            await after.add_roles(role)


@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return
    if (before.channel is None) and (not after.channel is None):
        User.local_user_list[member.id].set_last_voice_join(int(time.time()))
    elif (not before.channel is None) and (after.channel is None):
        cur_online = User.local_user_list[member.id].voice_online
        last_join = User.local_user_list[member.id].last_voice_join
        if last_join != 0:
            User.local_user_list[member.id].set_voice_online(cur_online + (int(time.time()) - last_join))


@bot.command(pass_context=True)
@commands.has_role(admin_role)
async def setbalance(ctx, user_id, value):
    user_id = int(user_id)
    await User.local_user_list[user_id].set_balance(int(value))
    await ctx.message.delete()


@bot.command(pass_context=True)
@commands.has_role(admin_role)
async def getbalance(ctx, user_id):
    user_id = int(user_id)
    balance = User.local_user_list[user_id].balance
    user_nickname = get(ctx.guild.members, id=user_id).display_name
    await ctx.send(f'Баланс {user_nickname}: {balance} донбасс-коинов<:donbass:750673857018462319>')
    await ctx.message.delete()


@bot.command(pass_context=True)
@commands.has_role(admin_role)
async def fuck_nicknames(ctx):
    await fuck_up_nicknames()
    await ctx.message.delete()


@bot.command(pass_context=True)
async def coinflip(ctx, bet):
    if bet == 'all':
        bet = User.local_user_list[ctx.author.id].balance
        if bet <= 0:
            return await ctx.send(f'<@{ctx.author.id}>, некорректная ставка.')
        coinflip = Coinflip_solo(ctx.author.id, int(bet))
        await coinflip.create()
        return
    if int(bet) <= 0:
        return await ctx.send(f'<@{ctx.author.id}>, некорректная ставка.')
    if User.local_user_list[ctx.author.id].balance >= int(bet):
        coinflip = Coinflip_solo(ctx.author.id, int(bet))
        await coinflip.create()
    else:
        await ctx.send(f'<@{ctx.author.id}>, недостаточно донбасс-коинов<:donbass:750673857018462319>. Попробуйте снизить ставку.')


@bot.command(pass_context=True)
@commands.has_role(admin_role)
async def reg(ctx, user, language):
    result = get_nickname(language)
    user_id = ctx.message.mentions[0].id
    await get(User.guild_donbass.members, id=user_id).edit(nick=result.title())
    await ctx.message.delete()


@bot.command(pass_context=True)
@commands.has_role(admin_role)
async def add_to_inventory(ctx, user_id, item, count=1):
    User.local_user_list[int(user_id)].add_to_inventory(item, count=count)


@bot.command(pass_context=True)
@commands.has_role(admin_role)
async def add_role_to_everyone(ctx, role_id):
    for member in User.guild_donbass.members:
        try:
            member.add_roles(get(User.guild_donbass.roles, id=int(role_id)))
        except:
            pass


@bot.command(pass_context=True)
@commands.has_role(admin_role)
async def add_to_everyone(ctx, item):
    User.add_to_everyones_inventory(item)


@bot.command(pass_context=True)
@commands.has_role(admin_role)
async def purge(ctx, count):
    msgs = []
    async for message in ctx.channel.history(limit=int(count)):
        msgs.append(message)
        # await message.delete()
        #time.sleep(0.3)
    await ctx.channel.delete_messages(msgs)


@bot.command(pass_context=True)
async def status(ctx, *, new_status=None):
    if new_status is None:
        User.local_user_list[ctx.author.id].set_status('Команда - "/status"')
        await ctx.send(f'<@{ctx.author.id}>, ваш статус удалён')
    else:
        User.local_user_list[ctx.author.id].set_status(new_status)
        await ctx.send(f'<@{ctx.author.id}>, ваш статус изменён')


@bot.command(pass_context=True)
async def give_role(ctx, user_id, role_id):
    if ctx.author.id != 204797248452821002:
        return
    role = get(User.guild_donbass.roles, id=int(role_id))
    await get(User.guild_donbass.members, id=int(user_id)).add_roles(role)


@bot.command(pass_context=True)
@commands.has_role(admin_role)
async def remove_role(ctx, user_id, role_id):
    role = get(User.guild_donbass.roles, id=int(role_id))
    await get(User.guild_donbass.members, id=int(user_id)).remove_roles(role)


@bot.command(pass_context=True, aliases=['me', 'я', 'профиль'])
async def profile(ctx):
    inventory = User.local_user_list[ctx.author.id].inventory
    status = User.local_user_list[ctx.author.id].status
    msg_count = User.local_user_list[ctx.author.id].msg_count
    balance = User.local_user_list[ctx.author.id].balance
    voice_online = User.local_user_list[ctx.author.id].voice_online
    online_mins = voice_online // 60
    online_hours = online_mins // 60
    online_mins = online_mins % 60
    cases = str(inventory.count('coin_case_1'))
    embed_ts =  Embed(color=ctx.author.color)
    embed_ts.set_author(name=f'{ctx.author.name}', icon_url=ctx.author.avatar_url)
    embed_ts.add_field(name='Статус', value=f'`{status}`', inline=False)
    embed_ts.add_field(name='Войс-онлайн', value=f'🎙️`{str(online_hours)}ч:{str(online_mins)}м`', inline=True)
    embed_ts.add_field(name='Сообщений', value=f'✉️`{str(msg_count)}`', inline=True)
    embed_ts.add_field(name='Баланс', value=f'<:donbass:750673857018462319>`{str(balance)}`')
    embed_ts.add_field(name='Инвентарь', value=f'{Case_openings.cases["coin_case_1"].emoji}`{cases}`', inline=False)
    embed_ts.set_image(url=ctx.author.avatar_url)
    await ctx.send(embed=embed_ts)


@bot.command(pass_context=True)
@commands.has_role(admin_role)
async def ban(ctx, member):
    if ctx.message.mentions[0].id == 204797248452821002 and ctx.author.id != 204797248452821002:
        await ctx.author.ban()
    else:
        await ctx.message.mentions[0].ban()
    await ctx.message.delete()


@bot.command(pass_context=True)
async def motivation(ctx):
    img_url = requests.get('https://inspirobot.me/api?generate=true').text
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as resp:
            buffer = BytesIO(await resp.read())
    await ctx.send(file=File(buffer, filename='motivation.jpg'))


@bot.command(pass_context=True)
@commands.has_role(admin_role)
async def test(ctx):
    role = get(User.guild_donbass.roles, id=853339781038604298)
    for member in User.guild_donbass.members:
        await member.add_roles(role)
    # role = get(User.guild_donbass.roles, id=549923660329123842)
    # await get(User.guild_donbass.members, id=204797248452821002).remove_roles(role)
    # await get(User.guild_donbass.roles, id=778244924243050496).delete()
    # await User.guild_donbass.remove_roles(role)
    # sent_message = await ctx.send('Coin Case 1')
    # await sent_message.add_reaction('1️⃣')
    # await sent_message.add_reaction('5️⃣')
    # await sent_message.add_reaction('🔟')
    # await ctx.message.delete()


@bot.command(pass_context=True)
async def transfer_coins(ctx, user, value):
    try:
        value = int(value)
    except:
        return
    if type(re.match(r'<@!\d+>', user)) is None or value <= 0 or len(ctx.message.mentions) != 1:
        return
    if User.local_user_list[ctx.author.id].balance < value:
        ins_embed = Embed(color=ctx.author.color)
        ins_embed.set_author(name=bot_name, icon_url=bot_ava_url)
        ins_embed.add_field(name=Embed.Empty, value='**Недостаточно донбасс-коинов<:donbass:750673857018462319> для перевода.**')
        return await ctx.send(embed=ins_embed)
    dest_user_id = int(ctx.message.mentions[0].id)
    dest_user_name = get(donbass.guild.members, id=dest_user_id).name
    dest_user_ava = get(donbass.guild.members, id=dest_user_id).avatar_url
    await User.local_user_list[ctx.author.id].transfer_coins(dest_user_id, value)
    embed_ts =  Embed(color=ctx.author.color, title=f'↓↓<:donbass:750673857018462319>{value}')
    embed_ts.set_author(name=f'{ctx.author.name}', icon_url=ctx.author.avatar_url)
    embed_ts.set_footer(text=dest_user_name, icon_url=dest_user_ava)
    await ctx.send(embed=embed_ts)
    


@bot.command(pass_context=True)
async def leaderboard(ctx, count=10):
    voice_top = User.get_top_users_by_voice_online(int(count))
    messages_top = User.get_top_users_by_messages(int(count))
    balance_top = User.get_top_users_by_balance(int(count))
    embed_ts =  Embed(color=ctx.author.color)
    embed_ts.set_author(name='Топ пользователей сервера')
    voice_top_msg = ''
    for index, user in enumerate(voice_top):
        try:
            online_mins = user.voice_online // 60
            online_hours = online_mins // 60
            online_mins = online_mins % 60
            try:
                voice_top_msg += f'{index+1}. {get(ctx.guild.members, id=user.user_id).name}`{online_hours}ч:{online_mins}м`\n'
            except:
                continue
        except:
            await Logger.Log(LogType.ERROR, f'failed to add user {user.user_id} to leaderboard')
    embed_ts.add_field(name='🎙️Войс-онлайн', value=voice_top_msg, inline=True)
    messages_top_msg = ''
    for index, user in enumerate(messages_top):
        try:
            messages_top_msg += f'{index+1}. {get(ctx.guild.members, id=user.user_id).name}`{user.msg_count}`\n'
        except:
            continue
    embed_ts.add_field(name='✉️Сообщений', value=messages_top_msg, inline=True)
    balance_top_msg = ''
    for index, user in enumerate(balance_top):
        try:
            balance_top_msg += f'{index+1}. {get(ctx.guild.members, id=user.user_id).name}<:donbass:750673857018462319>`{user.balance}`\n'
        except:
            continue
    embed_ts.add_field(name='<:donbass:750673857018462319>Баланс', value=balance_top_msg, inline=True)
    await ctx.send(embed=embed_ts)


@bot.command(pass_context=True)
@commands.has_role(admin_role)
async def regen_all(ctx):
    await regenerate_nicknames_for_everyone()
    await ctx.message.delete()


@bot.command(pass_context=True)
@commands.has_role(admin_role)
async def free_coins(ctx):
    money_amount = random.randint(50, 150)
    sent_message = await ctx.send('free money')
    await sent_message.add_reaction(get(donbass.guild.emojis, id=750673857018462319))
    def check(reaction, user):
        return (not user.bot) and (reaction.emoji.name == 'donbass') and (reaction.message.id == sent_message.id)
    await Logger.Log(LogType.INFO, f'Spawned {money_amount} free coins')
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await Logger.Log(LogType.INFO, 'free coins despawnesd')
        await sent_message.delete()
    else:
        await Logger.Log(LogType.INFO, f'User {user.id} got free {money_amount} coins')
        await User.local_user_list[user.id].increase_balance(money_amount)
        await sent_message.delete()


@bot.command(pass_context=True)
async def srat(ctx):
    await ctx.send(file=File('srat.mp4'))


@bot.command(pass_context=True)
@commands.has_role(admin_role)
async def giveaway(ctx, amount, duration):
    new_giveaway = Giveaway(int(amount), int(duration))
    await new_giveaway.start()


@bot.event
async def on_raw_reaction_add(payload):
    member = get(donbass.guild.members, id=payload.user_id)
    if member.bot:
        return
    message_id = payload.message_id
    if message_id == MEME_ROLE_MESSAGE_ID:
        role = get(donbass.guild.roles, id=747029137268539412)
        member = get(donbass.guild.members, id=payload.user_id)
        await member.add_roles(role)
    
    if message_id == ROLES_MESSAGE_ID:
        if payload.emoji.name == 'mark':
            return
        role = get(donbass.guild.roles, id=GAME_ROLES[payload.emoji.name])
        member = get(donbass.guild.members, id=payload.user_id)
        await member.add_roles(role)
    if payload.channel_id == FREE_COINS_CHANNEL_ID:
        msg = await get(donbass.guild.channels, id=FREE_COINS_CHANNEL_ID).fetch_message(message_id)
        money_amount = int(msg.content.split()[1])
        await User.local_user_list[payload.user_id].increase_balance(money_amount)
        await Logger.Log(LogType.INFO, f'User {payload.user_id} got {money_amount} free coins')
        await msg.delete()
    
    if str(message_id) in Giveaway.active_giveaways.keys():
        await Giveaway.active_giveaways[str(message_id)].add_participant(payload.user_id)


@bot.event
async def on_raw_reaction_remove(payload):
    message_id = payload.message_id
    if message_id == MEME_ROLE_MESSAGE_ID:
        role = get(donbass.guild.roles, id=747029137268539412)
        member = get(donbass.guild.members, id=payload.user_id)
        await member.remove_roles(role)
    if message_id == ROLES_MESSAGE_ID:
        if payload.emoji.name == 'mark':
            return
        role = get(donbass.guild.roles, id=GAME_ROLES[payload.emoji.name])
        member = get(donbass.guild.members, id=payload.user_id)
        await member.remove_roles(role)

        


bot.run(bot_token)

