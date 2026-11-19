#!/usr/bin/env python3
"""Rebuilds the GrimJow22 AniList bio from live AniList data.

Usage:
  python anilist_bio_updater.py            # dry run: prints the bio only
  python anilist_bio_updater.py --theme sololeveling --out bio_sl.md   # save a themed copy
  ANILIST_TOKEN=xxx python anilist_bio_updater.py --push   # updates your profile
(GitHub Actions runs this on a schedule, see .github/workflows/update-bio.yml)

Reading data needs no token. Pushing the bio needs an AniList access token.
Standard library only, no installs needed.
"""
import datetime
import json
import os
import random
import sys
import urllib.error
import urllib.request
from zoneinfo import ZoneInfo

USER = "GrimJow22"
API = "https://graphql.anilist.co"
# Where banner/poster files are served from. In GitHub Actions this is your own repo
# (set automatically); the fallback is only used for local runs.
ASSET_BASE = ("https://raw.githubusercontent.com/%s/main/" % os.environ["GITHUB_REPOSITORY"]
              if os.environ.get("GITHUB_REPOSITORY")
              else "https://raw.githubusercontent.com/RustyUjjwal/anilist-bio/main/")

# ---- static parts: edit these freely --------------------------------------
BANNER = "https://YOUR-BANNER-IMAGE-URL.jpg"   # leave "" to skip the banner
TAGLINE = "isekai addict &bull; action lover &bull; one more episode, I swear"
ABOUT = (
    "Hey, I'm **Jow**. I mostly live in fantasy, action and reincarnation "
    "stories, from Chinese donghua marathons to long-running manhwa."
)
FUN_FACT = ("Naruto's iconic headband was only created because the series creator, "
            "Masashi Kishimoto, got tired of drawing goggles on Naruto's face every single episode")
QUOTE = ("I don't know everything. I just know what I know. "
         "And right now, I know I have to keep moving forward.")
QUOTE_BY = "Sung Jinwoo (Solo Leveling)"
LINKS = [("Discord", "https://YOUR-LINK"), ("YouTube", "https://YOUR-LINK")]
TOP_N = 6          # favorites shown per list
WATCHING_N = 6     # currently watching/reading shown
COVER_W = 100      # cover image width in px (use 80 for a tighter row on mobile)
# AniCards cards (https://github.com/RLAlpha49/AniCards). Set CARD_ROWS = [] to turn off.
# Each inner list is one row; cards in a row sit side by side (they wrap on narrow screens).
# Each card is (cardType, variation, extra_url_params). Run the generator once first.
# The favourites grids show your AniList FAVOURITES, not your scores.
CARD_ROWS = [
    [("statusCompletionOverview", "split", "")],
    [("animeStats", "default", ""), ("mangaStats", "default", "")],
    [("favoritesGrid", "anime", "&gridCols=3&gridRows=3"),
     ("favoritesGrid", "manga", "&gridCols=3&gridRows=3")],
    [("currentlyWatchingReading", "anime", ""), ("currentlyWatchingReading", "manga", "")],
    [("animeGenreSynergy", "default", "")],
]
# False = the cards replace the repeating text (numbers, top picks, current lists, genres).
# True  = also write those text sections from live data.
TEXT_SECTIONS = False
CARD_USER_ID = 7824217          # your numeric AniList ID (more reliable than the username)
# ---- themes: blackclover, sololeveling, grimjow. Pick one with --theme NAME or the BIO_THEME env var ---------------
# Colours are hex with %23 in place of #. "preset" is an AniCards palette name; the
# colour overrides sit on top of it. Add your own theme by copying an entry.
THEMES = {
    "blackclover": {   # charcoal black, soft sage green, matches the banner art
        "symbol": "\u2618",
        "banner": "black-clover-banner.png",   # file in your repo root (or a full https URL)
        "tagline": None,   # None = use TAGLINE above
        "preset": "default",
        "colors": ("&titleColor=%239fb58f&backgroundColor=%230e100f&textColor=%23dfe4dc"
                   "&circleColor=%235d7a5a&borderColor=%233f4d40"),
    },
    "sololeveling": {  # near-black navy, muted steel blue, matches the banner art
        "symbol": "\u2694",
        "banner": "solo-levelling-banner.png",
        "tagline": "arise &bull; isekai addict &bull; action lover &bull; one more episode, I swear",
        "preset": "default",
        "colors": ("&titleColor=%239aa8d8&backgroundColor=%23070a10&textColor=%23d5d9e8"
                   "&circleColor=%233a4f8f&borderColor=%232f3858"),
    },
    "grimjow": {       # deep crimson and warm cream from the oni banner
        "symbol": "\u2694",
        "banner": "anilist-profile-banner-enlarged.png",
        "poster": "grimjow-wanted.jpg",   # wanted poster shown under About me
        "tagline": None,
        "preset": "default",
        "colors": ("&titleColor=%23e9b58f&backgroundColor=%23140a0a&textColor=%23efe0d4"
                   "&circleColor=%23a8332b&borderColor=%23552020"),
    },
}


def _arg(flag):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else None


# ---- rotation used by --theme auto (the workflow default) ----------------------
# Monday to Sunday: 2 days of each theme, then 1 random day. The random pick is
# seeded by the date, so every run on the same day gives the same theme.
SCHEDULE = ["blackclover", "blackclover", "sololeveling", "sololeveling",
            "grimjow", "grimjow", "random"]
BIO_TZ = "Asia/Kolkata"      # the day changes at midnight in this timezone


def pick_theme(today=None):
    today = today or datetime.datetime.now(ZoneInfo(BIO_TZ)).date()
    name = SCHEDULE[today.weekday()]
    if name == "random":
        name = random.Random(today.isoformat()).choice(list(THEMES))
    return name


THEME = _arg("--theme") or os.environ.get("BIO_THEME") or "auto"
if THEME == "auto":
    THEME = pick_theme()
if THEME not in THEMES:
    sys.exit(f"Unknown theme {THEME!r}. Choose from: auto, {', '.join(THEMES)}")
_T = THEMES[THEME]
CARD_PRESET = _T["preset"]
CARD_STYLE = _T["colors"] + "&borderRadius=8"   # extra look settings added to every card
CARD_W = 340       # px per card; two per row must fit your profile width (lower it if they stack)
# Per-card width overrides (px) by cardType; anything not listed uses CARD_W.
CARD_WIDTHS = {"animeGenreSynergy": 290}
POSTER_W = 260    # width of the wanted poster (grimjow theme)
FAV_N = 0          # own cover-image favourites section (0 = off, 6 = on). Use it if the AniCards grids fail
# ----------------------------------------------------------------------------


def gql(query, variables=None, token=None):
    # AniList sits behind Cloudflare, which rejects Python's default User-Agent with a 403,
    # so we send our own.
    headers = {"Content-Type": "application/json", "Accept": "application/json",
               "User-Agent": "anilist-bio-updater/1.0 (+https://github.com/RustyUjjwal/anilist-bio)"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300].replace("\n", " ")
        raise RuntimeError(f"AniList returned HTTP {e.code}: {body}") from None
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    return data["data"]


STATS_Q = """
query ($name: String) {
  User(name: $name) {
    statistics {
      anime { count episodesWatched
              statuses { status count }
              genres(limit: 5, sort: COUNT_DESC) { genre } }
      manga { count chaptersRead
              statuses { status count } }
    }
  }
}"""

LIST_Q = """
query ($name: String, $type: MediaType, $status: MediaListStatus, $chunk: Int) {
  MediaListCollection(userName: $name, type: $type, status: $status,
                      chunk: $chunk, perChunk: 500) {
    hasNextChunk
    lists { entries { score(format: POINT_100) updatedAt
                      media { id title { romaji } coverImage { large } } } }
  }
}"""

FAV_Q = """
query ($name: String) {
  User(name: $name) { favourites {
    anime(page: 1, perPage: 25) { nodes { id title { romaji } coverImage { large } } }
    manga(page: 1, perPage: 25) { nodes { id title { romaji } coverImage { large } } }
  } }
}"""

ABOUT_Q = "query ($name: String) { User(name: $name) { about(asHtml: false) } }"


def entries(media_type, status=None, sort="SCORE_DESC"):
    """All entries across every list and chunk, sorted globally (not per list)."""
    seen, out, chunk = set(), [], 1
    while True:
        d = gql(LIST_Q, {"name": USER, "type": media_type,
                         "status": status, "chunk": chunk})["MediaListCollection"]
        for lst in d["lists"]:
            for e in lst["entries"]:
                if e["media"]["id"] not in seen:
                    seen.add(e["media"]["id"])
                    out.append(e)
        if not d["hasNextChunk"]:
            break
        chunk += 1
    key = "score" if sort == "SCORE_DESC" else "updatedAt"
    return sorted(out, key=lambda e: e[key], reverse=True)


def favourites():
    """Your AniList favourites (in your own order), shaped like list entries."""
    f = gql(FAV_Q, {"name": USER})["User"]["favourites"]
    return ([{"media": n} for n in f["anime"]["nodes"]][:FAV_N],
            [{"media": n} for n in f["manga"]["nodes"]][:FAV_N])


def link(kind, e):
    title = e["media"]["title"]["romaji"].replace("[", "(").replace("]", ")")
    return f"[{title}](https://anilist.co/{kind}/{e['media']['id']})"


def covers(kind, items):
    """Row of clickable cover images (the spaces inside [ ] are required by AniList)."""
    parts = []
    for e in items:
        url = (e["media"].get("coverImage") or {}).get("large")
        parts.append(f"[ img{COVER_W}({url}) ](https://anilist.co/{kind}/{e['media']['id']})"
                     if url else link(kind, e))
    return "~~~\n" + " ".join(parts) + "\n~~~" if parts else "-"


def cards_block():
    base = "https://api.anicards.alpha49.com/card.svg"
    rows = [" ".join(
        f"img{CARD_WIDTHS.get(t, CARD_W)}({base}?userId={CARD_USER_ID}&cardType={t}&variation={v}"
        f"&colorPreset={CARD_PRESET}{CARD_STYLE}{x})" for t, v, x in row) for row in CARD_ROWS]
    return "~~~\n" + "\n".join(rows) + "\n~~~"


def status_count(stats, name):
    return next((s["count"] for s in stats["statuses"] if s["status"] == name), 0)


def encode_emoji(text):
    """AniList truncates posts at characters above U+FFFF, so entity-encode them."""
    return "".join(f"&#{ord(c)};" if ord(c) > 0xFFFF else c for c in text)


def _asset(path):
    """A bare file name means a file in your repo root; full URLs pass through."""
    return path if not path or path.startswith("http") else ASSET_BASE + path


def init_user():
    """Who the bio is for. Order: ANILIST_USER env, else the owner of ANILIST_TOKEN
    (so a fork needs no configuration), else the defaults at the top of this file."""
    global USER, CARD_USER_ID
    name, token = os.environ.get("ANILIST_USER"), os.environ.get("ANILIST_TOKEN")
    try:
        if name:
            USER = name
            CARD_USER_ID = int(os.environ.get("ANICARDS_USER_ID") or
                               gql("query ($n: String) { User(name: $n) { id } }",
                                   {"n": name})["User"]["id"])
        elif token:
            v = gql("query { Viewer { id name } }", token=token)["Viewer"]
            USER, CARD_USER_ID = v["name"], v["id"]
    except Exception as exc:
        if "--push" in sys.argv:   # never push someone else's data to this token's profile
            sys.exit(f"Could not look up your AniList user: {exc}")
        print("Could not look up the user, using defaults:", exc, file=sys.stderr)


def text_sections():
    """The sections the cards now replace. Only used when TEXT_SECTIONS = True."""
    st = gql(STATS_Q, {"name": USER})["User"]["statistics"]
    a, m = st["anime"], st["manga"]
    top_anime = [e for e in entries("ANIME") if e["score"] > 0][:TOP_N]
    top_manga = [e for e in entries("MANGA") if e["score"] > 0][:TOP_N]
    watching = entries("ANIME", "CURRENT", "UPDATED_TIME_DESC")[:WATCHING_N]
    reading = entries("MANGA", "CURRENT", "UPDATED_TIME_DESC")[:WATCHING_N]
    genres = " &bull; ".join(g["genre"] for g in a["genres"])
    L = ["## The numbers",
         f"- **Anime:** {a['count']} on my list, {status_count(a, 'COMPLETED')} completed, "
         f"{a['episodesWatched']} episodes watched",
         f"- **Manga/manhwa:** {m['count']} on my list, {status_count(m, 'CURRENT')} reading, "
         f"{m['chaptersRead']} chapters read",
         f"- **Plan to watch:** {status_count(a, 'PLANNING')}", "", "---", "",
         "## Top picks", "**Anime (highest rated)**"]
    L += [f"- {link('anime', e)}" for e in top_anime]
    L += ["", "**Manga / Manhwa (highest rated)**"]
    L += [f"- {link('manga', e)}" for e in top_manga] or ["- (rate some manga to fill this in)"]
    L += ["", "## Currently watching", covers("anime", watching)]
    L += ["", "## Currently reading", covers("manga", reading)]
    L += ["", "## Favorite genres", genres, "", "---", ""]
    return L


def build():
    L = []
    banner = _asset(_T.get("banner") or BANNER)
    if banner and "YOUR-" not in banner:
        L += [f"img800({banner})", ""]
    L += ["~~~", f"# {_T['symbol']} {USER} {_T['symbol']}", f"*{_T['tagline'] or TAGLINE}*", "~~~", "", "---", "",
          "## About me", ABOUT, ""]
    if _T.get("poster"):
        L += ["~~~", f"img{POSTER_W}({_asset(_T['poster'])})", "~~~", ""]
    L += ["---", ""]
    if CARD_ROWS:
        L += ["## Stats cards", cards_block(), "", "---", ""]
    if FAV_N:
        fav_anime, fav_manga = favourites()
        L += ["## Favourites", "**Anime**", covers("anime", fav_anime), "",
              "**Manga / Manhwa**", covers("manga", fav_manga), "", "---", ""]
    if TEXT_SECTIONS:
        L += text_sections()
    L += ["## Fun facts", f"~!{FUN_FACT}!~", "", f"> \"{QUOTE}\"", f"> \u2014 {QUOTE_BY}", ""]
    links = [f"- [{n}]({u})" for n, u in LINKS if "YOUR-" not in u]
    if links:
        L += ["## Find me"] + links
    L += ["", "Thanks for stopping by! Follows and recommendations are always welcome."]
    return encode_emoji("\n".join(L))


def push(bio):
    token = os.environ.get("ANILIST_TOKEN")
    if not token:
        sys.exit("Set ANILIST_TOKEN to push the bio.")
    current = gql(ABOUT_Q, {"name": USER})["User"]["about"] or ""
    if current.strip() == bio.strip():
        print("Bio unchanged, nothing to push.")
        return
    gql("mutation ($about: String) { SaveUser(about: $about) { id } }",
        {"about": bio}, token=token)
    print("Bio updated.")


if __name__ == "__main__":
    init_user()
    print("Theme:", THEME, "| user:", USER, file=sys.stderr)
    bio = build()
    out = _arg("--out")
    if out:
        open(out, "w", encoding="utf-8").write(bio.replace("&bull;", "\u2022") + "\n")
        print("Wrote", out)
    if "--push" in sys.argv:
        push(bio)
    elif not out:
        print(bio)
