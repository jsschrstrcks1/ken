# How to Install and Use Wrangler (Explained Like You're 5)

This is step zero-point-five. Do this after `01-cloudflare-github-setup.md` and before the main `README.md`. When you're done here, you'll have a tool called **wrangler** on your computer that lets you talk to Cloudflare from Terminal.

---

## What is wrangler?

Cloudflare has a website called the **dashboard** — you log in at https://dash.cloudflare.com and click buttons to do things.

Wrangler is a **remote control** for Cloudflare. Instead of clicking around the website, you type one command in Terminal and the same thing happens. For most Cloudflare tasks the dashboard is fine. For **two specific tasks** in this runbook, wrangler is faster and less error-prone.

Wrangler is made by Cloudflare themselves. It's open source (you can read the code). Proof: https://github.com/cloudflare/workers-sdk/tree/main/packages/wrangler

---

## Sidebar: "What's a CLI?"

CLI stands for **command-line interface**. It's the thing where you type words into a black window instead of clicking. If you've never opened one:

- **Mac:** press **Cmd + Space**, type `Terminal`, press Enter.
- **Windows:** click Start, type `PowerShell`, press Enter.
- **Linux:** you probably already know where Terminal is.

You'll see a blinking cursor next to some text like `yourname@yourcomputer ~ %`. That's where you type commands.

---

## Why do I need it? Can't I just use the website?

For most of Cloudflare, yes — the dashboard works fine. For the R2 migration there are **exactly two** commands where wrangler is the easiest path:

1. **Creating the R2 bucket.** One command vs. several dashboard clicks.
2. **Deploying the Worker code** (the small program that serves your pictures from R2). This one is *much* easier with wrangler than through the dashboard.

That's it. You'll use wrangler twice, ever. Then you can forget about it until the next migration.

---

## Step 1: Install Node.js (wrangler needs it)

Wrangler is a program written in a language called JavaScript. To run JavaScript on your computer, you need **Node.js**. Node.js comes bundled with a tool called **npm**, which is what actually installs wrangler.

If you type `npm --version` in Terminal and see `command not found`, Node.js isn't installed yet. Install it first.

### macOS (the primary path — you're probably here)

**If you already have Homebrew installed** (type `brew --version` to check):

```bash
brew install node
```

**If you don't have Homebrew** (or aren't sure):

1. Open https://nodejs.org in your browser.
2. Click the big green button that says **LTS** (it means "Long Term Support" — the stable version).
3. Download the `.pkg` installer.
4. Double-click it and accept all the defaults.
5. **Close Terminal and open it again** — otherwise Terminal won't know Node.js got installed.

### Windows

Go to https://nodejs.org → download the LTS `.msi` installer → run it → accept defaults.

### Linux (Ubuntu/Debian)

```bash
sudo apt install nodejs npm
```

### Verify (any OS)

```bash
node --version
npm --version
```

Both should print a version number (like `v20.x.x` and `10.x.x`). If they do, Node is ready.

---

## Step 2: Install wrangler

```bash
npm install -g wrangler
```

The `-g` means "globally" — wrangler will be available from any folder you `cd` into. Takes about 30 seconds. Ignore the messages about "packages looking for funding."

### Mac permission note

If the install fails with `EACCES: permission denied`, that's a well-known Mac quirk. Run it with `sudo`:

```bash
sudo npm install -g wrangler
```

Terminal will ask for your Mac login password. Type it (you won't see any characters as you type — that's normal) and press Enter.

### Verify

```bash
wrangler --version
```

Should print something like `⛅️ wrangler 4.82.2`.

If you see `wrangler: command not found` — **close Terminal and open it again**, then try the version command once more. Terminal needs to pick up the newly-installed program.

---

## Step 3: Log in to Cloudflare from wrangler

```bash
wrangler login
```

This opens your web browser and takes you to a Cloudflare page that says something like "wrangler is requesting access to your account." Click **Allow.**

Close the browser tab. Back in Terminal you'll see `Successfully logged in.`

This is a one-time setup. After this, every wrangler command you run will automatically use your Cloudflare account.

---

## Step 4: The two commands you'll actually run

### Command 1 — Create the R2 bucket (Step 1 of the main runbook)

```bash
wrangler r2 bucket create inthewake-media
```

You can run this from any folder. You'll see:
```
✅ Created bucket 'inthewake-media' with default storage class of Standard.
```

Check the Cloudflare dashboard → **R2** — your new bucket is listed there.

### Command 2 — Deploy the Worker (Step 4 of the main runbook)

```bash
cd "$KEN_DIR/admin/inthewake/r2-migration/"
wrangler deploy
```

Where `$KEN_DIR` is the path to your local clone of the `ken` repo. For example, on most Macs it's something like `/Users/yourname/Documents/GitHub/ken`.

This uploads `worker.js` to Cloudflare and tells Cloudflare to run it on the routes listed in `wrangler.toml`. Takes about 10 seconds.

**Important one-time edit before the first deploy:** open `wrangler.toml` and replace the placeholder `REPLACE_WITH_YOUR_ACCOUNT_ID` with your actual Cloudflare Account ID. Find it at Cloudflare dashboard → right sidebar → **Account ID** (32-character string).

The safest way to make this edit — no text editor required:

```bash
cd "$KEN_DIR/admin/inthewake/r2-migration/"
sed -i '' 's/REPLACE_WITH_YOUR_ACCOUNT_ID/<paste-your-account-id-here>/' wrangler.toml
```

On Linux, drop the `''` after `-i`:
```bash
sed -i 's/REPLACE_WITH_YOUR_ACCOUNT_ID/<paste-your-account-id-here>/' wrangler.toml
```

If deploy succeeds, you'll see a block like:
```
Uploaded inthewake-r2-images (2.81 sec)
Deployed inthewake-r2-images triggers (1.70 sec)
  cruisinginthewake.com/assets/ships/* (zone name: cruisinginthewake.com)
  ...
```

---

## What can go wrong (and how to fix it)

### `npm: command not found`

Node.js isn't installed yet. Go back to Step 1. The easiest path on Mac is the `.pkg` installer from https://nodejs.org.

### `EACCES: permission denied` when running `npm install -g`

Prefix the install command with `sudo`:
```bash
sudo npm install -g wrangler
```

### `wrangler: command not found` right after install

Close Terminal and open a fresh window. Your shell's PATH hasn't picked up the newly-installed binary yet.

### The login browser window never opens

Wrangler prints the login URL in Terminal. Copy it and paste it into your browser manually.

### Deploy error mentions `REPLACE_WITH_YOUR_ACCOUNT_ID`

You haven't edited `wrangler.toml` yet, or the edit didn't save. Use the `sed` command above — it's the most reliable way.

### `Invalid TOML document` error on deploy

The `wrangler.toml` file got corrupted — usually from trying to edit it by hand in `vi` without knowing `vi`'s modal commands. The fix is to restore the clean version from the git repo and re-apply just the one change you need:

```bash
cd "$KEN_DIR/admin/inthewake/r2-migration/"
git checkout -- wrangler.toml
sed -i '' 's/REPLACE_WITH_YOUR_ACCOUNT_ID/<paste-your-account-id-here>/' wrangler.toml
wrangler deploy
```

(Drop the `''` after `-i` on Linux.)

### Deploy error mentions "zone not found" or "zone is not active"

`cruisinginthewake.com` isn't on Cloudflare yet. Go back to `01-cloudflare-github-setup.md`, finish moving the nameservers, and wait for the activation email from Cloudflare. Then come back here.

### `wrangler r2 bucket lifecycle add --condition …` gives `Unknown argument: condition`

The `--condition` flag doesn't exist in wrangler's CLI. Use the Cloudflare dashboard for lifecycle rules — see Step 1 of the main runbook for the dashboard walkthrough. (This is an optional safety-net step; skipping it is fine.)

---

## Is wrangler safe? Am I giving Cloudflare too much power?

Wrangler's login token can **only** touch your own Cloudflare account — it can't reach anyone else's. You're the only one with the token on your computer, and you can revoke it any time:

Cloudflare dashboard → click your profile icon (top right) → **My Profile** → **API Tokens** → find the wrangler token → **Revoke.**

If you ever want to uninstall wrangler itself:

```bash
npm uninstall -g wrangler
```

---

## You're done!

Wrangler is installed and logged in. Head back to `README.md` — the main runbook will tell you exactly when to run each of the two wrangler commands above.

Soli Deo Gloria.
