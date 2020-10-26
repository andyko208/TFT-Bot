from io import BytesIO
from PIL import Image

import discord
from discord.ext import commands
from discord import File

import requests
from bs4 import BeautifulSoup

from PIL import Image
import urllib.request

import io

# 9/23 enable multisearch

# 10/26 incorporate pypy to run the program faster
TOKEN = 'NzA5MjQzODAzODEwMTM2MDk1.XrjEww.9QX2xNZaOsV2HpYXHe_BwCrxRCI'

g_summoner_name = ""
g_profile_region = "NA"

client = commands.Bot(command_prefix = '.')

client.remove_command('help')


@client.event
async def on_ready():
    print('Bot is online')

@client.event
async def on_member_join(member):
    print(f'{member} has joined a server.')

@client.event
async def on_member_remove(member):
    print(f'{member} has left a server.')

@client.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author

    help_embed = discord.Embed(
        colour = discord.Colour.orange()
    )

    help_embed.set_author(name='Commands:')
    help_embed.add_field(name='.tft {summoner name}', value='ex) .tft Hide on bush\nSelects a summoner to display stats for')
    help_embed.add_field(name='.match {match #}', value='ex) .match 1\nSelects a match to display its details for')
    help_embed.add_field(name='.region', value='Current search region set to')
    help_embed.add_field(name='.region {region name}', value='ex) .region NA\n Selects a server to search the summoner from')

    await ctx.send(embed=help_embed)



@client.command()
async def clear(ctx, amount=10):
    await ctx.channel.purge(limit=amount)
    await ctx.send('Message deleted.')

# 9/23
# enable multisearch of summoner_names
# @client.command()
# async def echo(*args):
#     output = ''
#     for name in args:
#         output += name
#         output += ' '
#     await client.say(output)

# private message to user
# @client.command(pass_context=True)
# async def help(ctx):
#     author = ctx.message.author
#
#     embed = discord.Embed(
#         colour = discord.Colour.orange()
#     )
#
#     embed.set_author(name='Help')
#     embed.add_field(name='.tft <summoner name>', value = 'displays recent tft game stats from "lolchess.gg"', inline=False)
#
#     await ctx.author.send(embed=embed)



@client.command()
async def tft(ctx, *, summoner_name):
    global g_summoner_name
    g_summoner_name = summoner_name
    global g_profile_region
    # request for lolchess.gg page

    page = requests.get(f'https://lolchess.gg/profile/{g_profile_region}/{summoner_name}')
    # https://lolchess.gg/profile/na/tommystrate
    soup = BeautifulSoup(page.content, "html.parser")

    # retrive summoner name and region
    profile_name = soup.find("span", {"class": "profile__summoner__name"})

    if profile_name == None:
        await ctx.send("Invalid Summoner name!")
    profile_name = profile_name.get_text().strip()
    profile_region = soup.find("em", {"class": "profile__summoner__region"})
    profile_region = profile_region.get_text()
    profile_name = profile_name.replace(f'{profile_region}', "")
    profile_name = profile_name.strip()
    # message that bot has started searching
    # await ctx.send(f'{profile_name}[{profile_region}] 님의 롤토체스 최근 10게임의 전적을 가져옵니다. 슝~')

    await ctx.send(f'[{profile_region}] server\nSearching stats for: "{profile_name}"')

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
    profile_tier = tier_info[0].strip()
    profile_tier_lp = ''
    if profile_tier != 'Unranked':
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

    # output embed
    embed_title = f'{profile_tier} - {profile_tier_lp}'
    if not profile_tier_lp:
        embed_title = f'{profile_tier}'
    num_games = len(list_placement)
    # if profile_tier_lp
    first_half_match = discord.Embed(
        title = embed_title,
        description = 'From most recent matches',
        colour = discord.Colour.blue()
    )
    first_half_match.set_author(name=f'{profile_name}', icon_url='https:' + profile_icon_img['src'])
    # embed.set_image(url='https://ddragon.leagueoflegends.com/cdn/10.10.3208608/img/item/3040.png')
    first_half_match.set_thumbnail(url='https:' + profile_tier_img['src'])
    # embed.set_footer(text='Click to load next five games')


    empty_match = discord.Embed(
        title = embed_title,
        description = 'The summoner has not played games yet.',
        colour = discord.Colour.red()
    )
    empty_match.set_author(name=f'{profile_name}', icon_url='https:' + profile_icon_img['src'])

    # embed.set_image(url='https://ddragon.leagueoflegends.com/cdn/10.10.3208608/img/item/3040.png')
    empty_match.set_thumbnail(url='https:' + profile_tier_img['src'])

    if not list_placement:
        await ctx.send(embed=empty_match)
        return

    for i in range(0, 10):
        if i < num_games:
            game_no = str(i+1)
            # print("list_placement:")
            # print(list_placement[i])
            # print("list_mode:")
            # print(list_mode[i])
            # print("list_age:")
            # print(list_mode[i])
            match_detail = 'Placement:' + list_placement[i] + list_mode[i]  + list_length[i]  + list_age[i]
            first_half_match.add_field(name='Match #' + game_no, value=match_detail, inline=True)

    await ctx.send(embed=first_half_match)

@client.command()
# aliases=['', '']
async def match(ctx, *, nth_game):
    global g_summoner_name
    if nth_game.lower() == 'all':
        nth_game = 1
    else:
        nth_game = int(nth_game)

    # if user did not call .tft command beforehand
    if not g_summoner_name:
        await ctx.send('Please call .tft {summoner name} first.')
        return
    if nth_game > 10:
        await ctx.send('Out of range!')
        return

    page = requests.get(f'https://lolchess.gg/profile/{g_profile_region}/{g_summoner_name}/s4')
    soup = BeautifulSoup(page.content, "html.parser")

    traits_divs = soup.find_all("div", {"class": "traits"})
    units_divs = soup.find_all("div",{"class": "units"})

    list_traits = [[] for i in range (10)]
    list_stars = [[] for i in range (10)]
    list_units = [[] for i in range (10)]
    list_trait_title = [[] for i in range (10)]
    list_unit_title = [[] for i in range (10)]
    list_items = [{} for i in range (10)]

    index = 0
    for traits in traits_divs:
        trait_imgs = traits.find_all("img")
        for trait_img in trait_imgs:
            list_traits[index].append(trait_img['src'])
            # Synergy: ~
            list_trait_title[index].append(trait_img['alt'])
        index += 1

    # Checks if a certain match exist
    if not list_traits[nth_game-1]:
        await ctx.send('Match history does not exist!')
        return
    else:
        await ctx.send('Match history DUDUDUNGA soon!')
    index = 0
    for units in units_divs:
        unit_divs = units.find_all("div", {"class": "unit"})
        prev_unit = ""
        dup_count = 1

        for unit_profile in unit_divs:
            stars = unit_profile.find_all("img")[0]['src']
            list_stars[index].append(stars)
            unit = unit_profile.find_all("img")[1]['src']
            list_units[index].append(unit)

            # Units: ~
            unit_names = unit_profile.find_all("img")[1]['alt']
            list_unit_title[index].append(unit_names)

            items_list = unit_profile.find("ul")
            items = items_list.find_all("img")
            temp_item_list = []
            for item in items:
                if item:
                    temp_item_list.append(item['src'])

            # taking care of duplicate units
            print(prev_unit)
            if prev_unit == unit:
                unit += str(dup_count)
                list_items[index][unit] = temp_item_list
                dup_count += 1
                prev_unit = unit
            else:
                list_items[index][unit] = temp_item_list
                prev_unit = unit
        index += 1

    background = Image.new('RGB', (1650, 256), 0)
    width = 20
    height = 96
    # height = 10


    # Synergy
    await ctx.send('Retrieving synergies...')
    for list in list_traits[nth_game - 1]:
        TRAIT_WIDTH = 34
        TRAIT_HEIGHT = 34

        synergy = Image.open(urllib.request.urlopen('https:' + list))
        new_size = (TRAIT_WIDTH, TRAIT_HEIGHT)
        synergy = synergy.resize(new_size)
        # when synergy is more than 5
        if len(list_traits[nth_game - 1]) > 5:
            # print(width)
            if width >= 240:
                width = 20
                height += 44
            background.paste(synergy, (width, height))
            width += synergy.width + 10
        else:
            height = 111
            background.paste(synergy, (width, height))
            width += synergy.width + 10

    start_width = 272

    # Stars
    await ctx.send('Retrieving units...')
    for list in list_stars[nth_game - 1]:
        # print(list)
        champ_star = Image.open(urllib.request.urlopen('https:' + list))
        new_size = (64, 20)

        champ_star = champ_star.resize(new_size)
        background.paste(champ_star, (start_width, 0))
        start_width += 138


    start_width = 250

    for unit_src in list_units[nth_game - 1]:
        last_char = len(unit_src) - 1
        if unit_src[last_char] != 'g':
            unit_src = unit_src[:-1]
        champion = Image.open(urllib.request.urlopen('https:' + unit_src))
        new_size = (128, 128)
        champion = champion.resize(new_size)
        background.paste(champion, (start_width, 30))
        start_width += champion.width + 10

    start_width = 250
    next_champ = start_width + 138

    # Items
    await ctx.send('Retrieving items...')
    key_champs = list_items[nth_game-1].keys()
    print(key_champs)
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
            start_width = next_champ
            next_champ += 138

    synergy_info = ''
    for trait in list_trait_title[nth_game-1]:
        synergy_info += trait + '\t'
    unit_info = ' '
    for unit in list_unit_title[nth_game-1]:
        unit_info += unit + '\t'
    # print(synergy_info)
    # print('start_width:' + str(start_width))
    # print('width:' + str(width))
    # print("items")
    # print(item_img.width)
    # print(item_img.height)

    buffer = io.BytesIO()
    background.save(buffer, format='PNG')
    buffer.seek(0)

    await ctx.send(file=File(buffer, 'nth_game.png'))
    await ctx.send('Synergy: ' + synergy_info + '\nUnits: ' + unit_info)
        # print(list_units[index])

@client.command(aliases=['region', 'r'])
async def set_region(ctx, *args):
    global g_profile_region
    if not args:
        await ctx.send(f'Current search region: {g_profile_region}')
        return
    else:
        new_region = args[0].upper()
        valid_region = {'BR', 'EUNE', 'EUW', 'JP', 'KR', 'LAN', 'LAS', 'NA', 'OCE',
        'TR', 'RU'}
        if new_region in valid_region:
            g_profile_region = new_region
            await ctx.send(f'Search region set to: {g_profile_region}')
            return
    await ctx.send('Invalid region!')





client.run(TOKEN)
