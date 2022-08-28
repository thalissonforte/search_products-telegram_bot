from src.telegramBot import TelegramBot
from src.driveBot import DriveBot

#bot = TelegramBot()
#bot.Start()

drive_bot = DriveBot()
print(drive_bot.getData(True))

