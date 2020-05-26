import discord
from discord.ext import commands
from discord import File

import requests
from bs4 import BeautifulSoup

from PIL import Image
import urllib.request

import io
# from io import BytesIO
# from PIL import Image

TOKEN = 'NzA5MjQzODAzODEwMTM2MDk1.Xsyvsw.D-mNAGDbfnqB6yQUPNKEpWwSEZM'

g_summoner_name = ""

client = commands.Bot(command_prefix = '.')
client.remove_command('help')

@client.event
async def on_ready():
    print('Bot is ready')
    # img = Image.open('C:\\Users\\고경명\\Desktop\\kaisa.png')


    # img = ("https://ddragon.leagueoflegends.com/cdn/10.10.3208608/img/item/3040.png")
    # response = ('https://ddragon.leagueoflegends.com/cdn/10.10.3208608/img/item/3040.png')
    # synergy1 = Image.open(urllib.request.urlopen('https://cdn.lolchess.gg/images/tft/traiticons-darken/trait_icon_brawler.png'))
    # synergy2 = Image.open(urllib.request.urlopen('https://cdn.lolchess.gg/images/tft/traiticons-darken/trait_icon_void.png'))
    # # print(synergy1)
    # # img = Image.open(synergy1)
    # # img = img.resize((12, 12))
    # # img.show()
    # synergy1.show()
    # synergy2.show()

@client.event
async def on_member_join(member):
    print(f'{member} has joined a server.')

@client.event
async def on_member_remove(member):
    print(f'{member} has left a server.')

# enable multisearch of summoner_names
@client.command()
async def echo(*args):
    output = ''
    for name in args:
        output += name
        output += ' '
    await client.say(output)

@client.command()
async def clear(ctx, amount=10):
    await ctx.channel.purge(limit=amount)
    await ctx.send('Message deleted.')

# private message to user
@client.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author

    embed = discord.Embed(
        colour = discord.Colour.orange()
    )

    embed.set_author(name='Help')
    embed.add_field(name='.tft <summoner name>', value = 'displays recent tft game stats from "lolchess.gg"', inline=False)

    await ctx.author.send(embed=embed)



@client.command()
async def tft(ctx, *, summoner_name):
    global g_summoner_name
    g_summoner_name = summoner_name
    # request for lolchess.gg page
    page = requests.get(f'https://lolchess.gg/profile/na/{summoner_name}/s3')
    soup = BeautifulSoup(page.content, "html.parser")

    # retrive summoner name and region
    profile_name = soup.find("span", {"class": "profile__summoner__name"})
    profile_name = profile_name.get_text()
    profile_name = "".join(profile_name.split())
    profile_region = soup.find("em", {"class": "profile__summoner__region"})
    profile_region = profile_region.get_text()
    profile_name = profile_name.replace(f'{profile_region}', "")

    # message that bot has started searching
    await ctx.send(f'{profile_name}[{profile_region}] 님의 롤토체스 최근 10게임의 전적을 가져옵니다. 슝~')

    # retrieve summoner's profile icon and tier info
    profile_icon_div = soup.find("div", {"class": "profile__icon"})
    profile_icon_img = profile_icon_div.find("img")
    # print(profile_icon_img['src'])

    profile_tier_div = soup.find("div", {"class": "profile__tier__icon"})
    profile_tier_img = profile_tier_div.find("img")
    # print(profile_tier_img['src'])

    profile_tier_summary_div = soup.find("div", {"class": "profile__tier__summary"})
    tier_spans = profile_tier_summary_div.find_all("span")
    tier_info = []
    for tier_span in tier_spans:
        tier_info.append(tier_span.get_text())
    profile_tier = tier_info[0]
    profile_tier_lp = tier_info[1]


    # tft stat info
    match_placement = soup.find_all("div", {"class": "placement"})
    match_mode = soup.find_all("div", {"class": "game-mode"})
    match_length = soup.find_all("div", {"class": "length"})
    match_age = soup.find_all("div", {"class": "age"})
    list_placement = []
    list_mode = []
    list_length = []
    list_age = []
    for placement in match_placement:
        list_placement.append(placement.get_text())
    for mode in match_mode:
        list_mode.append(mode.get_text())
    for length in match_length:
        list_length.append(length.get_text())
    for age in match_age:
        list_age.append(age.get_text())

    # synergy_div = soup.find_all("div", {"class": "traits"})
    # print(synergy_div)

    # how to use attachment images (img from local file)
    # stat = discord.File("C:\\Users\\고경명\\Desktop\\kaisa.png", filename="clicked_stat.png")
    # embed.set_image(url='attachment://clicked_stat.png')
    # await ctx.send(file=stat, embed=embed)

    # output embed
    embed = discord.Embed(
        title = f'{profile_tier} - {profile_tier_lp}',
        description = 'Five most recent games:',
        colour = discord.Colour.blue()
    )
    embed.set_author(name=f'{profile_name}', icon_url='https:' + profile_icon_img['src'])
    # embed.set_image(url='https://ddragon.leagueoflegends.com/cdn/10.10.3208608/img/item/3040.png')

    embed.set_thumbnail(url='https:' + profile_tier_img['src'])
    embed.set_footer(text='Click to load next five games')

    for i in range(0, 5):
        embed.add_field(name='Ranked', value=list_placement[i], inline=False)
        embed.add_field(name='Mode', value=list_mode[i], inline=True)
        embed.add_field(name='Length', value=list_length[i], inline=True)
        embed.add_field(name='Age', value=list_age[i], inline=True)
    await ctx.send(embed=embed)

@client.command()
async def stat(ctx, *, nth_game):
    global g_summoner_name

    # if user did not call .tft command beforehand
    if not g_summoner_name:
        await ctx.send('Please call .tft {summoner name} first.')
    page = requests.get(f'https://lolchess.gg/profile/na/{g_summoner_name}/s3')
    soup = BeautifulSoup(page.content, "html.parser")

    traits_divs = soup.find_all("div", {"class": "traits"})
    units_divs = soup.find_all("div",{"class": "units"})

    # _div = soup.find_all("div", {"class": "traits"})
    # traits_div = soup.find_all("div", {"class": "traits"})
    # traits_div = soup.find_all("div", {"class": "traits"})
    list_traits = [[] for i in range (10)]
    list_stars = [[] for i in range (10)]
    list_units = [[] for i in range (10)]
    list_items = [[] for i in range (10)]
    index = 0
    for traits in traits_divs:
        trait_imgs = traits.find_all("img")
        for trait_img in trait_imgs:
            list_traits[index].append(trait_img['src'])
        index += 1

    index = 0

    for units in units_divs:
        unit_divs = units.find_all("div", {"class": "unit"})
        # print(unit_divs)
        for unit_profile in unit_divs:
            list_stars[index].append(unit_profile.find_all("img")[0]['src'])
            list_units[index].append(unit_profile.find_all("img")[1]['src'])
            items_list = unit_profile.find("ul")
            items = items_list.find_all("img")
            for item in items:
                if item:
                    list_items[index].append(item['src'])
        index += 1
    background = Image.new('RGB', (1024, 512), 0)
    width = 10
    nth_game = int(nth_game)
    if nth_game > 10:
        await ctx.send('Cannot go beyond 10.')

    for list in list_traits[nth_game - 1]:
        print(list)
        synergy = Image.open(urllib.request.urlopen('https:' + list))
        # new_size = (synergy.width * 2, synergy.height * 2)
        # synergy = synergy.resize(new_size)
        if width >= 158:
            width = 0
        background.paste(synergy, (width, 128))
        width += synergy.width + 10
    print(synergy.width)
    print(synergy.height)
    start_width = width
    for list in list_stars[nth_game - 1]:
        print(list)
        champ_star = Image.open(urllib.request.urlopen('https:' + list))
        # new_size = (champ_star.width * 4, champ_star.height * 4)
        # champ_star = champ_star.resize(new_size)
        background.paste(champ_star, (width+50, 10))
        width += champ_star.width + 60
    print(champ_star.width)
    print(champ_star.height)
    width = start_width
    for list in list_units[nth_game - 1]:
        print(list)
        champion = Image.open(urllib.request.urlopen('https:' + list))
        # new_size = (int(champion.width * 1.5), int(champion.height * 2))
        # champion = champion.resize(new_size)
        background.paste(champion, (start_width, 70))
        start_width += champion.width + 40
    print(champion.width)
    print(champion.height)

    for list in list_items[nth_game - 1]:
        print(list)
        item = Image.open(urllib.request.urlopen('https:' + list))
        # new_size = (int(champion.width * 1.5), int(champion.height * 2))
        # champion = champion.resize(new_size)
        background.paste(item, (width, 216))
        width += item.width + 40
    print(item.width)
    print(item.height)

    # for list in list_items[nth_game - 1]:
    #     # resample=Image.BICUBIC
    #     print(list)
    #     item = Image.open(urllib.request.urlopen('https:' + list))
    #     background.paste(item, (width, 0))
    #     width += champion.width
    buffer = io.BytesIO()
    background.save(buffer, format='PNG')
    buffer.seek(0)
    # champion1 = Image.open(urllib.request.urlopen('https://cdn.lolchess.gg/images/tft/traiticons-darken/trait_icon_brawler.png'))
    # champion2 = Image.open(urllib.request.urlopen('https://cdn.lolchess.gg/images/tft/traiticons-darken/trait_icon_void.png'))
    # background.paste(champion1, (0, 0))
    # background.paste(champion2, (champion1.width, 0))
    # buffer = io.BytesIO()
    # background.save(buffer, format='PNG')
    # buffer.seek(0)
    await ctx.send(file=File(buffer, 'nth_game.png'))
        # print(list_units[index])

    # synergy1 = Image.open(urllib.request.urlopen('https://cdn.lolchess.gg/images/tft/traiticons-darken/trait_icon_brawler.png'))
    # synergy2 = Image.open(urllib.request.urlopen('https://cdn.lolchess.gg/images/tft/traiticons-darken/trait_icon_void.png'))
    # synergy1.show()
    # synergy2.show()
    # synergy1.show()
    # synergy2.show()
    # i = 0
    # for list in list_stars:
    #     print(i)
    #     print('\n')
    #     print(list)
    #     print('\n')
    #     i += 1
    # print('\n')
    # i = 0
    # for list in list_units:
    #     print(i)
    #     print('\n')
    #     print(list)
    #     print('\n')
    #     i += 1
    # print('\n')
    # i = 0
    # for list in list_traits:
    #     print(i)
    #     print('\n')
    #     print(list)
    #     print('\n')
    #     i += 1

    # profile_icon_img = traits_div.find("img")
    # print(traits_div)
    # print(profile_icon_img['src'])



# change search site, "fow.kr", "na.op.gg", etc.
# @client.command()
# async def ping(ctx):
#     await ctx.send(f'Pressed! {round(client.latency * 1000)}ms')
#
# # allows both commands, ".tft", ".test"
# @client.command(aliases=['dddg', 'test'])
# async def _8ball(ctx, *, question):
#     await ctx.send(f'tft or test: {question}')





client.run(TOKEN)
