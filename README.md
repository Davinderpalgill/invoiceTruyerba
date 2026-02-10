# Invoice Generator Web App

A professional invoice generator with a web UI that allows team members to create and download PDF invoices.

## 🚀 Quick Start (Local)

1. **Activate your virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

2. **Run the web app:**
   ```bash
   streamlit run app.py
   ```

3. **Open your browser:**
   The app will automatically open at `http://localhost:8501`

## 📦 Features

- ✅ User-friendly web form for invoice creation
- ✅ Dynamic line item management (add/remove items)
- ✅ Seller and buyer information inputs
- ✅ Automatic tax and total calculations
- ✅ Professional PDF generation with proper formatting
- ✅ Download generated invoices instantly
- ✅ Support for shipping, discounts, and taxes
- ✅ Bank/payment details section

## 🌐 Deploy to Railway

Railway offers free hosting credits and is perfect for team applications with custom domains.

### Step 1: Push to GitHub

1. Initialize git in this folder (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Invoice generator"
   git branch -M main
   ```

2. Create a new repository on GitHub

3. Push your code:
   ```bash
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

### Step 2: Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Sign in with your GitHub account
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your invoice generator repository
6. Railway will automatically detect and deploy your app
7. Wait 2-3 minutes for deployment to complete

### Step 3: Get Your App URL

1. Click on your deployed service
2. Go to the **"Settings"** tab
3. Under **"Domains"**, click **"Generate Domain"**
4. Copy the generated URL (e.g., `https://your-app.railway.app`)

**Share this URL with your team members!**

### 💰 Railway Pricing

- **Free tier**: $5 monthly credit (plenty for small teams)
- **Hobby plan**: $5/month for more resources
- Your app sleeps after inactivity and wakes up instantly when accessed

---

## 🌐 Alternative: Deploy to Streamlit Cloud (Free)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository, branch (main), and main file (`app.py`)
5. Click "Deploy"

Your app will be live at: `https://your-app-name.streamlit.app`

## 📝 Files

- `app.py` - Streamlit web UI application
- `invoice.py` - Core invoice generation logic and PDF rendering
- `requirements.txt` - Python dependencies for deployment
- `railway.toml` - Railway deployment configuration
- `.gitignore` - Files to exclude from git
- `.streamlit/config.toml` - Streamlit configuration
- `DejaVuSans*.ttf` - Unicode font files for ₹ symbol support

## 🛠️ Customization

### Change Default Values

Edit [app.py](app.py) to modify default seller information, tax rates, or other settings.

### Add Your Logo

Place your logo image in the project folder and update the invoice configuration to include:
```python
invoice.logo_path = "path/to/your/logo.png"
```

### Add Your Company Logo

1. Place your logo file in the Invoice folder with one of these names:
   - `logo.png` (recommended)
   - `logo.jpg`
   - `company_logo.png`
   - `company_logo.jpg`

2. Recommended size: 300x180 pixels or similar 5:3 aspect ratio
3. The app will automatically detect and use it on all invoices
4. Logo appears in the top-left corner of the PDF

### Font Support (₹ symbol)

The DejaVu fonts are included for proper Unicode support. If the rupee symbol doesn't display:
1. Ensure `DejaVuSans.ttf` and `DejaVuSans-Bold.ttf` are in the project folder
2. Or the system will fall back to "Rs." prefix

## 💡 Usage Tips

1. **Required Fields:** Fields marked with * must be filled
2. **Multiple Items:** Click "Add Another Item" to add more products/services
3. **Tax Rates:** Can be set per-item or globally for all items
4. **Preview:** Check the summary before downloading
5. **Download:** Click the download button after generation

## 🔒 Security Note

For production use with sensitive data:
- Consider adding authentication
- Use environment variables for sensitive defaults
- Deploy on a private Streamlit instance if needed

## 📧 Support

For questions or issues, contact your development team.
