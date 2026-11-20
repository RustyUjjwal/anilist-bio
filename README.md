# AniList bio auto-updater

Builds an AniList bio with stat cards and a themed banner, and keeps it updated with GitHub
Actions. Fork it, add one secret, and it works for **your** AniList account.

- Cards come from [AniCards](https://github.com/RLAlpha49/AniCards) (anime/manga stats, favourites, status overview, genre synergy, currently watching/reading).
- Twelve themes rotate on a schedule: Grimjow (the signature bio), Attack on Titan, Naruto, Demon Slayer, That Time I Got Reincarnated as a Slime, Mob Psycho 100, Haikyu!!, Jujutsu Kaisen, Bleach, Solo Leveling, Black Clover and One Piece. Each has its own colours, title symbol, translucent banner and a poster under "About me".
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
| `ROTATION`, `DAYS_PER_THEME`, `ROTATION_START` | By default a new theme every day, walking through `ROTATION` in order. Set `DAYS_PER_THEME = 2` to keep each theme longer, `RANDOM_DAY = True` to add a random day per cycle, or `ROTATION` to a shorter list. |
| `BIO_TZ` | Timezone that decides when the day changes, e.g. `"America/New_York"`. |
| `CARD_ROWS` | Which cards show and how they sit. Cards in the same inner list sit side by side. |
| `CARD_W`, `CARD_WIDTHS` | Card widths in px. Lower them if cards stack on your profile. |
| `TEXT_SECTIONS`, `FAV_N` | Optional text sections and cover-image favourites. Both off by default. |

**Images**: banners live in `banners/` and web-sized posters in `posters-web/`. A theme's
`banner` / `poster` entries point at those files (one poster or a list of posters). The included
artwork belongs to the original owner, so replace it with your own. Keep images web-sized
(a few hundred KB; huge files may not load on AniList). Large originals can live in other
folders (like `images/` and `posters/`) and are never read by the workflow.

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
- `banners/` and `posters-web/`: the images the bios link to.
- `reference-bios/`: sample output for each theme (reference only, not used by the workflow).
