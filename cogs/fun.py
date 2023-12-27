from discord.ext import commands
from discord import Member
from typing import Union

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mimic(self, ctx, user: Union[Member, int], *body):
        """Mimic a user!"""
        if isinstance(user, int):
            user = await self.bot.fetch_user(user)    
        avatar_url = user.avatar.url if user.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"

        webhook = await ctx.channel.create_webhook(name="Mimic Command")

        if not body:
            await ctx.respond("Please specify a message to mimic!")
            return
        message = " ".join(body)
        await webhook.send(content=message, username=user.name, avatar_url=avatar_url)
        await webhook.delete()
        
        await ctx.respond("Done!", delete_after=1)

    @mimic.error
    async def on_command_error(self, ctx: commands.Context, error: commands.MissingRequiredArgument):
        await ctx.respond("Please specify a valid discord user (or user id) and message to mimic! Syntax: `$mimic <user/user id> <message>`")


def setup(bot):
    bot.add_cog(Fun(bot))
