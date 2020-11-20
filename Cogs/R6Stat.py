# -*- coding: utf-8 -*-
# r6stat.py

import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import requests
import os
import json
import datetime
import asyncio


r6serverStatusURL='https://rainbow6.ubisoft.com/status/'
r6statPlayerURL='https://r6stats.com/stats/'
r6statURL='https://r6stats.com/search/'
platformList = ['pc', 'ps4', 'xbox']
sectionList = {'overall':'Overall', 'rank':'Ranked Stats', 'casual':'Casual Stats', 'kb':'Kills Breakdown', 'tp':'Team Play'}

DATA_PATH = 'Data'
TEAM_PATH = 'Team'
R6USER_DATA = 'R6_User.json'


class R6Stat(commands.Cog, name='R6Stat'):
    platform = platformList[0]
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='레식')
    async def r6stat(self, ctx, userName, section='overall'):
        html = requests.get(r6statURL + userName + '/' + self.platform + '/').text
        bs = BeautifulSoup(html, 'html.parser')
        
        if(bs.select('.page-stats-player')):
            playerName = bs.select('.player-info__player__username')[0].text
            level = bs.select('.quick-stat__value')[1].text
            kdRatio = bs.select('.quick-stat__value')[2].text
            
            playerId = bs.select('li.sub-navigation-link > a')[0].get('href')
            playerId = playerId.split("/")[2]
            playerIconUrl = f'https://ubisoft-avatars.akamaized.net/{playerId}/default_256_256.png'
            
            if section == 'overall':
                info = bs.select('.queue-stats-card.block__overall .stats-card-item')
            elif section == 'rank':
                info = bs.select('.queue-stats-card.block__ranked .stats-card-item')
            elif section == 'casual':
                info = bs.select('.queue-stats-card.block__casual .stats-card-item')
            elif section == 'kb':
                info = bs.select('.kills-breakdown-stats-card .stats-card-item')
            elif section == 'tp':
                info = bs.select('.team-play-stats-card .stats-card-item')
            
            embed = discord.Embed(title=f'{playerName}', description=f'👍 Lv.{level} - ⚔️ K/D: {kdRatio}', url=f'{r6statPlayerURL}{playerId}/', color=0x8E35FF)
            embed.add_field(name='Play Mode', value=sectionList[section], inline=False)

            for infoLabel, infoValue in info:
                embed.add_field(name=infoLabel.text, value=infoValue.text)
            
            embed.set_thumbnail(url=playerIconUrl)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send('플레이어가 존재하지 않습니다.')
        
        
    @commands.command(name='레식플랫폼')
    async def r6platform(self, ctx, _platform):
        for pf in platformList:
            if pf == _platform:
                self.platform = _platform
                break
        
        embed = discord.Embed(title=f'레식 전적 검색 플랫폼이 {self.platform.upper()}로 변경되었습니다.', color=0xEF0000)
        await ctx.send(embed=embed)
    
    @commands.command(name='레식서버')
    async def r6server(self, ctx):
        embed=discord.Embed(title='레식 서버', url=r6serverStatusURL, color=0xFFFFFE)
        await ctx.send(content='레식 서버', embed=embed)
        
        
    @commands.command(name='레식등록')
    async def r6user(self, ctx, userName):
        teamPath = f'{DATA_PATH}/{ctx.message.guild.id}/{TEAM_PATH}'
        if not os.path.exists(teamPath):
            os.mkdir(teamPath)
        
        html = requests.get(r6statURL + userName + '/' + self.platform + '/').text
        bs = BeautifulSoup(html, 'html.parser')
        
        if(bs.select('.page-stats-player')):
            playerName = bs.select('.player-info__player__username')[0].text
            playerLevel = bs.select('.quick-stat__value')[1].text
            kdRatio = bs.select('.quick-stat__value')[2].text
            winRate = bs.select('.queue-stats-card.block__overall .stats-card-item')[1].select('.stats-card-item__value')[0].text
            
            curDate = datetime.datetime.today().strftime('%Y/%m/%d-%X')
            
            userDataDict = { str(ctx.message.author.id): { 'discordName': f'{ctx.message.author.name}#{ctx.message.author.discriminator}', 'discordNick': ctx.message.author.nick, 'updateTime': curDate, 'r6Name': playerName, 'level': playerLevel, 'kd': kdRatio, 'winRate': winRate } }
            
            userData = f'{teamPath}/{R6USER_DATA}'
            if not os.path.exists(userData):
                with open(userData, 'w', -1, 'utf-8') as f:
                    json.dump(userDataDict, f, indent=4, ensure_ascii=False)
            else:
                data = dict()
                with open(userData, 'r+', -1, 'utf-8') as f:
                    data = json.load(f)
                    data.update(userDataDict)
                with open(userData, 'w', -1, 'utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            
            await ctx.send(f'"{ctx.message.author.nick}"님의 레식 계정이 "{playerName}"로 등록되었습니다.')
        
        else:
            await ctx.send(f'{userName} 계정이 존재하지 않습니다.')


def setup(bot):
    bot.add_cog(R6Stat(bot))
