########################
# Habbo User Validator #
# Created by DonaldDuck  # <---- Respect for founder :)
# ----Open  Source---- # <---- New ideas? Make it better! 
# ---Version:  0012--- # <---- Do not delete! Check on demand for the newest version!
# Habbo TR: DonaldDuck   # <---- For questions or ideas! habbo.com.tr
# Habbo NL: Berisan    # <---- habbo.nl
#   Malik#3169      # <---- My discord name
########################

# Get User input from channel. (Habboname, Man/Woman, Age(optional))
# Get User motto from Habbo with Habbo_api

# Set User channelname  example: Malik - DonaldDuck


import requests, json, random, string, os, discord, sqlite3
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import calendar;
import time;
from discord.utils import get

connection = sqlite3.connect("habboapi.db")

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="+",intents=intents)
erkek_id = 797550134036529212
kiz_id = 797553678911406100
kayitsiz_id = 797558861145702453
onaylanmadi_id = 796472818421334016


# My Methods
def user_exists(username):
    request = requests.get("https://www.habbo.com.tr/api/public/users?name=" + username)
    response = request.json()
    if "error" in response:
        return False
    else:
        return True

def create_verify_token():
    N = 3
    numbers = ''.join(random.choices( string.digits, k = N))
    token = '[Habbolog] ' + str(numbers)
    return token

def verify_token(db,guild_id,member_id):
    cursor = db.cursor()
    cursor.execute("SELECT token FROM verify_tokens WHERE guild_id=? AND member_id=?",
    (guild_id, member_id))
    token = cursor.fetchone()
    cursor.execute("SELECT member_habbo_nick FROM members WHERE member_guild_id=? AND member_discord_id=?",
    (guild_id, member_id))
    nickname = cursor.fetchone()
    request = requests.get("https://www.habbo.com.tr/api/public/users?name=" + nickname[0])
    habbo_motto = request.json()
    if habbo_motto['motto'] == token[0]:
        return True
    else:
        return False


# Database Add Queries
def add_guild(db, guild_id):
    cursor = db.cursor()
    ts = calendar.timegm(time.gmtime())
    cursor.execute("INSERT INTO guilds (guild_id, joined_at) VALUES (?,?)"
               ,(guild_id, ts))
    db.commit()

def add_user(db, guild_id, member_id,member_nick, member_hn, member_sex):
    cursor = db.cursor()
    ts = calendar.timegm(time.gmtime())
    cursor.execute("INSERT INTO members (member_discord_id, member_guild_id, member_habbo_nick, member_nick, member_sex, joined_at) VALUES (?,?,?,?,?,?)"
                ,(member_id,guild_id,member_hn, member_nick, member_sex,ts))
    db.commit()

def add_token(db,guild_id,member_id,token):
    cursor = db.cursor()
    ts = calendar.timegm(time.gmtime())
    cursor.execute("INSERT INTO verify_tokens (guild_id, member_id, token, created_at) VALUES (?,?,?,?)"
                ,(guild_id,member_id,token,ts))
    db.commit()

# Bot events
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_guild_join(guild):
    print(f"{bot.user.name} has joined {guild.name}")
    add_guild(connection,guild.id)

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(797580880955834378)
    embed=discord.Embed(title= member.name + ", Sunucuya Hoşgeldin!", description="Seni içeriye alabilmem için kayıt olman lazım!", color=0xffbb00)
    embed.set_author(name="Habbolog")
    embed.add_field(name="+kayıt [Isim] [Habbo Nick] [erkek/kadın]", value="Örnek: +kayıt Malik DonaldDuck e || e: erkek k: kadın", inline=True)
    embed.set_footer(text="Daha fazla bilgi için +yardım yada kayıt görevlilerini taglayınız")
    role = get(member.guild.roles, id=kayitsiz_id)
    await member.add_roles(role)
    await channel.send(member.mention)
    await channel.send(embed=embed)
# Benim komutlarim 
@bot.command()
async def kayıt(ctx, *args):
    if user_exists(args[1]):
        user = ctx.message.author
        nick = args[0] + " - " + args[1]
        if args[2] == "e":
            role = get(ctx.message.guild.roles, id=erkek_id)
        else:
            role = get(ctx.message.guild.roles, id=kiz_id)
        delete_role = get(ctx.message.guild.roles, id=kayitsiz_id)
        add_role = get(ctx.message.guild.roles, id=onaylanmadi_id)
        await user.remove_roles(delete_role)
        await user.add_roles(add_role)
        await user.add_roles(role)
        await user.edit(nick=nick)
        add_user(connection, user.guild.id, user.id, nick, args[1], args[2])
        user_token = create_verify_token()
        add_token(connection,user.guild.id,user.id, user_token)

        embed=discord.Embed(title= user.name + ", Son bir adım!", description="Lütfen doğrulama kodunuzu Habbo karakterinizin mottosuna yapıştırınız!", color=0xfff700)
        embed.set_author(name="Habbolog")
        embed.add_field(name="Doğrulama Kodu", value=user_token, inline=True)
        embed.add_field(name="Yazdıktan sonra:", value="+onayla yaziniz!", inline=True)
        embed.set_footer(text="Daha fazla bilgi için +yardım yada kayıt görevlilerini taglayınız")
        await ctx.send(embed=embed)

@bot.command()
async def onayla(ctx):
    if verify_token(connection,ctx.author.guild.id,ctx.author.id):
        delete_role = get(ctx.message.guild.roles, id=onaylanmadi_id)
        await ctx.author.remove_roles(delete_role)
        embed=discord.Embed(title= ctx.author.name + ", Sende artik bir üyemizsin!", description="Içerde uslu dur! Kurallari okumayi unutma :)", color=0x00ff33)
        embed.set_author(name="Habbolog")
        embed.set_footer(text="Daha fazla bilgi için +yardım yada kayıt görevlilerini taglayınız")
        await ctx.send(embed=embed)
    else:
        embed=discord.Embed(title= ctx.author.name + ", Bir hata oluştu!", description="Habbo mottonuzu değiştirdiginizden emin olunuz! 30 Saniye bekleyip tekrar deneyiniz!", color=0xff0000)
        embed.set_author(name="Habbolog")
        embed.set_footer(text="Daha fazla bilgi için +yardım yada kayıt görevlilerini taglayınız")
        await ctx.send(embed=embed)

@bot.command()
async def yardım(ctx):
    embed=discord.Embed(title="Komut bilgileri", description="Komutlari dogru bi sekilde kullandiginizdan emin olun!")
    embed.add_field(name="+kayit", value="+kayit [Isminiz] [Habbo Nickiniz] [e/k] Örnek: +kayit Malik DonaldDuck e", inline=False)
    embed.add_field(name="+onayla", value="+onayla ", inline=True)
    embed.set_footer(text="Daha fazla yardim icin kayit görevlisi tagleyebilirsiniz!")
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        await ctx.channel.send('Yardim icin +yardim yaziniz!')
        return
    raise error
bot.run(token)