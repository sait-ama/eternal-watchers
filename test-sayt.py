# SaytEW.py
# Требуется: requests, beautifulsoup4
# Рекомендуемый запуск без консоли: pythonw.exe SaytEW.py
# Логи: log.txt (append)

from pathlib import Path
import re
import unicodedata
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
import subprocess
import os
import json
import time
import random
from typing import Optional, Dict, List, Any, Tuple

# ----------------- ЛОГ -----------------
LOG_PATH = Path(__file__).parent / "log.txt"

def log(*args):
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    msg = " ".join(str(a) for a in args)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{ts} {msg}\n")
    except:
        try:
            print(ts, msg)
        except:
            pass

# ----------------- НАСТРОЙКИ -----------------
GUILD1_URL = 'https://remanga.org/guild/eternal-watchers-5fdc5a3d/about'
GUILD2_URL = 'https://remanga.org/guild/eternal-keepers-of-knowledge-06969ad9/about'
GUILD3_URL = 'https://remanga.org/guild/bed-s-bashkoi-kohaja-6a891c56/about'  # ШИЗА

BASE_URL = 'https://remanga.org'
MEDIA_BASE = 'https://remanga.org'
API_URL = 'https://api.remanga.org'

AVATAR_PLACEHOLDER = "avatars/placeholder.jpg"
AVATARS_DIR = Path("avatars")
AVATARS_DIR.mkdir(exist_ok=True)

# ----------------- MANUAL СПИСКИ -----------------
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
    ("WhitеFlower",31000),("Wladzer",10380)
]

guild2_manual_pairs = [
    ("URUS",8000),("Pepegaronni",10638),("allentina",19500),("@𝑻𝑶𝑿𝑰𝑪",11880),
    ("Ronin74",36010),("Ham021",22000),("mmarti",8000),("FlammeNoire",21640),("Kaizaki",11394),
    ("Dergauss",10000),("Trololo_Mio",8410),("Beast_",37930),("DestructionGod𒉭",40000),("Zatex",10004),
    ("Trillo",7210),("RiverFreedom",9000),(".谢怜.",9000),("Akashi550",8000),("Kim_5+",7000),
    ("Cracker_7",8500),("-AGGRESSIV-",7750),("mei_mei",9103),("SilentHill",23100),("HaiSan",15700),
    ("WebRU",14290),("DmitryFlow",22000),("AllD-995",14000),("Hatin",9720),("Рил_сучк@.",9280),
    ("Издатель",11030),("GidiK",9700),("Woods_s",23100),("RWBYLOVE",10000),("kintownskiy",10000),
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

guild3_manual_pairs = [
    ("sKILLer",201250),("МилыйКохай",190740),("UnlimitedCringeWorks",115000),("nothingCosta",111110),("Efiliyens",102000),
    ("Strayker5421",81910),("Gaynese",70540),("Globus136",60460),("Misikira",57440),("Leda",54940),
    ("Attri",50000),("DarQee",29570),("Sa_Yuri",24230),("Ле-Ст",22950),("Сайтама",19580),
    ("Агриэль",13000),("ПочуствовалБоль",12500),("Zeev",11660),("01bag",9500),("TogasoN",8890),
    ("Yuval-T",8100),("keysshi",8000),("Фиолкотёнок",7400),("Mistake900",6760),("Lionia",6490),
    ("Luksis",5000),("Никиторо",5000),("0000-0000",4420),("B@rmaley",4240),("Arbogastr",4010),
    ("Чтец_из_чая",4000),("Devasstone",3500),("Хронус777",3310),("He1emont",3000),("Гер-3",3000),
    ("DEAD927",3000),("_Fire_Knight_",2500),("RaZvRatNuk",2240),("Satisfied",2030),("SleepingForest22118",2000),
    ("Pepeopello",2000),("TeᴍƤeຮt",1500),("El_Duck",1500),("любовь-читателя",1460),("blackart",1460),
    ("Ярослав-Круть",1350),("Gagsner",1140),("Мысль",1100),("Yak0she4ka",1060),("MangaTOP",1000),
    ("Emerald_Грид_",400),("BILL-02",69),("Scаrlеtt",69),("y3sty",35),("tlsI23",0),
    ("lov_dddd",0),("SuuNaDeSsu",0),("小市民",0)
]

# ----------------- ВСПОМОГАТЕЛЬНОЕ -----------------
def super_normalize(name):
    if name is None:
        return ""
    s = unicodedata.normalize('NFKC', str(name)).strip().lower()
    s = re.sub(r'\s+', '', s)
    s = re.sub(r'[_\-.]', '', s)
    replacements = {
        'ᴍ': 'm', 'ᴛ': 't', 'ᴇ': 'e', 'ᴘ': 'p', 'ᴅ': 'd', 'ᴄ': 'c', 'ᴋ': 'k',
        'а': 'a', 'А': 'a', 'с': 'c', 'С': 'c', 'е': 'e', 'Е': 'e', 'о': 'o', 'О': 'o',
        'р': 'p', 'Р': 'p', 'т': 't', 'Т': 't', 'у': 'y', 'У': 'y'
    }
    return ''.join(replacements.get(c, c) for c in s)

def ensure_placeholder():
    ph = Path(AVATAR_PLACEHOLDER)
    if not ph.exists():
        try:
            ph.parent.mkdir(parents=True, exist_ok=True)
            ph.write_bytes(requests.get("https://via.placeholder.com/96").content)
            log("-> placeholder avatar created")
        except Exception as e:
            log("-> placeholder download failed:", e)

def parse_lightning_text(raw_text):
    if not raw_text:
        return 0
    raw = raw_text.strip().replace(",", ".").upper()
    try:
        if "K" in raw:
            return int(float(raw.replace("K","")) * 1000)
        if "M" in raw:
            return int(float(raw.replace("M","")) * 1_000_000)
        return int(float(raw))
    except Exception:
        digits = re.sub(r"[^\d]", "", raw)
        return int(digits) if digits else 0

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

# --- helpers для вытаскивания строк/картинок из разнородного JSON ---
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
        # запасной путь: первый <img> с media/card-item
        img = soup.find("img", src=re.compile(r"(media/|/media/)"))
        if img and img.get("src"):
            return _abs_media(img["src"])
    except Exception as e:
        log("[fetch_og_image] fail", page_url, e)
    return ""

# ----------------- СЕССИЯ ДЛЯ API -----------------
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

# ----------------- СБОР ГИЛЬДИЙ -----------------
def fetch_guild(guild_url, allowed_norms, guild_label):
    log(f"[fetch_guild] Start: {guild_label} -> {guild_url}")
    parsed: Dict[str, Dict] = {}
    avatars: Dict[str, str] = {}
    profiles: Dict[str, str] = {}
    author_ids: Dict[str, int] = {}
    try:
        resp = requests.get(guild_url, timeout=20)
        log(f"[fetch_guild] HTTP status: {resp.status_code}")
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        cards = soup.find_all("a", href=re.compile(r"^/user/\d+/about"))
        log(f"[fetch_guild] Found cards: {len(cards)}")
        for card in cards:
            nick_tag = card.find("span", class_=re.compile(r"font-semibold"))
            if not nick_tag:
                continue
            site_nick = nick_tag.text.strip()
            norm = super_normalize(site_nick)
            if norm not in allowed_norms:
                continue
            href = card.get("href") or ""
            profiles[norm] = BASE_URL + href if href else BASE_URL
            uid = _extract_user_id_from_href(href)
            if uid is not None:
                author_ids[norm] = uid
            img = card.find("img")
            avatar_path = Path(AVATAR_PLACEHOLDER)
            if img:
                avatar_url = img.get("src") or img.get("data-src") or img.get("data-original")
                if avatar_url:
                    avatar_path = AVATARS_DIR / f"{norm}.jpg"
                    if not avatar_path.exists():
                        try:
                            r = requests.get(_abs_media(avatar_url), timeout=20)
                            avatar_path.write_bytes(r.content)
                        except:
                            avatar_path = Path(AVATAR_PLACEHOLDER)
            avatars[norm] = avatar_path.as_posix()
            lightning_div = card.find("div", attrs={"data-slot": "badge"})
            lightning = parse_lightning_text(lightning_div.text) if lightning_div else 0
            parsed[norm] = {"site_nick": site_nick, "lightning": lightning}
        log(f"[fetch_guild] Parsed count: {len(parsed)}")
    except Exception as e:
        log("[fetch_guild] ERROR:", e)
    return parsed, avatars, profiles, author_ids

def build_participants(manual_pairs, parsed_map, avatars_map, profiles_map, author_ids_map, guild_label):
    out = []
    for display, init_val in manual_pairs:
        norm = super_normalize(display)
        current_v = parsed_map.get(norm, {}).get("lightning", init_val)
        display_label = parsed_map.get(norm, {}).get("site_nick", display)
        diff = max(current_v - init_val, 0)
        out.append({
            "norm": norm,
            "display": display_label,
            "initial": init_val,
            "current": current_v,
            "diff": diff,
            "avatar": avatars_map.get(norm, Path(AVATAR_PLACEHOLDER).as_posix()),
            "profile": profiles_map.get(norm, BASE_URL),
            "author_id": author_ids_map.get(norm),
            "guild": guild_label
        })
    out.sort(key=lambda x: x["diff"], reverse=True)
    return out

def fmt(n):
    return f"{n:,}".replace(",", " ")

def render_cards(parts):
    html = ""
    for i, p in enumerate(parts, start=1):
        html += (
            "<div class='card'>"
            f"<div class='place'>#{i}</div>"
            f"<div class='avatar' style=\"background-image: url('{p['avatar']}');\"></div>"
            "<div class='info'>"
            f"<div class='nickname'><a href='{p['profile']}' target='_blank'>{p['display']}</a></div>"
            "<div class='row'>"
            f"<div class='stat'><span class='label'>Начальный вклад</span><span class='val'>{fmt(p['initial'])}</span></div>"
            f"<div class='stat'><span class='label'>Текущий вклад</span><span class='val'>{fmt(p['current'])}</span></div>"
            f"<div class='stat big'><span class='label'>Сумма залитых молний</span><span class='val bigval'>{fmt(p['diff'])}</span></div>"
            "</div></div></div>\n"
        )
    return html

# ----------------- ПРИЗЫ -----------------
def fetch_prizes(prize_ids: List[int]):
    log(f"[fetch_prizes] start, ids={prize_ids}")
    prizes = {}
    for pid in prize_ids:
        try:
            url = f"{MEDIA_BASE}/prize/{pid}"
            title = f"Приз #{pid}"
            img = ""
            # пробуем вытащить по og:image
            img = fetch_og_image(url)
            # если не нашли, пробуем /card-item/<id>
            if not img:
                alt_url = f"{MEDIA_BASE}/card-item/{pid}"
                img = fetch_og_image(alt_url)
                if img:
                    url = alt_url
            prizes[pid] = {"id": pid, "title": title, "img": img, "url": url}
            log(f"[fetch_prizes] {pid} parsed")
        except Exception as e:
            log(f"[fetch_prizes] {pid} error {e}")
    log(f"[fetch_prizes] finished, parsed {len(prizes)}")
    return prizes

# ----------------- КАРТОЧКИ ЧЕРЕЗ API -----------------
def fetch_author_cards_api(author_id: int, ordering: str = "-rank", count: int = 30, max_pages: int = 100):
    s = make_session()
    results: List[Dict[str, Any]] = []
    page = 1
    max_retries = 3

    while page <= max_pages:
        url = f"{API_URL}/api/inventory/catalog/?author={author_id}&count={count}&ordering={ordering}&page={page}"
        per_req_headers = {"Referer": f"{MEDIA_BASE}/card?author={author_id}&ordering={ordering}"}

        data = None
        last_status = None
        for attempt in range(1, max_retries + 1):
            try:
                resp = s.get(url, headers=per_req_headers, timeout=20)
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
            title = first_str(
                it.get("title"), it.get("name"), it.get("label"),
                (it.get("item") or {}).get("title"),
                (it.get("item") or {}).get("name"),
            )
            rarity = first_str(
                it.get("rarity"), it.get("rarity_name"),
                (it.get("item") or {}).get("rarity"),
            )
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

            # если обложка не нашлась — дергаем страницу карты и достаём og:image
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

# ----------------- MAIN -----------------
log("=== SCRIPT START ===")
ensure_placeholder()

# 1) гильдии
g1_parsed, g1_avatars, g1_profiles, g1_ids = fetch_guild(GUILD1_URL, {super_normalize(d) for d,_ in guild1_manual_pairs}, "Eternal Watchers")
g2_parsed, g2_avatars, g2_profiles, g2_ids = fetch_guild(GUILD2_URL, {super_normalize(d) for d,_ in guild2_manual_pairs}, "Eternal Demonic")
g3_parsed, g3_avatars, g3_profiles, g3_ids = fetch_guild(GUILD3_URL, {super_normalize(d) for d,_ in guild3_manual_pairs}, "ШИЗА")

participants_g1 = build_participants(guild1_manual_pairs, g1_parsed, g1_avatars, g1_profiles, g1_ids, "Eternal Watchers")
participants_g2 = build_participants(guild2_manual_pairs, g2_parsed, g2_avatars, g2_profiles, g2_ids, "Eternal Demonic")
participants_g3 = build_participants(guild3_manual_pairs, g3_parsed, g3_avatars, g3_profiles, g3_ids, "ШИЗА")

top10 = sorted(participants_g1 + participants_g2, key=lambda x: x["diff"], reverse=True)[:10]

# 2) призы (реальные обложки через og:image)
prize_ids = [5917, 319, 318, 9596, 7478, 9597, 8253, 50363, 8252, 5916, 13758]
prizes = fetch_prizes(prize_ids)

# 3) карточки (EW+ED)
participants_cards: Dict[str, Dict] = {}
for p in (participants_g1 + participants_g2):
    norm = p["norm"]
    display = p["display"]
    author_id = p.get("author_id")
    if not author_id:
        continue
    log(f"[author-cards-api] fetching for {display} ({author_id})")
    cards = fetch_author_cards_api(author_id, ordering="-rank", count=30, max_pages=100)
    participants_cards[norm] = {
        "display": display,
        "author_id": author_id,
        "cards": cards
    }

# 4) HTML — старый дизайн + вкладки
cards_g1 = render_cards(participants_g1)
cards_g2 = render_cards(participants_g2)
cards_g3 = render_cards(participants_g3)
cards_t10 = render_cards(top10)

now_msk = datetime.now(timezone(timedelta(hours=3))).strftime("%d.%m.%Y %H:%M (МСК)")

html_template = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Eternal guilds — статистика</title>
<style>
:root{--bg:#0f1114;--card:#141618;--muted:#9aa4ad;--accent:#4aa3ff;--accent2:#82b5f7;--gold:#ffd24d;--text:#e6eef6}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:sans-serif}
header{text-align:center;padding:10px}
.tabs{display:flex;gap:6px;justify-content:center;margin-bottom:12px;flex-wrap:wrap}
.tab-btn{padding:8px 12px;border:1px solid #333;border-radius:6px;cursor:pointer;background:#222;color:#fff}
.tab-btn.active{background:#444}
.panel{display:none}
.panel.active{display:block}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px;padding:0 10px 12px}
.card{background:var(--card);border-radius:10px;padding:14px;display:flex;gap:14px}
.avatar{width:96px;height:96px;border-radius:50%;background-size:cover;background-position:center}
.place{font-weight:800;color:var(--gold);width:40px;text-align:center}
.info{flex:1}
.nickname a{color:var(--accent);text-decoration:none;font-weight:700}
.row{display:flex;gap:12px;flex-wrap:wrap;margin-top:8px}
.stat{background:rgba(255,255,255,0.05);padding:6px;border-radius:8px;min-width:100px}
.bigval{color:var(--gold)}
/* Призы */
.prizegrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;padding:0 10px 12px}
.prize{background:#141618;border:1px solid #2a2e32;border-radius:10px;overflow:hidden}
.pcover{width:100%;aspect-ratio:2/3;background:#111;background-size:cover;background-position:center}
.pcnt{padding:8px 10px}
.ptitle{font-size:14px;margin:0 0 6px}
.ptitle a{color:#e6eef6;text-decoration:none}
/* Карты участников */
.toolbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:0 10px 12px}
.search{flex:1;min-width:220px}
.search input{width:100%;padding:10px 12px;border-radius:8px;border:1px solid #2e3338;background:#171a1d;color:var(--text)}
.select{min-width:220px}
.select select{width:100%;padding:10px 12px;border-radius:8px;border:1px solid #2e3338;background:#171a1d;color:var(--text)}
.cardgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;padding:0 10px 12px}
.ccard{background:#141618;border:1px solid #2a2e32;border-radius:10px;overflow:hidden}
.ccover{width:100%;aspect-ratio:2/3;background:#111;background-size:cover;background-position:center}
.ccnt{padding:8px 10px}
.ctitle{font-size:14px;line-height:1.25;margin:0 0 6px}
.ctitle a{color:#e6eef6;text-decoration:none}
.cmeta{font-size:12px;color:#a8b0b7}
.badge{display:none} /* ранги выключены */
.empty{opacity:.7;padding:12px}
.lastupd{opacity:.8;font-size:13px;margin-top:6px}
/* Активность */
.actgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px;padding:0 10px 12px}
.act{background:#141618;border:1px solid #2a2e32;border-radius:10px;padding:10px}
.act h4{margin:0 0 6px;font-size:15px}
.act .muted{font-size:12px;color:#9aa4ad}
</style>
</head>
<body>
<header>
  <h1>Eternal guilds — статистика</h1>
  <div class="lastupd">Последнее обновление: __NOW__</div>
</header>
<div class="tabs">
  <button class="tab-btn active" data-target="tab1">Eternal Watchers</button>
  <button class="tab-btn" data-target="tab2">Eternal Demonic</button>
  <button class="tab-btn" data-target="tab3">ШИЗА</button>
  <button class="tab-btn" data-target="tab4">Общий TOP-10</button>
  <button class="tab-btn" data-target="tab5">Призы</button>
  <button class="tab-btn" data-target="tab6">Карты участников</button>
  <button class="tab-btn" data-target="tab7">Активность</button>
</div>

<section id="tab1" class="panel active"><div class="grid">__CARDS_G1__</div></section>
<section id="tab2" class="panel"><div class="grid">__CARDS_G2__</div></section>
<section id="tab3" class="panel"><div class="grid">__CARDS_G3__</div></section>
<section id="tab4" class="panel"><div class="grid">__CARDS_T10__</div></section>

<section id="tab5" class="panel">
  <div class="prizegrid" id="prize-grid"></div>
</section>

<section id="tab6" class="panel">
  <div class="toolbar">
    <div class="search"><input id="pc-search" placeholder="Поиск ника..."></div>
    <div class="select">
      <select id="pc-select">
        <option value="">— выбрать участника —</option>
      </select>
    </div>
  </div>
  <div id="pc-result" class="cardgrid"></div>
</section>

<section id="tab7" class="panel">
  <div class="actgrid" id="act-grid"></div>
</section>

<script>
const PARTICIPANT_CARDS = __PARTICIPANTS_CARDS_JSON__;
const DISPLAY_BY_NORM = __DISPLAY_BY_NORM__;
const PRIZES = __PRIZES_JSON__;
const ORDER_LINK = (authorId) => `https://remanga.org/card?author=${authorId}&ordering=-rank`;

document.querySelectorAll('.tab-btn').forEach(btn=>{
  btn.onclick=()=>{
    document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
    document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.target).classList.add('active');
  }
});

// ===== Призы =====
(function renderPrizes(){
  const grid = document.getElementById('prize-grid');
  const list = Object.values(PRIZES);
  if(!list.length){ grid.innerHTML = '<div class="empty">Список призов пуст.</div>'; return; }
  for(const p of list){
    const cover = typeof p.img === 'string' && p.img ? p.img : '';
    const el = document.createElement('div');
    el.className = 'prize';
    el.innerHTML = `
      <a href="${p.url || '#'}" target="_blank" rel="noopener">
        <div class="pcover" style="${cover ? `background-image:url('${cover.replace(/'/g,"&#39;")}')` : ''}"></div>
      </a>
      <div class="pcnt">
        <div class="ptitle"><a href="${p.url || '#'}" target="_blank" rel="noopener">${escapeHtml(String(p.title||('Приз '+(p.id||''))))}</a></div>
      </div>
    `;
    grid.appendChild(el);
  }
})();

// ===== Карты участников =====

// селект участников
(function fillSelect(){
  const sel = document.getElementById('pc-select');
  const entries = Object.entries(PARTICIPANT_CARDS).map(([norm, data])=>[norm, data.display]);
  entries.sort((a,b)=>a[1].localeCompare(b[1], 'ru'));
  for(const [norm, disp] of entries){
    const opt = document.createElement('option');
    opt.value = norm;
    opt.textContent = disp;
    sel.appendChild(opt);
  }
})();

// поиск по нику
document.getElementById('pc-search').addEventListener('input', function(){
  const q = this.value.trim().toLowerCase();
  const sel = document.getElementById('pc-select');
  if(!q){
    sel.value = '';
    renderCards(null);
    return;
  }
  const entries = Object.entries(PARTICIPANT_CARDS).map(([norm, data])=>[norm, data.display]);
  const found = entries.find(([norm, disp])=> (disp||'').toLowerCase().includes(q));
  if(found){
    sel.value = found[0];
    sel.dispatchEvent(new Event('change'));
  }
});

document.getElementById('pc-select').addEventListener('change', function(){
  const norm = this.value || null;
  renderCards(norm);
});

function renderCards(norm){
  const wrap = document.getElementById('pc-result');
  wrap.innerHTML = '';
  if(!norm){
    wrap.innerHTML = '<div class="empty">Выберите участника слева, либо начните вводить ник в поиске.</div>';
    return;
  }
  const data = PARTICIPANT_CARDS[norm];
  if(!data || !Array.isArray(data.cards) || !data.cards.length){
    wrap.innerHTML = '<div class="empty">Для этого участника карточек не найдено.</div>';
    return;
  }

  const linkTop = document.createElement('div');
  linkTop.className = 'empty';
  linkTop.innerHTML = `<a href="${ORDER_LINK(data.author_id)}" target="_blank">Все карты автора на Remanga</a>`;
  wrap.appendChild(linkTop);

  for(const c of data.cards){
    const el = document.createElement('div');
    el.className = 'ccard';
    const cover = typeof c.cover === 'string' ? c.cover : '';
    const title = typeof c.title === 'string' ? c.title : '';
    const rarity = typeof c.rarity === 'string' ? c.rarity : '';
    el.innerHTML = `
      <a href="${c.url || '#'}" target="_blank" rel="noopener">
        <div class="ccover" style="${cover ? `background-image:url('${cover.replace(/'/g,"&#39;")}')` : ''}"></div>
      </a>
      <div class="ccnt">
        <div class="ctitle">
          <a href="${c.url || '#'}" target="_blank" rel="noopener">${escapeHtml(title || 'Без названия')}</a>
        </div>
        <div class="cmeta">
          ${rarity ? 'Редкость: '+escapeHtml(rarity) : ''}
          ${data.author_id ? ` • <a href="${ORDER_LINK(data.author_id)}" target="_blank" rel="noopener">Все карты автора</a>` : ''}
        </div>
      </div>
    `;
    wrap.appendChild(el);
  }
}

function escapeHtml(s){
  return String(s).replace(/[&<>"']/g, ch => (
    {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]
  ));
}

// ===== Активность =====
(function renderActivity(){
  const grid = document.getElementById('act-grid');
  const src = __ACTIVITY_JSON__;
  if(!src.length){ grid.innerHTML = '<div class="empty">Пока нет активности.</div>'; return; }
  for(const a of src){
    const el = document.createElement('div');
    el.className = 'act';
    el.innerHTML = `
      <h4><a href="${a.profile}" target="_blank">${escapeHtml(a.display)}</a></h4>
      <div class="muted">${escapeHtml(a.guild)} • Залито: ${a.diff.toLocaleString('ru-RU')} ⚡ • Карточек: ${a.cards}</div>
    `;
    grid.appendChild(el);
  }
})();

// стартовый рендер
renderCards(null);
</script>
</body>
</html>
"""

# Активность: участники EW+ED с diff>0
activity = []
for p in (participants_g1 + participants_g2):
    if p["diff"] > 0:
        cards_count = len((participants_cards.get(p["norm"]) or {}).get("cards") or [])
        activity.append({
            "display": p["display"],
            "profile": p["profile"],
            "guild": p["guild"],
            "diff": p["diff"],
            "cards": cards_count
        })
# самые активные сверху
activity.sort(key=lambda x: (x["diff"], x["cards"]), reverse=True)

display_by_norm = {k: v["display"] for k,v in participants_cards.items()}

html = (
    html_template
    .replace("__NOW__", now_msk)
    .replace("__CARDS_G1__", cards_g1)
    .replace("__CARDS_G2__", cards_g2)
    .replace("__CARDS_G3__", cards_g3)
    .replace("__CARDS_T10__", cards_t10)
    .replace("__PARTICIPANTS_CARDS_JSON__", json.dumps(participants_cards, ensure_ascii=False))
    .replace("__DISPLAY_BY_NORM__", json.dumps(display_by_norm, ensure_ascii=False))
    .replace("__PRIZES_JSON__", json.dumps(prizes, ensure_ascii=False))
    .replace("__ACTIVITY_JSON__", json.dumps(activity, ensure_ascii=False))
)

Path("index.html").write_text(html, encoding="utf-8")
log("-> index.html saved")

# ---------- SAVE JSON ----------
with open("top10.json", "w", encoding="utf-8") as f:
    json.dump(top10, f, ensure_ascii=False, indent=2)

with open("history_ew.json", "w", encoding="utf-8") as f:
    json.dump(participants_g1, f, ensure_ascii=False, indent=2)

with open("history_ed.json", "w", encoding="utf-8") as f:
    json.dump(participants_g2, f, ensure_ascii=False, indent=2)

with open("participants_cards.json", "w", encoding="utf-8") as f:
    json.dump(participants_cards, f, ensure_ascii=False, indent=2)

with open("activity.json", "w", encoding="utf-8") as f:
    json.dump(activity, f, ensure_ascii=False, indent=2)

log("-> top10.json, history_ew.json, history_ed.json, participants_cards.json, activity.json saved")

# ---------- GIT PUSH ----------
def try_git_push():
    log("[GIT] Pushing...")
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

    def run(cmd):
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, creationflags=creationflags)
        if "commit" in cmd:
            log(f"[GIT] {' '.join(cmd[:3])} | stdout: {r.stdout.strip()[:200]}")
        if "push" in cmd:
            log(f"[GIT] {' '.join(cmd[:3])} | stderr: {r.stderr.strip()[:200]}")
        return r

    run(["git", "add", "index.html", "avatars", "top10.json", "history_ew.json", "history_ed.json", "participants_cards.json", "activity.json"])
    run(["git", "commit", "-m", f"Auto update: {datetime.now()}"])
    run(["git", "push", "origin", "main"])

try_git_push()
log("=== SCRIPT FINISHED ===")
