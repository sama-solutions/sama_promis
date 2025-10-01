# SAMA PROMIS Training Portal - Quick Start Guide

## Getting Started in 5 Minutes

This guide will help you quickly get started with the SAMA PROMIS Training Portal, whether you're opening it locally or accessing it via a web server.

---

## 🚀 Quick Start Options

### Option 1: Open Directly (Fastest - No Setup Required)

**Perfect for:** Quick access, reviewing content, offline use

1. **Navigate** to the training folder:
   ```
   /docs/training/
   ```

2. **Double-click** on `index.html`

3. **That's it!** The site opens in your browser with automatic path resolution

✅ **No server needed**  
✅ **Works offline**  
✅ **All navigation works automatically**

---

### Option 2: Use a Local Web Server (Recommended for Development)

**Perfect for:** Development, testing, optimal performance

#### With Python 3 (Easiest)
```bash
cd /path/to/sama_promis/docs/training
python3 -m http.server 8000
```
Then open: http://localhost:8000

#### With Node.js
```bash
cd /path/to/sama_promis/docs/training
npx http-server -p 8000
```
Then open: http://localhost:8000

#### With PHP
```bash
cd /path/to/sama_promis/docs/training
php -S localhost:8000
```
Then open: http://localhost:8000

#### With VSCode Live Server Extension
1. Install "Live Server" extension in VSCode
2. Open `/docs/training/` folder in VSCode
3. Right-click `index.html` → "Open with Live Server"
4. Site opens automatically in your browser

---

## 📚 First Steps After Opening

### 1. Register Your Account (2 minutes)

1. Click **"S'inscrire"** (Register) button on the homepage
2. Fill in your information:
   - Full name
   - Email address
   - Organization
   - Select your role (Administrator, Project Manager, Donor, etc.)
3. Click **"S'inscrire"** to create your account

Your data is saved locally in your browser - no internet connection required!

### 2. Choose Your Training Path (1 minute)

Select the training that matches your role:

- **👨‍💼 Administrator** - System setup, user management, security
- **📊 Project Manager** - Project management, budgets, procurement
- **💰 Donor** - Public portal, compliance profiles, project monitoring
- **🤝 Beneficiary/Partner** - Portal navigation, proposals, contracts
- **✅ Compliance Officer** - Compliance tasks, profiles, reporting
- **🛒 Procurement Officer** - Procurement plans, tenders, execution
- **👤 Portal User** - Portal navigation, interaction tracking
- **🌍 Citizen** - Public portal, data consultation, exports

### 3. Start Learning (2 minutes)

1. Click on your chosen role card
2. Select a training level:
   - **User Level** - Learn to use the system
   - **Trainer Level** - Learn to teach others (requires User certification)
3. Begin with Module 1, Lesson 1
4. Complete lessons, take quizzes, earn your certificate!

---

## 🎯 Key Features

### Progress Tracking
- ✅ Your progress is automatically saved
- 📊 View completion percentage for each module
- 🔄 Resume where you left off anytime

### Interactive Quizzes
- 📝 Test your knowledge after each module
- ⏱️ Timed assessments
- 💯 Instant feedback and explanations
- 🎯 80% passing score required

### Certificates
- 🏆 Earn official certificates upon completion
- 📄 Download as PDF
- 🔍 QR code for verification
- 📅 Valid for 2-3 years (depending on level)

### Offline Support
- 💾 All data stored locally in your browser
- 🌐 No internet required after initial load
- 🔒 Your data stays on your device

---

## 🔧 Troubleshooting

### CSS Styles Not Loading?

**Problem:** Page looks broken, no colors or formatting

**Solution:**
- Make sure you opened `index.html` (not a nested file)
- Check that `assets/` folder exists in the same directory
- Try using a local web server (Option 2 above)

### Links Not Working?

**Problem:** Clicking navigation links does nothing

**Solution:**
- Open browser console (F12) and check for errors
- Verify `assets/js/path-resolver.js` exists
- Try a different browser (Chrome/Firefox recommended)
- Use a local web server for best compatibility

### Progress Not Saving?

**Problem:** Your progress resets when you close the browser

**Solution:**
- Check that cookies/localStorage are enabled in your browser
- Don't use "Private/Incognito" mode
- Make sure you're using the same browser profile

### Quiz Not Submitting?

**Problem:** Quiz submit button doesn't work

**Solution:**
- Make sure you answered ALL questions
- Check browser console (F12) for JavaScript errors
- Refresh the page and try again

---

## 💡 Tips for Best Experience

### Browser Recommendations

**Best Support (file:// mode):**
- ✅ Chrome/Chromium
- ✅ Firefox
- ⚠️ Safari (limited)
- ⚠️ Edge (limited)

**All Browsers Work Great with Local Server!**

### Learning Tips

1. **Take your time** - Training is self-paced
2. **Practice as you learn** - Try features in SAMA PROMIS
3. **Review before quizzes** - 80% passing score required
4. **Retake if needed** - No limit on quiz attempts
5. **Ask for help** - Contact support@samaetat.sn

### Navigation Shortcuts

- **Home** - Click SAMA PROMIS logo
- **Back to Training** - Use browser back button
- **Jump to Module** - Use sidebar navigation
- **Next Lesson** - Click "Suivant" button at bottom

---

## 📞 Getting Help

### Technical Support
- **Email:** support@samaetat.sn
- **Phone:** +221 33 XXX XX XX

### Training Questions
- **Email:** formation@samaetat.sn
- **Documentation:** See `README.md` for detailed info

### Report Issues
- Check `README.md` for detailed troubleshooting
- Contact support with:
  - Browser name and version
  - Operating system
  - Screenshot of the issue
  - Error messages from console (F12)

---

## 📖 Additional Resources

### Full Documentation
- **README.md** - Complete technical documentation
- **IMPLEMENTATION_COMPLETE.md** - Implementation details

### Training Materials
- **Downloads Section** - PDF guides, cheat sheets, videos
- **Resources** - Additional learning materials

### Certification Info
- **Certification Page** - Requirements, process, renewal
- **FAQ** - Common questions answered

---

## 🎓 Certification Process

### User Certification
1. ✅ Complete all modules for your role
2. ✅ Pass module quizzes (80% minimum)
3. ✅ Pass final exam (80% minimum)
4. 🏆 Receive certificate (valid 2 years)

### Trainer Certification
1. ✅ Hold valid User certification
2. ✅ Complete Trainer-level modules
3. ✅ Pass trainer exam (85% minimum)
4. ✅ Submit teaching demonstration
5. 🏆 Receive trainer certificate (valid 3 years)

---

## 🔄 Next Steps

After completing this quick start:

1. **Explore** the homepage and familiarize yourself with the layout
2. **Register** your account to start tracking progress
3. **Choose** your role and begin your first module
4. **Complete** lessons at your own pace
5. **Earn** your certification!

---

## ⚡ Quick Reference

| Task | Action |
|------|--------|
| **Start Training** | Open `index.html` → Register → Choose Role |
| **Resume Training** | Open `index.html` → Navigate to your role |
| **Take Quiz** | Complete module → Click "Passer le Quiz" |
| **View Progress** | Check progress bar on training page |
| **Download Certificate** | Complete all modules → Certification page |
| **Reset Progress** | Browser DevTools → Application → Clear Storage |

---

**Ready to start?** Open `index.html` and begin your SAMA PROMIS training journey! 🚀

---

*Last Updated: 2024*  
*Version: 1.0.0*  
*For detailed technical information, see README.md*
