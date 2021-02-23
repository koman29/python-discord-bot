# comenzi: kick, ban, mute, setprefix, getip, whois, weather
# todo: music player


import requests
import socket
import os
from datetime import datetime, timedelta

import random
import youtube_dl

import asyncio
import discord
from discord.ext.commands import Bot, has_permissions, MissingPermissions
from discord.ext import commands


client = Bot('/')
color = 0x4169e1

weather_key = os.getenv('WEATHER_KEY')
welcome_channel = None

@client.event
async def on_ready():
  print(f'{client.user} is Ready')
  welcome_channel = client.get_channel("WELCOME CHANNEL ID HERE")

  with open('mozza.png', 'rb') as myfile:
    await client.user.edit(avatar=myfile.read(), username='Mozzard')


@client.event
async def on_member_join(member:discord.Member):
  await welcome_channel.send(f'Welcome {member.username}')

@client.event
async def on_member_leave(member:discord.Member):
  await welcome_channel.send(f'Goodbye {member.username}')

# @client.command()
# async def join(ctx):
#   if ctx.author.voice == None:
#     return await ctx.send('You are not connected to a voice channel')

#   await ctx.send(f'Joining **{ctx.author.voice.channel}**')

#   try:await ctx.author.voice.channel.connect()
#   except discord.ClientException:
#     await client.move_to(ctx.author.voice.channel)

# @client.command(aliases=['disconnect', 'dc'])
# async def leave(ctx):
#   pass

# @client.command(aliases=['p'])
# async def play(ctx):
#   pass

@client.command(aliases=['wth'])
async def weather(ctx, city:str):
  res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_key}').json()

  temp = round(res['main']['temp'] - 273.15, 2)

  if '-' in str(res['timezone']):
    n_time = datetime.now() - timedelta(seconds=res['timezone'])
  else:
    n_time = datetime.now() + timedelta(seconds=res['timezone'])

  feels_like = round(res['main']['feels_like'] - 273.15, 2)
  humidity = res['main']['humidity']

  embed = discord.Embed(title='Weather', color=color)
  embed.add_field(name='City', value=city, inline=False)
  embed.add_field(name='Time', value=n_time.strftime('%-H:%-M:%-S'), inline=False)
  embed.add_field(name='Temperature', value=str(temp) + ' °C', inline=False)
  embed.add_field(name='Feels Like', value=str(feels_like) + ' °C', inline=False)
  embed.add_field(name='Humidity', value=str(humidity) + ' %', inline=False)

  await ctx.send(embed=embed)

@client.command()
async def whois(ctx, member:discord.Member):
  embed = discord.Embed(title='Whois', color=color)
  embed.set_thumbnail(url=member.avatar_url)
  embed.add_field(name='Username', value=member.name, inline=False)
  embed.add_field(name='Server Nickname', value=member.nick, inline=False)
  embed.add_field(name='ID', value=member.id, inline=False)
  embed.add_field(name='Account Created', value=member.created_at, inline=False)
  embed.add_field(name='Joined the Server', value=member.joined_at, inline=False)

  await ctx.send(embed=embed)


# TODO: finish this
@client.command(aliases=['serverstats', 'server', 'status', 'ss'])
async def serverstatus(ctx):
  embed = discord.Embed(title='Server Status', color=color)
  embed.set_thumbnail(url=ctx.guild.icon_url)
  embed.add_field(name='Name', value=ctx.guild.name, inline=False)
  embed.add_field(name='ID', value=ctx.guild.id, inline=False)
  embed.add_field(name='Server Creation Date', value='blabla', inline=False)
  embed.add_field(name='Member Count', value=ctx.guild.member_count, inline=False)

  await ctx.send(embed=embed)

@client.command()
async def getip(ctx, domain:str=None):
  ip = socket.gethostbyname(domain)
  await ctx.send(f'The IP of **{domain}** is **{ip}**')

@client.command()
@has_permissions(administrator=True)
async def prefix(ctx, newPrefix:str=None):
  if newPrefix == None:
    await ctx.send(f'The current prefix is **{client.command_prefix}**')
  else:
    client.command_prefix = newPrefix
    await ctx.send(f'Prefix has been changed to **{newPrefix}**')

@client.command()
@has_permissions(kick_members=True)
async def kick(ctx, member:discord.Member, reason:str=None):
    await member.kick(reason=(reason if reason != None else None))

    await ctx.send(f'**{member.username}** has been kicked' + (f' for **{reason}**' if reason != None else None))
    await member.send(f'You have been kicked from **{ctx.guild}** for **{reason}**')

@client.command()
@has_permissions(ban_members=True)
async def ban(ctx, member:discord.Member, duration=None, reason:str=None):
  if duration:
    await member.ban(reason=(reason if reason != None else None))
    await asyncio.sleep(duration/60)
    await member.unban(reason=(reason if reason != None else None))
  else:
    await member.ban(reason=(reason if reason != None else None))

  await ctx.send(f'**{member.username}** has been banned' + (f' with the reason **{reason}**' if reason != None else None) + (f' for **{duration}** minutes' if duration != None else None))
  await member.send(f'You have been banned from **{ctx.guild}** ' + (' with the reason **{reason}**' if reason != None else None) + (' for **{duration}** minutes' if duration != None else None))

@client.command()
@has_permissions(mute_members=True)
async def mute(ctx, member:discord.Member, duration=None, reason:str=None):
  role = discord.utils.get(ctx.guild.roles, name="Muted")

  if duration:
      await member.add_roles(role)
      await asyncio.sleep(duration/60)
      await member.remove_roles(role)
  else:
      await member.add_roles(role)

  await ctx.send(f'**{member.username}** has been banned' + (f' with the reason **{reason}**' if reason != None else None) + (f' for **{duration}** minutes' if duration != None else None))
  await member.send(f'You have been banned from **{ctx.guild}** ' + (' with the reason **await {reason}**' if reason != None else None) + (' for **{duration}** minutes' if duration != None else None))

@client.command()
async def ping(ctx):
  await ctx.send('Pong !')                         

@client.command(aliases=['spam'])
async def mention(ctx, member:discord.Member):
  await ctx.message.delete()
  for _ in range(3):
    await ctx.send('> ' + member.mention)

@client.command()
@has_permissions(manage_messages=True)
async def clear(ctx, amount:int):
  await ctx.channel.purge(limit=amount+1)

  if amount == 1:
    message = await ctx.send(f'**{amount}** message have been deleted.')
  else:
    message = await ctx.send(f'**{amount}** messages have been deleted.')
  
  await asyncio.sleep(2.5)
  await message.delete()

@kick.error
async def kick_error(ctx, error):
  if isinstance(error, MissingPermissions):
    await ctx.send("You don't have permission to do that!")

@ban.error
async def ban_error(ctx, error):
  if isinstance(error, MissingPermissions):
    await ctx.send("You don't have permission to do that!")

@mute.error
async def mute_error(ctx, error):
  if isinstance(error, MissingPermissions):
    await ctx.send("You don't have permission to do that!")

@clear.error
async def clear_error(ctx, error):
  if isinstance(error, MissingPermissions):
    await ctx.send("You don't have permission to do that!")

client.run('TOKEN')
