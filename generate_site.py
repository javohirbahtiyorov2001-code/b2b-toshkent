#!/usr/bin/env python3
"""
Premium site generator — loremflickr keyword photos, unique per lead (lock=id).
Usage:
  python3 generate_site.py                         # first 10 Dentistry leads
  python3 generate_site.py --all                   # ALL real leads
  python3 generate_site.py --niche Restaurant      # specific niche
  python3 generate_site.py --limit 20              # custom limit
"""
import json, sys, os, re, hashlib

NICHE_KEYWORDS = {
    "Dentistry":      "dental,dentist,teeth,smile,clinic",
    "Clinic":         "medical,hospital,healthcare,doctor",
    "Pharmacy":       "pharmacy,medicine,drugstore,health",
    "Restaurant":     "restaurant,food,dining,gourmet",
    "Cafe":           "coffee,cafe,espresso,interior",
    "Bakery":         "bakery,bread,pastry,cake",
    "Hotel":          "hotel,lobby,luxury,resort",
    "Fitness":        "gym,fitness,workout,sport",
    "Beauty":         "beauty,salon,spa,cosmetics",
    "Education":      "education,school,classroom,university",
    "Construction":   "construction,architecture,building",
    "Real Estate":    "apartment,interior,architecture,modern",
    "Auto Sales":     "car,automobile,showroom",
    "Auto Service":   "garage,mechanic,workshop,repair",
    "IT Services":    "technology,office,computer,startup",
    "Logistics":      "warehouse,logistics,truck,cargo",
    "Retail":         "store,shopping,products,retail",
    "Furniture":      "furniture,interior,design,home",
    "Flowers":        "flowers,floral,bouquet,roses",
    "Travel":         "travel,tourism,landscape,adventure",
    "Accounting":     "office,business,finance,desk",
    "Electrical":     "electrical,engineering,panel,technician",
    "Cleaning":       "cleaning,hygiene,service,office",
    "Landscaping":    "garden,plants,landscape,outdoor",
    "Photography":    "photography,camera,studio,portrait",
    "Event Hall":     "event,banquet,wedding,celebration",
    "Kindergarten":   "children,kids,colorful,classroom",
    "HVAC":           "air+conditioning,cooling,technician",
}

FAKE_SOURCES = {"auto-generated", "none", ""}

def is_real(lead):
    return (lead.get("source") or "") not in FAKE_SOURCES

def photo_url(keywords, width, height, lock):
    return f"https://loremflickr.com/{width}/{height}/{keywords}?lock={lock}"

def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = h[0]*2 + h[1]*2 + h[2]*2
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_str(h, a=1):
    r, g, b = hex_to_rgb(h)
    return f"rgba({r},{g},{b},{a})"

def luminance(h):
    try:
        r, g, b = [x/255 for x in hex_to_rgb(h)]
        return 0.2126*r + 0.7152*g + 0.0722*b
    except:
        return 0.1

SERVICES = {
    "Dentistry": [
        ("🦷", "Tish oqlash", "1 seansta professional oqlash"),
        ("🔬", "Implantatsiya", "Umrbod kafolat bilan implantlar"),
        ("😁", "Estetik tish", "Vinir va zirkoniy tojlar"),
        ("🪥", "Breket sistemasi", "Zamonaviy keramik breketlar"),
        ("💉", "Og'riqsiz davolash", "Zamonaviy anesteziya"),
        ("📋", "Bepul konsultatsiya", "Mutaxassis bilan ko'rik"),
    ],
    "Clinic": [
        ("🩺", "Umumiy ko'rik", "Tajribali shifokorlar"),
        ("🔬", "Laboratoriya", "Tez va aniq tahlillar"),
        ("🩻", "Diagnostika", "MRT, UZI, rentgen"),
        ("💊", "Davolash", "Zamonaviy usullar"),
        ("🏥", "Statsionar", "24/7 yordam"),
        ("📋", "Bepul maslahat", "Shifokorlar maslahati"),
    ],
    "Restaurant": [
        ("🍽️", "O'zbek taomlari", "An'anaviy retseptlar"),
        ("🍖", "Grill va kabob", "Yog'och ustida pishirilgan"),
        ("🥗", "Salat bar", "Yangi va sog'lom"),
        ("🎂", "Konfet va shirinlik", "O'zimiz tayyorlaymiz"),
        ("🚚", "Yetkazib berish", "Tez va issiq"),
        ("🎉", "Bayram ziyofati", "Korporativ va to'y"),
    ],
    "Fitness": [
        ("💪", "Shaxsiy murabbiy", "Individual dastur"),
        ("🏋️", "Trenajyor zali", "Zamonaviy jihozlar"),
        ("🧘", "Yoga va meditatsiya", "Ruh va tana uyg'unligi"),
        ("🥊", "Boks va kurash", "Professional treninglar"),
        ("🏃", "Kardio zona", "Yugurish va velosiped"),
        ("🍎", "Ovqatlanish tavsiyalari", "Dietolog bilan"),
    ],
}

TAGLINES = {
    "Dentistry": "Chiroyli tabassum — yangi boshlang'ich",
    "Clinic":    "Sog'ligingiz — bizning ustuvorligimiz",
    "Restaurant":"Har bir taom — zavq va san'at",
    "Fitness":   "Kuchli tana — kuchli ruh",
    "Beauty":    "Chiroyli his — yangi siz",
    "Hotel":     "Komfort va dam olish — bir joyda",
    "Education": "Bilim — kelajakka eng yaxshi investitsiya",
}

def get_services(niche):
    return SERVICES.get(niche, [
        ("⭐", "Premium xizmat", "Yuqori sifatli yondashuv"),
        ("🏆", "Tajriba", "Sohadagi yetakchilar"),
        ("🤝", "Kafolat", "100% natija kafolati"),
        ("⚡", "Tezlik", "Vaqtingizni hurmat qilamiz"),
        ("💎", "VIP munosabat", "Har bir mijoz maxsus"),
        ("📞", "24/7 qo'llab-quvvatlash", "Har doim yoningizda"),
    ])

def generate_html(lead):
    lid      = lead.get("id", 1)
    name     = lead.get("name", "Kompaniya")
    niche    = lead.get("niche", "Clinic")
    phone    = lead.get("phone", "")
    address  = lead.get("address", "Toshkent")
    slug     = lead.get("slug") or re.sub(r"[^a-z0-9]+", "-", name.lower())
    primary  = lead.get("colors", {}).get("primary", "#0a1628")
    accent   = lead.get("colors", {}).get("accent", "#00b4d8")

    kw       = NICHE_KEYWORDS.get(niche, niche.lower().replace(" ", ","))
    tagline  = TAGLINES.get(niche, f"{niche} xizmatlari — professional yondashuv")
    services = get_services(niche)
    phone_clean = re.sub(r"\D", "", phone)

    # Photo URLs — each uses lock=lid for consistent unique images
    hero_photo  = photo_url(kw, 1200, 800, lid)
    mid_photo   = photo_url(kw, 1200, 600, lid + 100)
    team_photo  = photo_url(kw, 600, 400, lid + 200)

    lum = luminance(primary)
    dark_bg = lum < 0.2
    text_on_primary = "#ffffff" if dark_bg else "#0a0a0a"
    accent_lum = luminance(accent)
    text_on_accent = "#0a0a0a" if accent_lum > 0.4 else "#ffffff"

    pr = rgb_str(primary, 0.88)
    pr_mid = rgb_str(primary, 0.55)

    words = name.split()
    logo_first = words[0]
    logo_rest = " ".join(words[1:]) if len(words) > 1 else ""

    svc_html = "".join(
        f'<div class="card"><div class="card-icon">{icon}</div>'
        f'<h3>{title}</h3><p>{desc}</p></div>'
        for icon, title, desc in services
    )

    return f"""<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} — {niche} | Toshkent</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --p:{primary};--a:{accent};--at:{text_on_accent};
  --dark:#0c0c0e;--mid:#1c1c20;--light:#f4f4f6;
  --txt:#1a1a1e;--mute:#6b7280;
  --ease:cubic-bezier(.16,1,.3,1);
}}
html{{scroll-behavior:smooth;-webkit-font-smoothing:antialiased}}
body{{font-family:'Inter',sans-serif;background:#fff;color:var(--txt);overflow-x:hidden}}

/* NAV */
nav{{
  position:fixed;inset:0 0 auto;z-index:100;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 clamp(1.5rem,5vw,3.5rem);height:64px;
  background:rgba(255,255,255,.92);backdrop-filter:blur(24px);
  border-bottom:1px solid rgba(0,0,0,.07);
}}
.logo{{
  font-family:'Syne',sans-serif;font-weight:800;font-size:1.05rem;
  color:var(--dark);letter-spacing:-.02em;
  display:flex;align-items:center;gap:.2rem;
}}
.logo em{{color:var(--a);font-style:normal}}
.nav-right{{display:flex;align-items:center;gap:1rem}}
.nav-addr{{font-size:.75rem;color:var(--mute);max-width:200px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.nav-cta{{
  font-family:'Syne',sans-serif;font-size:.8rem;font-weight:700;
  background:var(--a);color:var(--at);
  padding:.5rem 1.2rem;border-radius:6px;text-decoration:none;
  transition:filter .18s,transform .15s;white-space:nowrap;
}}
.nav-cta:hover{{filter:brightness(1.1);transform:translateY(-1px)}}

/* HERO — full-bleed photo + left-anchored text */
.hero{{
  min-height:100dvh;padding-top:64px;
  display:grid;grid-template-columns:1fr 1fr;
  overflow:hidden;
}}
.hero-text{{
  display:flex;flex-direction:column;justify-content:center;
  padding:4rem clamp(1.5rem,5vw,3.5rem);
  background:var(--dark);position:relative;
  overflow:hidden;
}}
.hero-text::before{{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,var(--p) 0%,var(--dark) 100%);
  opacity:.7;
}}
.hero-content{{position:relative;z-index:1}}
.badge{{
  display:inline-flex;align-items:center;gap:.5rem;
  background:rgba(255,255,255,.08);
  border:1px solid rgba(255,255,255,.15);
  color:var(--a);font-size:.7rem;font-weight:600;
  letter-spacing:.12em;text-transform:uppercase;
  padding:.4rem 1rem;border-radius:100px;margin-bottom:2rem;
}}
h1{{
  font-family:'Syne',sans-serif;
  font-size:clamp(2.4rem,4.5vw,4rem);
  font-weight:800;line-height:1.05;
  letter-spacing:-.04em;color:#fff;
  margin-bottom:1.2rem;
}}
h1 .line2{{color:var(--a)}}
.hero-sub{{
  font-size:1rem;color:rgba(255,255,255,.62);
  line-height:1.7;margin-bottom:2.5rem;max-width:38ch;
}}
.hero-actions{{display:flex;gap:.75rem;flex-wrap:wrap;margin-bottom:3rem}}
.btn-fill{{
  font-family:'Syne',sans-serif;font-size:.9rem;font-weight:700;
  background:var(--a);color:var(--at);
  padding:.85rem 1.8rem;border-radius:8px;text-decoration:none;
  transition:filter .18s,transform .15s var(--ease);
  display:inline-flex;align-items:center;gap:.5rem;
}}
.btn-fill:hover{{filter:brightness(1.12);transform:translateY(-2px)}}
.btn-line{{
  font-family:'Syne',sans-serif;font-size:.9rem;font-weight:600;
  border:1.5px solid rgba(255,255,255,.25);color:rgba(255,255,255,.8);
  padding:.83rem 1.6rem;border-radius:8px;text-decoration:none;
  transition:border-color .2s,background .2s;
}}
.btn-line:hover{{border-color:rgba(255,255,255,.5);background:rgba(255,255,255,.07)}}
.kpi-row{{
  display:flex;gap:2rem;padding-top:2.5rem;
  border-top:1px solid rgba(255,255,255,.1);
}}
.kpi .n{{
  font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;
  color:#fff;line-height:1;
}}
.kpi .l{{font-size:.7rem;color:rgba(255,255,255,.45);margin-top:.3rem;letter-spacing:.05em}}

/* HERO PHOTO SIDE */
.hero-photo{{position:relative;overflow:hidden;background:var(--dark)}}
.hero-photo img{{
  width:100%;height:100%;object-fit:cover;
  display:block;
  filter:saturate(1.1) contrast(1.05);
  transition:transform 6s ease;
}}
.hero-photo:hover img{{transform:scale(1.04)}}
.photo-badge{{
  position:absolute;bottom:2rem;left:2rem;
  background:rgba(255,255,255,.95);backdrop-filter:blur(12px);
  border-radius:12px;padding:1rem 1.4rem;
  display:flex;align-items:center;gap:.8rem;
  box-shadow:0 8px 32px rgba(0,0,0,.18);
}}
.pb-dot{{width:10px;height:10px;border-radius:50%;background:var(--a);flex-shrink:0;
  box-shadow:0 0 0 3px {rgb_str(accent, 0.25)};
  animation:pulse 2s infinite;}}
@keyframes pulse{{0%,100%{{box-shadow:0 0 0 3px {rgb_str(accent, 0.25)}}}
  50%{{box-shadow:0 0 0 6px {rgb_str(accent, 0.1)}}}}}
.pb-text .t{{font-family:'Syne',sans-serif;font-size:.82rem;font-weight:700;color:var(--dark)}}
.pb-text .s{{font-size:.7rem;color:var(--mute);margin-top:.1rem}}

/* SERVICES */
.services{{padding:6rem clamp(1.5rem,5vw,3.5rem);background:#fff}}
.section-wrap{{max-width:1200px;margin:0 auto}}
.eyebrow{{
  font-family:'Syne',sans-serif;font-size:.68rem;font-weight:700;
  letter-spacing:.18em;text-transform:uppercase;color:var(--a);
  margin-bottom:.8rem;display:flex;align-items:center;gap:.6rem;
}}
.eyebrow::before{{content:'';width:24px;height:2px;background:var(--a);flex-shrink:0}}
.section-title{{
  font-family:'Syne',sans-serif;
  font-size:clamp(1.7rem,3vw,2.5rem);
  font-weight:800;letter-spacing:-.04em;
  color:var(--dark);line-height:1.1;
  margin-bottom:3rem;max-width:22ch;
}}
.grid-3{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.25rem}}
.card{{
  padding:2rem 1.75rem;border-radius:14px;
  border:1px solid #e5e7eb;
  transition:transform .3s var(--ease),border-color .2s,box-shadow .3s;
  cursor:default;
}}
.card:hover{{
  transform:translateY(-6px);
  border-color:var(--a);
  box-shadow:0 16px 40px rgba(0,0,0,.09),0 0 0 1px {rgb_str(accent, 0.12)};
}}
.card-icon{{font-size:1.8rem;margin-bottom:1rem;display:block}}
.card h3{{font-family:'Syne',sans-serif;font-weight:700;font-size:.95rem;color:var(--dark);margin-bottom:.4rem}}
.card p{{font-size:.83rem;color:var(--mute);line-height:1.6}}

/* PHOTO FEATURE STRIP */
.strip{{
  display:grid;grid-template-columns:1fr 1fr;
  min-height:480px;overflow:hidden;
}}
.strip-img{{position:relative;overflow:hidden;background:var(--dark)}}
.strip-img img{{width:100%;height:100%;object-fit:cover;display:block;
  filter:saturate(1.05);
}}
.strip-img::after{{
  content:'';position:absolute;inset:0;
  background:linear-gradient(to right,{pr} 0%,transparent 100%);
  pointer-events:none;
}}
.strip-text{{
  background:var(--dark);display:flex;flex-direction:column;
  justify-content:center;padding:4rem 3.5rem;
  position:relative;
}}
.strip-text::before{{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,var(--p),var(--dark));opacity:.6;
}}
.strip-inner{{position:relative;z-index:1}}
.strip-text h2{{
  font-family:'Syne',sans-serif;font-size:clamp(1.6rem,2.8vw,2.2rem);
  font-weight:800;color:#fff;letter-spacing:-.04em;
  line-height:1.15;margin-bottom:1rem;
}}
.strip-text p{{color:rgba(255,255,255,.65);line-height:1.75;margin-bottom:2rem;font-size:.95rem}}
.strip-text a{{
  font-family:'Syne',sans-serif;font-weight:700;font-size:.9rem;
  background:var(--a);color:var(--at);
  padding:.85rem 1.8rem;border-radius:8px;text-decoration:none;
  display:inline-block;width:fit-content;
  transition:filter .18s,transform .15s;
}}
.strip-text a:hover{{filter:brightness(1.1);transform:translateY(-2px)}}

/* REVIEWS */
.reviews{{background:var(--light);padding:6rem clamp(1.5rem,5vw,3.5rem)}}
.reviews-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.25rem;margin-top:3rem}}
.rc{{background:#fff;border-radius:14px;padding:2rem;box-shadow:0 2px 16px rgba(0,0,0,.05)}}
.stars{{font-size:.9rem;color:#f59e0b;letter-spacing:.1em;margin-bottom:.75rem}}
.rc-text{{font-size:.88rem;color:#4b5563;line-height:1.75;margin-bottom:1.25rem;font-style:italic}}
.rc-author{{display:flex;align-items:center;gap:.75rem}}
.av{{
  width:38px;height:38px;border-radius:50%;flex-shrink:0;
  background:linear-gradient(135deg,var(--p),var(--a));
  display:flex;align-items:center;justify-content:center;
  font-family:'Syne',sans-serif;font-size:.72rem;font-weight:700;color:#fff;
}}
.av-name{{font-family:'Syne',sans-serif;font-size:.85rem;font-weight:700;color:var(--dark)}}
.av-role{{font-size:.72rem;color:var(--mute)}}

/* FINAL CTA */
.final-cta{{
  background:var(--dark);padding:6rem clamp(1.5rem,5vw,3.5rem);
  text-align:center;position:relative;overflow:hidden;
}}
.final-cta::before{{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,var(--p),transparent);opacity:.5;
}}
.cta-inner{{position:relative;z-index:1;max-width:560px;margin:0 auto}}
.final-cta h2{{
  font-family:'Syne',sans-serif;font-size:clamp(1.8rem,4vw,2.8rem);
  font-weight:800;color:#fff;letter-spacing:-.04em;
  line-height:1.1;margin-bottom:1rem;
}}
.final-cta p{{color:rgba(255,255,255,.6);line-height:1.75;margin-bottom:2.5rem}}
.cta-btns{{display:flex;gap:.75rem;justify-content:center;flex-wrap:wrap}}

/* FOOTER */
footer{{
  background:#0c0c0e;color:rgba(255,255,255,.4);
  padding:2.5rem clamp(1.5rem,5vw,3.5rem);
}}
.footer-inner{{
  max-width:1200px;margin:0 auto;
  display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:1.5rem;
}}
.f-logo{{font-family:'Syne',sans-serif;font-weight:800;color:#fff;font-size:1rem}}
.f-logo em{{color:var(--a);font-style:normal}}
.f-links{{display:flex;gap:1.5rem;list-style:none}}
.f-links a{{color:rgba(255,255,255,.4);text-decoration:none;font-size:.8rem;transition:color .2s}}
.f-links a:hover{{color:#fff}}
.f-copy{{font-size:.75rem}}

@media(max-width:768px){{
  .hero{{grid-template-columns:1fr}}
  .hero-photo{{height:280px}}
  .strip{{grid-template-columns:1fr}}
  .strip-img{{height:240px;order:2}}
  .strip-img::after{{background:linear-gradient(to bottom,{pr} 0%,transparent 100%)}}
  .nav-addr{{display:none}}
}}
</style>
</head>
<body>

<nav>
  <div class="logo">{logo_first}<em>{"·" if not logo_rest else logo_rest}</em></div>
  <div class="nav-right">
    <span class="nav-addr">{address}</span>
    <a href="tel:{phone_clean}" class="nav-cta">📞 {phone}</a>
  </div>
</nav>

<section class="hero">
  <div class="hero-text">
    <div class="hero-content">
      <div class="badge">
        <span style="width:6px;height:6px;border-radius:50%;background:var(--a);display:block;animation:pulse 2s infinite"></span>
        {niche} · Toshkent
      </div>
      <h1>{name}<br><span class="line2">{tagline.split("—")[0].strip()}</span></h1>
      <p class="hero-sub">{tagline} — biz bilan professional darajada.</p>
      <div class="hero-actions">
        <a href="tel:{phone_clean}" class="btn-fill">📞 Qo'ng'iroq</a>
        <a href="#services" class="btn-line">Xizmatlar →</a>
      </div>
      <div class="kpi-row">
        <div class="kpi"><div class="n">10+</div><div class="l">Yillik tajriba</div></div>
        <div class="kpi"><div class="n">5K+</div><div class="l">Mijozlar</div></div>
        <div class="kpi"><div class="n">100%</div><div class="l">Kafolat</div></div>
      </div>
    </div>
  </div>
  <div class="hero-photo">
    <img src="{hero_photo}" alt="{name}" loading="eager">
    <div class="photo-badge">
      <div class="pb-dot"></div>
      <div class="pb-text">
        <div class="t">{name}</div>
        <div class="s">{address}</div>
      </div>
    </div>
  </div>
</section>

<section class="services" id="services">
  <div class="section-wrap">
    <div class="eyebrow">Xizmatlar</div>
    <h2 class="section-title">Biz taklif qiladigan<br>imkoniyatlar</h2>
    <div class="grid-3">{svc_html}</div>
  </div>
</section>

<div class="strip">
  <div class="strip-img">
    <img src="{mid_photo}" alt="{niche}" loading="lazy">
  </div>
  <div class="strip-text">
    <div class="strip-inner">
      <div class="eyebrow" style="margin-bottom:.6rem">Nima uchun biz?</div>
      <h2>Toshkentdagi eng ishonchli {niche.lower()} markazi</h2>
      <p>Zamonaviy uskunalar, malakali mutaxassislar va qulay narxlar — barchasi {name} da.</p>
      <a href="tel:{phone_clean}">Hozir bog'laning →</a>
    </div>
  </div>
</div>

<section class="reviews">
  <div class="section-wrap">
    <div class="eyebrow">Mijozlar fikri</div>
    <h2 class="section-title">Ular biz haqimizda</h2>
    <div class="reviews-grid">
      <div class="rc">
        <div class="stars">★★★★★</div>
        <p class="rc-text">"Professional xizmat va iliq munosabat. Natijadan juda mamnunman, barcha do'stlarimga tavsiya qilaman."</p>
        <div class="rc-author"><div class="av">SA</div>
        <div><div class="av-name">Sardor A.</div><div class="av-role">Doimiy mijoz · 3 yil</div></div></div>
      </div>
      <div class="rc">
        <div class="stars">★★★★★</div>
        <p class="rc-text">"Toshkentda shu sohaning eng yaxshi mutaxassislari shu yerda. Narxlar adolatli, sifat yuqori darajada."</p>
        <div class="rc-author"><div class="av">DM</div>
        <div><div class="av-name">Dilnoza M.</div><div class="av-role">Yangi mijoz · 2024</div></div></div>
      </div>
      <div class="rc">
        <div class="stars">★★★★★</div>
        <p class="rc-text">"Dastlab xavotirlandim, lekin jamoa juda yoqimli va professional. Yana kelamiz, rahmat!"</p>
        <div class="rc-author"><div class="av">FK</div>
        <div><div class="av-name">Feruza K.</div><div class="av-role">Mijoz · 2023</div></div></div>
      </div>
    </div>
  </div>
</section>

<section class="final-cta">
  <div class="cta-inner">
    <h2>Bugun biz bilan bog'laning</h2>
    <p>Bepul konsultatsiya va maxsus taklif uchun hoziroq qo'ng'iroq qiling.</p>
    <div class="cta-btns">
      <a href="tel:{phone_clean}" class="btn-fill">📞 {phone}</a>
      <a href="https://t.me/{phone_clean}" target="_blank" class="btn-line" style="color:#fff">✈️ Telegram</a>
    </div>
    <p style="margin-top:1.5rem;font-size:.78rem;color:rgba(255,255,255,.35)">{address}</p>
  </div>
</section>

<footer>
  <div class="footer-inner">
    <div class="f-logo">{logo_first}<em>{"·" if not logo_rest else logo_rest}</em></div>
    <ul class="f-links">
      <li><a href="#services">Xizmatlar</a></li>
      <li><a href="tel:{phone_clean}">{phone}</a></li>
    </ul>
    <p class="f-copy">© 2025 {name}. Barcha huquqlar himoyalangan.</p>
  </div>
</footer>

</body>
</html>"""

def load_leads():
    files = [
        "/Users/macbookpro/Applications/b2b-automation/pipeline/dental_clinic_leads.json",
        "/Users/macbookpro/Applications/b2b-automation/pipeline/new_leads_100.json",
        "/Users/macbookpro/Applications/b2b-automation/pipeline/seed_leads.json",
    ]
    all_leads = []
    for f in files:
        if os.path.exists(f):
            with open(f) as fp:
                all_leads.extend(json.load(fp))
    return all_leads

def main():
    args = sys.argv[1:]
    all_leads = load_leads()
    real = [l for l in all_leads if is_real(l)]

    if "--all" in args:
        targets = real
    else:
        niche_filter = args[args.index("--niche")+1] if "--niche" in args else None
        limit = int(args[args.index("--limit")+1]) if "--limit" in args else 10

        if niche_filter:
            targets = [l for l in real if niche_filter.lower() in (l.get("niche","")).lower()][:limit]
        else:
            targets = [l for l in real if "dent" in (l.get("niche","")+" "+l.get("name","")).lower()][:limit]

    out = "/Users/macbookpro/Applications/b2b-automation/generated_sites"
    os.makedirs(out, exist_ok=True)

    for lead in targets:
        slug = lead.get("slug") or re.sub(r"[^a-z0-9]+", "-", lead.get("name","lead").lower())
        path = os.path.join(out, f"{slug}.html")
        with open(path, "w") as f:
            f.write(generate_html(lead))
        print(f"✓  {lead.get('name')} → {slug}.html")

    print(f"\n{len(targets)} sites generated.")

if __name__ == "__main__":
    main()
