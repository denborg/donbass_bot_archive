import pymongo
from config import mongodb_url
from logger import Logger, LogType


class db_handler:
    _DEFAULT_BALANCE = 100


    @staticmethod
    async def set_balance(user_id, value):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        members.update_one({'id':user_id}, {'$set': {'balance':value}})
        client.close()
        await Logger.Log(LogType.INFO, f'Set balance of {user_id} to {value} coins')


    @staticmethod
    async def increase_balance(user_id, value):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        members.update_one({'id':user_id}, {'$inc': {'balance':value}})
        client.close()
        await Logger.Log(LogType.INFO, f'Increased balance of {user_id} by {value} coins')


    @staticmethod
    async def decrease_balance(user_id, value):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        members.update_one({'id':user_id}, {'$inc': {'balance':-value}})
        client.close()
        await Logger.Log(LogType.INFO, f'Decreased balance of {user_id} by {value} coins')
    

    @staticmethod
    async def add_user(user_id):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        try:
            members.insert_one({'id':user_id, 'balance':db_handler._DEFAULT_BALANCE, 'inventory': [], 'msg_count': 1, 'status':'Команда - "/status"', 'last_voice_join': 0, 'voice_online': 0})
        except:
            await Logger.Log(LogType.ERROR, f'{user_id} already exists in database')
        client.close()


    @staticmethod
    async def get_user_by_id(user_id):
        # creates a new user if user with specified id does not exist
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        user = members.find_one({'id': user_id})
        if user is None:
            await db_handler.add_user(user_id)
            user = {'id':user_id, 'balance':db_handler._DEFAULT_BALANCE, 'inventory':[], 'msg_count': 1, 'status': 'Команда - "/status"', 'last_voice_join': 0, 'voice_online': 0}
            return user
        del user['_id']
        client.close()
        return user


    @staticmethod
    def get_inventory(user_id):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        user = members.find_one({'id': user_id})
        client.close()
        return user['inventory']


    @staticmethod
    def has_item_in_inventory(user_id, item):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        user = members.find_one({'id': user_id})
        client.close()
        return item in user['inventory']


    @staticmethod
    def add_to_everyones_inventory(item):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        members.update_many({}, {'$push': {'inventory': item}})


    @staticmethod
    def add_item_to_inventory(user_id, items):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        members.update_one({'id':user_id}, {'$push': {'inventory' :{'$each': items}}})
        client.close()


    @staticmethod
    def get_top_by_voice_online(count=10):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        users = list(members.find({}).limit(count).sort('voice_online', -1))
        return users


    @staticmethod
    def get_top_by_messages(count=10):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        users = list(members.find({}).limit(count).sort('msg_count', -1))
        return users


    @staticmethod
    def get_top_by_balance(count=10):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        users = list(members.find({}).limit(count).sort('balance', -1))
        return users


    @staticmethod
    def remove_item_from_inventory(user_id, item, count=1):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        user = members.find_one({'id': user_id})
        for _ in range(count):
            user['inventory'].remove(item)
        members.update_one({'id':user_id}, {'$set': {'inventory': user['inventory']}})
        client.close()


    @staticmethod
    def increment_msg_count(user_id):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        members.update_one({'id':user_id}, {'$inc':{'msg_count':1}})


    @staticmethod
    def get_status(user_id):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        user = members.find_one({'id': user_id})
        client.close()
        return user['status']


    @staticmethod
    def set_status(user_id, status):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        members.update_one({'id':user_id}, {'$set':{'status':status}})


    @staticmethod
    def set_last_voice_join(user_id, last_voice_join):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        members.update_one({'id':user_id}, {'$set':{'last_voice_join': last_voice_join}})


    @staticmethod
    def add_giveaway(giveaway):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        giveaways = db.giveaways
        giveaways.insert_one(giveaway.to_dict())
        client.close()

    
    @staticmethod
    def update_giveaway(giveaway):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        giveaways = db.giveaways
        giveaways.replace_one({'message_id': giveaway.message_id}, giveaway.to_dict())
        client.close()


    @staticmethod
    def remove_giveaway(giveaway):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        giveaways = db.giveaways
        giveaways.delete_one({'message_id':giveaway.message_id})
        client.close()


    @staticmethod
    def get_giveaways():
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        giveaways = db.giveaways
        giveaways_list = giveaways.find()
        return giveaways_list


    @staticmethod
    def set_voice_online(user_id, voice_online):
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        members.update_one({'id':user_id}, {'$set':{'voice_online': voice_online}})


    @staticmethod
    def get_all_users():
        client = pymongo.MongoClient(mongodb_url)
        db = client.donbass
        members = db.members
        users = members.find()
        user_list = dict()
        for user in users:
            del user['_id']
            user_list[user['id']] = user
        client.close()
        return user_list


    


    # @staticmethod
    # def add_invoice():
    #     pass