# AniList bio auto-updater

Rebuilds the GrimJow22 AniList bio and pushes it to AniList with GitHub Actions.

## Theme rotation
Monday and Tuesday: Black Clover. Wednesday and Thursday: Solo Leveling.
Friday and Saturday: Grimjow. Sunday: a random theme (same pick all day).
The day changes at midnight India time. Edit `SCHEDULE` / `BIO_TZ` in the script to change it.
To pin one theme, add a repo variable `BIO_THEME` (blackclover, sololeveling or grimjow).

## Files that must be in the repo root
- anilist_bio_updater.py
- .github/workflows/update-bio.yml
- black-clover-banner.png
- solo-levelling-banner.png
- anilist-profile-banner-enlarged.png
- grimjow-wanted.jpg

## Setup
1. AniList token: create a client at https://anilist.co/settings/developer with redirect URL
   https://anilist.co/api/v2/oauth/pin, then open
   https://anilist.co/api/v2/oauth/authorize?client_id=YOUR_ID&response_type=token and approve.
   The token lasts about a year.
2. Repo Settings > Secrets and variables > Actions > New repository secret: ANILIST_TOKEN.
3. Actions tab > "Update AniList bio" > Run workflow.

## Notes
- Cards come from AniCards (userId 7824217). Run the generator once at anicards.alpha49.com/generator.
- Local test: `python anilist_bio_updater.py --theme grimjow --out test.md` (no token needed).
- When the token expires the run fails: make a new token and update the secret.
- Public repos pause scheduled runs after 60 days without repo activity.
