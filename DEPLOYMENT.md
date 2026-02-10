# 🚀 Railway Deployment - Quick Guide

## What You Need
✅ GitHub account
✅ Railway account (sign up at railway.app with GitHub)

## Files Ready for Deployment
✅ `railway.toml` - Tells Railway how to run your app
✅ `requirements.txt` - Python dependencies
✅ `.gitignore` - Excludes unnecessary files
✅ All source code and fonts

---

## 📋 Step-by-Step Deployment

### 1️⃣ Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Invoice generator app ready for deployment"

# Set main branch
git branch -M main

# Add your GitHub repo (create one at github.com/new first)
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git

# Push to GitHub
git push -u origin main
```

### 2️⃣ Deploy on Railway

1. **Go to** [railway.app](https://railway.app)
2. **Sign in** with GitHub
3. **Click** "New Project"
4. **Select** "Deploy from GitHub repo"
5. **Choose** your invoice repository
6. **Wait** ~2 minutes for automatic deployment

### 3️⃣ Get Your Public URL

1. Click on your deployed service
2. Go to **Settings** tab
3. Scroll to **Domains** section
4. Click **Generate Domain**
5. Copy the URL (e.g., `https://invoice-production-xyz.railway.app`)

### 4️⃣ Share with Team

Send the URL to your team - they can now:
- Access the invoice generator from anywhere
- Fill in customer details
- Add products/services
- Generate and download professional PDF invoices

---

## 🔧 Troubleshooting

**App not starting?**
- Check Railway logs in the "Deployments" tab
- Ensure all files were pushed to GitHub
- Verify `requirements.txt` and `railway.toml` are in the root folder

**Fonts not working?**
- Ensure `DejaVuSans.ttf` and `DejaVuSans-Bold.ttf` are committed to git
- Check the `.gitignore` file doesn't exclude `.ttf` files

**Need to update the app?**
```bash
git add .
git commit -m "Update invoice generator"
git push
```
Railway will automatically redeploy!

---

## 💡 Pro Tips

- **Free Credits**: Railway gives $5/month free credits (great for small teams)
- **Custom Domain**: Add your own domain in Railway Settings → Domains
- **Environment Variables**: Add sensitive data (API keys, etc.) in Railway Settings → Variables
- **Auto-Sleep**: App sleeps after inactivity to save credits, wakes instantly on access
- **Monitoring**: Check usage and logs in Railway dashboard

---

## 🎯 What Happens After Deployment?

Your team gets a professional invoice generator:
- ✅ Web-based (no software installation needed)
- ✅ Accessible from any device
- ✅ Professional PDF output
- ✅ Customizable for each invoice
- ✅ Automatic calculations
- ✅ Instant download

**All from a single URL!**
