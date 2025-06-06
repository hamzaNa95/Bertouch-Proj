import discord
from discord.ext import commands
from keep_alive import keep_alive
keep_alive()

# Your bot token
TOKEN = ""

# Command prefix
PREFIX = "&"

# Default role to remove
DEFAULT_ROLE_TO_REMOVE = "⛔ • Unverified"

# Specific roles to assign
ROLE_VB = "🌌・Sénior"
ROLE_VG = "🌸・Señorita"

# Intents setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Bot instance
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Remove default help command
bot.remove_command("help")

# In-memory log channel storage per guild (consider replacing with DB/file for persistence)
log_channels = {}

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

@bot.command(name="setlog")
@commands.has_permissions(administrator=True)
async def set_log_channel(ctx, channel: discord.TextChannel):
    log_channels[ctx.guild.id] = channel.id
    await ctx.send(f"✅ Log channel set to {channel.mention}")

async def log_verification(ctx, member: discord.Member, role_name: str):
    guild_id = ctx.guild.id
    log_channel_id = log_channels.get(guild_id)

    if log_channel_id:
        log_channel = ctx.guild.get_channel(log_channel_id)
        if log_channel:
            embed = discord.Embed(
                title="✅ Verification Log",
                description=f"**User:** {member.mention}\n**Role Assigned:** {role_name}\n**Verified By:** {ctx.author.mention}",
                color=discord.Color.green()
            )
            await log_channel.send(embed=embed)

async def assign_specific_role(ctx, member: discord.Member, role_name: str):
    guild = ctx.guild
    role_to_add = discord.utils.get(guild.roles, name=role_name)
    role_to_remove = discord.utils.get(guild.roles, name=DEFAULT_ROLE_TO_REMOVE)

    if not role_to_add:
        await ctx.send(f"❌ Role **{role_name}** not found.")
        return

    if role_to_add >= guild.me.top_role or (role_to_remove and role_to_remove >= guild.me.top_role):
        await ctx.send("❌ I don't have permission to manage one of the roles.")
        return

    if role_to_remove in member.roles:
        await member.remove_roles(role_to_remove)
        await ctx.send(f"✅ Removed default role **{role_to_remove.name}** from {member.mention}.")

    await member.add_roles(role_to_add)
    await ctx.send(f"✅ Assigned role **{role_to_add.name}** to {member.mention}.")

    # Log the verification
    await log_verification(ctx, member, role_name)

@bot.command(name="vb")
@commands.has_permissions(manage_roles=True)
async def verify_boy(ctx, member: discord.Member):
    await assign_specific_role(ctx, member, ROLE_VB)

@bot.command(name="vg")
@commands.has_permissions(manage_roles=True)
async def verify_girl(ctx, member: discord.Member):
    await assign_specific_role(ctx, member, ROLE_VG)

@verify_boy.error
@verify_girl.error
@set_log_channel.error
async def command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have the required permissions.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing arguments.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Please mention a valid user or channel.")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")

@bot.command(name="help")
async def custom_help(ctx):
    help_message = (
        "**🛠️ Available Commands:**\n\n"
        "`&vb @User` - Assigns 'Verified-Boys' role and removes 'Unverified'.\n"
        "`&vg @User` - Assigns 'Verified-Girls' role and removes 'Unverified'.\n"
        "`&setlog #channel` - Sets the channel where verification logs will be posted.\n"
    )
    await ctx.send(help_message)

# Run the bot
bot.run(TOKEN)
