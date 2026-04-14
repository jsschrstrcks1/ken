# Cloudflare R2 Migration Runbook

> **New to Cloudflare?** Start with [`01-cloudflare-github-setup.md`](./01-cloudflare-github-setup.md) — it walks through connecting Cloudflare to your GitHub Pages site in plain language. Come back here once that's done.

Moves all InTheWake image content off GitHub Pages and onto Cloudflare R2, served through a Cloudflare Worker at the current canonical paths. **Zero HTML changes, zero broken URLs.**

## Why R2 (vs. alternatives)

| Option | Monthly cost | CDN | URL change |
|---|---|---|---|
| **Cloudflare R2** | **$0** (10GB free, zero egress) | **Cloudflare edge** | None (Worker proxy) |
| AWS S3 + CloudFront | ~$0.05 + $0.085/GB egress | CloudFront | None or domain swap |
| Git submodule | $0 | None (GitHub Pages only) | None |

R2 wins because the site is image-heavy (4,486 WebP + 835 JPG) and scales without egress cost.

## Prerequisites (user action required)

1. **Cloudflare account** — sign up at cloudflare.com (free plan is fine)
2. **Domain on Cloudflare** — move `cruisinginthewake.com` DNS to Cloudflare (free). Verify `CNAME cruisinginthewake.com → jsschrstrcks1.github.io` stays resolvable after the move.
3. **`wrangler` CLI** — `npm install -g wrangler` (used to create and deploy the Worker)
4. **`rclone`** — `brew install rclone` or equivalent (used to sync images into R2)

## Step 1: Create the R2 bucket

```bash
# Log in to Cloudflare from wrangler
wrangler login

# Create the bucket
wrangler r2 bucket create inthewake-media

# Enable versioning for safety (so accidental deletes are recoverable)
wrangler r2 bucket lifecycle add inthewake-media \
  --name "keep-versions-30d" \
  --condition "object-version-age-greater-than=30"
```

## Step 2: Configure rclone for R2

Create an rclone remote for R2. Get your R2 API token from Cloudflare dashboard → R2 → Manage R2 API Tokens.

```bash
rclone config
# Select: n (new remote)
# Name: r2
# Type: 5 (Amazon S3 Compliant)
# Provider: 4 (Cloudflare R2)
# env_auth: false
# access_key_id: <from R2 API token>
# secret_access_key: <from R2 API token>
# endpoint: https://<account-id>.r2.cloudflarestorage.com
# region: auto
```

## Step 3: Sync images to R2

Run from the InTheWake repository root:

```bash
bash ../ken/admin/inthewake/r2-migration/rclone-sync.sh
```

Or manually, one tree at a time:

```bash
rclone sync assets/ships/      r2:inthewake-media/assets/ships/      --progress
rclone sync ports/img/         r2:inthewake-media/ports/img/         --progress
rclone sync assets/social/     r2:inthewake-media/assets/social/     --progress
rclone sync assets/images/     r2:inthewake-media/assets/images/     --progress
rclone sync assets/venues/     r2:inthewake-media/assets/venues/     --progress
rclone sync assets/articles/   r2:inthewake-media/assets/articles/   --progress
rclone sync assets/brand/      r2:inthewake-media/assets/brand/      --progress
rclone sync assets/icons/      r2:inthewake-media/assets/icons/      --progress
rclone sync assets/img/        r2:inthewake-media/assets/img/        --progress
rclone sync authors/img/       r2:inthewake-media/authors/img/       --progress
rclone sync authors/ico/       r2:inthewake-media/authors/ico/       --progress
rclone sync solo/images/       r2:inthewake-media/solo/images/       --progress
rclone sync images/            r2:inthewake-media/images/            --progress
```

Expected upload size: ~2GB.

## Step 4: Deploy the Worker

```bash
cd ../ken/admin/inthewake/r2-migration/
# Edit wrangler.toml to set your account_id and route pattern
wrangler deploy
```

The Worker intercepts image paths and serves from R2 with aggressive caching. See `worker.js` for the route list.

## Step 5: Preview verification

Before flipping production DNS, test on a preview subdomain:

```bash
# Deploy to a preview route
wrangler deploy --route "preview.cruisinginthewake.com/*"
```

Then run the automated check:

```bash
bash ../ken/admin/inthewake/r2-migration/verify-images.sh preview.cruisinginthewake.com
```

This crawls a sample of 50 pages across port/ship/restaurant types, fetches every image URL from both production and preview, and compares HTTP 200 rates + byte counts.

## Step 6: Production cutover

1. Flip Worker route to `cruisinginthewake.com/*` for the image path patterns (NOT the whole domain — HTML still served by GitHub Pages)
2. Monitor Cloudflare analytics for 24 hours; watch for 404 spikes
3. After 24 hours clean: remove image directories from the InTheWake repo

## Step 7: Remove images from the InTheWake repo

Once R2 is verified as the live source:

```bash
cd InTheWake
git rm -r assets/ships/ ports/img/ assets/social/ assets/images/ \
         assets/venues/ assets/articles/ assets/brand/ assets/icons/ \
         assets/img/ authors/img/ authors/ico/ solo/images/ images/
git commit -m "Phase 3A: remove image directories now served from Cloudflare R2"
```

R2 versioning (set up in Step 1) retains the files for 30 days as a safety net.

## Step 8: Update deploy workflow

Add the image directory excludes to `.github/workflows/static.yml` rsync step to prevent any stale copies from deploying:

```yaml
--exclude='assets/ships/' \
--exclude='ports/img/' \
--exclude='assets/social/' \
# ... etc
```

## Rollback plan

If R2 has unforeseen issues, disable the Worker route — image requests will 404 until either:
1. The Worker is re-enabled, OR
2. `git revert` the image-deletion commit from Step 7, re-push, and wait for GitHub Pages deploy

Keep rollback window short (hours) so the R2 path is the canonical source.

## Fallback: Git submodule approach

If R2 proves unworkable:
1. Create `jsschrstrcks1/InTheWake-media` repository
2. Push image directories there
3. Add as a git submodule to InTheWake at `./`
4. Update `.github/workflows/static.yml` checkout step with `submodules: recursive`

Same file layout works for either approach.

Soli Deo Gloria.
