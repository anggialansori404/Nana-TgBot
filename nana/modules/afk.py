import os, requests, html, time

from bs4 import BeautifulSoup

from pyrogram import Filters, InlineKeyboardMarkup, InlineKeyboardButton

from nana import app, setbot, Owner, OwnerName, Command
from nana.helpers.parser import mention_markdown, escape_markdown
from nana.helpers.msg_types import Types, get_message_type
from nana.modules.database.afk_db import set_afk, get_afk


__MODULE__ = "AFK"
__HELP__ = """
Set yourself to afk.
When marked as AFK, any mentions will be replied to with a message to say you're not available!
And that mentioned will notify you by your Assistant.

If you're restart your bot, all counter and data in cache will be reset.
But you will still in afk, and always reply when got mentioned.

──「 **Set AFK status** 」──
-> `afk (*reason)`
Set yourself to afk, give a reason if need. When someone tag you, you will says in afk with reason, and that mentioned will sent in your assistant PM.

To exit from afk status, send anything to anywhere, exclude PM and saved message.

* = Optional
"""

# Set priority to 11 and 12
MENTIONED = []
AFK_RESTIRECT = {}
DELAY_TIME = 60 # seconds

@app.on_message(Filters.user("self") & (Filters.command(["afk"], Command) | Filters.regex("^brb ")))
async def afk(client, message):
	if len(message.text.split()) >= 2:
		set_afk(True, message.text.split(None, 1)[1])
		await message.edit("{} sekarang AFK!\nKarena {}".format(mention_markdown(message.from_user.id, message.from_user.first_name), message.text.split(None, 1)[1]))
		await setbot.send_message(Owner, "Kamu sedang AFK!\nKarena {}".format(message.text.split(None, 1)[1]))
	else:
		set_afk(True, "")
		await message.edit("{} is now AFK!".format(mention_markdown(message.from_user.id, message.from_user.first_name)))
		await setbot.send_message(Owner, "You are now AFK!")
	await message.stop_propagation()


@app.on_message(Filters.mentioned & ~Filters.bot, group=11)
async def afk_mentioned(client, message):
	global MENTIONED
	get = get_afk()
	if get and get['afk']:
		if "-" in str(message.chat.id):
			cid = str(message.chat.id)[4:]
		else:
			cid = str(message.chat.id)

		if cid in list(AFK_RESTIRECT):
			if int(AFK_RESTIRECT[cid]) >= int(time.time()):
				return
		AFK_RESTIRECT[cid] = int(time.time()) + DELAY_TIME
		if get['reason']:
			await message.reply("Maaf, {} Sedang AFK!\nKarena of {}".format(mention_markdown(Owner, OwnerName), get['reason']))
		else:
			await message.reply("Maaf, {} Sedang AFK!".format(mention_markdown(Owner, OwnerName)))

		content, message_type = get_message_type(message)
		if message_type == Types.TEXT:
			if message.text:
				text = message.text
			else:
				text = message.caption
		else:
			text = message_type.name

		MENTIONED.append({"user": message.from_user.first_name, "user_id": message.from_user.id, "chat": message.chat.title, "chat_id": cid, "text": text, "message_id": message.message_id})
		button = InlineKeyboardMarkup([[InlineKeyboardButton("Pergi Ke Pesan", url="https://t.me/c/{}/{}".format(cid, message.message_id))]])
		await setbot.send_message(Owner, "{} menyebut nama mu di {}\n\n{}\n\nJumlah Total: `{}`".format(mention_markdown(message.from_user.id, message.from_user.first_name), message.chat.title, text[:3500], len(MENTIONED)), reply_markup=button)

@app.on_message(Filters.user("self") & Filters.group, group=12)
async def no_longer_afk(client, message):
	global MENTIONED
	get = get_afk()
	if get and get['afk']:
		await setbot.send_message(message.from_user.id, "Yeay! Sekarang kamu sudah tidak AFK!")
		set_afk(False, "")
		text = "**Total {} menyebutmu**\n".format(len(MENTIONED))
		for x in MENTIONED:
			msg_text = x["text"]
			if len(msg_text) >= 11:
				msg_text = "{}...".format(x["text"])
			text += "- [{}](https://t.me/c/{}/{}) ({}): {}\n".format(escape_markdown(x["user"]), x["chat_id"], x["message_id"], x["chat"], msg_text)
		await setbot.send_message(message.from_user.id, text)
		MENTIONED = []

