# build_participants_cards.py
# Собирает participants_cards.json для вкладки "Карты участников"
# Требуется: requests, beautifulsoup4
# Запуск: python build_participants_cards.py

from pathlib import Path
import re
import unicodedata
import requests
from bs4 import BeautifulSoup
import json
import time
import random
from typing import Optional, Dict, List, Any

# ---------- Константы ----------
BASE_DIR = Path(__file__).parent
OUT_FILE = BASE_DIR / "participants_cards.json"
LOG_PATH = BASE_DIR / "log.txt"

BASE_URL = "https://remanga.org"
MEDIA_BASE = "https://remanga.org"
API_URL = "https://api.remanga.org"

GUILD1_URL = "https://remanga.org/guild/eternal-watchers-5fdc5a3d/about"
GUILD2_URL = "https://remanga.org/guild/eternal-keepers-of-knowledge-06969ad9/about"

# Только для EW и ED (как в твоём предыдущем решении)
guild1_manual_pairs = [
    ("CalistoTzy",114000),("МилыйКохай",109320),("Casepona",157780),("Zurichka",36000),("Яштуг",119860),
    ("Belashik",104070),("Werty-Servyt",95790),("MARKUTTs",44500),("AkiraGame",47500),("EW_NoBoN",53000),
    ("healot",16500),("_festashka_",56250),("rezord_aye",20070),("Chitandael",29380),("Okiarya",40400),
    ("Tavik",48770),("Satisfied",38170),("MeeQ_Q",39750),("Thostriel",37810),("Overcooling",35500),
    ("ADMIRAL_SENGOKU",28000),("Arbogastr",31500),("KodokunaYurei",54990),("HARLEQU1N",21790),("Andre_Falkonen",32890),
    ("Bagas",22360),("Йорм",13160),("EW_Taya_",36440),("Clf",24190),("Кайден",37610),("𝕹𝖎𝖐𝖎𝖙𝖆⁹",44630),
    ("Loly2810",14650),("Xmmxmm",10000),("гдемойстояк",10000),("Frostik4",25700),("desport",24730),
    ("Merrihew",27430),("Misikira",16300),("CreamWhite",21000),("тот_кто_смотрит....",17540),("Payk_",25000),
    ("ミュージシャン",105000),("Р03А",23260),("Dark_AngeI",10080),("Bloodborrn",13540),("vladosrat",44060),
    ("MonaLize",27900),("Abigor.",13920),("Госька",26040),("PupsTv",11200),("Gree.in",10010),
    ("Капитан-зануда",12000),("TeᴍƤeຮt",10000),("Feel_what_life_is",26710),("mangalev",11760),("Chiru-san",10050),
    ("Efiliyens",13310),("spidvrassrochku",10860),("Cкрытый_интриган",12750),("osmodeuss",10050),("Talent",7510),
    ("SalliKrash",32500),("__ASURA__",10090),("Jedı",16550),("Sunshi",7660),("FrozenJFX",22610),
    ("Я_лучший_в_мире",18080),("RayZe",11430),("К4йдэн",10220),("Harutsu",31280),("No_warries",14270),
    ("TeChal",10180),("Hellsait",9780),("ToKKeBi11",8940),("Чмошка-Мошка",10880),("NikesNt",10040),
    ("zarti",10080),("loli69228",26090),("Laytee",10030),("Старейшина-Чу",16550),("_Abyss_",12550),
    ("역사관",16480),("DarQee",1000),("Volcopik",82050),("Charisma",4000),("EW_МанкиДиГлупый",40000),
    ("WhitеFlower",31000),("Wladzer",10380),("Strayker5421",0),("URUS",-24760),("Pepegaronni",-24320),("Белохвостый",43630)
]

guild2_manual_pairs = [
    ("allentina",19500),("@𝑻𝑶𝑿𝑰𝑪",11880),
    ("Ronin74",36010),("Ham021",22000),("mmarti",8000),("FlammeNoire",21640),("Kaizaki",11394),
    ("Dergauss",10000),("Trololo_Mio",8410),("Beast_",37930),("DestructionGod𒉭",40000),("Zatex",10004),
    ("Trillo",7210),("RiverFreedom",9000),(".谢怜.",9000),("Akashi550",8000),("Kim_5+",7000),
    ("Cracker_7",8500),("-AGGRESSIV-",7750),("mei_mei",9103),("SilentHill",23100),("HaiSan",15700),
    ("WebRU",14290),("DmitryFlow",22000),("AllD-995",14000),("Hatin",9720),("Рил_сучк@.",9280),
    ("Издатель",11030),("GidiK",9700),("Woods_s",23100),("RWBYLOVE",10000),("kintownскиy",10000),
    ("Sw1ty",8000),("Ley-Ley",7100),("OblakaT_T",9000),("BanShei",7000),("Читатель+друг",8000),
    ("Jdhdbx",11110),("Vaenkh",8500),("moonsh1ne",8050),("Sas47",11010),("Takahikoo",8000),("Aki_Ram",6000),
    ("Mefisto51",26000),("S.a.m.u.r.a.i.",8000),("So1oMooN",7000),("etoRomantic",8000),("Амен",8000),
    ("Vallynor",9000),("Saytoriya",9000),("KOST9N",8000),("feazxch",8000),("Velial_Salivan",8000),
    ("Dr.Rи",8000),("tenofmoses",6000),("BigMen07",6000),("Hazenberg",6000),("--Lucifiel--",10500),
    ("Akihiko",7900),("TiltExist",10910),("stas211242",9130),("CKCKCK",8000),("ДолинаРекиСетунь",20570),
    ("over-time",9190),("Alafex",7000),("Luneheim",6000),("Fox94",10000),("SamuraFs",6000),("Sanctuary_",10000),
    ("Sunburst",9000),("Sckat_Man",4000),("LLIKoJIoma",6000),("Acediaqq",6000),("necromant",6020),
    ("Henati",6000),("oportew",5000),("Aleksan_09",6000),("alan-hui",7260)
]

# ---------- Утилиты ----------
def log(*args):
    ts = time.strftime("[%Y-%m-%d %H:%M:%S]")
    msg = " ".join(str(a) for a in args)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{ts} {msg}\n")
    except:
        print(ts, msg)

def super_normalize(name):
    if name is None:
        return ""
    s = unicodedata.normalize('NFKC', str(name)).strip().lower()
    s = re.sub(r'\s+', '', s)
    s = re.sub(r'[_\-.]', '', s)
    repl = {'ᴍ':'m','ᴛ':'t','ᴇ':'e','ᴘ':'p','ᴅ':'d','ᴄ':'c','ᴋ':'k',
            'а':'a','А':'a','с':'c','С':'c','е':'e','Е':'e','о':'o','О':'o',
            'р':'p','Р':'p','т':'t','Т':'t','у':'y','У':'y'}
    return ''.join(repl.get(c, c) for c in s)

def _abs_media(url: str) -> str:
    if not url:
        return ""
    if url.startswith("http"):
        return url
    if url.startswith("/"):
        return MEDIA_BASE + url
    if url.startswith("media/") or url.startswith("static/"):
        return f"{MEDIA_BASE}/{url}"
    return url

def _extract_user_id_from_href(href: str) -> Optional[int]:
    m = re.search(r"/user/(\d+)/about", href or "")
    return int(m.group(1)) if m else None

def first_str(*vals: Any) -> str:
    for v in vals:
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, dict):
            for k in ("name","title","label","value","ru","en","text"):
                x = v.get(k)
                if isinstance(x, str) and x.strip():
                    return x.strip()
    return ""

def first_cover(*vals: Any) -> str:
    stack: List[Any] = list(vals)
    seen = set()
    while stack:
        v = stack.pop(0)
        if id(v) in seen:
            continue
        seen.add(id(v))
        if isinstance(v, str) and v:
            u = v.strip()
            if u:
                return _abs_media(u)
        if isinstance(v, dict):
            for k in ("cover","image","img","url","path","cover_url","image_url","poster","poster_url"):
                if k in v:
                    vv = v[k]
                    if isinstance(vv, str) and vv.strip():
                        return _abs_media(vv.strip())
                    if isinstance(vv, dict):
                        stack.append(vv)
            for k in ("item","media","images","data","attributes"):
                if k in v and isinstance(v[k], (dict,list)):
                    stack.append(v[k])
        if isinstance(v, list):
            stack.extend(v)
    return ""

def fetch_og_image(page_url: str) -> str:
    try:
        r = requests.get(page_url, timeout=20)
        if r.status_code != 200:
            return ""
        soup = BeautifulSoup(r.text, "html.parser")
        m = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name":"og:image"})
        if m and m.get("content"):
            return _abs_media(m["content"].strip())
        img = soup.find("img", src=re.compile(r"(media/|/media/)"))
        if img and img.get("src"):
            return _abs_media(img.get("src"))
    except Exception as e:
        log("[fetch_og_image] fail", page_url, e)
    return ""

# ---------- HTTP сессия ----------
_session_api: Optional[requests.Session] = None
def make_session() -> requests.Session:
    global _session_api
    if _session_api:
        return _session_api
    s = requests.Session()
    s.headers.update({
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/126.0.0.0 Safari/537.36"),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": MEDIA_BASE,
    })
    _session_api = s
    return s

def _sleep_jitter(base: float = 0.55, spread: float = 0.45):
    time.sleep(base + random.random() * spread)

# ---------- Парс гильдий (только для author_id и видимого ника) ----------
def fetch_guild_ids(guild_url: str, allowed_norms: set, guild_label: str):
    log(f"[fetch_guild_ids] Start: {guild_label} -> {guild_url}")
    display_by_norm: Dict[str, str] = {}
    author_ids: Dict[str, int] = {}
    try:
        resp = requests.get(guild_url, timeout=20)
        log(f"[fetch_guild_ids] HTTP status: {resp.status_code}")
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        cards = soup.find_all("a", href=re.compile(r"^/user/\d+/about"))
        log(f"[fetch_guild_ids] Found cards: {len(cards)}")
        for card in cards:
            nick_tag = card.find("span", class_=re.compile(r"font-semibold"))
            if not nick_tag:
                continue
            site_nick = nick_tag.text.strip()
            norm = super_normalize(site_nick)
            if norm not in allowed_norms:
                continue
            href = card.get("href") or ""
            uid = _extract_user_id_from_href(href)
            if uid is not None:
                author_ids[norm] = uid
                display_by_norm[norm] = site_nick
    except Exception as e:
        log("[fetch_guild_ids] ERROR:", e)
    return display_by_norm, author_ids

# ---------- Загрузка карт автора через API ----------
def fetch_author_cards_api(author_id: int, ordering: str = "-rank", count: int = 30, max_pages: int = 100):
    s = make_session()
    results: List[Dict[str, Any]] = []
    page = 1
    max_retries = 3

    while page <= max_pages:
        url = f"{API_URL}/api/inventory/catalog/?author={author_id}&count={count}&ordering={ordering}&page={page}"
        headers = {"Referer": f"{MEDIA_BASE}/card?author={author_id}&ordering={ordering}"}
        data = None
        last_status = None

        for attempt in range(1, max_retries + 1):
            try:
                resp = s.get(url, headers=headers, timeout=20)
                last_status = resp.status_code
                if resp.status_code in (403, 429):
                    wait = 2.0 * attempt + random.random() * 1.5
                    log(f"[author-cards-api] {author_id} page {page}: HTTP {resp.status_code}, retry in {wait:.1f}s")
                    time.sleep(wait)
                    continue
                if resp.status_code != 200:
                    log(f"[author-cards-api] {author_id} page {page}: HTTP {resp.status_code}, stop")
                    break
                data = resp.json()
                break
            except Exception as e:
                log(f"[author-cards-api] {author_id} page {page}: error {e}, attempt {attempt}/{max_retries}")
                time.sleep(1.2 * attempt)

        if data is None:
            if results and last_status in (403, 429):
                log(f"[author-cards-api] {author_id} page {page}: {last_status}, keep partial ({len(results)})")
                break
            break

        items = None
        if isinstance(data, dict):
            items = data.get("results") or data.get("items") or data.get("data") or data.get("results_list")
        if items is None and isinstance(data, list):
            items = data

        if not items:
            log(f"[author-cards-api] {author_id} page {page}: empty, stop")
            break

        for it in items:
            title = first_str(it.get("title"), it.get("name"), it.get("label"),
                              (it.get("item") or {}).get("title"),
                              (it.get("item") or {}).get("name"))
            rarity = first_str(it.get("rarity"), it.get("rarity_name"),
                               (it.get("item") or {}).get("rarity"))
            cover_url = first_cover(
                it.get("cover"), it.get("image"), it.get("img"), it.get("cover_url"),
                (it.get("media") or {}).get("cover"),
                (it.get("item") or {}).get("cover"),
                (it.get("images") or {}).get("cover"),
                (it.get("attributes") or {}).get("cover"),
                it
            )
            card_id = it.get("id") or it.get("card_id") or it.get("pk")
            card_url = f"{MEDIA_BASE}/card/{card_id}" if card_id else "#"
            if not cover_url and card_id:
                cover_url = fetch_og_image(card_url)

            results.append({
                "id": card_id,
                "title": title or f"Card {card_id or ''}".strip(),
                "cover": cover_url,
                "rarity": rarity or "",
                "url": card_url
            })

        _sleep_jitter()
        next_url = data.get("next") if isinstance(data, dict) else None
        if next_url:
            page += 1
            continue
        page += 1

    log(f"[author-cards-api] {author_id}: collected {len(results)} cards")
    return results

# ---------- Main ----------
def main():
    log("=== BUILD PARTICIPANTS_CARDS START ===")
    allowed_g1 = {super_normalize(d) for d,_ in guild1_manual_pairs}
    allowed_g2 = {super_normalize(d) for d,_ in guild2_manual_pairs}

    g1_display, g1_ids = fetch_guild_ids(GUILD1_URL, allowed_g1, "Eternal Watchers")
    g2_display, g2_ids = fetch_guild_ids(GUILD2_URL, allowed_g2, "Eternal Demonic")

    participants_cards: Dict[str, Dict] = {}

    # EW
    for norm, author_id in g1_ids.items():
        display = g1_display.get(norm, norm)
        log(f"[build] EW -> {display} ({author_id})")
        cards = fetch_author_cards_api(author_id, ordering="-rank", count=30, max_pages=100)
        participants_cards[norm] = {"display": display, "author_id": author_id, "cards": cards}

    # ED
    for norm, author_id in g2_ids.items():
        display = g2_display.get(norm, norm)
        log(f"[build] ED -> {display} ({author_id})")
        cards = fetch_author_cards_api(author_id, ordering="-rank", count=30, max_pages=100)
        if norm in participants_cards and not participants_cards[norm]["cards"]:
            # если вдруг попали одинаковые ники в обеих гильдиях (маловероятно)
            participants_cards[norm]["cards"] = cards
            participants_cards[norm]["display"] = display
            participants_cards[norm]["author_id"] = author_id
        else:
            participants_cards[norm] = {"display": display, "author_id": author_id, "cards": cards}

    OUT_FILE.write_text(json.dumps(participants_cards, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"-> saved {OUT_FILE.name} ({len(participants_cards)} участников)")
    log("=== BUILD PARTICIPANTS_CARDS FINISH ===")

if __name__ == "__main__":
    main()
