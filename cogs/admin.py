import subprocess
from discord.ext import commands
from discord import File
from os import mkdir, remove
from pathlib import Path

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Execute command
    @commands.slash_command()
    async def execute(self, ctx, execute_command: str):
        """Evaluates a shell command (owner only)"""
        await ctx.response.defer()

        if ctx.author.id != 1039885147761283113:
            await ctx.respond("Only my master can do that >:(")
            return
        
        command = "".join(execute_command)
        output = subprocess.run(command, shell = True,capture_output = True)
        if output.stdout:
            # If the output exceeds 2000 characters, send it as a file
            if len(output.stdout.decode('utf-8')) > 2000:
                # Check if temp folder exists
                if not Path("temp").exists(): mkdir("temp")

                with open("temp/output.txt", "w+") as f:
                    f.write(output.stdout.decode('utf-8'))

                await ctx.respond(f"I executed `{command}` and got:", file=File("temp/output.txt", "output.txt"))

                # Delete the file
                remove("temp/output.txt")
            else:
                await ctx.respond(f"I executed `{command}` and got:")
                await ctx.send(f"```{output.stdout.decode('utf-8')}```")
        else:
            await ctx.respond(f"I executed `{command}` and got no output")

    # Evaluate command
    @commands.slash_command()
    async def evaluate(self, ctx, expression: str):
        """Evaluates a python code (owner only)"""
        await ctx.response.defer()

        if ctx.author.id != 1039885147761283113:
            await ctx.respond("Only my master can do that >:(")
            return
        
        try:
            output = eval(expression)
        except Exception as e:
            await ctx.respond(f"I executed `{expression}` and got an error:\n{e}")
            return
        
        # Check if output is a text or readable object, for now, output only supports discord-readable message data types
        if not isinstance(output, (str, int, float)):
            await ctx.respond(f"I'm sorry but I can only accept letters and numbers or string-based characters.")
            return

        # Print the output
        if output:
            await ctx.respond(f"I executed `{expression}` and got:\n```{output}```")
    
def setup(bot):
    bot.add_cog(Admin(bot))
