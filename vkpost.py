import vk_api
import discord
import re
import settings


def get_post(number=1):
	news_off = number
	cooked = []
	vk_session = vk_api.VkApi(token=settings.vk_token)
	vk = vk_session.get_api()
	a = vk.wall.get(owner_id='', domain='enthusiasticgg', count=1, offset=str(news_off))
	print(a)
	text = a['items'][0]['text']
	id_from_id = str(a['items'][0]['from_id']) + "_" + str(a['items'][0]['id'])

	profile_to_replace = re.findall(r'\[(.*?)\]', text)
	profile_link = re.findall(r'\[(.*?)\|', text)
	profile_name = re.findall(r'\|(.*?)\]', text)
	profiles = []

	try:
		for i in range(len(profile_link)):
			profiles.append(profile_name[i] + " (@" + profile_link[i] + ")")
		counter = 0
		for i in profile_to_replace:
			text = text.replace("[" + i + "]", profiles[counter])
			counter += 1
	except:
		pass

	embed = discord.Embed(description=text, colour=discord.Colour.from_str('#dfbc67'))
	footer = u"\n\nКомментарии: http://vk.com/wall" + id_from_id
	embed.set_footer(text=footer)
	try:
		photo_link = a['items'][0]['attachments'][0]['photo']['sizes'][-1]['url']
		embed.set_image(url=photo_link)
	except:
		pass
	cooked.append(embed)
	cooked.append(a['items'][0]["date"])
	return cooked
