# aviator-bot-ui

Browser-accessible Aviator bot UI with a safe local simulator and an optional 1xBet Playwright adapter (simulate-only by default).

Important warnings
- Automating gambling sites may violate the site's Terms of Service and could be illegal in your jurisdiction. Only run live automation against accounts you own and are allowed to automate.
- This project does NOT include any bypass for captchas, 2FA, or other protections. If those appear, you must intervene manually.

Quick start (recommended, simulator-only)
1. Clone
   git clone https://github.com/sibuya404/aviator-bot-ui.git
   cd aviator-bot-ui/server
2. Install
   npm install
3. Run
   npm run start
4. Open http://localhost:3000 in your browser

To enable Playwright (live adapter), read README section "Running the 1xBet adapter".

License: MIT
