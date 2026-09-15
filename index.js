import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
import asyncio
import os
from dotenv import load_dotenv
 
load_dotenv()
 
# ==================== CONFIG ====================
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "1547715438396444742"))
CLAIM_CHANNEL_ID = 1549158153231540404
CUSTOMER_ROLE_NAME = "Customer"
MANAGER_ROLE_ID = 986267425345519737
CLOSE_TIMEOUT_MINUTES = 35
 
# ==================== PRODUCTS ====================
PRODUCTS = {
    "nexy_temp": {"name": "Nexy Temp Spoofer", "price": "$15", "desc": "Temporary HWID spoofer — memory-only", "emoji": "📗"},
    "nexy_perm": {"name": "Nexy Perm Spoofer", "price": "$35", "desc": "Permanent HWID spoofer — registry + firmware", "emoji": "📘"},
    "onyx_fn": {"name": "Onyx FN", "price": "$25", "desc": "Premium Fortnite cheat — aimbot, ESP, kernel", "emoji": "🎮"},
    "onyx_r6": {"name": "Onyx R6", "price": "$25", "desc": "Premium R6 cheat — aimbot, ESP, anti-aim", "emoji": "🛡️"},
    "onyx_apex": {"name": "Onyx Apex", "price": "$25", "desc": "Premium Apex cheat — aimbot, ESP, radar", "emoji": "⚡"},
    "fortnite_private": {"name": "Fortnite Private", "price": "$30", "desc": "Dedicated Fortnite cheat — advanced features", "emoji": "🔥"},
    "valorant_full": {"name": "Valorant Full", "price": "$40", "desc": "Valorant cheat + Vanguard kernel bypass", "emoji": "💀"},
}
 
GUIDES = {
    "perm_spoofer": {
        "title": "📘 Nexy Perm Spoofer — Complete Guide",
        "content": (
            "**Permanent HWID Spoofer Setup**\n\n"
            "**Step 1: Download & Run**\n"
            "1. Download Nexy Perm from our website\n"
            "2. Run as Administrator (right-click → Run as Admin)\n"
            "3. Wait for the GUI to load\n\n"
            "**Step 2: Execute Spoof**\n"
            "1. Click 'Spoof Hardware'\n"
            "2. Wait for completion (30-60 seconds)\n"
            "3. You'll see a green checkmark when done\n\n"
            "**Step 3: Finalize**\n"
            "1. Restart your computer (required)\n"
            "2. Your HWID is now permanently spoofed\n\n"
            "**What Gets Changed:**\n"
            "✓ MAC Address\n"
            "✓ Disk Serial Number\n"
            "✓ Motherboard ID\n"
            "✓ BIOS Serial\n"
            "✓ Registry entries (HDD/SSD ID)\n\n"
            "**Compatible Anticheat:**\n"
            "✓ EAC (Easy Anti-Cheat)\n"
            "✓ BattlEye\n"
            "✓ Vanguard\n\n"
            "**How to Revert:**\n"
            "Run Nexy Perm again → click 'Revert' → Restart PC"
        )
    },
    "temp_spoofer": {
        "title": "📗 Nexy Temp Spoofer — Complete Guide",
        "content": (
            "**Temporary HWID Spoofer Setup**\n\n"
            "**What is Temp Spoof?**\n"
            "Changes your HWID in memory only. Resets on restart. No permanent changes.\n\n"
            "**How to Use:**\n"
            "1. Run Nexy Temp as Administrator\n"
            "2. Click 'Enable Temporary Spoof'\n"
            "3. Launch your game immediately after\n"
            "4. HWID is spoofed for this session\n"
            "5. Restart PC to reset\n\n"
            "**Auto-resets on reboot** — no manual revert needed\n\n"
            "**Best For:**\n"
            "✓ Testing before permanent spoof\n"
            "✓ Short gaming sessions\n"
            "✓ Multiple accounts on same PC\n"
            "✓ Trying undetected cheats safely\n\n"
            "**⚠️ IMPORTANT:**\n"
            "❌ Temp spoof does NOT work for Valorant (Vanguard blocks it)\n"
            "✓ Works for Fortnite, R6, Apex, Rust"
        )
    },
    "fortnite_ban": {
        "title": "🎮 Fortnite Ban Recovery — Full Guide",
        "content": (
            "**Fortnite HWID Ban Recovery**\n\n"
            "**Step 1: Spoof Your Hardware**\n"
            "1. Download & run Nexy Perm\n"
            "2. Click 'Spoof Hardware'\n"
            "3. Restart your computer\n\n"
            "**Step 2: Create New Account**\n"
            "1. Create a **new Epic account** with:\n"
            "   - Fresh email address (not old one)\n"
            "   - New phone number\n"
            "2. Verify email + phone\n\n"
            "**Step 3: Install & Play**\n"
            "1. Install Fortnite fresh\n"
            "2. Wait 24 hours before playing (recommended)\n"
            "3. Use your spoofed account\n"
            "4. Never reuse old hardware IDs\n\n"
            "**Account Ban vs HWID Ban:**\n"
            "• Account ban = only that account (can appeal or switch account)\n"
            "• HWID ban = your hardware (must spoof)\n\n"
            "**For Undetected Gameplay:**\n"
            "Use **Onyx FN** — kernel-level, undetected cheat"
        )
    },
    "r6_ban": {
        "title": "🛡️ Rainbow Six Siege Ban Recovery — Full Guide",
        "content": (
            "**R6 BattlEye Ban Recovery**\n\n"
            "**Why R6 is Aggressive:**\n"
            "R6 uses BattlEye — one of the toughest anticheat systems. HWID bans are permanent.\n\n"
            "**Step 1: Spoof HWID**\n"
            "1. Run Nexy Perm as Administrator\n"
            "2. Click 'Spoof Hardware'\n"
            "3. Restart your computer\n\n"
            "**Step 2: Clear BattlEye Cache**\n"
            "1. Delete: `C:\\Program Files (x86)\\Rainbow Six Siege\\BattlEye`\n"
            "2. Reinstall the BattlEye launcher (it auto-reinstalls on launch)\n\n"
            "**Step 3: New Account**\n"
            "1. Create new Uplay/Steam account\n"
            "2. Verify with fresh email\n"
            "3. Install R6 from scratch\n\n"
            "**Step 4: Spoof Before Injecting**\n"
            "⚠️ CRITICAL: Always spoof BEFORE injecting cheats\n"
            "Never inject without active spoof\n\n"
            "**For Undetected Gameplay:**\n"
            "Use **Onyx R6** — kernel-level R6 cheat, built for BattlEye bypass"
        )
    },
    "valorant_ban": {
        "title": "💀 Valorant Vanguard Ban Recovery — Full Guide",
        "content": (
            "**Valorant/Vanguard Ban Recovery**\n\n"
            "**Why Valorant is Hardest:**\n"
            "Vanguard is kernel-level anticheat. Extremely aggressive. Permanent bans.\n\n"
            "**Step 1: Spoof Hardware (Aggressive)**\n"
            "1. Run Nexy Perm as Administrator\n"
            "2. Click 'Spoof Hardware'\n"
            "3. Restart PC\n\n"
            "**Step 2: Clear Cached IDs (Optional but Recommended)**\n"
            "1. Backup your data\n"
            "2. Reinstall Windows (clears all cached hardware IDs)\n"
            "3. This is the safest way to defeat Vanguard\n\n"
            "**Step 3: Create New Riot Account**\n"
            "1. New Riot account (not linked to old)\n"
            "2. Fresh email address\n"
            "3. Fresh phone number\n"
            "4. Verify both\n\n"
            "**Step 4: Fresh Install**\n"
            "1. Install Valorant fresh\n"
            "2. Play on spoofed hardware\n\n"
            "⚠️ **IMPORTANT:**\n"
            "❌ DO NOT use Temp Spoof for Valorant — Vanguard will detect it\n"
            "✓ Use Nexy Perm (permanent spoof)\n✓ Use Valorant Full for undetected gameplay"
        )
    },
    "getting_started": {
        "title": "🚀 Getting Started with Nexy — Quick Start",
        "content": (
            "**Welcome to Nexy Cheats!**\n\n"
            "**What We Offer:**\n"
            "✓ Kernel-level cheats (undetected)\n"
            "✓ HWID spoofers (permanent & temporary)\n"
            "✓ 24/7 customer support\n"
            "✓ Regular updates after game patches\n\n"
            "**Getting Started:**\n\n"
            "**1️⃣ Browse Products**\n"
            "→ `/cheats list` — see all products\n"
            "→ `/cheats guide <product>` — get detailed guide\n\n"
            "**2️⃣ Purchase**\n"
            "→ Click product link from shop\n"
            "→ Complete payment\n"
            "→ Get download link instantly\n\n"
            "**3️⃣ Setup**\n"
            "→ Run installer as Administrator\n"
            "→ Follow the product guide\n"
            "→ For HWID bans, spoof BEFORE playing\n\n"
            "**4️⃣ Need Help?**\n"
            "→ `/support` — open support ticket\n"
            "→ Our team responds in <30 minutes\n\n"
            "**Status:**\n"
            "🟢 All products 100% Undetected right now"
        )
    }
}
 
# ==================== STATE ====================
closing_timers = {}
 
# ==================== HELPER FUNCTIONS ====================
def has_customer_role(member: discord.Member) -> bool:
    return any(role.name == CUSTOMER_ROLE_NAME for role in member.roles)
 
def get_claim_link() -> str:
    return f"https://discord.com/channels/{GUILD_ID}/{CLAIM_CHANNEL_ID}"
 
# ==================== TICKET SYSTEM ====================
def is_ticket_channel(channel_name: str) -> bool:
    return channel_name.startswith("support-") or channel_name.startswith("buy-")
 
async def close_timer(channel_id: int, guild_id: int, channel_name: str):
    await asyncio.sleep(CLOSE_TIMEOUT_MINUTES * 60)
    guild = bot.get_guild(guild_id)
    if not guild:
        return
    channel = guild.get_channel(channel_id)
    if not channel:
        return
    if closing_timers.get(channel_id) != asyncio.current_task():
        return
    try:
        await channel.send(f"⏰ Ticket **{channel_name}** inactive for {CLOSE_TIMEOUT_MINUTES} min — closing.")
        await asyncio.sleep(3)
        await channel.delete()
    except:
        pass
    finally:
        closing_timers.pop(channel_id, None)
 
def reset_close_timer(channel_id: int, guild_id: int, channel_name: str):
    if not is_ticket_channel(channel_name):
        return
    if channel_id in closing_timers:
        closing_timers[channel_id].cancel()
    task = asyncio.create_task(close_timer(channel_id, guild_id, channel_name))
    closing_timers[channel_id] = task
 
# ==================== BOT SETUP ====================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)
 
@bot.event
async def on_ready():
    print(f"✅ {bot.user} online")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Sync error: {e}")
 
# ==================== ROLE CHECK DECORATOR ====================
def role_required():
    async def predicate(interaction: discord.Interaction) -> bool:
        if not has_customer_role(interaction.user):
            embed = discord.Embed(
                title="❌ Customer Role Required",
                description=(
                    f"You don't have the **Customer** role yet.\n\n"
                    f"**[Click here to claim it]({get_claim_link()})**\n\n"
                    f"Once you have the role, you can access all commands."
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True
    return app_commands.check(predicate)
 
# ==================== SLASH COMMANDS ====================
@bot.tree.command(name="cheats", description="Browse Nexy products and guides")
@app_commands.describe(
    action="Choose action",
    product="Product name (if choosing guide)"
)
@app_commands.choices(action=[
    app_commands.Choice(name="List all products", value="list"),
    app_commands.Choice(name="Get guide for product", value="guide"),
])
@role_required()
async def cheats(interaction: discord.Interaction, action: str, product: str = None):
    if action == "list":
        embed = discord.Embed(
            title="🔥 Nexy Product Catalog",
            description="All products kernel-level and undetected",
            color=discord.Color.red()
        )
        for key, prod in PRODUCTS.items():
            embed.add_field(
                name=f"{prod['emoji']} {prod['name']}",
                value=f"**{prod['price']}** — {prod['desc']}",
                inline=False
            )
        embed.set_footer(text="Use /cheats guide <product_name> for detailed guides")
        await interaction.response.send_message(embed=embed)
    
    elif action == "guide":
        if not product:
            await interaction.response.send_message("❌ Please specify a product name!", ephemeral=True)
            return
        
        prod_key = product.lower().replace(" ", "_")
        if prod_key not in GUIDES:
            available = ", ".join(GUIDES.keys())
            await interaction.response.send_message(
                f"❌ Guide not found for '{product}'\n\n**Available guides:**\n{available}",
                ephemeral=True
            )
            return
        
        guide = GUIDES[prod_key]
        embed = discord.Embed(
            title=guide["title"],
            description=guide["content"],
            color=discord.Color.blue()
        )
        embed.set_footer(text="Need help? Use /support to open a ticket")
        await interaction.response.send_message(embed=embed)
 
@bot.tree.command(name="status", description="Check product status")
@role_required()
async def status(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🟢 Status — All Products Undetected",
        description="Last checked: Just now",
        color=discord.Color.green()
    )
    embed.add_field(name="🎮 Fortnite", value="🟢 Onyx FN — Undetected\n🟢 Fortnite Private — Undetected", inline=False)
    embed.add_field(name="🛡️ R6 Siege", value="🟢 Onyx R6 — Undetected", inline=False)
    embed.add_field(name="💀 Valorant", value="🟢 Valorant Full — Undetected", inline=False)
    embed.add_field(name="⚡ Apex", value="🟢 Onyx Apex — Undetected", inline=False)
    embed.add_field(name="🗂️ Spoofers", value="🟢 Nexy Perm — Undetected\n🟢 Nexy Temp — Undetected", inline=False)
    embed.set_footer(text="All products updated within 2 hours of game patches")
    await interaction.response.send_message(embed=embed)
 
@bot.tree.command(name="support", description="Open a support ticket")
@role_required()
async def support(interaction: discord.Interaction):
    guild = interaction.guild
    user = interaction.user
    username = user.name.lower().replace(" ", "_")
    channel_name = f"support-{username}"
    
    for ch in guild.text_channels:
        if ch.name == channel_name:
            embed = discord.Embed(
                title="⚠️ Ticket Already Open",
                description=f"You already have an active ticket: {ch.mention}",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
    
    try:
        await interaction.response.defer(ephemeral=True)
        
        ticket_channel = await guild.create_text_channel(
            channel_name,
            topic=f"Support ticket for {user.mention} ({user.id})"
        )
        
        embed = discord.Embed(
            title="🎫 Support Ticket Opened",
            description=f"Hi {user.mention}! 👋\n\nOur support team will respond within 30 minutes.\n\n**Please describe your issue below:**",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Ticket: {channel_name}")
        await ticket_channel.send(embed=embed)
        
        class SupportActions(ui.View):
            @ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red)
            async def close(self, interaction: discord.Interaction, button: ui.Button):
                embed = discord.Embed(
                    title="Closing Ticket...",
                    description="This channel will be deleted in 5 seconds.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed)
                await asyncio.sleep(5)
                await ticket_channel.delete()
            
            @ui.button(label="📞 Need Manager Help", style=discord.ButtonStyle.blurple)
            async def escalate(self, interaction: discord.Interaction, button: ui.Button):
                manager_role = guild.get_role(MANAGER_ROLE_ID)
                if not manager_role:
                    await interaction.response.send_message("❌ Manager role not found", ephemeral=True)
                    return
                
                embed = discord.Embed(
                    title="🔔 Manager Escalation",
                    description=f"{manager_role.mention}\n\n**{user.mention}** needs manager assistance.\n\n**Please wait** — a manager will be with you shortly.",
                    color=discord.Color.gold()
                )
                await ticket_channel.send(embed=embed)
                
                await interaction.response.send_message(
                    "✅ Manager notified — please wait for response",
                    ephemeral=True
                )
        
        await ticket_channel.send("Use the buttons below for ticket management.", view=SupportActions())
        reset_close_timer(ticket_channel.id, guild.id, channel_name)
        
        embed = discord.Embed(
            title="✅ Ticket Created",
            description=f"Your support ticket has been opened: {ticket_channel.mention}",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to create ticket: {str(e)}",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
 
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    channel_name = message.channel.name
    if is_ticket_channel(channel_name):
        reset_close_timer(message.channel.id, message.guild.id, channel_name)
    
    await bot.process_commands(message)
 
if __name__ == "__main__":
    bot.run(TOKEN)
