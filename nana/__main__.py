import time
import logging
import importlib
import random
import sys
import traceback
import threading
import asyncio

import pyrogram
from pyrogram import Filters, InlineKeyboardMarkup, InlineKeyboardButton
from nana import app, Owner, log, Command, ASSISTANT_BOT, setbot, USERBOT_VERSION, ASSISTANT_VERSION, get_self, get_bot

from nana.modules import ALL_MODULES
from nana.assistant import ALL_SETTINGS


BOT_RUNTIME = 0
HELP_COMMANDS = {}


loop = asyncio.get_event_loop()

async def get_runtime():
	return BOT_RUNTIME

async def reload_userbot():
	await app.start()
	for modul in ALL_MODULES:
		imported_module = importlib.import_module("nana.modules." + modul)
		importlib.reload(imported_module)

async def reinitial_restart():
	await get_bot()
	await get_self()

async def reboot():
	global BOT_RUNTIME, HELP_COMMANDS
	importlib.reload(importlib.import_module("nana.modules"))
	importlib.reload(importlib.import_module("nana.assistant"))
	from nana.modules import ALL_MODULES
	from nana.assistant import ALL_SETTINGS
	# await setbot.send_message(Owner, "Bot is restarting...")
	await setbot.restart()
	await app.restart()
	await reinitial_restart()
	# Reset global var
	BOT_RUNTIME = 0
	HELP_COMMANDS = {}
	# Assistant bot
	for setting in ALL_SETTINGS:
		imported_module = importlib.import_module("nana.assistant." + setting)
		importlib.reload(imported_module)
	# Nana userbot
	for modul in ALL_MODULES:
		imported_module = importlib.import_module("nana.modules." + modul)
		if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
			imported_module.__MODULE__ = imported_module.__MODULE__
		if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
			if not imported_module.__MODULE__.lower() in HELP_COMMANDS:
				HELP_COMMANDS[imported_module.__MODULE__.lower()] = imported_module
			else:
				raise Exception("Can't have two modules with the same name! Please change one")
		if hasattr(imported_module, "__HELP__") and imported_module.__HELP__:
			HELP_COMMANDS[imported_module.__MODULE__.lower()] = imported_module
		importlib.reload(imported_module)
	# await setbot.send_message(Owner, "Restart successfully!")

async def restart_all():
	# Restarting and load all plugins
	asyncio.get_event_loop().create_task(reboot())

RANDOM_STICKERS = ["CAADAgAD6EoAAuCjggf4LTFlHEcvNAI", "CAADAgADf1AAAuCjggfqE-GQnopqyAI", "CAADAgADaV0AAuCjggfi51NV8GUiRwI"]


async def except_hook(errtype, value, tback):
	sys.__excepthook__(errtype, value, tback)
	errors = traceback.format_exception(etype=errtype, value=value, tb=tback)
	button = InlineKeyboardMarkup([[InlineKeyboardButton("🐞 Report bugs", callback_data="report_errors")]])
	text = "An error has accured!\n\n```{}```\n".format("".join(errors))
	if errtype == ModuleNotFoundError:
		text += "\nHint: Try this in your terminal `pip install -r requirements.txt`"
	await setbot.send_message(Owner, text, reply_markup=button)

async def reinitial():
	await setbot.start()
	await app.start()
	await get_bot()
	await get_self()
	await setbot.stop()
	await app.stop()

async def start_bot():
	# sys.excepthook = except_hook
	print("----- Checking user and bot... -----")
	await reinitial()
	print("----------- Check done! ------------")
	# Assistant bot
	await setbot.start()
	for setting in ALL_SETTINGS:
		imported_module = importlib.import_module("nana.assistant." + setting)
	# Nana userbot
	await app.start()
	for modul in ALL_MODULES:
		imported_module = importlib.import_module("nana.modules." + modul)
		if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
			imported_module.__MODULE__ = imported_module.__MODULE__
		if hasattr(imported_module, "__MODULE__") and imported_module.__MODULE__:
			if not imported_module.__MODULE__.lower() in HELP_COMMANDS:
				HELP_COMMANDS[imported_module.__MODULE__.lower()] = imported_module
			else:
				raise Exception("Can't have two modules with the same name! Please change one")
		if hasattr(imported_module, "__HELP__") and imported_module.__HELP__:
			HELP_COMMANDS[imported_module.__MODULE__.lower()] = imported_module
	log.info("-----------------------")
	log.info("Userbot modules: " + str(ALL_MODULES))
	log.info("-----------------------")
	log.info("Assistant modules: " + str(ALL_SETTINGS))
	log.info("-----------------------")
	log.info("Bot run successfully!")
	await setbot.idle()

if __name__ == '__main__':
	BOT_RUNTIME = int(time.time())
	loop.run_until_complete(start_bot())
