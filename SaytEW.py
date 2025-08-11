# SaytEW.py
# Требуется: requests, beautifulsoup4, pillow
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
from PIL import Image
from io import BytesIO
import base64
import shutil  # для поиска git.exe

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
AVATAR_PLACEHOLDER = "avatars/placeholder.jpg"
AVATARS_DIR = Path("avatars")
AVATARS_DIR.mkdir(exist_ok=True)

# Папка для карт призов
CARDS_DIR = Path("cards")
CARDS_DIR.mkdir(exist_ok=True)

# ID карт для вкладки "Призы" — порядок = приоритет; первые 3 попадут в топ-3
prizes_ids = [5917, 319, 318, 9596, 7478, 9597, 8253, 50363, 8252, 5916, 13758]

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

# ----------------- ФУНКЦИИ -----------------
def super_normalize(name):
    if name is None:
        return ""
    s = unicodedata.normalize('NFKC', str(name)).strip().lower()
    s = re.sub(r'\s+', '', s)
    s = re.sub(r'[_\-.]', '', s)
    replacements = {'ᴍ':'m','ᴛ':'t','ᴇ':'e','ᴘ':'p','ᴅ':'d','ᴄ':'c','ᴋ':'k',
        'а':'a','А':'a','с':'c','С':'c','е':'e','Е':'e','о':'o','О':'o',
        'р':'p','Р':'p','т':'t','Т':'t','у':'y','У':'y'}
    return ''.join(replacements.get(c, c) for c in s)

def ensure_placeholder():
    """Создаём локальный плейсхолдер без интернета."""
    ph = Path(AVATAR_PLACEHOLDER)
    if ph.exists():
        return
    try:
        ph.parent.mkdir(parents=True, exist_ok=True)
        png_b64 = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQAB"
            "DQottAAAAABJRU5ErkJggg=="
        )
        ph.write_bytes(base64.b64decode(png_b64))
        log("-> placeholder avatar created (local)")
    except Exception as e:
        log("-> placeholder create failed:", e)

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

def fetch_guild(guild_url, allowed_norms, guild_label):
    log(f"[fetch_guild] Start: {guild_label} -> {guild_url}")
    parsed, avatars, profiles = {}, {}, {}
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
            img = card.find("img")
            avatar_path = Path(AVATAR_PLACEHOLDER)
            if img:
                avatar_url = img.get("src") or img.get("data-src") or img.get("data-original")
                if avatar_url:
                    avatar_path = AVATARS_DIR / f"{norm}.jpg"
                    if not avatar_path.exists():
                        try:
                            r = requests.get(avatar_url, timeout=20)
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
    return parsed, avatars, profiles

def build_participants(manual_pairs, parsed_map, avatars_map, profiles_map, guild_label):
    out = []
    for display, init_val in manual_pairs:
        norm = super_normalize(display)
        current_v = parsed_map.get(norm, {}).get("lightning", init_val)
        display_label = parsed_map.get(norm, {}).get("site_nick", display)
        diff = max(current_v - init_val, 0)
        out.append({
            "norm": norm, "display": display_label, "initial": init_val, "current": current_v, "diff": diff,
            "avatar": avatars_map.get(norm, Path(AVATAR_PLACEHOLDER).as_posix()),
            "profile": profiles_map.get(norm, BASE_URL), "guild": guild_label
        })
    out.sort(key=lambda x: x["diff"], reverse=True)
    return out

def fmt(n): return f"{n:,}".replace(",", " ")

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
def resize_image_15(img_bytes):
    try:
        img = Image.open(BytesIO(img_bytes))
        w, h = img.size
        new_size = (max(1, int(w * 0.85)), max(1, int(h * 0.85)))
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        img = img.resize(new_size, Image.LANCZOS)
        out = BytesIO()
        img.save(out, format="WEBP", quality=85)
        return out.getvalue()
    except Exception as e:
        log("resize_image_15 error:", e)
        return img_bytes

def fetch_prizes():
    """Парсинг карт: берём alt для названия, мангу и автора ищем в ближайшем wrapper блоке."""
    log(f"[fetch_prizes] start, ids={prizes_ids}")
    prizes = []
    for card_id in prizes_ids:
        url = f"{BASE_URL}/card/{card_id}"
        try:
            resp = requests.get(url, timeout=20)
            if resp.status_code != 200:
                log(f"[fetch_prizes] {card_id} -> HTTP {resp.status_code}")
                continue
            soup = BeautifulSoup(resp.text, "html.parser")

            card_img_wrap = soup.select_one(".cs-card-item")
            if not card_img_wrap:
                log(f"[fetch_prizes] {card_id} -> .cs-card-item not found")
                continue

            wrapper = None
            for parent in card_img_wrap.parents:
                if parent.name == "div" and parent.get("class") and any("bg-secondary" in c for c in parent.get("class")):
                    wrapper = parent
                    break
            if wrapper is None:
                wrapper = card_img_wrap.parent

            img_tag = card_img_wrap.select_one("img")
            if not img_tag:
                log(f"[fetch_prizes] {card_id} -> img not found")
                continue
            img_url = img_tag.get("src") or img_tag.get("data-src") or img_tag.get("data-original")
            if not img_url:
                log(f"[fetch_prizes] {card_id} -> img src empty")
                continue
            card_title = (img_tag.get("alt") or "").strip() or f"Card {card_id}"

            manga_tag = wrapper.select_one('a[href^="/manga/"]')
            manga_title = manga_tag.get_text(strip=True) if manga_tag else "—"
            manga_url = BASE_URL + manga_tag["href"] if manga_tag and manga_tag.get("href") else "#"

            author_tag = wrapper.select_one('a[href^="/user/"]')
            author_text = author_tag.get_text(strip=True) if author_tag else "—"
            author_name = re.sub(r'^\s*Автор:\s*', '', author_text, flags=re.I) if author_text else "—"
            author_url = BASE_URL + author_tag["href"] if author_tag and author_tag.get("href") else "#"

            img_name = f"{card_id}.webp"
            img_path = CARDS_DIR / img_name
            if not img_path.exists():
                try:
                    img_bytes = requests.get(img_url, timeout=20).content
                    resized = resize_image_15(img_bytes)
                    img_path.write_bytes(resized)
                except Exception as e:
                    log(f"[fetch_prizes] {card_id} image save error: {e}")
                    continue

            prizes.append({
                "id": card_id, "title": card_title,
                "manga": manga_title, "manga_url": manga_url,
                "author": author_name, "author_url": author_url,
                "image": img_path.as_posix()
            })
            log(f"[fetch_prizes] {card_id} parsed")
        except Exception as e:
            log(f"[fetch_prizes] ERROR {card_id}: {e}")
    log(f"[fetch_prizes] finished, parsed {len(prizes)}")
    return prizes

def render_prize_cards_top3(parts):
    html = ""
    top3 = parts[:3]
    for i, p in enumerate(top3, start=1):
        html += f"""
        <div class="prize-card prize-card--top">
            <div class="prize-num">№{i}</div>
            <div class="prize-img"><img src="{p['image']}" alt="{p['title']}"></div>
            <p class="prize-title">{p['title']}</p>
            <a class="prize-manga" href="{p['manga_url']}" target="_blank">{p['manga']}</a>
            <p class="prize-author">Автор: <a href="{p['author_url']}" target="_blank">{p['author']}</a></p>
        </div>
        """
    return html

def render_prize_cards_rest(parts):
    html = ""
    for p in parts[3:]:
        html += f"""
        <div class="prize-card prize-card--rest">
            <div class="prize-img"><img src="{p['image']}" alt="{p['title']}"></div>
            <p class="prize-title">{p['title']}</p>
            <a class="prize-manga" href="{p['manga_url']}" target="_blank">{p['manga']}</a>
            <p class="prize-author">Автор: <a href="{p['author_url']}" target="_blank">{p['author']}</a></p>
        </div>
        """
    return html

# ----------------- MAIN -----------------
log("=== SCRIPT START ===")
ensure_placeholder()

g1_parsed, g1_avatars, g1_profiles = fetch_guild(GUILD1_URL, {super_normalize(d) for d,_ in guild1_manual_pairs}, "Eternal Watchers")
g2_parsed, g2_avatars, g2_profiles = fetch_guild(GUILD2_URL, {super_normalize(d) for d,_ in guild2_manual_pairs}, "Eternal Demonic")
g3_parsed, g3_avatars, g3_profiles = fetch_guild(GUILD3_URL, {super_normalize(d) for d,_ in guild3_manual_pairs}, "ШИЗА")

participants_g1 = build_participants(guild1_manual_pairs, g1_parsed, g1_avatars, g1_profiles, "Eternal Watchers")
participants_g2 = build_participants(guild2_manual_pairs, g2_parsed, g2_avatars, g2_profiles, "Eternal Demonic")
participants_g3 = build_participants(guild3_manual_pairs, g3_parsed, g3_avatars, g3_profiles, "ШИЗА")

top10 = sorted(participants_g1 + participants_g2, key=lambda x: x["diff"], reverse=True)[:10]

cards_g1 = render_cards(participants_g1)
cards_g2 = render_cards(participants_g2)
cards_g3 = render_cards(participants_g3)
cards_t10 = render_cards(top10)

# призы
prizes_list = fetch_prizes()
cards_prizes_top = render_prize_cards_top3(prizes_list)
cards_prizes_rest = render_prize_cards_rest(prizes_list)

now_msk = datetime.now(timezone(timedelta(hours=3))).strftime("%d.%m.%Y %H:%M (МСК)")

# ----------------- HTML -----------------
html_template = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Eternal guilds — статистика</title>
<style>
:root{--bg:#0f1114;--card:#141618;--muted:#9aa4ad;--accent:#4aa3ff;--accent2:#82b5f7;--gold:#ffd24d;--text:#e6eef6}
body{margin:0;background:var(--bg);color:var(--text);font-family:sans-serif}
header{text-align:center;padding:10px}
.tabs{display:flex;gap:6px;justify-content:center;margin-bottom:12px;flex-wrap:wrap}
.tab-btn{padding:8px 12px;border:1px solid #333;border-radius:6px;cursor:pointer;background:#222;color:#fff}
.tab-btn.active{background:#444}
.panel{display:none}
.panel.active{display:block}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px}
.card{background:var(--card);border-radius:10px;padding:14px;display:flex;gap:14px}
.avatar{width:96px;height:96px;border-radius:50%;background-size:cover;background-position:center}
.place{font-weight:800;color:var(--gold);width:40px;text-align:center}
.info{flex:1}
.nickname a{color:var(--accent);text-decoration:none;font-weight:700}
.row{display:flex;gap:12px;flex-wrap:wrap;margin-top:8px}
.stat{background:rgba(255,255,255,0.05);padding:6px;border-radius:8px;min-width:100px}
.bigval{color:var(--gold)}

/* Призы */
.prizes-title{margin:12px 0 6px 6px;color:var(--muted);font-weight:700;letter-spacing:.3px}

/* Топ-3: крупнее и с подсветкой */
.grid-prizes-top{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;justify-items:center}
.prize-card{background:var(--card);border-radius:12px;padding:12px;text-align:center;position:relative;transition:transform .15s ease}
.prize-card:hover{transform:translateY(-2px)}
.prize-card--top{width:280px;box-shadow:0 6px 22px rgba(0,0,0,.35), 0 0 0 1px rgba(255,210,77,.15)}
.prize-num{position:absolute;top:8px;left:8px;background:linear-gradient(180deg, rgba(255,210,77,.95), rgba(255,180,0,.95));color:#181a1d;font-weight:900;padding:6px 10px;border-radius:8px}

/* Остальные: компактнее и с серой обводкой */
.grid-prizes-rest{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;justify-items:center}
.prize-card--rest{width:210px;border:1px solid #2b2f33}

/* Общие элементы карточек */
.prize-img img{width:100%;border-radius:6%;object-fit:cover}
.prize-title{font-size:1.06em;font-weight:800;margin-top:8px;color:var(--text)}
.prize-manga{display:inline-block;margin-top:4px;color:var(--accent);text-decoration:none;font-weight:600}
.prize-manga:hover{text-decoration:underline}
.prize-author{font-size:.92em;color:var(--muted);margin-top:2px}
.prize-author a{color:var(--accent);text-decoration:none}
.prize-author a:hover{text-decoration:underline}
</style>
</head>
<body>
<header>
<h1>Eternal guilds — статистика</h1>
<div>Последнее обновление: __NOW__</div>
</header>
<div class="tabs">
<button class="tab-btn active" data-target="tab1">Eternal Watchers</button>
<button class="tab-btn" data-target="tab2">Eternal Demonic</button>
<button class="tab-btn" data-target="tab3">ШИЗА</button>
<button class="tab-btn" data-target="tab4">Общий TOP-10</button>
<button class="tab-btn" data-target="tab5">Призы</button>
</div>
<section id="tab1" class="panel active"><div class="grid">__CARDS_G1__</div></section>
<section id="tab2" class="panel"><div class="grid">__CARDS_G2__</div></section>
<section id="tab3" class="panel"><div class="grid">__CARDS_G3__</div></section>
<section id="tab4" class="panel"><div class="grid">__CARDS_T10__</div></section>
<section id="tab5" class="panel">
  <div class="prizes-title">Топ-3</div>
  <div class="grid-prizes-top">__CARDS_PRIZES_TOP__</div>
  <div class="prizes-title">Карта фонда</div>
  <div class="grid-prizes-rest">__CARDS_PRIZES_REST__</div>
</section>
<script>
document.querySelectorAll('.tab-btn').forEach(btn=>{
 btn.onclick=()=>{
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(btn.dataset.target).classList.add('active');
 }
});
</script>
</body>
</html>
"""

html = html_template.replace("__NOW__", now_msk)\
    .replace("__CARDS_G1__", cards_g1)\
    .replace("__CARDS_G2__", cards_g2)\
    .replace("__CARDS_G3__", cards_g3)\
    .replace("__CARDS_T10__", cards_t10)\
    .replace("__CARDS_PRIZES_TOP__", cards_prizes_top)\
    .replace("__CARDS_PRIZES_REST__", cards_prizes_rest)

Path("index.html").write_text(html, encoding="utf-8")
log("-> index.html saved")

# ---------- SAVE JSON ----------
with open("top10.json", "w", encoding="utf-8") as f:
    json.dump(top10, f, ensure_ascii=False, indent=2)
with open("history_ew.json", "w", encoding="utf-8") as f:
    json.dump(participants_g1, f, ensure_ascii=False, indent=2)
with open("history_ed.json", "w", encoding="utf-8") as f:
    json.dump(participants_g2, f, ensure_ascii=False, indent=2)
log("-> top10.json, history_ew.json & history_ed.json saved")

# ---------- GIT PUSH (надёжный для двойного клика) ----------
def try_git_push():
    """Надёжный автопуш: cwd=папка скрипта, проверка .git, поиск git.exe, лог stdout/stderr, коммит только при изменениях."""
    try:
        script_dir = Path(__file__).resolve().parent
        os.chdir(script_dir)

        if not (script_dir / ".git").exists():
            log("[GIT] skipped: .git не найден (запуск не из репозитория)")
            return

        git_path = shutil.which("git")
        if not git_path:
            log("[GIT] skipped: git не найден в PATH")
            return

        def run(cmd):
            p = subprocess.run([git_path] + cmd, capture_output=True, text=True)
            if p.stdout:
                log(f"[GIT] {' '.join(cmd)} | stdout:", p.stdout.strip())
            if p.stderr:
                log(f"[GIT] {' '.join(cmd)} | stderr:", p.stderr.strip())
            return p.returncode

        noj = script_dir / ".nojekyll"
        if not noj.exists():
            noj.write_text("", encoding="utf-8")
            log("[GIT] created .nojekyll")

        run(["add", "index.html", "avatars", "cards", "top10.json", "history_ew.json", "history_ed.json", ".nojekyll"])

        rc = subprocess.run([git_path, "diff", "--cached", "--quiet"]).returncode
        if rc == 0:
            log("[GIT] нет изменений — коммит/пуш пропущены")
            return

        msg = f"Auto update: {datetime.now()}"
        run(["commit", "-m", msg])
        run(["push", "origin", "main"])
        log("[GIT] push done")
    except Exception as e:
        log("[GIT] ERROR:", e)

try_git_push()
log("=== SCRIPT FINISHED ===")
