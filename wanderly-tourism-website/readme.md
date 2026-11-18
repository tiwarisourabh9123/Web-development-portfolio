# ⛰ Wanderly - Tourism Website

> **"Where Every Journey Begins"**

Wanderly is a **single-page, responsive tourism website** built with pure **HTML, CSS and JavaScript** (plus a little jQuery). It is a front-end only project: there is no server, no database and no backend.

---

## 📋 Table of Contents
- [Features](#-features)
- [Page Sections](#-page-sections)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Run Locally](#-run-locally)
- [Deploy on GitHub Pages](#-deploy-on-github-pages)
- [Important: Contact Form & Backend](#-important-contact-form--backend)
- [Customize](#-customize)
- [Author](#-author)
- [License](#-license)

---

## ✨ Features
- Single-page layout with smooth navigation between sections
- Fully responsive design (desktop, tablet and mobile menu)
- Light / dark mode toggle, remembered in the browser (`localStorage`)
- Active nav link updates as you scroll
- Image carousel and photo gallery
- Back-to-top button
- Contact section with a message form and direct email link

## 🧭 Page Sections
| Section | Description |
|---------|-------------|
| **Home** | Hero banner with a welcome message |
| **Events** | Upcoming treks, walks and island trips |
| **Explore** | Travel inspiration and quote |
| **Tours** | Upcoming tours with a photo gallery |
| **About** | Image carousel and brand intro |
| **Contact** | Message form and contact details |

## 🛠 Tech Stack
- **HTML5** - structure
- **CSS3** - styling and responsive layout (`style.css`, `responsive.css`)
- **JavaScript (ES6) + jQuery 3.6** - interactions, dark mode, scroll behaviour
- **Font Awesome 4.7** and **Google Fonts** - icons and typography (loaded from CDN, internet required)

## 📁 Project Structure
```
wanderly-tourism-website/
├── index.html            # The single page
├── css/
│   ├── style.css         # Main styles
│   └── responsive.css    # Mobile / tablet styles
├── js/
│   └── script.js         # Dark mode, nav highlight, scroll button
├── img/                  # Images, icons, manifest
├── .github/              # Issue templates
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── LICENSE
└── README.md
```

## 🚀 Run Locally
```bash
git clone <your-repository-url>
cd wanderly-tourism-website
```
Then simply open `index.html` in your browser, or use the **Live Server** extension in VS Code. No build step or installation is needed.

## 🌐 Deploy on GitHub Pages
1. Push the project to a GitHub repository.
2. Open the repository **Settings → Pages**.
3. Under **Branch**, select `main` and `/ (root)`, then click **Save**.
4. After a minute your site is live at `https://<your-username>.github.io/<repository-name>/`.

---

## ⚠️ Important: Contact Form & Backend

**The "Send us a message" form does not send messages to a server, because this project has no backend.**

This is a static website. A website can only collect form data in the browser; to *receive* it, something on a server must accept the data and store it or email it to you. That part is not built here.

### What actually happens when someone clicks Submit
The form is set up as a simple `mailto:` form:
```html
<form action="mailto:sourabhtiwari9123@gmail.com" method="post" enctype="text/plain">
```
- It tries to **open the visitor's default email app** with the message prepared.
- If the visitor has no email app set up (common on shared or school computers, or when using web mail only), **nothing will happen**.
- No message is saved or delivered by the website itself, and there is no success or error message.
- The form fields are not validated.

The **email link** in the contact box (`Mail: sourabhtiwari9123@gmail.com`) works reliably, because it is a plain `mailto:` link.

### How to make the form really work
You need a backend or a form service. Pick one:

| Option | Effort | Notes |
|--------|--------|-------|
| **[Formspree](https://formspree.io)** / **[Web3Forms](https://web3forms.com)** / **[Getform](https://getform.io)** | Easiest | Create a free form, then replace the form `action` with the URL they give you. Messages arrive in your email. No code on your server. |
| **[EmailJS](https://www.emailjs.com)** | Easy | Send email directly from JavaScript in the browser, with no server of your own. |
| **Your own backend** | More work | Build an API (for example Node.js + Express with Nodemailer, or PHP, Python Flask/Django) that receives the form data via `POST` and emails or stores it. |

Example with Formspree (only the `action` and `method` change):
```html
<form action="https://formspree.io/f/your-form-id" method="POST">
```
Note: GitHub Pages only serves static files, so it cannot run backend code itself. Use one of the services above, or host the backend elsewhere (Render, Railway, Vercel, etc.).

### Other things that are also static (demo content)
- The **"All Details"**, **"Learn more"** and **"Explore more"** buttons are placeholders and do not open further pages yet.
- The events and tour dates are sample content. Edit them in `index.html`.
- There is no booking, login or payment system.

---

## 🎨 Customize
- **Text and dates:** edit `index.html`.
- **Colours and fonts:** edit `css/style.css` (main accent colour is `#fc036b`).
- **Images:** replace files in the `img/` folder, keeping the same file names, or update the paths in `index.html`.
- **Contact details:** search for `sourabhtiwari9123@gmail.com` in `index.html` and change it.

## 👨‍💻 Author
**Sourabh Tiwari**
📧 [sourabhtiwari9123@gmail.com](mailto:sourabhtiwari9123@gmail.com)

Contributions, issues and suggestions are welcome - see [CONTRIBUTING.md](CONTRIBUTING.md).

## 🛡️ License
Released under the [MIT License](LICENSE).

## 🙏 Support
If you like this project, please give it a ⭐ on GitHub.
