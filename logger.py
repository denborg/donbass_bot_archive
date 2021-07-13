from enum import Enum


class Logger:
    channel = None


    def __init__(self, log_channel):
        Logger.channel = log_channel
    

    async def log(self, type, message):
        await Logger.channel.send(f'{type.name}: {message}')
        print(f'{type.name}: {message}')


    @staticmethod
    async def Log(type, message):
        await Logger.channel.send(f'{type.name}: {message}')
        print(f'{type.name}: {message}')


class LogType(Enum):
    ERROR = 'ERROR'
    INFO = 'INFO'