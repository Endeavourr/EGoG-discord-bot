import discord
import logging
import datetime
import asyncio
import settings
import vkpost


logging.basicConfig(level=logging.DEBUG)


class MyClient(discord.Client):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.vk_checker_task = None
		self.role_ch_id = settings.role_ch_id
		self.emoji_to_role = {
			discord.PartialEmoji(name='LoL', id=1008477234073440286): 1006664584628805782,
			discord.PartialEmoji(name='ow_1', id=1008478096426532955): 1006664496242249730,
		}

	async def setup_hook(self) -> None:
		self.vk_checker_task = self.loop.create_task(self.checker())

	async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
		if payload.message_id != self.role_ch_id:
			return

		guild = self.get_guild(payload.guild_id)
		if guild is None:
			return

		try:
			role_id = self.emoji_to_role[payload.emoji]
		except KeyError:
			return

		role = guild.get_role(role_id)
		if role is None:
			return

		try:
			await payload.member.add_roles(role)
		except discord.HTTPException:
			pass

	async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
		if payload.message_id != self.role_ch_id:
			return

		guild = self.get_guild(payload.guild_id)
		if guild is None:
			return

		try:
			role_id = self.emoji_to_role[payload.emoji]
		except KeyError:
			return

		role = guild.get_role(role_id)
		if role is None:
			return

		member = guild.get_member(payload.user_id)
		if member is None:
			return

		try:
			await member.remove_roles(role)
		except discord.HTTPException:
			pass

	async def checker(self):
		await self.wait_until_ready()
		while not self.is_closed():
			print('Проверка... ' + str(datetime.datetime.now()))
			with open('timestamp', 'r') as t:
				timestamp = int(t.read())
			last_posts = 1
			end = False
			while not end:
				post = vkpost.get_post(last_posts)
				if post[1] > timestamp:
					last_posts += 1
				else:
					first = vkpost.get_post(0)
					last = vkpost.get_post()
					timestamp1 = last[1]
					if timestamp1 > first[1]:
						with open('timestamp', 'w') as t:
							t.write(str(timestamp1))
					else:
						with open('timestamp', 'w') as t:
							t.write(str(first[1]))
					print('Найдено ' + str(last_posts - 1) + ' новых постов!')
					end = True

			if last_posts > 1:
				for post_c in range(last_posts - 1):
					post = vkpost.get_post(last_posts - 1 - post_c)
					text_to_send = post[0]
					channel = self.get_channel(settings.news_ch_id)
					await channel.send(embed=text_to_send)
			if first[1] > timestamp:
				post = vkpost.get_post(0)
				text_to_send = post[0]
				channel = self.get_channel(settings.news_ch_id)
				await channel.send(embed=text_to_send)
			await asyncio.sleep(1 * 60)


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = MyClient(intents=intents)
client.run(settings.token)
