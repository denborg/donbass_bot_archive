from db import db_handler


class User:
    local_user_list = dict()
    guild_donbass = None


    def __init__(self, user_id, balance, inventory, msg_count, status, last_voice_join, voice_online):
        self.user_id = user_id
        self.balance = balance
        self.inventory = inventory
        self.msg_count = msg_count
        self.status = status
        self.last_voice_join = last_voice_join
        self.voice_online = voice_online


    def increment_msg_count(self):
        self.msg_count += 1
        db_handler.increment_msg_count(self.user_id)


    async def increase_balance(self, value):
        await db_handler.increase_balance(self.user_id, value)
        self.balance += value


    async def decrease_balance(self, value):
        await db_handler.decrease_balance(self.user_id, value)
        self.balance -= value


    async def transfer_coins(self, dest_user_id, value):
        await self.decrease_balance(value)
        await User.local_user_list[dest_user_id].increase_balance(value)


    async def set_balance(self, value):
        await db_handler.set_balance(self.user_id, value)
        self.balance = value

    
    def add_to_inventory(self, item, count=1):
        for _ in range(count):
            self.inventory.append(item)
        db_handler.add_item_to_inventory(self.user_id, [item for i in range(count)])


    def remove_from_inventory(self, item, count=1):
        for _ in range(count):
            self.inventory.remove(item)
        db_handler.remove_item_from_inventory(self.user_id, item, count)


    def set_status(self, value):
        db_handler.set_status(self.user_id, value)
        self.status = value

    
    def set_last_voice_join(self, value):
        db_handler.set_last_voice_join(self.user_id, value)
        self.last_voice_join = value


    def set_voice_online(self, value):
        db_handler.set_voice_online(self.user_id, value)
        self.voice_online = value


    @staticmethod
    async def load_users_to_local_list(guild):
        User.guild_donbass = guild
        users_in_db = db_handler.get_all_users()
        for user in guild.members:
            if user.id in users_in_db.keys():
                User.local_user_list[user.id] = User.from_dict(users_in_db[user.id])
                continue
            user_duct = await db_handler.get_user_by_id(user.id)
            user_obj = User.from_dict(user_duct)
            User.local_user_list[user.id] = user_obj


    @staticmethod
    def get_top_users_by_voice_online(count=10):
        users = db_handler.get_top_by_voice_online(count)
        to_return = []
        for user in users:
            to_return.append(User.from_dict(user))
        return to_return


    @staticmethod
    def get_top_users_by_messages(count=10):
        users = db_handler.get_top_by_messages(count)
        to_return = []
        for user in users:
            to_return.append(User.from_dict(user))
        return to_return


    @staticmethod
    def get_top_users_by_balance(count=10):
        users = db_handler.get_top_by_balance(count)
        to_return = []
        for user in users:
            to_return.append(User.from_dict(user))
        return to_return


    @staticmethod
    def add_to_everyones_inventory(item):
        for user in User.local_user_list.values():
            user.inventory.append(item)
        db_handler.add_to_everyones_inventory(item)


    @staticmethod
    async def new_user(user_id):
        await db_handler.add_user(user_id)
        User.local_user_list[user_id] = User(user_id, db_handler._DEFAULT_BALANCE, [], 1, 'Команда - "/status"', 0, 0)


    @classmethod
    def from_dict(cls, dict):
        return cls(dict['id'], dict['balance'], dict['inventory'], dict['msg_count'], dict['status'], dict['last_voice_join'], dict['voice_online'])