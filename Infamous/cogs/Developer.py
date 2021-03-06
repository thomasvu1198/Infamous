import copy
import datetime
import inspect
import logging
import os
import random

import aiohttp
import asyncpg
import discord
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands

from .utils import checks

logging.basicConfig(level=logging.INFO)


class Developer(commands.Cog):
    """Hidden Commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @checks.is_admin()
    async def load(self, ctx, extension_name: str):
        """Loads a cog."""

        try:
            self.bot.load_extension(f'cogs.{extension_name.title()}')
        except (AttributeError, ImportError):
            await ctx.message.add_reaction(':BlurpleX:452390303698124800')
            return
        await ctx.message.add_reaction(':BlurpleCheck:452390337382449153')

    @commands.command(hidden=True, aliases=['r'])
    @checks.is_admin()
    async def reload(self, ctx, *, module):
        """Reloads a cog."""

        try:
            self.bot.unload_extension(f'cogs.{module.capitalize()}')
            self.bot.load_extension(f'cogs.{module.capitalize()}')
        except Exception:
            await ctx.message.add_reaction(':BlurpleX:452390303698124800')
        else:
            await ctx.message.add_reaction(':BlurpleCheck:452390337382449153')

    @commands.command(hidden=True)
    @checks.is_admin()
    async def unload(self, ctx, *, module):
        """Unloads a cog."""

        try:
            self.bot.unload_extension(f'cogs.{module.capitalize()}')
        except Exception:
            await ctx.message.add_reaction(':BlurpleX:452390303698124800')
        else:
            await ctx.message.add_reaction(':BlurpleCheck:452390337382449153')

    @commands.command(hidden=True)
    @checks.is_admin()
    async def quit(self, ctx):
        """Closes the bot."""

        delta_uptime = datetime.datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        embed = discord.Embed(color=self.bot.embed_color)
        embed.set_author(name=self.bot.user, icon_url=self.bot.user.avatar_url)
        embed.description = f'Well that was a good {days}d {hours}h {minutes}m {seconds}s of activity.'
        await ctx.send(embed=embed)
        await self.bot.db.close()
        await self.bot.logout()

    @commands.command(hidden=True, aliases=['rs'])
    @checks.is_admin()
    async def restart(self, ctx):
        """Restart bot."""

        await ctx.send("Restarting..")
        os.system("python3.6 Infamous/cogs/utils/restart.py")
        await self.bot.logout()

    @commands.group(hidden=True, case_insensitive=True, invoke_without_command=True)
    async def find(self, ctx, discrim: str):
        """Find people with the same discriminator."""

        if len(discrim) > 5 or len(discrim) < 4:
            return await ctx.send('There must be 4 digits.')

        if "#" in discrim:
            discrim = discrim.strip("#")

        if discrim.isalpha():
            return await ctx.send('They must be numbers.')

        user = [str(x.name) for x in ctx.guild.members if x.discriminator == f'{discrim}']
        users = ' \n'.join(user)

        if len(user) >= 20:
            users = ', '.join(user)

        if not users:
            users = None

        embed = discord.Embed(color=self.bot.embed_color)
        embed.title = f'List of users with the #{str(discrim)} discriminator'
        embed.description = f'`{users}`'
        embed.set_footer(text=f'{len(user)} users found')
        await ctx.send(embed=embed)

    @find.command(hidden=True)
    async def user(self, ctx, id: int):
        """Shows who the user id belongs to."""

        if len(str(id)) < 17:
            return await ctx.send('That is not a user id.')

        try:
            user = ctx.guild.get_member(id)
            embed = discord.Embed(color=self.bot.embed_color)
            embed.set_author(name=user)
            embed.title = 'Discord ID'
            embed.description = id
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name='Created at', value=user.created_at.strftime('%a %b %m %Y at %I:%M %p %Z'),
                            inline=False)

            await ctx.send(embed=embed)
        except:
            user = await self.bot.fetch_user(id)
            embed = discord.Embed(color=self.bot.embed_color)
            embed.set_author(name=user)
            embed.title = 'Discord ID'
            embed.description = id
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name='Created at', value=user.created_at.strftime('%a %b %m %Y at %I:%M %p %Z'),
                            inline=False)
            await ctx.send(embed=embed)
            pass

    @commands.command(hidden=True)
    @checks.is_admin()
    async def say(self, ctx, *, text: commands.clean_content):
        """Make the bot say anything."""

        await ctx.send(text)

    @commands.command(hidden=True)
    @checks.is_admin()
    async def loop(self, ctx, time: int, command: str):
        """Executes a command for x times."""

        for x in range(time):
            x = self.bot.get_command(command)
            await ctx.invoke(x)

    @commands.group(case_insensitive=True, invoke_without_command=True, hidden=True)
    @checks.is_admin()
    async def imitate(self, ctx, user: discord.Member, *, text):
        """Use webhooks to imitate a user."""
        await ctx.message.delete()
        url = os.getenv("WEBHOOK")

        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
            await webhook.send(text, username=str(user.display_name), avatar_url=user.avatar_url)

    @imitate.command()
    @checks.is_admin()
    async def random(self, ctx, *, text):
        """Imitate a random person."""

        await ctx.message.delete()
        user = random.choice([x for x in ctx.guild.members if not x.bot])
        url = os.getenv("WEBHOOK")

        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
            await webhook.send(text, username=user.display_name, avatar_url=user.avatar_url)

    @imitate.command(hidden=True)
    @checks.is_admin()
    async def custom(self, ctx, user: int, *, text):
        """Imitate a person outside the server"""

        await ctx.message.delete()
        user = await self.bot.get_user_info(user)
        url = os.getenv("WEBHOOK")

        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
            await webhook.send(text, username=user.display_name, avatar_url=user.avatar_url)

    @commands.command(hidden=True)
    @checks.is_admin()
    async def clear(self, ctx, *, amount: int):
        """Deletes bot messages."""

        async for m in ctx.channel.history(limit=amount + 1):
            if m.author.id == self.bot.user.id:
                await m.delete()

        await ctx.send(f"Cleared `{amount}` messages!", delete_after=5)

    # Originally from Rapptz
    @commands.command(hidden=True)
    async def source(self, ctx, *, command: str = None):
        """Shows source code for each command """

        source_url = 'https://github.com/OneEyedKnight/Infamous'
        if command is None:
            return await ctx.send(source_url)

        obj = self.bot.get_command(command.replace('.', ' '))
        if obj is None:
            return await ctx.send('Could not find command.')

        src = obj.callback.__code__
        lines, firstlineno = inspect.getsourcelines(src)
        if not obj.callback.__module__.startswith('discord'):
            location = os.path.relpath(src.co_filename).replace('\\', '/')
        else:
            location = obj.callback.__module__.replace('.', '/') + '.py'
            source_url = 'https://github.com/Rapptz/discord.py'

        final_url = f'{source_url}/blob/master/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}'

        await ctx.send(final_url)

    @commands.command(hidden=True)
    @checks.is_admin()
    async def sudo(self, ctx, member: discord.Member, *, command):
        fake_msg = copy.copy(ctx.message)
        fake_msg._update(ctx.message.channel, dict(content=ctx.prefix + command))
        fake_msg.author = member
        new_ctx = await ctx.bot.get_context(fake_msg)
        await ctx.bot.invoke(new_ctx)

    @commands.command(hidden=True)
    @checks.is_admin()
    async def block(self, ctx, user: discord.Member, *, reason):
        try:
            async with ctx.db.acquire() as db:
                await db.execute("INSERT INTO blocked VALUES($1, $2)", user.id, reason)

            self.bot.blocked[user.id] = reason
        except asyncpg.exceptions.UniqueViolationError:
            return await ctx.send(f"{user.name} is already blocked")

        await ctx.send(f"Blocked {user.name} from using the bot because: {reason}")

    @commands.command(hidden=True)
    @checks.is_admin()
    async def unblock(self, ctx, user: discord.Member):
        try:
            async with ctx.db.acquire() as db:
                await db.execute("DELETE FROM blocked WHERE id=$1", user.id)

            del self.bot.blocked[user.id]
        except asyncpg.exceptions.UniqueViolationError:
            return await ctx.send(f"{user.name} was never blocked")

        await ctx.send(f"{user.name} has been unblocked.")

    @commands.command(hidden=True)
    @checks.in_testing()
    async def beta(self, ctx):
        """Toggle on or off your beta testing role."""

        role = discord.utils.get(ctx.guild.roles, id=407090515583041537)
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.message.add_reaction('➖')
        else:
            await ctx.author.add_roles(role)
            await ctx.message.add_reaction('➕')

    @commands.command(hidden=True)
    @checks.is_admin()
    async def guilds(self, ctx):
        p = []
        for page, guild in enumerate(self.bot.guilds):
            p.append(discord.Embed(color=self.bot.embed_color, description=f"Owned by: {guild.owner}",
                                   timestamp=guild.created_at)
                     .set_author(name=f"{guild.name} | Page {page+1} of {len(self.bot.guilds)}")
                     .add_field(name="Users", value=len([m for m in guild.members if not m.bot]), inline=True)
                     .add_field(name="Bots", value=len([m for m in guild.members if m.bot]), inline=True)
                     .add_field(name="Roles", value=len([m for m in guild.roles if not m.name == "@everyone"]))
                     .add_field(name="Text Channels", value=len(guild.text_channels), inline=True)
                     .add_field(name="Voice Channels", value=len(guild.voice_channels), inline=True)
                     .set_image(url=guild.icon_url_as(size=1024) or "https://imgur.com/Xy8i2UB.png")
                     .set_footer(text="Created at")
                     )

        await ctx.paginate(entries=p)

    @commands.command(hidden=True)
    @checks.is_admin()
    async def blocked(self, ctx):
        p = []
        for user in self.bot.blocked.keys():
            user_ = ctx.guild.get_member(user) or self.bot.get_user(user)
            p.append(f"**{user_}**: {self.bot.blocked[user]}")

        await ctx.send(embed=discord.Embed(description="People who have abused the bot/exploit bugs go here.",
                                           color=self.bot.embed_color)
                       .set_author(name="Infamous Blacklist")
                       .add_field(name="Blacklist", value='\n'.join(p))
                       )


def setup(bot):
    bot.add_cog(Developer(bot))
