import discord
from discord.ext import commands
from discord import ui
import re
import asyncio
import random
import os
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIG ====================
TOKEN = os.getenv("DISCORD_TOKEN")
BOT_NAME = "Nexy AI Assistant"
GUILD_ID = int(os.getenv("GUILD_ID", "1547715438396444742"))
CUSTOMER_ROLE_ID = int(os.getenv("CUSTOMER_ROLE_ID", "0")) or None

HUMAN_SUPPORT_ROLE_ID = 1547715438438256751
REVIEW_CHANNEL_ID = 1547715439700746265
CLAIM_CHANNEL_ID = 1549158153231540404
REVIEW_LINK = f"https://discord.com/channels/{GUILD_ID}/{REVIEW_CHANNEL_ID}"

CLOSE_TIMEOUT_MINUTES = 35

TICKET_PREFIXES = ["support-", "buy-"]
CASUAL_CHANNELS = ["chat", "general", "lounge", "off-topic", "general-chat"]
CASUAL_PREFIXES = ["chat-", "general-"]

def is_casual_channel(channel_name: str) -> bool:
    return channel_name in CASUAL_CHANNELS or any(channel_name.startswith(p) for p in CASUAL_PREFIXES)

def is_ticket_channel(channel_name: str) -> bool:
    return any(channel_name.startswith(p) for p in TICKET_PREFIXES)

def has_customer_role(member: discord.Member) -> bool:
    if not CUSTOMER_ROLE_ID:
        return False
    return any(r.id == CUSTOMER_ROLE_ID for r in member.roles)

# ==================== STATE ====================
closing_timers = {}
escalated_channels = set()
user_memory = {}

def get_user_memory(user_id: int) -> dict:
    if user_id not in user_memory:
        user_memory[user_id] = {"greeted": False, "claim_notice_sent": False}
    return user_memory[user_id]

# ==================== GREETING ====================
def get_greeting(name: str) -> str:
    return random.choice([
        f"Yo {name}! How can I help you today?",
        f"Hey {name}! What's on your mind?",
        f"Yo {name}! Ready to drop some knowledge. What do you need?",
        f"What's up {name}! Got a question or just vibin?",
        f"{name}! What's the play today?",
    ])

# ==================== PRODUCT CATALOG ====================
NEXY_CATALOG = f"""
**🛒 {BOT_NAME} — Product Catalog**

**🟢 All products are 100% Undetected.**

---

**🎮 Nyrex — Fortnite Cheat**
• Aimbot, ESP, Radar, and more
• Prices: €5.99 (1D) | €9.99 (3D) | €20.99 (7D) | €34.00 (30D) | €199.99 (Lifetime)

**🎯 Nyrex R6 — Rainbow Six Siege Cheat**
• Aimbot, ESP, Anti-aim, BattlEye bypass
• Prices: €6.99 (1D) | €15.99 (3D) | €35.99 (7D) | €69.99 (30D)

**🛡️ Perm Spoofer — Permanent HWID Spoofer**
• Changes disk serial, MAC, motherboard, TPM, and ARP
• Prices: €24.00 (One-time) | €34.00 (+TPM+Disk) | €64.00 (Lifetime + TPM + Disk + ARP)

**⚡ Temp Spoofer — Temporary HWID Spoofer**
• Memory-only — resets on reboot
• Prices: €4.99 (1D) | €15.99 (7D) | €24.99 (Lifetime)

---

📌 **Website:** https://nexycheats.cc
💬 **Need help?** Just describe your issue.
"""

# ==================== AI RESPONSES ====================
NEXY_AI = {
    "catalog": {
        "keywords": ["catalog", "products", "what do you offer", "product list", "what cheats", "what spoofers"],
        "response": NEXY_CATALOG
    },
    "nyrex": {
        "keywords": ["nyrex", "nyrex cheat", "fortnite cheat"],
        "response": """
**🎮 Nyrex — Premium Fortnite Cheat**

**What it does:**
• **Aimbot** — smooth, human-like locking
• **ESP/Wallhack** — see enemies, loot, and traps through walls
• **Radar** — track enemies in real-time
• **Private driver** available for lifetime users

**Pricing:**
• €5.99 (1D) | €9.99 (3D) | €20.99 (7D) | €34.00 (30D) | €199.99 (Lifetime)

🟢 **Status:** Undetected on the latest patch.
"""
    },
    "nyrex r6": {
        "keywords": ["nyrex r6", "r6 cheat", "rainbow six cheat", "nyrex r6x"],
        "response": """
**🎯 Nyrex R6 — Premium Rainbow Six Siege Cheat**

**What it does:**
• **Aimbot** with bone prediction
• **ESP** — see enemies, gadgets, and traps
• **Anti-aim** — avoid headshots
• **BattlEye bypass** built in

**Pricing:**
• €6.99 (1D) | €15.99 (3D) | €35.99 (7D) | €69.99 (30D)

🟢 **Status:** Undetected on BattlEye.
"""
    },
    "perm spoofer": {
        "keywords": ["perm spoofer", "permanent spoofer", "perm spoof"],
        "response": """
**🛡️ Perm Spoofer — Permanent HWID Solution**

**What it changes:**
• Disk Serial Number
• MAC Address
• Motherboard ID
• TPM
• ARP

**Pricing:**
• €24.00 (One-time) | €34.00 (+TPM+Disk) | €64.00 (Lifetime + TPM + Disk + ARP)

🟢 **Status:** Undetected on EAC, BattlEye, and Vanguard.
"""
    },
    "temp spoofer": {
        "keywords": ["temp spoofer", "temporary spoofer", "temp spoof"],
        "response": """
**⚡ Temp Spoofer — Temporary HWID Solution**

Changes your HWID in memory only — resets on reboot.

**Pricing:**
• €4.99 (1D) | €15.99 (7D) | €24.99 (Lifetime)

🟢 **Status:** Undetected on all games.
"""
    },
    "fortnite ban": {
        "keywords": ["fortnite ban", "banned from fortnite", "epic ban", "fortnite banned"],
        "response": """
**🚫 Banned from Fortnite? Let's fix that.**

**Step 1:** Run **Perm Spoofer** to change your hardware IDs.
**Step 2:** Create a new Epic account with fresh email and phone number.
**Step 3:** Wait 24 hours before playing.
**Step 4:** Never reuse old hardware IDs.

💡 **Did you get a ban message from Epic? What did it say?**
"""
    },
    "r6 ban": {
        "keywords": ["r6 ban", "rainbow six ban", "battleye ban", "r6 banned"],
        "response": """
**🚫 Banned from R6? Here's the fix.**

**Step 1:** Run **Perm Spoofer** to change your HWID.
**Step 2:** Delete the BattlEye folder in your game directory.
**Step 3:** Create a new Uplay/Steam account.
**Step 4:** Spoof before injecting every time.

💡 **Was it a permanent ban or a temporary one?**
"""
    },
    "pricing": {
        "keywords": ["price", "prices", "cost", "how much", "€", "euro"],
        "response": """
**💰 Nexy Pricing — All Products**

**🎮 Nyrex** — €5.99 (1D) | €9.99 (3D) | €20.99 (7D) | €34.00 (30D) | €199.99 (Lifetime)

**🎯 Nyrex R6** — €6.99 (1D) | €15.99 (3D) | €35.99 (7D) | €69.99 (30D)

**🛡️ Perm Spoofer** — €24.00 (One-time) | €34.00 (+TPM+Disk) | €64.00 (Lifetime)

**⚡ Temp Spoofer** — €4.99 (1D) | €15.99 (7D) | €24.99 (Lifetime)

🟢 All products undetected.
"""
    },
    "benefits": {
        "keywords": ["benefits", "advantage", "why nexy", "why choose nexy"],
        "response": """
**🔥 Why Nexy?**

• 🟢 100% Undetected — kernel-level protection
• ⚡ Fast Updates — within hours of game patches
• 🛡️ Premium Spoofers — temp and perm options
• 🎮 Top-tier Cheats — Nyrex and Nyrex R6
• 💬 24/7 Support — real humans when you need them
"""
    },
    "website": {
        "keywords": ["website", "nexy website", "nexycheats", "url", "link"],
        "response": "🌐 Our website is **https://nexycheats.cc** — products, status, reviews, and more."
    },
    "what is nexy": {
        "keywords": ["what is nexy", "tell me about nexy", "what does nexy do"],
        "response": """
**Nexy — Premium Cheat & Spoofer Provider**

• **Nyrex** — Fortnite cheat
• **Nyrex R6** — R6 cheat
• **Perm Spoofer** — Permanent HWID spoofer
• **Temp Spoofer** — Temporary HWID spoofer

All products 🟢 100% Undetected.
🌐 **Website:** https://nexycheats.cc
"""
    },
    "detected status": {
        "keywords": ["is nexy detected", "detected right now", "undetected", "safe to inject"],
        "response": """
**🟢 All Nexy Products Are Undetected**

| Product | Status |
|---------|--------|
| Nyrex | 🟢 Undetected |
| Nyrex R6 | 🟢 Undetected |
| Perm Spoofer | 🟢 Undetected |
| Temp Spoofer | 🟢 Undetected |

Updates pushed within hours of any game patch.
"""
    },
}

FOLLOW_UPS = {
    "fortnite ban": "Did you get a ban message from Epic? What did it say?",
    "r6 ban": "Was it a permanent ban or a temporary one?",
}

# ==================== RESPONSE HELPERS ====================
def get_nexy_response(query: str):
    q = query.lower()
    best = None
    best_score = 0
    for key, data in NEXY_AI.items():
        for kw in data["keywords"]:
            if kw in q and len(kw) > best_score:
                best_score = len(kw)
                best = data["response"]
    return best

def get_follow_up(query: str):
    q = query.lower()
    for k, v in FOLLOW_UPS.items():
        if k in q:
            return v
    return None

# ==================== CLOSE TIMER ====================
async def close_timer(channel_id: int, guild_id: int):
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
        await channel.send(f"⏰ This ticket has been inactive for {CLOSE_TIMEOUT_MINUTES} minutes and will now close.")
        await asyncio.sleep(3)
        await channel.delete()
    except:
        pass
    finally:
        closing_timers.pop(channel_id, None)

def reset_close_timer(channel_id: int, guild_id: int):
    if channel_id in closing_timers:
        closing_timers[channel_id].cancel()
    task = asyncio.create_task(close_timer(channel_id, guild_id))
    closing_timers[channel_id] = task

# ==================== SUPPORT VIEW (2 buttons) ====================
class SupportView(discord.ui.View):
    def __init__(self, user_id: int, channel_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.channel_id = channel_id

    @discord.ui.button(label="🆘 I need real human support", style=discord.ButtonStyle.danger, custom_id="human_support")
    async def human_support(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This button is not for you.", ephemeral=True)
            return
        guild = interaction.guild
        role = guild.get_role(HUMAN_SUPPORT_ROLE_ID)
        escalated_channels.add(self.channel_id)
        if role:
            await interaction.response.send_message(
                f"{role.mention} — {interaction.user.mention} needs real human support. Please check this ticket."
            )
        else:
            await interaction.response.send_message("⚠️ Support role not found — ping a staff member.")

    @discord.ui.button(label="✅ Issue Resolved", style=discord.ButtonStyle.success, custom_id="issue_resolved")
    async def issue_resolved(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This button is not for you.", ephemeral=True)
            return

        # Send review request in the ticket
        await interaction.response.send_message(
            f"✅ Glad it's working! 🙌\n\n"
            f"If you've got a minute, please leave a review in <#{REVIEW_CHANNEL_ID}> — it helps a ton.\n\n"
            f"This ticket will auto-close in **{CLOSE_TIMEOUT_MINUTES} minutes**."
        )

        # Disable the button so it can't be spammed
        self.children[1].disabled = True
        try:
            await interaction.message.edit(view=self)
        except:
            pass

        # Start the 35-min close timer
        reset_close_timer(self.channel_id, interaction.guild.id)

# ==================== BOT SETUP ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== SLASH COMMANDS ====================
def customer_check(interaction: discord.Interaction):
    if not has_customer_role(interaction.user):
        return f"❌ You need the **Customer** role to use this.\n\nClaim it here: <#{CLAIM_CHANNEL_ID}>"
    return None

@bot.tree.command(name="permguide", description="Get the Nexy Permanent Spoofer guide")
async def permguide_cmd(interaction: discord.Interaction):
    err = customer_check(interaction)
    if err:
        await interaction.response.send_message(err, ephemeral=True)
        return
    embed = discord.Embed(
        title="📘 NEXY PERMANENT GUIDE",
        description="Access the official Nexy Permanent Spoofer guide below:\n\n🔗 **https://nexy-temp-guide.gitbook.io/nexy-perm-guide**",
        color=0x8B5CF6
    )
    embed.set_footer(text="NEXY Team • Nexy reviews and handles all tickets")
    view = ui.View()
    view.add_item(ui.Button(label="Open Permanent Guide", url="https://nexy-temp-guide.gitbook.io/nexy-perm-guide", emoji="📘"))
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="tempguide", description="Get the Nexy Temporary Spoofer guide")
async def tempguide_cmd(interaction: discord.Interaction):
    err = customer_check(interaction)
    if err:
        await interaction.response.send_message(err, ephemeral=True)
        return
    embed = discord.Embed(
        title="📗 NEXY TEMPORARY GUIDE",
        description="Access the official Nexy Temporary Spoofer guide below:\n\n🔗 **https://nexy-temp-guide.gitbook.io/nexy-temp-guide-docs**",
        color=0x8B5CF6
    )
    embed.set_footer(text="NEXY Team • Nexy reviews and handles all tickets")
    view = ui.View()
    view.add_item(ui.Button(label="Open Temporary Guide", url="https://nexy-temp-guide.gitbook.io/nexy-temp-guide-docs", emoji="📗"))
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="cheatsetup", description="Get the Nexy Cheat Setup guide")
async def cheatsetup_cmd(interaction: discord.Interaction):
    err = customer_check(interaction)
    if err:
        await interaction.response.send_message(err, ephemeral=True)
        return
    embed = discord.Embed(
        title="📙 NEXY CHEAT SETUP GUIDE",
        description="Access the official Nexy Cheat Setup guide below:\n\n🔗 **https://nexy-temp-guide.gitbook.io/nexy-cheat-guide**",
        color=0x8B5CF6
    )
    embed.set_footer(text="NEXY Team • Nexy reviews and handles all tickets")
    view = ui.View()
    view.add_item(ui.Button(label="Open Cheat Setup Guide", url="https://nexy-temp-guide.gitbook.io/nexy-cheat-guide", emoji="📙"))
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="manual", description="Hire a staff member to do the Perm Guide via AnyDesk")
async def manual_cmd(interaction: discord.Interaction):
    err = customer_check(interaction)
    if err:
        await interaction.response.send_message(err, ephemeral=True)
        return
    embed = discord.Embed(
        title="📖 AnyDesk Manual — Nexy",
        description=(
            "💰 **Perm Guide Assistance**\n"
            "For **€20** you can hire a Staff member (NOT Trial Staff) to perform the Perm Guide for you via **AnyDesk**.\n\n"
            "⚠️ **Note**\n"
            "This is different from the ASUS Manual."
        ),
        color=0x8B5CF6
    )
    embed.set_footer(text="NEXY Team")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="tempvsperm", description="Difference between Temp & Perm Spoofer")
async def tempvsperm_cmd(interaction: discord.Interaction):
    err = customer_check(interaction)
    if err:
        await interaction.response.send_message(err, ephemeral=True)
        return
    embed = discord.Embed(title="Difference Between Temp & Perm Spoofer", color=0x8B5CF6)
    embed.add_field(name="Permanent Spoofer (Perm):", value=(
        "• Permanently alters hardware identifiers (serials).\n"
        "• Identifiers remain persistent across system reboots.\n"
        "• Requires a full clean Windows reinstallation.\n"
        "• Ideal for permanent hardware ID resets."
    ), inline=False)
    embed.add_field(name="Temporary Spoofer (Temp):", value=(
        "• Hardware changes are temporary for the active session (resets upon system reboot).\n"
        "• Requires reapplying the temporary configuration after each restart.\n"
        "• No clean Windows reinstallation required.\n"
        "• Ideal for testing or short-session usage."
    ), inline=False)
    embed.set_footer(text="NEXY Team")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cheats", description="Browse Nexy product catalog")
async def cheats_cmd(interaction: discord.Interaction):
    err = customer_check(interaction)
    if err:
        await interaction.response.send_message(err, ephemeral=True)
        return
    await interaction.response.send_message(NEXY_CATALOG)

@bot.tree.command(name="status", description="Check product status")
async def status_cmd(interaction: discord.Interaction):
    err = customer_check(interaction)
    if err:
        await interaction.response.send_message(err, ephemeral=True)
        return
    await interaction.response.send_message(NEXY_AI["detected status"]["response"])

@bot.tree.command(name="pricing", description="Show Nexy pricing")
async def pricing_cmd(interaction: discord.Interaction):
    err = customer_check(interaction)
    if err:
        await interaction.response.send_message(err, ephemeral=True)
        return
    await interaction.response.send_message(NEXY_AI["pricing"]["response"])

# ==================== EVENTS ====================
@bot.event
async def on_ready():
    print(f"✅ {BOT_NAME} is online as {bot.user}")
    try:
        guild = discord.Object(id=GUILD_ID)
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ Synced {len(synced)} commands to guild {GUILD_ID}")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    print("🔥 Button-driven support active!")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # Staff with support role silence the bot in a ticket
    if any(r.id == HUMAN_SUPPORT_ROLE_ID for r in message.author.roles):
        escalated_channels.add(message.channel.id)
        return

    channel_name = message.channel.name
    channel_id = message.channel.id
    guild = message.guild
    member = message.author
    content = message.content.lower()
    user_name = member.display_name

    # ============================================================
    # 1. CASUAL MODE — chat channels, only when mentioned
    # ============================================================
    if is_casual_channel(channel_name):
        if message.content.startswith("!"):
            await bot.process_commands(message)
            return
        if not bot.user.mentioned_in(message):
            return

        clean = re.sub(r'<@!?[0-9]+>', '', message.content).strip().lower()
        if not clean or clean in ["yo", "hey", "hi", "hello", "sup", "whats up"]:
            await message.reply(f"Yo {user_name}! What's on your mind?")
            return

        resp = get_nexy_response(clean)
        if resp:
            await message.reply(resp)
            return

        if "how are you" in clean:
            await message.reply("I'm doing great, thanks for asking! 😊")
        elif "good bot" in clean:
            await message.reply("Ayy, thanks! 🙌")
        elif "bye" in clean:
            await message.reply(f"See ya! 👋 {BOT_NAME} has got your back.")
        else:
            await message.reply(f"Yo {user_name}! What's on your mind?")
        return

    # ============================================================
    # 2. TICKET MODE
    # ============================================================
    if not is_ticket_channel(channel_name):
        return

    if channel_id in escalated_channels:
        return

    await bot.process_commands(message)

    memory = get_user_memory(member.id)

    # 🛑 Hard gate — no Customer role = ask to claim, do nothing else
    if not has_customer_role(member):
        if not memory.get("claim_notice_sent"):
            memory["claim_notice_sent"] = True
            await message.reply(
                f"👋 Hi {member.mention}!\n\n"
                f"You don't have the **Customer** role yet — that's required before I can help you with anything (guides, products, bans, spoofers).\n\n"
                f"**Claim your Customer role here:** <#{CLAIM_CHANNEL_ID}>\n\n"
                f"Once you've claimed it, just reply here again and I'll help you with whatever you need. 💜"
            )
        return

    # First message after becoming Customer — greet by name
    if not memory.get("greeted"):
        memory["greeted"] = True
        await message.reply(get_greeting(user_name))
        return

    # Manual / AnyDesk
    if "manual" in content or "anydesk" in content:
        embed = discord.Embed(
            title="📖 AnyDesk Manual — Nexy",
            description=(
                "💰 **Perm Guide Assistance**\n"
                "For **€20** you can hire a Staff member (NOT Trial Staff) to perform the Perm Guide for you via **AnyDesk**.\n\n"
                "⚠️ **Note**\n"
                "This is different from the ASUS Manual."
            ),
            color=0x8B5CF6
        )
        view = SupportView(member.id, channel_id)
        await message.reply(embed=embed, view=view)
        return

    # Temp vs Perm
    if "temp" in content and "perm" in content and ("difference" in content or "vs" in content):
        embed = discord.Embed(title="Difference Between Temp & Perm Spoofer", color=0x8B5CF6)
        embed.add_field(name="Permanent Spoofer (Perm):", value=(
            "• Permanently alters hardware identifiers (serials).\n"
            "• Identifiers remain persistent across system reboots.\n"
            "• Requires a full clean Windows reinstallation.\n"
            "• Ideal for permanent hardware ID resets."
        ), inline=False)
        embed.add_field(name="Temporary Spoofer (Temp):", value=(
            "• Hardware changes are temporary for the active session (resets upon system reboot).\n"
            "• Requires reapplying the temporary configuration after each restart.\n"
            "• No clean Windows reinstallation required.\n"
            "• Ideal for testing or short-session usage."
        ), inline=False)
        embed.set_footer(text="NEXY Team")
        view = SupportView(member.id, channel_id)
        await message.reply(embed=embed, view=view)
        return

    # Guide shortcuts
    if "perm spoofer" in content or "perm guide" in content:
        embed = discord.Embed(
            title="📘 NEXY PERMANENT GUIDE",
            description="Access the official Nexy Permanent Spoofer guide below:\n\n🔗 **https://nexy-temp-guide.gitbook.io/nexy-perm-guide**",
            color=0x8B5CF6
        )
        view = ui.View()
        view.add_item(ui.Button(label="Open Permanent Guide", url="https://nexy-temp-guide.gitbook.io/nexy-perm-guide", emoji="📘"))
        await message.reply(embed=embed, view=view)
        return

    if "temp spoofer" in content or "temp guide" in content:
        embed = discord.Embed(
            title="📗 NEXY TEMPORARY GUIDE",
            description="Access the official Nexy Temporary Spoofer guide below:\n\n🔗 **https://nexy-temp-guide.gitbook.io/nexy-temp-guide-docs**",
            color=0x8B5CF6
        )
        view = ui.View()
        view.add_item(ui.Button(label="Open Temporary Guide", url="https://nexy-temp-guide.gitbook.io/nexy-temp-guide-docs", emoji="📗"))
        await message.reply(embed=embed, view=view)
        return

    if "cheat setup" in content or "setup guide" in content or "cheat guide" in content:
        embed = discord.Embed(
            title="📙 NEXY CHEAT SETUP GUIDE",
            description="Access the official Nexy Cheat Setup guide below:\n\n🔗 **https://nexy-temp-guide.gitbook.io/nexy-cheat-guide**",
            color=0x8B5CF6
        )
        view = ui.View()
        view.add_item(ui.Button(label="Open Cheat Setup Guide", url="https://nexy-temp-guide.gitbook.io/nexy-cheat-guide", emoji="📙"))
        await message.reply(embed=embed, view=view)
        return

    # "help" → just answer + buttons
    if any(w in content for w in ["help", "need help", "support", "human", "i need support"]):
        view = SupportView(member.id, channel_id)
        await message.reply(
            f"Gotcha {user_name} — tell me what's happening and I'll help you out.\n\n"
            f"If it's something only a human can fix, tap the **🆘** button. If your issue is solved, tap **✅ Issue Resolved**.",
            view=view
        )
        if channel_id in closing_timers:
            reset_close_timer(channel_id, guild.id)
        return

    # General AI response
    response = get_nexy_response(message.content)
    if response:
        follow_up = get_follow_up(message.content)
        if follow_up:
            response = f"{response}\n\n💡 {follow_up}"
        view = SupportView(member.id, channel_id)
        await message.reply(response, view=view)
        if channel_id in closing_timers:
            reset_close_timer(channel_id, guild.id)
        return

    # Ban help
    if "ban" in content or "banned" in content:
        if "fortnite" in content:
            r = NEXY_AI["fortnite ban"]["response"]
        elif "r6" in content or "rainbow" in content:
            r = NEXY_AI["r6 ban"]["response"]
        else:
            r = f"I see you're dealing with a ban, {user_name}. Which game — Fortnite, R6, Valorant?"
        view = SupportView(member.id, channel_id)
        await message.reply(r, view=view)
        if channel_id in closing_timers:
            reset_close_timer(channel_id, guild.id)
        return

    # Product / pricing questions
    if any(w in content for w in ["product", "catalog", "offer", "cheat", "spoofer", "price", "cost", "€"]):
        view = SupportView(member.id, channel_id)
        await message.reply(NEXY_CATALOG, view=view)
        if channel_id in closing_timers:
            reset_close_timer(channel_id, guild.id)
        return

    # Fallback
    view = SupportView(member.id, channel_id)
    await message.reply(
        f"What can I help you with, {user_name}?\n\n"
        f"You can ask me about:\n• Products & Pricing\n• Ban help\n• Spoofers (temp vs perm)\n• Why Nexy\n• AnyDesk manual service\n\n"
        f"Or tap a button below:",
        view=view
    )
    if channel_id in closing_timers:
        reset_close_timer(channel_id, guild.id)

# ==================== RUN ====================
if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_TOKEN not set in environment")
    else:
        bot.run(TOKEN)
