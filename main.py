import datetime
import discord
from discord.ext import bridge, commands
from dotenv import load_dotenv
from os import getenv, chdir
from pathlib import Path

# Go to project root directory
chdir(Path(__file__).parent.resolve())

# Load environment variables
load_dotenv("dev.env")

# Prepare playback support
playback_support=False
if Path("wavelink").exists() and Path("wavelink/Lavalink.jar").is_file() and Path("wavelink/application.yml").is_file():
    import wavelink
    playback_support=True

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot
bot = bridge.Bot(command_prefix = "$", intents = intents)

###############################################
# Initiate wavelink for music playback feature
###############################################
if playback_support:
    async def wavelink_setup():
        await bot.wait_until_ready()
        # https://wavelink.dev/en/latest/recipes.html
        ENV_LAVALINK_HOST = getenv("ENV_LAVALINK_HOST") if getenv("ENV_LAVALINK_HOST") is not None else "0.0.0.0"
        ENV_LAVALINK_PORT = getenv("ENV_LAVALINK_PORT") if getenv("ENV_LAVALINK_PORT") is not None else "2333"
        ENV_LAVALINK_PASS = getenv("ENV_LAVALINK_PASS") if getenv("ENV_LAVALINK_PASS") is not None else "youshallnotpass"

        node: wavelink.Node = wavelink.Node(
            uri=f"ws://{ENV_LAVALINK_HOST}:{ENV_LAVALINK_PORT}",
            password=ENV_LAVALINK_PASS
        )

        await wavelink.Pool.connect(
            client=bot,
            nodes=[node]
        )

###############################################
# ON READY
###############################################))
@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

    # start wavelink setup if playback support is enabled
    if playback_support:
        await wavelink_setup()

###############################################
# ON GUILD JOIN
###############################################
@bot.event
async def on_member_join(member):
    if datetime.datetime.now().hour < 12:
        await member.send(
            f'Good morning **{member.mention}**! Enjoy your stay in **{member.guild.name}**!'
        )
    elif datetime.datetime.now().hour < 18:
        await member.send(
            f'Good afternoon **{member.mention}**! Enjoy your stay in **{member.guild.name}**'
        )
    else:
        await member.send(
            f'Good evening **{member.mention}**! Enjoy your stay in **{member.guild.name}**'
        )


###############################################
# ON USER MESSAGE
###############################################
@bot.event
async def on_message(message):
    # https://discord.com/channels/881207955029110855/1146373275669241958
    await bot.process_commands(message)

    if message.author == bot.user:
       return
        
with open('commands.txt', 'r') as file:
    commands = file.read().splitlines()
    # Debug
    #print(commands)
    for command in commands:
        if command:
            if command.startswith('#'):
                continue

            # Disable voice commands if playback support is not enabled
            if command.__contains__("voice") and not playback_support:
                continue

            try:
                bot.load_extension(f'cogs.{command}')
            except Exception as e:
                print(f"\ncogs.{command} failed to load, skipping... The following error of the cog is shown below:\n")
                print(e, end="\n\n")
                continue

bot.run(getenv('TOKEN')) 
