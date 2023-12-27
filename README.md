# Germini
AI powered Discord Bot powered by [Google Gemini with Vision](https://ai.google.dev/docs) with other useful and fun features.

**Features ✨**
- Explains, summarizes, or suggests message responses
- It can analyze image using Gemini's vision capabilities
- It can also act as a music bot (through wavelink)

# Setup
To create and host this bot

Go to [Discord Developers Portal](https://discord.com/developers) and create your bot, you should be able to google how to make one and obtain its token :)

https://www.google.com/search?q=how+to+make+discord+bot

**Note that the bot needs to have the following permissions checked upon consent on behalf of authorization**
- Manage webhooks
- Read messages/view channels
- Send messages
- Send messages in threads (for threads support)
- Embeds
- Attach files 
- Read message history
- **Use slash commands**

For voice, it is also needed for music bot functionality:
- Connect
- Speak

## Installing host dependencies
This bot requires python with `pip` I also recommend using `venv` especially on Debian based systems.

For debian, install python and pip
```
sudo apt install python-is-python3 python3-pip python3-venv build-essential git
```
Optional dependencies would be music support
```
sudo apt install ffmpeg openjdk-17-jdk
```

Then clone this repository with `git clone https://github.com/zavocc/germini`

## Installing python packages
For Debian and package manager managed python modules, it is recommended to create a virtual environment to ensure working dependencies are met
```
cd
python -m venv python-bot
source python-bot/bin/activate
```
and install dependencies from the requirements file
`pip install -r requirements.txt`

**After it's finished, you need to uninstall `py-cord` and `discord.py` first** due to `wavelink` installs `discord.py` automatically
```
pip uninstall -y py-cord discord.py
pip install py-cord
```
# Configuration
## Obtaining the tokens
On discord developers portal page, go to your Applications where you create an app for your bot, go to "Bot" section on your selected app, and obtain the token. Note this down as viewing the token can only be seen once. 

**⚠️ Tokens are like passwords for bots, you should not store it on certain insecure channels such as public domains, public repositories, or in USB flash drive in plaintext, which otherwise the malicious party can gain control over your bot! I would recommend storing it locally somewhere secure such as credentials manager as they provide encryption as access your sensitive data**

----

After you obtained your token to power your Discord bot. You can then proceed going to [Google AI Studio](https://makersuite.google.com)

**Note: You might need to wait upon joining for waitlist**

If you already have access to Google AI Studio, you can then click the "Get API Key" in the top left corner

and click **Create API key in new project**

**⚠️ Like tokens, API keys should also not be stored on insecure channels!**

## Configuration File
Before you can start the bot, you can then fill the configuration file (named as `dev.env` with actual tokens and values:
```
TOKEN = "INSERT_TOKEN"

# Lavalink Environment Variables
ENV_LAVALINK_HOST = 127.0.0.1
ENV_LAVALINK_PORT = 2222
ENV_LAVALINK_PASS = "changeme"

# Google AI Studio API token
GOOGLE_AI_TOKEN = "INSERT_API_KEY"
```
# Starting
Then you can proceed to start the with `python3 main.py`

# Activating music cog
On this project's root directory, place the [Lavalink.jar](https://github.com/lavalink-devs/Lavalink/releases/download/4.0.0/Lavalink.jar) to `wavelink` directory
