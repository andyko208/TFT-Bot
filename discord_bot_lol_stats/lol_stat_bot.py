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
async def game(ctx, *, nth_game):
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
    # list_items = [[] for i in range (10)]
    list_items = [{} for i in range (10)]



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
        prev_unit = ""
        dup_count = 1
        for unit_profile in unit_divs:
            stars = unit_profile.find_all("img")[0]['src']
            list_stars[index].append(stars)
            unit = unit_profile.find_all("img")[1]['src']
            list_units[index].append(unit)
            items_list = unit_profile.find("ul")
            items = items_list.find_all("img")
            temp_item_list = []
            for item in items:
                if item:
                    temp_item_list.append(item['src'])
                    # print(item)
                    # print(index)
            # taking care of duplicate units
            print(prev_unit)
            if prev_unit == unit:
                unit += str(dup_count)
                # print(unit)
                list_items[index][unit] = temp_item_list
                dup_count += 1
                prev_unit = unit
            else:
                list_items[index][unit] = temp_item_list
                prev_unit = unit
        index += 1
    # print(list_items)
    background = Image.new('RGB', (1650, 256), 0)
    width = 20
    height = 96
    # height = 10
    nth_game = int(nth_game)
    if nth_game > 10:
        await ctx.send('Cannot go beyond 10.')

    # Synergy
    for list in list_traits[nth_game - 1]:
        TRAIT_WIDTH = 34
        TRAIT_HEIGHT = 34

        synergy = Image.open(urllib.request.urlopen('https:' + list))
        new_size = (TRAIT_WIDTH, TRAIT_HEIGHT)
        synergy = synergy.resize(new_size)
        # when synergy is more than 5
        if len(list_traits[nth_game - 1]) > 5:
            print(width)
            if width >= 240:
                width = 20
                height += 44
            background.paste(synergy, (width, height))
            width += synergy.width + 10
        else:
            height = 111
            background.paste(synergy, (width, height))
            width += synergy.width + 10
    # print("synergy")
    # print(synergy.width)
    # print(synergy.height)

    start_width = 272
    # Stars
    for list in list_stars[nth_game - 1]:
        # print(list)
        champ_star = Image.open(urllib.request.urlopen('https:' + list))
        new_size = (64, 20)

        champ_star = champ_star.resize(new_size)
        background.paste(champ_star, (start_width, 0))
        start_width += 138
    # print(list_items)
    print("champ_star")
    print(champ_star.width)
    print(champ_star.height)

    start_width = 250
    for unit_src in list_units[nth_game - 1]:
        # print(list)
        last_char = len(unit_src) - 1
        print(unit_src)
        if unit_src[last_char] != 'g':
            unit_src = unit_src[:-1]
        print(unit_src)
        champion = Image.open(urllib.request.urlopen('https:' + unit_src))
        new_size = (128, 128)
        champion = champion.resize(new_size)
        background.paste(champion, (start_width, 30))
        start_width += champion.width + 10
    print("champion")
    print(champion.width)
    print(champion.height)

    start_width = 250
    next_champ = start_width + 138
    # Items
    key_champs = list_items[nth_game-1].keys()
    # print(key_champs)
    for key_champ in key_champs:
        if list_items[nth_game-1][key_champ]:
            for item in list_items[nth_game-1][key_champ]:
                item_img = Image.open(urllib.request.urlopen('https:' + item))
                new_size = (37, 37)
                item_img = item_img.resize(new_size)
                background.paste(item_img, (start_width, 180))
                start_width += item_img.width + 5
            start_width = next_champ
            next_champ += 138
        else:
            print('inside else')
            start_width = next_champ
            next_champ += 138
    print('start_width:' + str(start_width))
    print('width:' + str(width))
    print("items")
    print(item_img.width)
    print(item_img.height)

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
