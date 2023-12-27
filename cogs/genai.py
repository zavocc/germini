from discord.ext import commands
from os import getenv, remove, mkdir
from pathlib import Path
import google.generativeai as genai
import discord
import requests

#######################################################
# Pre-startup checks and initializations
#######################################################

if getenv("GOOGLE_AI_TOKEN") is None or getenv("GOOGLE_AI_TOKEN") == "INSERT_API_KEY":
    raise Exception("GOOGLE_AI_TOKEN is not configured in the dev.env file. Please configure it and try again.")

genai.configure(api_key=getenv("GOOGLE_AI_TOKEN"))

#######################################################
# END OF INITIALIZATION
#######################################################

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.author = "Germini"

    ###############################################
    # Ask command
    ###############################################
    @commands.slash_command()
    @discord.option(
        "attachment",
        description="Upload an image to be used as a prompt (Experimental)",
        required=False,
    )
    async def ask(self, ctx, prompt: str, attachment: discord.Attachment):
        """Ask a question to Gemini-based AI (Experimental)"""
        await ctx.response.defer()

        # DEBUG FOR MULTIMODAL SUPPORT
        #if attachment:
        #    file = await attachment.to_file()
        #    print(file)
        #    print(type(file))
        #    print(attachment.url)
        #    await ctx.respond(file=file)

        # For now we only support PNG until there is a better way to process images finding out the MIME type dynamically
        # It will go through reading the parameter model attributes and checking if it is a valid MIME type (in this case, image/png)
        # Much faster than downloading the file and checking the MIME type

        # Initialize the variable to None for default file format attachment for multimodal support
        _xfileformat = None
        if attachment:
            if attachment.content_type == "image/jpeg":
                _xfileformat = "jpeg"
            elif attachment.content_type == "image/png":
                _xfileformat = "png"
            else:
                await ctx.respond("Sorry, I can only process PNG or JPEG images!")
                return

        # Model configuration
        prompt = fr"{prompt}"
        generation_config={
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 4096,
        }
        # Use the default model if no attachment is provided
        model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config)

        # Enable multimodal support if an attachment is provided
        if attachment:
            # Create a temporary directory for the attachment
            if not Path("temp").exists(): mkdir("temp")

            _xattachments = requests.get(attachment.url, allow_redirects=True)

            # Check if processing and downloading the attachment was successful
            if _xattachments.status_code == 200:
                with open(f"temp/mmdalattachment.{_xfileformat}", "wb") as f:
                    f.write(_xattachments.content)
            else:
                await ctx.respond("Sorry, there was an error processing your attachment!")

                # Erase the file to free up resources and ensure user privacy
                remove(f"temp/mmdalattachment.{_xfileformat}")
                del(_xattachments)

                # Return to prevent further execution
                return

            # Process image data
            imagedata = [
                {
                    "mime_type": f"image/{_xfileformat}",
                    "data": Path(f"temp/mmdalattachment.{_xfileformat}").read_bytes()
                },
            ]

            # Process prompt according to the Google AI documentation
            prompt = [prompt + '\n',
                      imagedata[0],]

            # Set the model to vision pro
            model = genai.GenerativeModel(model_name="gemini-pro-vision", generation_config=generation_config)

        # Generate the answer
        answer = model.generate_content(prompt)

        # Check if the answer is valid, send a message when ValueError is raised
        try:
            answer.text
        except ValueError:
            # Print the exception and other troubleshooting info to the console for debugging purposes
            print(answer.prompt_feedback)

            # Send a message to the user
            await ctx.respond("Sorry, I can't answer that question. Try asking another question.")
            return

        # Check to see if this message is more than 2000 characters which embeds will be used for displaying the message
        embedmsg = False
        if len(answer.text) > 2000:
            embedmsg=True
            embed = discord.Embed(
                # Truncate the title to 256 characters if it exceeds beyond that since discord wouldn't allow it
                title=str(prompt)[0:256],
                description=str(answer.text),
                color=discord.Color.random()
            )
            embed.set_author(name=self.author)
            embed.set_footer(text="Responses generated by AI may not give accurate results! Double check with facts!")

        if embedmsg:
            await ctx.respond(embed=embed)
        else:
            await ctx.respond(answer.text)

        # Purge some files when needed
        if attachment: remove(f"temp/mmdalattachment.{_xfileformat}")


    ###############################################
    # Rephrase command
    ###############################################
    @commands.message_command(name="Rephrase this message")
    async def rephrase(self, ctx, message: discord.Message):
        """Rephrase this message (Context menu)"""
        await ctx.response.defer()

        # Model configuration
        prompt = fr"Can you rephrase this message to something more understandable, casual, but concise?: {str(message.content)}"
        generation_config={
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 4096,
        }

        model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config)
        answer = model.generate_content(prompt)

        # Check if the answer is valid, send a message when ValueError is raised
        try:
            answer.text
        except ValueError:
            # Print the exception and other troubleshooting info to the console for debugging purposes
            print(answer.prompt_feedback)

            # Send a message to the user
            await ctx.respond("Sorry, I can't answer that question. Try asking another question.")
            return

        await ctx.respond(f"**Result:**\n {answer.text}")

    ###############################################
    # Explain command
    ###############################################
    @commands.message_command(name="Explain this message")
    async def explain(self, ctx, message: discord.Message):
        """Understand this message (Context menu)"""
        await ctx.response.defer()

        # Model configuration
        prompt = fr"""
Can you explain about this user's message based from the following provided data: {str(message.content)}

By the way, some things to pay attention:
- If you see a discord ID along with @ symbol and a username, it means that the user is mentioned, therefore you should ignore it.
- Only extract and explain the message content, not the message ID, author, channel, etc.
- Summarize key points and explain it in a way that is understandable to the user.
"""
        generation_config={
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 4096,
        }

        model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config)
        answer = model.generate_content(prompt)

        # Check if the answer is valid, send a message when ValueError is raised
        try:
            answer.text
        except ValueError:
            # Print the exception and other troubleshooting info to the console for debugging purposes
            print(answer.prompt_feedback)

            # Send a message to the user
            await ctx.respond("Sorry, I can't explain that message. I'm still learning!")
            return

        await ctx.author.send(f"> {message.content}\n {answer.text}")
        await ctx.respond("📨 Check your DMs!")

    ###############################################
    # Suggestions command
    ###############################################
    @commands.message_command(name="Suggest a response")
    async def suggest(self, ctx, message: discord.Message):
        """Suggest a response based on this message (Context menu)"""
        await ctx.response.defer()

        # Model configuration
        prompt = fr"""
What can I respond to this message?
Draft 2-3 messages, send it in a markdown format, bullet, and 1 suggestions per tone mentioned.
Message content: {str(message.content)}
"""

        generation_config={
            "temperature": 0.4,
            "top_p": 1,
            "top_k": 32,
            "max_output_tokens": 4096,
        }

        model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config)
        answer = model.generate_content(prompt)

        # Check if the answer is valid, send a message when ValueError is raised
        try:
            answer.text
        except ValueError:
            # Print the exception and other troubleshooting info to the console for debugging purposes
            print(answer.prompt_feedback)

            # Send a message to the user
            await ctx.respond("Sorry, I can't answer that question. Try asking another question.")
            return

        # To protect privacy, send the message to the user
        await ctx.author.send(f"> {message.content}\n**Here you can use these message:**\n\n{answer.text}")
        await ctx.respond("📨 Check your DMs!")

def setup(bot):
    bot.add_cog(AI(bot))
