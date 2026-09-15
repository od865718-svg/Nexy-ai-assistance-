# Nexy Bot — Railway Deployment Guide

## Files You Have
- `bot.py` — main bot code
- `requirements.txt` — dependencies
- `.env.example` — environment variables template

## Quick Setup (Choose One Path)

### Path 1: GitHub → Railway (Recommended)

**Step 1: Upload to GitHub**
1. Create GitHub account (github.com)
2. Click **"+"** → **"New repository"**
3. Name it `nexy-bot`
4. Click **"Create repository"**
5. Click **"Upload files"**
6. Drag these files in:
   - `bot.py`
   - `requirements.txt`
7. Click **"Commit changes"**

**Step 2: Connect to Railway**
1. Go to railway.app
2. Sign up with GitHub
3. Click **"New Project"**
4. Click **"Deploy from GitHub repo"**
5. Select `nexy-bot` repo
6. Click **"Deploy"**

**Step 3: Add Environment Variables**
1. In Railway dashboard, click your bot service
2. Go to **"Variables"** tab
3. Add these:
```
DISCORD_TOKEN = (your bot token)
GUILD_ID = 1547715438396444742
CLAIM_CHANNEL_ID = 1549158153231540404
```

**Step 4: Wait for Deploy**
- Railway auto-builds in 2-3 minutes
- Check "Deployments" tab
- When it says "Success" ✅ — you're live

---

### Path 2: Direct Upload (Simpler but needs local setup)

**If you want to test locally first:**

1. Create `.env` file (copy from `.env.example`)
2. Add your Discord token to `.env`
3. Run locally:
```bash
pip install -r requirements.txt
python bot.py
```

Then upload to GitHub/Railway as above.

---

## Get Your Discord Token

1. Go to Discord Developer Portal: https://discord.com/developers/applications
2. Click **"New Application"**
3. Name it `Nexy Bot`
4. Go to **"Bot"** section
5. Click **"Add Bot"**
6. Under TOKEN, click **"Copy"**
7. That's your `DISCORD_TOKEN`

## Invite Bot to Server

1. In Developer Portal, go to **"OAuth2"** → **"URL Generator"**
2. Scopes: Select `bot`
3. Permissions: Select `Administrator`
4. Copy the URL that appears
5. Open in browser
6. Select your server
7. Click **"Authorize"**

---

## After Deployment

**Test the bot:**
- Go to your Discord server
- Type `/cheats list`
- If it responds ✅ — deployed successfully

**Make changes later:**
```bash
# Update code locally
# Commit to GitHub
git add .
git commit -m "Update: description"
git push

# Railway auto-redeploys in 2-3 minutes
```

**Check logs:**
- Railway dashboard → Click bot service → "Logs" tab
- Shows real-time output

---

## Troubleshooting

❌ **Bot doesn't respond:**
- Check DISCORD_TOKEN is correct
- Make sure bot has permissions in server
- Railway: click "Redeploy" to restart

❌ **Unknown command:**
- Give bot Administrator role
- Wait 30 seconds for commands to sync
- Restart bot

❌ **Bot keeps crashing:**
- Check Railway logs for error
- Usually missing env var or bad token

---

## You're Done

Your bot is now:
- ✅ Running 24/7 on Railway
- ✅ Auto-deploys on GitHub updates
- ✅ Has all features (guides, support, manager escalation)
- ✅ Role-gated commands
- ✅ Support tickets with auto-close

Questions? Check the logs.
