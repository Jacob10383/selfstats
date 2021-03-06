import discord
from discord.ext import commands
import crasync
import aiohttp
import random
import json
import os


def random_color():
    color = ('#%06x' % random.randint(8, 0xFFFFFF))
    color = int(color[1:], 16)
    color = discord.Color(value=color)
    return color


class Clan:
    '''Get info about a clan'''

    def __init__(self, bot):
        self.bot = bot
        with open('data/config.json') as f:
            config = json.load(f)
            if 'TAG' not in config:
                tag = None
            else:
                tag = config['TAG']
        self.tag = os.environ.get('TAG') or tag
        self.client = clashroyale.Client(token="0ef94cfa74974bd5bf8ba09c809df0d313d562607da64482b85761dfbc7babec", is_async=True)


    @commands.command()
    async def clan(self, ctx, clan_tag=None):
        '''Returns clan info for a clan'''
        em = discord.Embed(title='Clan Info')
        em.color = random_color()

        if clan_tag is None:
            tag = self.tag
            if tag is None:
                em.description - 'Please add `TAG` to your config.'
                return await ctx.send(embed=em)
            try:
                profile = await self.client.get_profile(tag)
            except Exception as e:
                em.description = f'`{e}`'
                return await ctx.send(embed=em)
        else:
            clan_tag = clan_tag.strip('#').replace('O', '0')
            clan = await self.client.get_clan(clan_tag)

        try:
            clan = await profile.get_clan()
        except ValueError:
            em.description = 'You are not in a clan!'
            return await ctx.send(embed=em)
        except Exception as e:
            pass

        if clan.rank == 0:
            rank = 'Unranked'
        else:
            rank = f'{clan.rank}'

        if clan.clan_chest.status == 'inactive':
            tier = "Inactive"
        else:
            crowns = 0
            for m in clan.members:
                crowns += m.clan_chest_crowns
            if crowns < 70:
                tier = "0/10"
            if crowns > 70 and crowns < 160:
                tier = "1/10"
            if crowns > 160 and crowns < 270:
                tier = "2/10"
            if crowns > 270 and crowns < 400:
                tier = "3/10"
            if crowns > 400 and crowns < 550:
                tier = "4/10"
            if crowns > 550 and crowns < 720:
                tier = "5/10"
            if crowns > 720 and crowns < 910:
                tier = "6/10"
            if crowns > 910 and crowns < 1120:
                tier = "7/10"
            if crowns > 1120 and crowns < 1350:
                tier = "8/10"
            if crowns > 1350 and crowns < 1600:
                tier = "9/10"
            if crowns == 1600:
                tier = "10/10"
        em.add_field(name='Clan Chest Tier', value=tier)
        members = f'{clan.memberCount}/50'

        pushers = []
        if len(clan.members) >= 3:
            for i in range(3):
                pushers.append(
                    f"**{clan.members[i].name}**\n{clan.members[i].trophies} trophies\n#{clan.members[i].tag}")
        contributors = list(reversed(sorted(clan.members, key=lambda x: x.crowns)))

        ccc = []
        if len(clan.members) >= 3:
            for i in range(3):
                ccc.append(
                    f"**{contributors[i].name}**\n{contributors[i].crowns} crowns\n#{contributors[i].tag}")

        em.title = f'{clan.name} (#{clan.tag})'
        em.set_author(name='Clan Info', icon_url=ctx.author.avatar_url)
        em.description = clan.description

        em.add_field(name='Score', value=f'{clan.score}')
        em.add_field(name='Required Trophies', value=f'{clan.requiredScore}')
        em.add_field(name='Donations', value=f'{clan.donations}')
        em.add_field(name='Region', value=clan.region)
        em.add_field(name='Global Rank', value=rank)
        em.add_field(name='Type', value=clan.type_name)
        em.add_field(name='Clan Chest', value=chest)
        em.add_field(name='Members', value=members)
        em.add_field(name='Top Players', value='\n\n'.join(pushers))
        em.add_field(name='Top Contributors', value='\n\n'.join(ccc))
        em.set_thumbnail(url=clan.badge.image)
        em.set_footer(text='Selfbot made by SharpBit | Powered by cr-api', icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')
        await ctx.send(embed=em)


    @commands.command()
    async def clanchest(self, ctx, clan=None):
        '''Returns clan chest info for a clan'''
        em = discord.Embed(title='Clan Chest Info')
        em.color = random_color()

        if clan is None:
            tag = self.tag
            if tag is None:
                em.description = 'Please add `TAG` to your config.'
                return await ctx.send(embed=em)
            try:
                profile = await self.client.get_profile(tag)
            except Exception as e:
                em.description = f'`{e}`'
                return await ctx.send(embed=em)
        else:
            clan_tag = clan.strip('#').replace('O', '0')
            clan = await self.client.get_clan(clan_tag)

        try:
            clan = await profile.get_clan()
        except ValueError:
            em.description = 'You are not in a clan'
            return await ctx.send(embed=em)
        except Exception as e:
            pass

        chest = clan.clan_chest

        em.title = f'{clan.name} (#{clan.tag})'
        em.set_author(name='Clan Chest', icon_url=ctx.author.avatar_url)
        em.description = clan.description

        top_contributors = list(reversed(sorted(clan.members, key=lambda x: x.crowns)))
        worst_contributors = list(sorted(clan.members, key=lambda x: x.crowns))
        ccc = []
        if len(clan.members) >= 3:
            for i in range(3):
                ccc.append(
                    f"**{top_contributors[i].name}**\n{top_contributors[i].crowns} crowns\n#{top_contributors[i].tag}")

        wc = []
        if len(clan.members) >= 3:
            for i in range(3):
                wc.append(
                    f'**{worst_contributors[i].name}**\n{worst_contributors[i].crowns} crowns\n#{worst_contributors[i].tag}')

        em.add_field(name='Crowns Earned', value=f'{chest.crowns}')
        em.add_field(name='Required Crowns', value=f'{chest.required}')
        em.add_field(name='Percent Earned',
                     value=f'({(clan.clan_chest.crowns / clan.clan_chest.required) * 100:.3f}%)')
        em.add_field(name='Percent Required', value=f'{chest.percent:.3f}%')
        em.add_field(name='Top Contributors', value='\n\n'.join(ccc))
        em.add_field(name='Worst Contributors', value='\n\n'.join(wc))

        em.set_thumbnail(clan.badge_url)
        em.set_footer(text='Selfbot made by SharpBit | Powered by cr-api',
                      icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')

        await ctx.send(embed=em)

    @commands.group(invoke_without_command=True)
    async def members(self, ctx):
        '''A command group that finds the worst and best members in a clan'''
        await ctx.send(f'Proper usage: `{ctx.prefix}members <best|worst>`')

    @members.command()
    async def worst(self, ctx, clan=None):
        '''Find the worst members in a clan'''
        em = discord.Embed(title='Least Valuable Members')
        em.color = random_color()

        if clan is None:
            tag = self.tag
            if tag is None:
                em.description = 'Please add `TAG` to your config.'
                return await ctx.send(embed=em)
            try:
                profile = await self.client.get_profile(tag)
            except Exception as e:
                em.description = f'`{e}`'
                return await ctx.send(embed=em)
        else:
            clan_tag = clan.strip('#').replace('O', '0')
            clan = await self.client.get_clan(clan_tag)

        try:
            clan = await profile.get_clan()
        except ValueError:
            em.description = 'You are not in a clan'
            return await ctx.send(embed=em)
        except Exception as e:
            pass

        if len(clan.members) < 4:
            return await ctx.send('Clan must have more than 4 players for stats.')
        else:
            for m in clan.members:
                m.score = ((m.donations / 5) + (m.crowns * 10) + (m.trophies / 7)) / 3

            to_kick = sorted(clan.members, key=lambda m: m.score)[:4]

            em.description = 'Here are the least valuable members of the clan currently.'
            em.set_author(name=clan)
            em.set_thumbnail(url=clan.badge.image)
            em.set_footer(text='Selfbot made by SharpBit | Powered by cr-api.com',
                          icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')

            for m in reversed(to_kick):
                em.add_field(name=f'{m.name}, Role: {m.role_name}',
                             value=f"#{m.tag}\n{m.trophies} trophies\n{m.crowns} crowns\n{m.donations} donations")

            await ctx.send(embed=em)

    @members.command()
    async def best(self, ctx, clan=None):
        '''Find the best members in a clan'''
        em = discord.Embed(title='Most Valuable Members')
        em.color = random_color()

        if clan is None:
            tag = self.tag
            if tag is None:
                em.description - 'Please add `TAG` to your config.'
                return await ctx.send(embed=em)
            try:
                profile = await self.client.get_profile(tag)
            except Exception as e:
                em.description = f'`{e}`'
                return await ctx.send(embed=em)
        else:
            clan_tag = clan.strip('#').replace('O', '0')
            clan = await self.client.get_clan(clan_tag)

        try:
            clan = await profile.get_clan()
        except ValueError:
            em.description = 'You are not in a clan'
            return await ctx.send(embed=em)
        except Exception as e:
            pass

        if len(clan.members) < 4:
            return await ctx.send('Clan must have more than 4 players for stats.')
        else:
            for m in clan.members:
                m.score = ((m.donations / 5) + (m.crowns * 10) + (m.trophies / 7)) / 3

        best = sorted(clan.members, key=lambda m: m.score, reverse=True)[:4]

        em.description = 'Here are the most valuable members of the clan currently.'
        em.set_author(name=clan)
        em.set_thumbnail(url=clan.badge_url)
        em.set_footer(text='Selfbot made by SharpBit | Powered by cr-api.com',
                      icon_url='http://cr-api.com/static/img/branding/cr-api-logo.png')

        for m in reversed(best):
            em.add_field(name=f'{m.name}, Role: {m.role_name}',
                         value=f"#{m.tag}\n{m.trophies} trophies\n{m.crowns} crowns\n{m.donations} donations")

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Clan(bot))
