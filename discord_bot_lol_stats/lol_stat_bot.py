import discord
from discord.ext import commands

import requests
from bs4 import BeautifulSoup

TOKEN = 'NzA5MjQzODAzODEwMTM2MDk1.Xr8iHQ.YboJnU6F__StpE792u_nX-rOYNk'

client = commands.Bot(command_prefix = '.')


@client.event
async def on_ready():
    print('Bot is ready')

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

@client.command()
async def tft(ctx, *, summoner_name):

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
    print(profile_icon_img['src'])

    profile_tier_div = soup.find("div", {"class": "profile__tier__icon"})
    profile_tier_img = profile_tier_div.find("img")
    print(profile_tier_img['src'])

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

    # big div that surround whole list
    # matches_div = soup.find("div", {"class": "profile__match-history-v2__items"})
    # for match in matches_div:




    # output embed
    embed = discord.Embed(
        title = f'{profile_tier} - {profile_tier_lp}',
        description = 'Five most recent games:',
        colour = discord.Colour.blue()
    )
    embed.set_author(name=f'{profile_name}', icon_url='https:' + profile_icon_img['src'])
    # embed.set_image(url='https://pbs.twimg.com/profile_images/1235620509766701061/0-advR1e_400x400.jpg')

    # embed.set_thumbnail(url='https://vignette.wikia.nocookie.net/leagueoflegends/images/4/4e/Boots_of_Speed_item.png/revision/latest/scale-to-width-down/40?cb=20171221060501')
    embed.set_thumbnail(url='https:' + profile_tier_img['src'])
    embed.set_footer(text='This is a footer')
    for i in range(0, 5):
        embed.add_field(name='Ranked', value=list_placement[i], inline=False)
        embed.add_field(name='Mode', value=list_mode[i], inline=True)
        embed.add_field(name='Length', value=list_length[i], inline=True)
        embed.add_field(name='Age', value=list_age[i], inline=True)

    await ctx.send(embed=embed)



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



# @client.command()
# async def tft(ctx, *, summoner_name):
#     # res = requests.get(f'https://lolchess.gg/profile/na/"{summoner_name}"/s3/matches?hl=en-US')
#     await ctx.send(f'Searching stats for {summoner_name}')
#     html = urlopen(f'https://lolchess.gg/profile/na/{summoner_name}/s3/matches?hl=en-US')
#     bsObject = BeautifulSoup(html, "html.parser")
#     div = bsObject.find('div', {'class':''})
#     # for meta in bsObject.head.find_all('meta'):
#     #     print(meta.get('content'))
#     # spe_div = find(class='profile__match-history-v2')
#     for tags in bsObject.find_all("div", class_= "placement"):
#         print('hello')
#         print(tags.text.strip())

    # soup = BeautifulSoup(html, 'html.parser')
    # print(soup.find('title'))
    # title = bsObejct.find('title')

    # for
    # await ctx.send(bsObject.head.find("div",{"class":"keywords"}).get('content'))
