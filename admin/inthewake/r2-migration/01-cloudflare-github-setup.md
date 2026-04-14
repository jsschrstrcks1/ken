# How to Connect Cloudflare to GitHub (Explained Like You're 5)

This is step zero. Do this one first. When you're done here, come back and open `README.md` to finish moving your pictures to their new home.

---

## What are we doing?

Imagine your website is a library called **GitHub**. People come visit to read the books. Right now, when someone asks for your library, they walk straight through the front door and GitHub hands them what they want.

We're going to put a friendly receptionist named **Cloudflare** in front of the library's door.

Why? Because later, we want the receptionist to grab the **pictures** from a different room (called R2) instead of making GitHub carry them around. GitHub is great at books (web pages), but we want a specialist for pictures.

Today we're **just hiring the receptionist.** No pictures are moving yet. Your website will keep working the whole time.

---

## What you need before you start

1. **A Cloudflare account.** It's free. We'll make one in a minute.
2. **Access to wherever you bought your domain name** (`cruisinginthewake.com`). This could be GoDaddy, Namecheap, Google Domains, Porkbun, or similar. You'll need your login there.
3. **About 30 minutes of your time, plus some waiting.** Some steps need 1 to 24 hours to "settle." You don't have to watch — just come back later.

If you don't remember where you bought the domain: check your email for receipts from GoDaddy, Namecheap, or anything with "domain" in the subject line.

---

## Step 1: Make a Cloudflare account

1. Go to **https://cloudflare.com**
2. Click **Sign Up** in the top-right corner.
3. Type in your email and pick a password. Write the password down somewhere safe.
4. Check your email for a "Verify your email" message. Click the link inside.

That's it. You now have a Cloudflare account.

---

## Step 2: Tell Cloudflare about your website

1. After logging in, Cloudflare shows you a dashboard (a page full of options).
2. Click **Add a Site** (sometimes labeled **Add a domain**).
3. Type `cruisinginthewake.com` and click **Add Site**.
4. Cloudflare asks which plan you want. Choose **Free**. (There are paid plans. You don't need them.)
5. Click **Continue**.

Cloudflare now looks at your domain and tries to figure out where everything currently points. This takes about 30 seconds. When it's done, you see a page with a **list of DNS records**.

### 🛟 Safety step: take a screenshot of that list

Before you change anything, **take a screenshot of the whole list** and save it somewhere you can find it. If anything goes wrong later, this screenshot is how we put things back.

---

## Step 3: Check the DNS list

Think of **DNS records** as directions for the internet. They say "when someone asks for this name, send them to this address." You should see a few rows.

Look for one that has:
- **Name:** `cruisinginthewake.com` or `@` or `www`
- **Content:** something like `jsschrstrcks1.github.io`, OR four IP addresses that start with `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`

That's your GitHub Pages connection. Good — it's already there. **Don't delete it.**

### Turn the cloud orange

Next to each row is a little **cloud icon** ☁️. It's either grey or orange.

- **Orange cloud** = Cloudflare receptionist is active for this record. This is what we want.
- **Grey cloud** = Cloudflare is just passing directions through; it's not helping.

Click any grey cloud on your GitHub Pages record to turn it **orange**. Do NOT turn on the orange cloud for email records (rows that say `MX` in the type column) — those should stay grey. If you're not sure, leave them alone.

When you're done, click **Continue** at the bottom.

---

## Step 4: Change the nameservers at your domain registrar

This is the step that feels scary. It's not scary. We're just telling the internet's phone book to start listening to Cloudflare instead of your old provider.

Here's the analogy: right now, when someone asks "where is cruisinginthewake.com?", the internet asks your domain registrar. We're changing that so the internet asks Cloudflare instead.

### What Cloudflare tells you to do

Cloudflare shows you a page with something like:

> **Replace the nameservers with:**
> `alice.ns.cloudflare.com`
> `bob.ns.cloudflare.com`

(The names will be different for you — usually a flower name and a name like that.)

**Write these two names down** on paper or copy them into a notes app. You're about to paste them somewhere else.

### What to do at your registrar

1. Open a new browser tab and log in to wherever you bought `cruisinginthewake.com` (GoDaddy, Namecheap, etc.).
2. Find the domain `cruisinginthewake.com` in your list.
3. Look for a setting called **Nameservers** or **DNS** or **Change Nameservers.**
   - On GoDaddy: domain → **DNS** tab → scroll down to **Nameservers** → click **Change**
   - On Namecheap: domain → **Domain** tab → **Nameservers** section → choose **Custom DNS**
   - On Google Domains: domain → **DNS** → scroll to **Name servers** → **Use custom name servers**
   - Other providers: search their help for "change nameservers"
4. There will be **two or more nameserver names already there.** They probably include the registrar's name (like `ns1.godaddy.com`). **Delete these** and replace with the two Cloudflare names you wrote down.
5. Save.

That's it. You've just handed the keys to Cloudflare.

### Tell Cloudflare you're done

Go back to the Cloudflare tab. There's a button that says **Done, check nameservers** or **Check nameservers**. Click it.

Cloudflare says: "Great, we'll check every few minutes. We'll email you when it's active."

---

## Step 5: Wait

This is the part where you close the browser tab and go do something else.

- **Usually takes:** 5 minutes to 2 hours
- **Sometimes takes:** up to 24 hours
- **While you wait:** your website keeps working normally. Visitors don't notice anything.

You'll get an email from Cloudflare with the subject **"cruisinginthewake.com is now active on Cloudflare."** When that arrives, you're ready for Step 6.

If you're impatient, you can check yourself: go back to the Cloudflare dashboard, click your domain, and look at the top. It says **Active** when ready. If it says **Pending**, keep waiting.

---

## Step 6: Check that everything still works

Once Cloudflare emails you:

1. Open your website at `https://cruisinginthewake.com` in a fresh browser tab.
2. Click around — go to a few pages, look at images, click some links.
3. Everything should look the same as before.

### Fancy check (optional)

If you want proof the receptionist is there:

1. Press **F12** in your browser (or right-click → Inspect) to open DevTools.
2. Click the **Network** tab.
3. Refresh the page.
4. Click the first item in the list (usually named the same as the page).
5. Look at the right side for **Response Headers.**
6. You should see a line that says something like `cf-ray: abc123...` — that's the receptionist's signature. ✅

If the site doesn't load, skip to the "What can go wrong" section below.

---

## Step 7: Turn on HTTPS (30 seconds)

HTTPS is the little padlock 🔒 in the browser address bar. It means the connection is secure. Let's make sure Cloudflare always uses it.

1. In Cloudflare dashboard → click your domain → on the left sidebar, click **SSL/TLS**.
2. You'll see a sub-menu. Click **Overview.**
3. Set the encryption mode to **Full.**
   - ⚠️ Do NOT pick **Full (strict)** — GitHub Pages doesn't need strict mode and will break if you pick it.
4. Still in SSL/TLS, click **Edge Certificates** in the sidebar.
5. Scroll down to **Always Use HTTPS** and toggle it **ON.**

Done. Cloudflare will now quietly upgrade any `http://` request to `https://`.

---

## What can go wrong (and how to fix it)

### The site shows a Cloudflare error page saying "Error 522" or "Connection timed out"

**What it means:** The SSL/TLS mode is wrong.

**Fix:** Go to Cloudflare → your domain → SSL/TLS → Overview → set to **Full** (not Full (strict)).

### The site loads but it's the old, cached version

**What it means:** Cloudflare is showing you a saved copy.

**Fix:** Cloudflare dashboard → your domain → **Caching** → **Configuration** → click **Purge Everything.** Wait 30 seconds, reload.

### The site doesn't load at all, browser says "site can't be reached"

**What it means:** Nameserver change hasn't fully propagated across the internet yet.

**Fix:** Wait an hour. Try again. If still broken after 24 hours, go back to your registrar and verify the two nameserver names are exactly what Cloudflare told you to use (no typos).

### Email stopped working on `@cruisinginthewake.com`

**What it means:** The DNS scan in Step 2 missed an **MX record** (the record that tells email where to go).

**Fix:** Go to Cloudflare → your domain → **DNS** → **Records.** Check if there's an `MX` type record. If not, look at the screenshot you took in Step 2 and add any missing `MX` rows back. Their cloud should stay **grey** (email doesn't use Cloudflare).

### Something else broke and you want to undo everything

Go back to your registrar and change the nameservers back to what they were before. Your screenshot from Step 2 has the original settings. The undo takes another 1–24 hours to settle, but it's a complete rollback.

---

## You're done! 🎉

You just hired a receptionist. Your site is running through Cloudflare now.

**Next step:** Come back to this folder and open `README.md`. That walks through moving your pictures to Cloudflare R2 (the "different room" from the analogy at the start). The receptionist you just hired is how those pictures will reach your visitors.

Soli Deo Gloria.
