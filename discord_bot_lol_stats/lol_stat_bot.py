import discord
from discord.ext import commands

import requests
from bs4 import BeautifulSoup

TOKEN = 'NzA5MjQzODAzODEwMTM2MDk1.Xr3MnA.HQh4S0j3lsq5vvZ9YuHytvh9tXc'

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
    await ctx.send(f'{summoner_name}님의 롤토체스 최근 10게임의 전적을 가져옵니다. 슝~')
    page = requests.get(f'https://lolchess.gg/profile/na/{summoner_name}/s3/matches?hl=en-US')
    soup = BeautifulSoup(page.content, "html.parser")

    profile_div = soup.find("div", {"class": "profile__icon"})
    profile_img = profile_div.find("img")
    print(profile_img['src'])
    # profile_items = []
    # print(profile_div)
    # for item in profile_div:
    #     profile_img = item.find("img")

        # if item.img:
        #     profile_items.append(item['src'])
        # profile_items.append(item.get_text())

    print('items:')


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

    embed = discord.Embed(
        title = f'{summoner_name}',
        description = 'From the most recent',
        colour = discord.Colour.blue()
    )
    const Discord = require('discord.js');
    const exampleEmbed = new Discord.MessageEmbed()
        .attachFiles([profile_img], 'profile_img')
        .setImage('attachment://profile_img')
    embed.set_footer(text='This is a footer')
    # embed.set_image(url='https://pbs.twimg.com/profile_images/1235620509766701061/0-advR1e_400x400.jpg')
    embed.set_thumbnail(url='attachment://profile_img')
    # embed.set_author(name='Author Name',icon_url='https://encrypted-tbn0.gstatic.com/images?q=tbn%3AANd9GcRvUdp2cYonGeH1Jq8CRlllvxt4eB-0Qkkno8u8gn7vvqXxwAf9&usqp=CAU')
    for i in range(0, 6):
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
