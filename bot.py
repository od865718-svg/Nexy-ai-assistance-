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
MANAGER_ROLE_ID = int(os.getenv("MANAGER_ROLE_ID", "0")) or None

# Locked-in IDs
HUMAN_SUPPORT_ROLE_ID = 1547715438438256751
REVIEW_CHANNEL_ID = 1547715439700746265
REVIEW_LINK = f"https://discord.com/channels/{GUILD_ID}/{REVIEW_CHANNEL_ID}"

CLOSE_TIMEOUT_MINUTES = 35

# Channel prefixes the AI watches in tickets
TICKET_PREFIXES = ["support-", "buy-"]
CASUAL_CHANNELS = ["chat", "general", "lounge", "off-topic", "general-chat"]
CASUAL_PREFIXES = ["chat-", "general-"]

def is_casual_channel(channel_name: str) -> bool:
    return channel_name in CASUAL_CHANNELS or any(channel_name.startswith(p) for p in CASUAL_PREFIXES)

def is_ticket_channel(channel_name: str) -> bool:
    return any(channel_name.startswith(p) for p in TICKET_PREFIXES)

# ==================== STATE ====================
closing_timers = {}
escalated_channels = set()
user_memory = {}

def get_user_memory(user_id: int) -> dict:
    if user_id not in user_memory:
        user_memory[user_id] = {"greeted": False}
    return user_memory[user_id]

# ==================== GREETINGS ====================
def get_greeting(name: str) -> str:
    return random.choice([
        f"Yo {name}! How can I help you today?",
        f"Hey {name}! What's on your mind?",
        f"Yo {name}! Ready to drop some knowledge. What do you need?",
        f"What's up {name}! Got a question or just vibin?",
        f"{name}! What's the play today?",
    ])

# ==================== STAFF NOTICE ====================
STAFF_NOTICE = """**Hey {user}, quick update regarding staff availability and queue:**

🕒 **NEXY Staff Availability & Queue Notice**
The NEXY staff team is currently active around these hours (core support window runs through afternoon, evening, and late night in EU / Israel timezone, catering to our international customers).

Staff is actively working through tickets and orders right now and will assist you shortly!

⚠️ Please avoid spamming mentions (@Staff) so your ticket remains orderly in the queue.

📋 **What to leave here while waiting:**
• Your Invoice ID or order ID from SellAuth / email
• Product / Game name and Windows version
• Clear screenshots of any error message or issue

*This ensures staff can resolve your problem immediately once they open your ticket!*

NEXY Support • Staff reviews and handles all tickets"""

# ==================== PRODUCT CATALOG ====================
NEXY_CATALOG = f"""
**🛒 {BOT_NAME} — Product Catalog**

**🟢 All products are 100% Undetected.**

---

**🎮 Nyrex — Fortnite Cheat**
• Aimbot, ESP, Radar, and more
• Private driver available
• Prices: €5.99 (1D) | €9.99 (3D) | €20.99 (7D) | €34.00 (30D) | €199.99 (Lifetime)

**🎯 Nyrex R6 — Rainbow Six Siege Cheat**
• Aimbot, ESP, Anti-aim, BattlEye bypass
• Kernel-level protection
• Prices: €6.99 (1D) | €15.99 (3D) | €35.99 (7D) | €69.99 (30D)

**🛡️ Perm Spoofer — Permanent HWID Spoofer**
• Changes disk serial, MAC, motherboard, TPM, and ARP
• One-time setup — stays until you revert
• Prices: €24.00 (One-time) | €34.00 (+TPM+Disk) | €64.00 (Lifetime + TPM + Disk + ARP)

**⚡ Temp Spoofer — Temporary HWID Spoofer**
• Memory-only — resets on reboot
• No registry or firmware changes
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

Yo! Nyrex is our flagship Fortnite cheat — built for domination with zero compromises.

**What it does:**
• **Aimbot** — smooth, human-like locking
• **ESP/Wallhack** — see enemies, loot, and traps through walls
• **Radar** — track enemies in real-time
• **Private driver** available for lifetime users

**Pricing:**
• €5.99 — 1 Day
• €9.99 — 3 Days
• €20.99 — 7 Days
• €34.00 — 30 Days
• €199.99 — Lifetime (includes private driver)

**Why Nyrex?**
• 🟢 100% Undetected on EAC
• 🛡️ Kernel-level — EAC can't scan our memory
• ⚡ Updates within hours of game patches
• 🔒 Private, not public — no signature detection

🟢 **Status:** Undetected on the latest patch.
"""
    },
    "nyrex r6": {
        "keywords": ["nyrex r6", "r6 cheat", "rainbow six cheat", "nyrex r6x"],
        "response": """
**🎯 Nyrex R6 — Premium Rainbow Six Siege Cheat**

Yo! Nyrex R6 is built specifically for Rainbow Six Siege — BattlEye doesn't stand a chance.

**What it does:**
• **Aimbot** with bone prediction (headshots all day)
• **ESP** — see enemies, gadgets, and traps
• **Anti-aim** — avoid headshots like a pro
• **BattlEye bypass** built in

**Pricing:**
• €6.99 — 1 Day
• €15.99 — 3 Days
• €35.99 — 7 Days
• €69.99 — 30 Days

**Why Nyrex R6?**
• 🟢 100% Undetected on BattlEye
• ⚡ Kernel-level driver — BE cannot touch it
• 🎯 Optimized for R6's unique mechanics
• 🔒 Private and secure

🟢 **Status:** Undetected on the latest patch.
"""
    },
    "perm spoofer": {
        "keywords": ["perm spoofer", "permanent spoofer", "perm spoof"],
        "response": """
**🛡️ Perm Spoofer — Permanent HWID Solution**

This is the big one — permanent HWID spoofing for when you're really banned.

**What it changes:**
• Disk Serial Number
• MAC Address
• Motherboard ID
• TPM (Trusted Platform Module)
• ARP (Address Resolution Protocol)

**Pricing:**
• €24.00 — One-time
• €34.00 — One-time + TPM + Disk spoofer
• €64.00 — Lifetime + TPM + Disk + ARP spoofer

**Why Perm Spoofer?**
• 🟢 100% Undetected on EAC, BattlEye, and Vanguard
• 🔒 Permanent changes — stays until you manually revert
• ⚡ One-time setup — then you're done

🟢 **Status:** Undetected on all games.
"""
    },
    "temp spoofer": {
        "keywords": ["temp spoofer", "temporary spoofer", "temp spoof"],
        "response": """
**⚡ Temp Spoofer — The Ultimate Temporary HWID Solution**

Yo! Temp Spoofer changes your HWID in memory only — resets on reboot. Perfect for testing or quick sessions.

**Pricing:**
• €4.99 — 1 Day
• €15.99 — 7 Days
• €24.99 — Lifetime

**Why Temp Spoofer?**
• 🟢 100% Undetected — EAC, BattlEye, and Vanguard compatible
• ⚡ Instant spoof — no reboot required
• 🔒 Safe — no registry or firmware changes

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

Use **Nyrex R6** — it's built specifically for BattlEye bypass.

💡 **Was it a permanent ban or a temporary one?**
"""
    },
    "pricing": {
        "keywords": ["price", "prices", "cost", "how much", "€", "euro"],
        "response": """
**💰 Nexy Pricing — All Products**

**🎮 Nyrex (Fortnite)**
• 1 Day — €5.99 | 3 Days — €9.99 | 7 Days — €20.99 | 30 Days — €34.00 | Lifetime — €199.99

**🎯 Nyrex R6 (Rainbow Six)**
• 1 Day — €6.99 | 3 Days — €15.99 | 7 Days — €35.99 | 30 Days — €69.99

**🛡️ Perm Spoofer**
• One-time — €24.00 | +TPM+Disk — €34.00 | Lifetime — €64.00

**⚡ Temp Spoofer**
• 1 Day — €4.99 | 7 Days — €15.99 | Lifetime — €24.99

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
• 🔒 Private & Secure — no signature detection
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

We offer kernel-level cheats and spoofers for Fortnite and R6:
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

# ==================== HUMAN SUPPORT BUTTON ====================
class HumanSupportButton(discord.ui.View):
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
        role = guild.get_role(HUMAN_SUPPORT_ROLE_ID) if HUMAN_SUPPORT_ROLE_ID else None
        escalated_channels.add(self.channel_id)
        if role:
            await interaction.response.send_message(
                f"{role.mention} — {interaction.user.mention} needs real human support. Please assist."
            )
        else:
            await interaction.response.send_message("⚠️ Support role not configured — ping a staff member.")

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

# ==================== BOT SETUP ====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== SLASH COMMANDS ====================

# ---- Guides ----
@bot.tree.command(name="permguide", description="Get the Nexy Permanent Spoofer guide")
async def permguide_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📘 NEXY PERMANENT GUIDE",
        description=(
            "Access the official Nexy Permanent Spoofer guide below:\n\n"
            "🔗 **https://nexy-temp-guide.gitbook.io/nexy-perm-guide**"
        ),
        color=0x8B5CF6
    )
    embed.set_footer(text="NEXY Team • Nexy reviews and handles all tickets")
    view = ui.View()
    view.add_item(ui.Button(
        label="Open Permanent Guide",
        url="https://nexy-temp-guide.gitbook.io/nexy-perm-guide",
        emoji="📘"
    ))
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="tempguide", description="Get the Nexy Temporary Spoofer guide")
async def tempguide_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📗 NEXY TEMPORARY GUIDE",
        description=(
            "Access the official Nexy Temporary Spoofer guide below:\n\n"
            "🔗 **https://nexy-temp-guide.gitbook.io/nexy-temp-guide-docs**"
        ),
        color=0x8B5CF6
    )
    embed.set_footer(text="NEXY Team • Nexy reviews and handles all tickets")
    view = ui.View()
    view.add_item(ui.Button(
        label="Open Temporary Guide",
        url="https://nexy-temp-guide.gitbook.io/nexy-temp-guide-docs",
        emoji="📗"
    ))
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="cheatsetup", description="Get the Nexy Cheat Setup guide")
async def cheatsetup_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📙 NEXY CHEAT SETUP GUIDE",
        description=(
            "Access the official Nexy Cheat Setup guide below:\n\n"
            "🔗 **https://nexy-temp-guide.gitbook.io/nexy-cheat-guide**"
        ),
        color=0x8B5CF6
    )
    embed.set_footer(text="NEXY Team • Nexy reviews and handles all tickets")
    view = ui.View()
    view.add_item(ui.Button(
        label="Open Cheat Setup Guide",
        url="https://nexy-temp-guide.gitbook.io/nexy-cheat-guide",
        emoji="📙"
    ))
    await interaction.response.send_message(embed=embed, view=view)

# ---- Manual (AnyDesk assistance) ----
@bot.tree.command(name="manual", description="Hire a staff member to do the Perm Guide for you via AnyDesk")
async def manual_cmd(interaction: discord.Interaction):
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
    embed.set_footer(text="NEXY • Today")
    await interaction.response.send_message(embed=embed)

# ---- Temp vs Perm Spoofer ----
@bot.tree.command(name="tempvsperm", description="Difference between Temp & Perm Spoofer")
async def tempvsperm_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Difference Between Temp & Perm Spoofer",
        color=0x8B5CF6
    )
    embed.add_field(
        name="Permanent Spoofer (Perm):",
        value=(
            "• Permanently alters hardware identifiers (serials).\n"
            "• Identifiers remain persistent across system reboots.\n"
            "• Requires a full clean Windows reinstallation.\n"
            "• Ideal for permanent hardware ID resets."
        ),
        inline=False
    )
    embed.add_field(
        name="Temporary Spoofer (Temp):",
        value=(
            "• Hardware changes are temporary for the active session (resets upon system reboot).\n"
            "• Requires reapplying the temporary configuration after each restart.\n"
            "• No clean Windows reinstallation required.\n"
            "• Ideal for testing or short-session usage."
        ),
        inline=False
    )
    embed.add_field(
        name="\u200b",
        value="*If you need further guidance on selecting an option, feel free to ask our staff team.*",
        inline=False
    )
    embed.set_footer(text="NEXY Team • Yesterday")
    await interaction.response.send_message(embed=embed)

# ---- Catalog ----
@bot.tree.command(name="cheats", description="Browse Nexy product catalog")
async def cheats_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(NEXY_CATALOG)

@bot.tree.command(name="status", description="Check product status")
async def status_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(NEXY_AI["detected status"]["response"])

@bot.tree.command(name="pricing", description="Show Nexy pricing")
async def pricing_cmd(interaction: discord.Interaction):
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
    print("🔥 Fully autonomous support — no commands needed!")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # Staff with the support role silence the bot in a ticket
    if HUMAN_SUPPORT_ROLE_ID and any(r.id == HUMAN_SUPPORT_ROLE_ID for r in message.author.roles):
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
        elif any(w in clean for w in ["cheat", "spoofer", "ban", "hwid", "inject", "detected"]):
            await message.reply(f"Yo {user_name}! If you need help with cheats, spoofers, or bans, open a support ticket and I'll assist you properly! 🎫")
        else:
            await message.reply(f"Yo {user_name}! What's on your mind? Need help with cheats, spoofers, or just chatting?")
        return

    # ============================================================
    # 2. TICKET MODE — support-* and buy-* channels
    # ============================================================
    if not is_ticket_channel(channel_name):
        return

    if channel_id in escalated_channels:
        return

    await bot.process_commands(message)

    memory = get_user_memory(member.id)

    # First message in ticket — greet by name
    if not memory.get("greeted"):
        memory["greeted"] = True
        await message.reply(get_greeting(user_name))
        return

    # "Help" trigger — post staff notice + tag staff
    if any(w in content for w in ["help", "need help", "support", "human"]):
        role = guild.get_role(HUMAN_SUPPORT_ROLE_ID) if HUMAN_SUPPORT_ROLE_ID else None
        if role:
            await message.channel.send(STAFF_NOTICE.format(user=user_name))
            await message.channel.send(f"{role.mention} — {member.mention} needs assistance. Please check this ticket.")
        else:
            await message.reply("I'll get a human for you. Please wait...")

    # "Waiting for key" — tag Manager, go silent
    if "waiting for key" in content or "need key" in content:
        role = guild.get_role(MANAGER_ROLE_ID) if MANAGER_ROLE_ID else None
        if role:
            escalated_channels.add(channel_id)
            await message.channel.send(f"{role.mention} — Someone's waiting for a key in here. Please assist.")
            return

    # "Fixed / thanks" — review + auto-close timer
    if any(w in content for w in ["thanks", "thank you", "fixed", "done", "solved", "working", "all good"]):
        await message.reply(
            f"✅ Glad it's working! 🙌\n\n"
            f"If you've got a minute, please leave a review in <#{REVIEW_CHANNEL_ID}> — it helps a ton.\n\n"
            f"This ticket will auto-close in {CLOSE_TIMEOUT_MINUTES} minutes."
        )
        reset_close_timer(channel_id, guild.id)
        return

    # "Manual" trigger — show AnyDesk service
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
        embed.set_footer(text="NEXY Team")
        await message.reply(embed=embed)
        return

    # "Temp vs Perm" trigger
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
        await message.reply(embed=embed)
        return

    # Guide shortcuts
    if "perm spoofer" in content or "perm guide" in content:
        embed = discord.Embed(
            title="📘 NEXY PERMANENT GUIDE",
            description=(
                "Access the official Nexy Permanent Spoofer guide below:\n\n"
                "🔗 **https://nexy-temp-guide.gitbook.io/nexy-perm-guide**"
            ),
            color=0x8B5CF6
        )
        view = ui.View()
        view.add_item(ui.Button(label="Open Permanent Guide", url="https://nexy-temp-guide.gitbook.io/nexy-perm-guide", emoji="📘"))
        await message.reply(embed=embed, view=view)
        return

    if "temp spoofer" in content or "temp guide" in content:
        embed = discord.Embed(
            title="📗 NEXY TEMPORARY GUIDE",
            description=(
                "Access the official Nexy Temporary Spoofer guide below:\n\n"
                "🔗 **https://nexy-temp-guide.gitbook.io/nexy-temp-guide-docs**"
            ),
            color=0x8B5CF6
        )
        view = ui.View()
        view.add_item(ui.Button(label="Open Temporary Guide", url="https://nexy-temp-guide.gitbook.io/nexy-temp-guide-docs", emoji="📗"))
        await message.reply(embed=embed, view=view)
        return

    if "cheat setup" in content or "setup guide" in content or "cheat guide" in content:
        embed = discord.Embed(
            title="📙 NEXY CHEAT SETUP GUIDE",
            description=(
                "Access the official Nexy Cheat Setup guide below:\n\n"
                "🔗 **https://nexy-temp-guide.gitbook.io/nexy-cheat-guide**"
            ),
            color=0x8B5CF6
        )
        view = ui.View()
        view.add_item(ui.Button(label="Open Cheat Setup Guide", url="https://nexy-temp-guide.gitbook.io/nexy-cheat-guide", emoji="📙"))
        await message.reply(embed=embed, view=view)
        return

    # General AI response
    response = get_nexy_response(message.content)
    if response:
        follow_up = get_follow_up(message.content)
        if follow_up:
            response = f"{response}\n\n💡 {follow_up}"
        view = HumanSupportButton(member.id, channel_id)
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
        view = HumanSupportButton(member.id, channel_id)
        await message.reply(r, view=view)
        if channel_id in closing_timers:
            reset_close_timer(channel_id, guild.id)
        return

    # Product / pricing questions
    if any(w in content for w in ["product", "catalog", "offer", "cheat", "spoofer", "price", "cost", "€"]):
        view = HumanSupportButton(member.id, channel_id)
        await message.reply(NEXY_CATALOG, view=view)
        if channel_id in closing_timers:
            reset_close_timer(channel_id, guild.id)
        return

    # Fallback
    view = HumanSupportButton(member.id, channel_id)
    await message.reply(
        f"What can I help you with, {user_name}?\n\n"
        f"You can ask me about:\n• Products & Pricing\n• Ban help\n• Spoofers (temp vs perm)\n• Why Nexy\n• AnyDesk manual service\n\n"
        f"Or click the button below for human support.",
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
