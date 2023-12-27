import discord
import wavelink
from discord.ext import commands

# For now everything is taken from https://pypi.org/project/WavelinkPycord/ but "class"ified bad pun intended
class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_user = None

    @commands.slash_command()
    @commands.guild_only()
    async def play(self, ctx: commands.Context, search: str) -> None:
        """Simple play command."""

        try:
            if not ctx.voice_client:
                vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            else:
                vc: wavelink.Player = ctx.voice_client
        except AttributeError:
            return await ctx.respond('Please join a voice channel.')

        # This overrides the track playing so we detect if there is a track playing and is not a person who queued it
        if vc.playing:
            if ctx.author.guild_permissions.administrator == False and ctx.guild.owner_id != ctx.author.id:
                if self.current_user != ctx.author.id:
                    return await ctx.respond('You are not the one who queued this track.')

        # Search for tracks using the given query and assign it to the tracks variable
        try:
            tracks = await wavelink.Playable.search(search, source=wavelink.TrackSource.YouTube)
        except discord.ext.commands.errors.MissingRequiredArgument:
            await ctx.respond('Please specify a search query.')
            return

        # If there are no tracks found, return a message
        if not tracks:
            await ctx.respond(f'No tracks found with query: `{search}`')
            return
        
        # If there are tracks found, play the first search result
        track = tracks[0]

        await vc.play(track)
        await ctx.respond(f'▶️ Playing track: **{track.title}**')

        # Temporarily save user id to check if the user is the one who queued the track
        # For moral purposes

        # Set the user currently playing the track to the class-level variable
        self.current_user = ctx.author.id

    @commands.slash_command()
    @commands.guild_only()
    async def playerqueue(self, ctx: commands.Context):
        """Show the player queue state."""
        vc: wavelink.Player = ctx.voice_client
    
        user = await self.bot.fetch_user(self.current_user)
        avatar_url = user.avatar.url if user.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"

        embed = discord.Embed(
            title='Now Playing',
            description=f'[{vc.current.title}]({vc.current.uri})',
            color=discord.Color.red()
        )

        embed.add_field(name='Playing on', value=vc.channel)
        # Player status
        if not vc.paused:
            embed.add_field(name='Status', value='Playing')
        else:
            embed.add_field(name='Status', value='Paused')

        # Add fields for the music author, duration, and requester
        embed.add_field(name='Author', value=vc.current.author)

        # Obtain the duration of the track and convert it to minutes and seconds
        # _ is a throwaway variable since it errors about unsupported operand types
        seconds, _ = divmod(vc.current.length, 1000)
        minutes, seconds = divmod(seconds, 60)
    
        embed.add_field(name='Duration', value=f'{minutes:02d}:{seconds:02d}')
        embed.add_field(name='URL', value=vc.current.uri)

        embed.set_footer(text=(vc.current.source if not str(vc.current.source).__contains__("Unknown") else "HTTP playback"))
        embed.set_author(name=user.name, icon_url=avatar_url)
        await ctx.respond(embed=embed)

    @commands.slash_command()
    @commands.guild_only()
    async def pause(self, ctx: commands.Context):
        """Pause the currently playing track."""
        vc: wavelink.Player = ctx.voice_client

        # We are not rude people
        if ctx.author.guild_permissions.administrator == False and ctx.guild.owner_id != ctx.author.id:
            if self.current_user != ctx.author.id:
                return await ctx.respond('You are not the one who queued this track.')
                
        # Check if there's even a voice client connected
        try:
            vc.connected
        except AttributeError:
            return await ctx.respond('Not currently connected to a voice channel.')
        
        # Check if we are playing a track before pausing
        if not vc.playing or vc.paused: return await ctx.respond('There is no track currently playing.')
        
        # Pause the track
        await vc.pause(True)
        await ctx.respond(f'⏸️ Paused track: **{vc.current.title}**')

    @commands.slash_command()
    @commands.guild_only()
    async def resume(self, ctx: commands.Context):
        """Resume the currently paused track."""
        vc: wavelink.Player = ctx.voice_client

        # We are not rude people
        if ctx.author.guild_permissions.administrator == False and ctx.guild.owner_id != ctx.author.id:
            if self.current_user != ctx.author.id:
                return await ctx.respond('You are not the one who queued this track.')

        # Check if there's even a voice client connected
        try:
            vc.connected
        except AttributeError:
            return await ctx.respond('Not currently connected to a voice channel.')

        if not vc.paused: return await ctx.respond('Track is currently not paused.')

        # Resume the track
        await vc.pause(False)
        await ctx.respond(f'▶️ Resumed track: **{vc.current.title}**')

    @commands.slash_command()
    @commands.guild_only()
    async def stop(self, ctx: commands.Context):
        vc: wavelink.Player = ctx.voice_client

        # Lets not be selfish and allow the user who queued the track to stop it... Only the guild owner can stop the track in case he playing porn or something
        if ctx.author.guild_permissions.administrator == False and ctx.guild.owner_id != ctx.author.id:
            if self.current_user != ctx.author.id:
                return await ctx.respond('You are not the one who queued this track.')

        # Check if there's even a voice client connected
        try:
            vc.connected
        except AttributeError:
            return await ctx.respond('Not currently connected to a voice channel.')

        # Store the title in the variable before stopping the track to notifiy the user since once it's stopped, vc.current.title will be None
        current_track_title = vc.current.title
        await vc.stop()
        await ctx.respond(f'⏹️ Stopped track: **{current_track_title}**')

    @commands.slash_command()
    @commands.guild_only()
    async def disconnect(self, ctx: commands.Context) -> None:
        """Simple disconnect command.

        This command assumes there is a currently connected Player.
        """
        vc: wavelink.Player = ctx.voice_client

        # Disconnect only if the user initiated the connection, server administrator or the guild owner
        if ctx.author.guild_permissions.administrator == False and ctx.guild.owner_id != ctx.author.id:
            if self.current_user != ctx.author.id:
                return await ctx.respond('You are not the one who queued this track or has insufficent admin permissions to do this.')

        # Check if there's even a voice client connected
        try:
            vc.connected
        except AttributeError:
            return await ctx.respond('Not currently connected to a voice channel.')

        # Check if we are playing a track before disconnecting
        if vc.playing and vc.connected:
            # Store the title in the variable before stopping the track to notifiy the user since once it's stopped, vc.current.title will be None
            current_track_title = vc.current.title

            await vc.stop()
            await ctx.respond(f'Stopped track: **{current_track_title}**')

        try:
            await vc.disconnect()
            await ctx.respond('Disconnected.')
        except AttributeError:
            await ctx.respond('Not currently connected to a voice channel.')

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("You can only use this command in a server.")
        else:
            raise error

def setup(bot):
    bot.add_cog(Voice(bot))
