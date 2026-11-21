# AniList Bio Auto-Updater

A GitHub repo that **rewrites your AniList bio for you, every day, with no server and no cost.**
Each day it picks a theme (colours, banner, poster, stat cards), builds your bio and sends it to
AniList. You set it up once and then forget it.

- **12 anime themes included**: Grimjow (signature), Attack on Titan, Naruto, Demon Slayer,
  That Time I Got Reincarnated as a Slime, Mob Psycho 100, Haikyu!!, Jujutsu Kaisen, Bleach,
  Solo Leveling, Black Clover and One Piece.
- **Live stat cards** from [AniCards](https://github.com/RLAlpha49/AniCards): status overview,
  anime and manga stats, favourites grids, currently watching/reading, genre synergy.
- **Your own text** (tagline, about, fun fact, quote, links) shows on every theme.
- Works for **any AniList account**. The script finds your username from your token.

Sample output for every theme is in [`reference-bios/`](reference-bios/).

---

## How it works (30 seconds)

```
GitHub Actions (timer)  ->  anilist_bio_updater.py  ->  AniList API  ->  your profile bio
      5 times a day          builds the bio text        updates "About"
```

Banners and posters are image files in this repo. AniList shows them by loading them from
GitHub. The stat cards are small pictures drawn live by AniCards.

---

## Before you start

You need:

- A **GitHub account** (free) and an **AniList account**.
- About **20 minutes**. No coding is needed. Everything is done in your web browser.

Two rules that trip people up:

1. **Your repo must be PUBLIC.** AniList loads your banner and poster from GitHub. A private repo
   hides them, so the images will show as broken.
2. **Your repo's main branch must be called `main`** (it is by default).

---

## Part 1: Copy the repo

1. Sign in to GitHub and open this repo's page.
2. Click **Fork** (top right), keep the name, click **Create fork**.
3. In your fork, open the **Actions** tab. If GitHub shows a green button *"I understand my
   workflows, go ahead and enable them"*, click it. (Forks have scheduled runs switched off
   until you do this.)

> Tip: if the owner enabled it, you can click **Use this template** instead. Make it public.

## Part 2: Get your AniList token

The token lets the workflow edit your bio. It is the only AniList thing you need.

1. Go to <https://anilist.co/settings/developer> and click **Create New Client**.
2. Fill in:
   - **Name:** anything, e.g. `Bio Updater`
   - **Redirect URL:** `https://anilist.co/api/v2/oauth/pin`
3. Save. You will see your client with a **number**. That is the **Client ID**. Copy it.
4. Put your number in this link and open it in your browser:

   `https://anilist.co/api/v2/oauth/authorize?client_id=YOUR_ID&response_type=token`

5. Click **Authorize**. The next page shows a very long text, which is your token.
   **Copy all of it** (don't miss the end).

You do not need the Client Secret. The token works for about **1 year**.

## Part 3: Save the token as a secret

1. In your fork go to **Settings > Secrets and variables > Actions**.
2. Stay on the **Secrets** tab and click **New repository secret**.
3. **Name:** `ANILIST_TOKEN` (exactly, capital letters, underscore).
4. **Secret:** paste your token. Click **Add secret**.

**Is it safe in a public repo?** Yes. GitHub stores secrets encrypted. Nobody can read it back,
and it never appears in your files or logs. **Never paste the token anywhere else** (not in a
file, chat or screenshot). Make sure it is under **Secrets**, not **Variables**.

## Part 4: Set up your stat cards (once)

1. Open <https://anicards.alpha49.com/generator>.
2. Enter your AniList username and generate.

This makes sure AniCards has your profile data. If you skip it, the cards may show an error
picture until you do it. Cards can lag a little behind AniList, which is normal.

## Part 5: Make it yours

Open `anilist_bio_updater.py` in your fork, click the **pencil icon** (Edit), and change these
lines near the top. Use **Ctrl+F** to find them. Click **Commit changes** when done.

| Line to change | What to put |
|---|---|
| `TAGLINE` | One line under your name, e.g. `"anime addict &bull; one more episode"`. Use `&bull;` for a dot. |
| `ABOUT` | Your "about me" paragraph. `**word**` makes bold. |
| `FUN_FACT` | A fun fact. It is hidden behind a spoiler tag on AniList. Don't end it with `!`. |
| `QUOTE` and `QUOTE_BY` | A favourite quote and who said it. |
| `LINKS` | Your links, e.g. `[("Discord", "https://..."), ("YouTube", "https://...")]`. Any link still containing `YOUR-` is hidden automatically. |
| `BIO_TZ` | Your timezone, e.g. `"America/New_York"` or `"Europe/London"`. The theme changes at midnight in this zone. |
| `ROTATION_START` | Today's date as `datetime.date(2026, 11, 20)` (year, month, day). The first theme in `ROTATION` starts that day. |

**Do not edit** `USER` or `CARD_USER_ID`. The workflow finds your account from the token.

The included banners and posters are the original owner's artwork. Replace them with yours (see
[Images](#images)) or keep them for testing.

## Part 6: First run

1. Open the **Actions** tab, click **Update AniList bio** on the left, then **Run workflow** and
   the green **Run workflow** button.
2. Wait about 30 seconds and refresh. A **green tick** means success.
3. Click the run, then the **update** job, then the step **Rebuild bio and push to AniList**.
   You should see:
   - `Theme: <name> | user: <your username>` and
   - `Bio updated.` (or `Bio unchanged, nothing to push.`)
4. Open your AniList profile and **hard refresh** (Ctrl+Shift+R).

After that it runs by itself. A red cross means something is wrong. See
[Troubleshooting](#troubleshooting).

---

## When does it run?

The workflow file `.github/workflows/update-bio.yml` has two timers (GitHub uses **UTC**):

| Timer | UTC | India (IST) example |
|---|---|---|
| Every 6 hours | 00:00, 06:00, 12:00, 18:00 | 05:30, 11:30, 17:30, 23:30 |
| Daily | 18:35 | 00:05 (just after midnight, so the new day's theme starts) |

If your timezone is not IST, you can leave the timers as they are. The theme still changes at
midnight in the `BIO_TZ` you set, and the next run after that applies it. To change the timers,
edit the `cron` lines. Some quirks:

- GitHub often starts runs **5 to 30 minutes late**, and sometimes skips one.
- **Public repos pause scheduled runs after 60 days** with no commits. Make any small commit, or
  click **Enable workflow** in the Actions tab, to restart them.
- You can always run it by hand with **Run workflow**.

## How themes rotate

The theme changes **every day** and walks through the `ROTATION` list in order, then starts over.
Day 1 is `ROTATION_START`. These settings sit near the middle of the script:

| Setting | Meaning |
|---|---|
| `ROTATION` | The themes in order. Remove names to skip a theme. |
| `DAYS_PER_THEME` | `1` = new theme daily. `2` = each theme for 2 days. |
| `RANDOM_DAY` | `True` adds one random-theme day at the end of every cycle. |
| `ROTATION_START` | The date the cycle begins. |
| `BIO_TZ` | The timezone that decides when the day changes. |

**Keep one theme only (pin it):** in your repo go to **Settings > Secrets and variables > Actions
> Variables > New repository variable**, name `BIO_THEME`, value = a theme name. Delete the
variable to go back to the rotation.

Theme names: `grimjow`, `attackontitan`, `naruto`, `demonslayer`, `slime`, `mobpsycho`,
`haikyuu`, `jujutsukaisen`, `bleach`, `sololeveling`, `blackclover`, `onepiece`.

## Make your own theme

In `anilist_bio_updater.py`, find `THEMES = {` and copy an existing block. Example:

```python
    "mytheme": {
        "symbol": "\u2605",                       # shown either side of your name
        "banner": "banners/mytheme-banner.png",   # image at the top
        "poster": "posters-web/mytheme.jpg",      # under "About me" (optional)
        "tagline": None,                          # None = use TAGLINE; or your own text
        "preset": "default",
        "colors": ("&titleColor=%23F2C14E&backgroundColor=%230B0F0B&textColor=%23E8EFE8"
                   "&circleColor=%232E9E4F&borderColor=%23D4A62A"),
    },
```

- **Colours** are hex codes where `#` is written as `%23` (so `#F2C14E` becomes `%23F2C14E`).
  `title` = card headings, `background` = card fill, `text` = card text, `circle` = chart
  accent, `border` = card outline. Soft, muted colours look best on AniList.
- **Several posters:** `"poster": ["posters-web/a.jpg", "posters-web/b.jpg"]` shows them side by side.
- **No poster or banner:** just delete that line.
- Then add `"mytheme"` to `ROTATION` (or pin it with `BIO_THEME`).

## Change the cards

`CARD_ROWS` controls the cards. Each inner list is one row, and cards in the same list sit side
by side. Each card is `(cardType, variation, extra)`:

```python
CARD_ROWS = [
    [("animeStats", "default", ""), ("mangaStats", "default", "")],            # two side by side
    [("favoritesGrid", "anime", "&gridCols=3&gridRows=3")],                    # one on its own
]
```

Card types used here: `statusCompletionOverview`, `animeStats`, `mangaStats`, `favoritesGrid`
(variations `anime`, `manga`, and others), `currentlyWatchingReading` (`anime` or `manga`) and
`animeGenreSynergy`. AniCards has many more. Browse them in the generator and copy the
`cardType` and `variation` from the link it gives you.

- **Width:** `CARD_W` (default 340 px) is the width of each card, and `CARD_WIDTHS` overrides one
  card type. If two cards stack instead of sitting side by side, lower `CARD_W` to about 300.
- **Turn all cards off:** `CARD_ROWS = []`.
- **Favourites grids show your AniList favourites**, so mark some on AniList first.
- **Text sections instead of cards:** set `TEXT_SECTIONS = True` to also write counts, top picks
  by score, currently watching/reading covers and favourite genres from live data.
- **Cover-image favourites without AniCards:** set `FAV_N = 6` (shows 6 favourite covers).

---

## Images

| Folder | What goes there | Size to aim for |
|---|---|---|
| `banners/` | One banner per theme | 1200 x 600, a few hundred KB to ~1.5 MB |
| `posters-web/` | One poster per theme (web size) | 700 px wide, ~200 KB |
| `images/`, `posters/` | Original big artwork (optional) | Not used by the workflow |

**Use small files.** Very large images (several MB) may fail to load on AniList. The big
originals can stay on your computer. They only make the repo heavy, so you can delete
`images/` and `posters/` from your fork.

**Make web-sized files from your own artwork** with the two helper tools in `tools/`. You need
[Python](https://www.python.org/downloads/) and one install: `pip install pillow numpy`.

```
python tools/banner_maker.py my-art.jpg banners/mytheme-banner.png
python tools/poster_maker.py my-poster.png posters-web/mytheme.jpg
```

- **`banner_maker.py`** crops your picture to 1200 x 600 and makes it translucent with soft
  edges. Options: `--opacity 0.75` (how solid; `0.3` is very faint) and `--fit` (keep the whole
  picture instead of cropping, good for logos). Save it as a `.png` so the transparency stays.
- **`poster_maker.py`** shrinks a big poster to a small JPG. Options: `--width 700` and
  `--quality 86`. A poster of 8 MB usually becomes about 200 KB.

To upload files on GitHub: open the folder, then **Add file > Upload files**.

**Only use artwork you are allowed to use.** The included art belongs to its owners.

---

## Try it on your computer (optional)

Safe: it does not change your profile.

```
python anilist_bio_updater.py --theme naruto --out test.md
```

(On Windows use `py` if `python` is not found.) Open `test.md` to see the bio text. Add `--push`
with the token set in `ANILIST_TOKEN` to update your profile from your own machine. Leave out
`--theme` to see today's theme.

---

## Troubleshooting

Open the failed run, then the step **Rebuild bio and push to AniList** and read the last lines.

| What you see | Cause | Fix |
|---|---|---|
| `Set ANILIST_TOKEN to push the bio.` | Secret missing or misnamed | Re-add it under **Secrets** as exactly `ANILIST_TOKEN` (not under Variables) |
| `HTTP 401` or "Invalid token" | Token wrong, incomplete or expired | Make a new token (Part 2) and replace the secret |
| `Could not look up your AniList user` | Token problem or AniList is down | Check the token; try again later |
| `HTTP 403` | AniList blocked the request | Re-run. If it keeps happening, open an issue with the full message |
| `HTTP 400 ... Cannot query field` | AniList changed its API | Open an issue with the message |
| Green tick, profile looks old | Browser cache | Hard refresh (Ctrl+Shift+R) or use a private window |
| `Bio unchanged, nothing to push.` | Your bio already matches | Normal. The theme only changes at midnight |
| Banner or poster shows broken | Repo is private, wrong file name or folder, or the branch is not `main` | Make the repo **public**; check the path in `THEMES` matches the file exactly (names are case-sensitive) |
| A card shows an error or is blank | AniCards has no data for you yet | Do Part 4, then open the card link in a browser to read its message |
| Favourites grid is empty | No favourites on AniList | Favourite some anime and manga on AniList |
| Cards stack instead of sitting side by side | Too wide for your profile | Lower `CARD_W` (try 300) |
| Workflow not listed in the Actions tab | File is in the wrong place | It must be exactly `.github/workflows/update-bio.yml` |
| Never runs by itself | Actions not enabled on a fork, or 60 days with no commits | Enable workflows (Part 1); make a small commit |
| Theme never changes | `BIO_THEME` variable is set | Delete the variable in Settings > Secrets and variables > Actions > Variables |
| Theme changes at the wrong hour | Wrong `BIO_TZ` | Set your timezone name |

## Keep it working

- **Token expires after about a year.** Runs then fail with a 401. Repeat Part 2 and replace the
  secret. GitHub usually emails you when a run fails.
- **Lost or leaked token?** On AniList go to **Settings > Apps** and revoke it, then make a new one.
- **Do not add collaborators you don't trust.** Anyone with write access can edit the workflow.

## What is in this repo

```
anilist_bio_updater.py        the script that builds and pushes the bio
.github/workflows/update-bio.yml   the schedule
banners/                      one banner per theme
posters-web/                  one web-sized poster per theme
reference-bios/               sample output of every theme (not used by the workflow)
tools/banner_maker.py         makes a translucent banner from your artwork
tools/poster_maker.py         shrinks a poster to a small web-sized file
images/, posters/             original large artwork (optional, not used)
```

## Credits

- Stat cards by [AniCards](https://github.com/RLAlpha49/AniCards) (a free third-party service,
  not affiliated with AniList).
- Data and bio hosting by [AniList](https://anilist.co).
- Anime artwork belongs to its respective owners.
