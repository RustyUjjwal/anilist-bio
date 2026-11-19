# AniList bio auto-updater

Builds an AniList bio with stat cards and a themed banner, and keeps it updated with GitHub
Actions. Fork it, add one secret, and it works for **your** AniList account.

- Cards come from [AniCards](https://github.com/RLAlpha49/AniCards) (anime/manga stats, favourites, status overview, genre synergy, currently watching/reading).
- Three themes included (Black Clover, Solo Leveling, Grimjow) that rotate on a schedule.
- No server needed. The workflow talks to AniList directly.

## Quick start

1. **Fork this repo** (or click "Use this template" if the owner enabled it). Keep it public or private.
2. **Create an AniList token**
   1. Go to https://anilist.co/settings/developer and create a client. Name: anything.
      Redirect URL: `https://anilist.co/api/v2/oauth/pin`
   2. Open `https://anilist.co/api/v2/oauth/authorize?client_id=YOUR_ID&response_type=token`
      (use your Client ID) and click Authorize. Copy the token. It lasts about a year.
3. **Add it as a secret**: repo Settings > Secrets and variables > Actions > New repository
   secret. Name `ANILIST_TOKEN`, value = the token. Secrets stay private, even in a public repo.
   Never paste the token into a file.
4. **Set up your AniCards profile once**: open https://anicards.alpha49.com/generator, enter your
   username and generate. Without this the cards may show errors.
5. **Edit the text** at the top of `anilist_bio_updater.py` (see below), then commit.
6. Open the **Actions** tab > "Update AniList bio" > **Run workflow**. Check your profile.

Your username and AniCards user ID are found automatically from your token. You don't need to
type them anywhere.

## What to customise

At the top of `anilist_bio_updater.py`:

| Setting | What it does |
|---|---|
| `TAGLINE`, `ABOUT`, `FUN_FACT`, `QUOTE`, `QUOTE_BY`, `LINKS` | The text in your bio. These are the original owner's, so change them. |
| `THEMES` | Colours, title symbol, banner and optional poster per theme. Copy an entry to add your own. |
| `SCHEDULE` | Which theme on which weekday (Monday first). Use `"random"` for a random day. |
| `BIO_TZ` | Timezone that decides when the day changes, e.g. `"America/New_York"`. |
| `CARD_ROWS` | Which cards show and how they sit. Cards in the same inner list sit side by side. |
| `CARD_W`, `CARD_WIDTHS` | Card widths in px. Lower them if cards stack on your profile. |
| `TEXT_SECTIONS`, `FAV_N` | Optional text sections and cover-image favourites. Both off by default. |

**Images**: put your banner (and poster) files in the repo root and point a theme's `banner` /
`poster` at the file name. The included images belong to the original owner. Replace them,
and delete the `poster` line from a theme if you don't want one. Use web-sized images
(a few hundred KB; huge files may not load on AniList).

**Pin one theme**: add a repo variable `BIO_THEME` (Settings > Secrets and variables > Actions >
Variables) set to a theme name. Remove it to go back to the rotation.

## Testing without pushing

```
python anilist_bio_updater.py --theme grimjow --out test.md
```

This writes the bio to a file and needs no token. It uses the defaults at the top of the file
for the user unless you set `ANILIST_USER=yourname`. Paste the file into your AniList bio
by hand if you only want a one-off.

## Good to know

- Scheduled runs: every 6 hours, plus one just after midnight India time. GitHub can delay them.
  Public repos pause schedules after 60 days with no repo activity (push any commit to resume).
- When the token expires the run fails. Make a new one and replace the secret.
- AniCards is a free third-party service. Cards can lag behind your AniList data, and it is
  not affiliated with AniList.
- Only use artwork you're allowed to use.

## Files

- `anilist_bio_updater.py`: builds the bio and pushes it.
- `.github/workflows/update-bio.yml`: the schedule.
- Banner/poster images in the root.
- `anilist_bio_*.md`: sample output for each theme (reference only).
