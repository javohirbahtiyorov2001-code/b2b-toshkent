#!/usr/bin/env python3
"""Template-based unique website generator — no API key needed."""

import json, os, re
from pathlib import Path

ROOT = Path(__file__).parent.parent
OUTPUT_DIR = ROOT / "generated_sites"
OUTPUT_DIR.mkdir(exist_ok=True)

def slug(name):
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

def wa_link(phone, name):
    num = re.sub(r'[^0-9]', '', phone)
    return f"https://wa.me/{num}?text=Salom%2C%20{name.replace(' ','%20')}%20bilan%20bog%27lanmoqchiman"

# ── NICHE TEMPLATES ──────────────────────────────────────────────────────────

def make_restaurant(lead):
    n=lead['name']; p=lead['phone']; a=lead.get('address','Toshkent'); w=wa_link(p,n)
    svcs=lead.get('services',['Milliy taomlar','Kabob','Non-tandır','Choy'])
    svc_cards=''.join(f'<div class="dish"><span class="dish-icon">🍽️</span><h3>{s}</h3><p>Narxi: {15000+i*8000:,} so\'mdan</p></div>' for i,s in enumerate(svcs))
    return f"""<!DOCTYPE html><html lang="uz"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{n} — Toshkent Restorani</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display+SC:wght@700;900&family=Karla:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{{--primary:#2D0A00;--accent:#DC2626;--gold:#A16207;--cream:#FEF9F0}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Karla',sans-serif;background:var(--cream);color:#1a0800}}
nav{{position:fixed;top:0;width:100%;background:rgba(45,10,0,.95);backdrop-filter:blur(8px);z-index:999;display:flex;align-items:center;justify-content:space-between;padding:1rem 2rem}}
.logo{{font-family:'Playfair Display SC';color:#fff;font-size:1.4rem;letter-spacing:2px}}
.nav-links{{display:flex;gap:2rem;list-style:none}}
.nav-links a{{color:#ddd;text-decoration:none;font-size:.9rem;letter-spacing:1px}}
.nav-links a:hover{{color:var(--gold)}}
.hero{{height:100vh;background:linear-gradient(160deg,#2D0A00 0%,#7f1d1d 50%,#2D0A00 100%);display:flex;align-items:center;justify-content:center;text-align:center;position:relative;overflow:hidden}}
.hero::before{{content:'';position:absolute;inset:0;background:url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23a16207' fill-opacity='0.08'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")}}
.hero-content{{position:relative;z-index:1}}
.hero h1{{font-family:'Playfair Display SC';font-size:clamp(2.5rem,6vw,5rem);color:#fff;line-height:1.1;margin-bottom:1rem;text-shadow:0 2px 20px rgba(0,0,0,.5)}}
.hero p{{color:var(--gold);font-size:1.2rem;margin-bottom:2rem;letter-spacing:2px}}
.btn{{display:inline-block;background:var(--accent);color:#fff;padding:.9rem 2.5rem;border-radius:4px;text-decoration:none;font-size:1rem;font-weight:700;letter-spacing:1px;transition:.3s;border:none;cursor:pointer}}
.btn:hover{{background:#991b1b;transform:translateY(-2px)}}
.btn-gold{{background:var(--gold)}}
.btn-gold:hover{{background:#854d0e}}
section{{padding:5rem 2rem}}
.container{{max-width:1100px;margin:0 auto}}
.section-title{{font-family:'Playfair Display SC';font-size:2.2rem;color:var(--primary);text-align:center;margin-bottom:3rem}}
.section-title::after{{content:'';display:block;width:60px;height:3px;background:var(--gold);margin:.8rem auto 0}}
.menu-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.5rem}}
.dish{{background:#fff;padding:2rem;border-radius:8px;text-align:center;box-shadow:0 4px 20px rgba(45,10,0,.08);transition:.3s;border-bottom:3px solid transparent}}
.dish:hover{{transform:translateY(-6px);border-bottom-color:var(--accent);box-shadow:0 12px 40px rgba(45,10,0,.15)}}
.dish-icon{{font-size:3rem;display:block;margin-bottom:1rem}}
.dish h3{{font-family:'Playfair Display SC';color:var(--primary);margin-bottom:.5rem}}
.dish p{{color:var(--gold);font-weight:700}}
.atmos{{background:var(--primary);color:#fff}}
.atmos .section-title{{color:var(--gold)}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1rem}}
.gallery-item{{height:220px;border-radius:8px;background:linear-gradient(135deg,#7f1d1d,#dc2626);display:flex;align-items:center;justify-content:center;font-size:3rem;position:relative;overflow:hidden}}
.gallery-item::after{{content:attr(data-label);position:absolute;bottom:0;left:0;right:0;padding:1rem;background:linear-gradient(transparent,rgba(0,0,0,.7));color:#fff;font-size:.9rem;text-align:center}}
.reviews{{background:#fff9f0}}
.review-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem}}
.review-card{{background:#fff;padding:2rem;border-radius:8px;border-left:4px solid var(--gold);box-shadow:0 4px 16px rgba(0,0,0,.05)}}
.stars{{color:#f59e0b;font-size:1.2rem;margin-bottom:.5rem}}
.review-card p{{color:#555;font-style:italic;margin-bottom:1rem;line-height:1.7}}
.review-author{{font-weight:700;color:var(--primary)}}
.info-section{{display:grid;grid-template-columns:1fr 1fr;gap:3rem;align-items:center}}
.hours-table{{width:100%}}
.hours-table tr{{border-bottom:1px solid #f0e0d0}}
.hours-table td{{padding:.7rem .5rem;color:#555}}
.hours-table td:last-child{{text-align:right;font-weight:600;color:var(--accent)}}
.reservation-form{{background:#fff;padding:2.5rem;border-radius:12px;box-shadow:0 8px 40px rgba(45,10,0,.12)}}
.reservation-form h3{{font-family:'Playfair Display SC';color:var(--primary);font-size:1.5rem;margin-bottom:1.5rem}}
.form-group{{margin-bottom:1.2rem}}
.form-group label{{display:block;font-size:.85rem;font-weight:700;color:#666;margin-bottom:.4rem;letter-spacing:1px;text-transform:uppercase}}
.form-group input,.form-group select{{width:100%;padding:.8rem 1rem;border:2px solid #e5d5c5;border-radius:6px;font-size:1rem;font-family:'Karla';transition:.2s}}
.form-group input:focus,.form-group select:focus{{outline:none;border-color:var(--gold)}}
footer{{background:var(--primary);color:#ccc;padding:3rem 2rem;text-align:center}}
footer .logo{{font-size:1.6rem;margin-bottom:1rem;display:block}}
footer p{{font-size:.9rem;margin:.3rem 0}}
footer a{{color:var(--gold);text-decoration:none}}
.wa-btn{{position:fixed;bottom:2rem;right:2rem;width:60px;height:60px;background:#25D366;border-radius:50%;display:flex;align-items:center;justify-content:center;text-decoration:none;box-shadow:0 4px 20px rgba(37,211,102,.5);z-index:1000;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{box-shadow:0 4px 20px rgba(37,211,102,.5)}}50%{{box-shadow:0 4px 40px rgba(37,211,102,.8)}}}}
.wa-btn svg{{width:32px;height:32px;fill:#fff}}
.hamburger{{display:none;flex-direction:column;gap:5px;cursor:pointer;background:none;border:none;padding:.5rem}}
.hamburger span{{width:25px;height:2px;background:#fff;display:block}}
@media(max-width:768px){{.nav-links{{display:none;position:fixed;top:60px;left:0;right:0;background:var(--primary);flex-direction:column;padding:2rem;gap:1.5rem}}.nav-links.open{{display:flex}}.hamburger{{display:flex}}.info-section{{grid-template-columns:1fr}}}}
.reveal{{opacity:0;transform:translateY(30px);transition:.6s ease}}
.reveal.visible{{opacity:1;transform:none}}
</style></head><body>
<nav>
  <span class="logo">{n}</span>
  <ul class="nav-links" id="navLinks">
    <li><a href="#menu">Menyu</a></li>
    <li><a href="#atmosfera">Atmosfera</a></li>
    <li><a href="#sharh">Sharhlar</a></li>
    <li><a href="#rezervatsiya">Rezervatsiya</a></li>
  </ul>
  <button class="hamburger" onclick="document.getElementById('navLinks').classList.toggle('open')"><span></span><span></span><span></span></button>
</nav>
<section class="hero">
  <div class="hero-content">
    <p>✦ TOSHKENT'NI ENG YAXSHI TA'MI ✦</p>
    <h1>{n}</h1>
    <p style="font-size:1rem;margin-bottom:2rem;color:#f5d0a9">Har bir taom — unutilmas tajriba</p>
    <a href="#rezervatsiya" class="btn">Rezervatsiya Qilish</a>
    &nbsp;
    <a href="{w}" class="btn btn-gold">WhatsApp</a>
  </div>
</section>
<section id="menu">
  <div class="container">
    <h2 class="section-title">Bizning Menyumiz</h2>
    <div class="menu-grid">{svc_cards}</div>
  </div>
</section>
<section class="atmos" id="atmosfera">
  <div class="container">
    <h2 class="section-title">Atmosfera</h2>
    <div class="gallery">
      <div class="gallery-item" data-label="Asosiy zal">🕌</div>
      <div class="gallery-item" data-label="VIP xona">🌹</div>
      <div class="gallery-item" data-label="Ochiq hovli">🌿</div>
    </div>
  </div>
</section>
<section class="reviews" id="sharh">
  <div class="container">
    <h2 class="section-title">Mijozlar Fikri</h2>
    <div class="review-grid">
      <div class="review-card reveal"><div class="stars">★★★★★</div><p>"Toshkentdagi eng mazali milliy taomlar shu yerda. Kabubl alohida tavsiya etaman!"</p><span class="review-author">— Aziz T.</span></div>
      <div class="review-card reveal"><div class="stars">★★★★★</div><p>"Xizmat ko'rsatish darajasi zo'r, atmosfera juda qulay. Oila bilan kelganmiz, hammamiz mamnun!"</p><span class="review-author">— Malika R.</span></div>
      <div class="review-card reveal"><div class="stars">★★★★★</div><p>"Narx-navo adolatli, ovqat sifati juda yuqori. Har hafta kelamanmiz!"</p><span class="review-author">— Jahon S.</span></div>
    </div>
  </div>
</section>
<section id="rezervatsiya">
  <div class="container">
    <div class="info-section">
      <div>
        <h2 class="section-title" style="text-align:left">Ish Vaqtimiz</h2>
        <table class="hours-table">
          <tr><td>Dushanba–Juma</td><td>10:00 – 23:00</td></tr>
          <tr><td>Shanba–Yakshanba</td><td>09:00 – 00:00</td></tr>
        </table>
        <p style="margin-top:1.5rem;color:#666">📍 {a}</p>
        <p style="margin-top:.5rem"><a href="tel:{p}" style="color:var(--accent);font-size:1.2rem;font-weight:700">{p}</a></p>
      </div>
      <div class="reservation-form">
        <h3>Stol Bron Qilish</h3>
        <div class="form-group"><label>Ismingiz</label><input type="text" placeholder="To'liq ism"></div>
        <div class="form-group"><label>Telefon</label><input type="tel" placeholder="+998 90 000 00 00"></div>
        <div class="form-group"><label>Sana</label><input type="date"></div>
        <div class="form-group"><label>Mehmonlar soni</label><select><option>2 kishi</option><option>4 kishi</option><option>6 kishi</option><option>8+ kishi</option></select></div>
        <a href="{w}" class="btn" style="width:100%;text-align:center;display:block">Tasdiqlash →</a>
      </div>
    </div>
  </div>
</section>
<footer>
  <span class="logo">{n}</span>
  <p>📍 {a}</p>
  <p>📞 <a href="tel:{p}">{p}</a></p>
  <p style="margin-top:1rem;color:#666">© 2025 {n}. Barcha huquqlar himoyalangan.</p>
</footer>
<a href="{w}" class="wa-btn" target="_blank"><svg viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg></a>
<script>
document.querySelectorAll('.reveal').forEach(el=>new IntersectionObserver(([e])=>{{if(e.isIntersecting)el.classList.add('visible')}},{{threshold:.2}}).observe(el))
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',e=>{{e.preventDefault();document.querySelector(a.getAttribute('href'))?.scrollIntoView({{behavior:'smooth'}})}}))
</script></body></html>"""

def make_fitness(lead):
    n=lead['name']; p=lead['phone']; a=lead.get('address','Toshkent'); w=wa_link(p,n)
    svcs=lead.get('services',['Kuchlilik trenirovkasi','Kardio','Yoga','Boks'])
    svc_cards=''.join(f'<div class="service-card reveal"><span class="num">0{i+1}</span><h3>{s}</h3><p>Tajribali murabbiylar bilan individual yondashuv</p></div>' for i,s in enumerate(svcs))
    return f"""<!DOCTYPE html><html lang="uz"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{n} — Sport Markazi</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Inter:wght@400;600&family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#0F1923;--card:#141e2a;--accent:#F97316;--yellow:#FACC15;--text:#e2e8f0}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text)}}
nav{{position:fixed;top:0;width:100%;background:rgba(15,25,35,.95);border-bottom:1px solid rgba(249,115,22,.2);z-index:999;display:flex;align-items:center;justify-content:space-between;padding:1rem 2rem}}
.logo{{font-family:'Orbitron';color:var(--accent);font-size:1.2rem;letter-spacing:3px}}
.nav-links{{display:flex;gap:2rem;list-style:none}}
.nav-links a{{color:#94a3b8;text-decoration:none;font-size:.85rem;letter-spacing:2px;text-transform:uppercase;transition:.2s}}
.nav-links a:hover{{color:var(--accent)}}
.hero{{min-height:100vh;background:radial-gradient(ellipse at 30% 50%,rgba(249,115,22,.15) 0%,transparent 60%),var(--bg);display:flex;align-items:center;padding:6rem 2rem 4rem}}
.hero-inner{{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center}}
.hero-text .tag{{font-family:'Orbitron';color:var(--accent);font-size:.75rem;letter-spacing:4px;margin-bottom:1.5rem;display:block}}
.hero-text h1{{font-family:'Orbitron';font-size:clamp(2rem,4vw,3.5rem);line-height:1.1;margin-bottom:1.5rem;text-shadow:0 0 40px rgba(249,115,22,.3)}}
.hero-text h1 span{{color:var(--accent)}}
.hero-text p{{color:#94a3b8;font-size:1.1rem;margin-bottom:2.5rem;line-height:1.7}}
.stats-row{{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem;padding:2rem;background:var(--card);border-radius:12px;border:1px solid rgba(249,115,22,.2)}}
.stat span{{font-family:'JetBrains Mono';font-size:2rem;color:var(--yellow);display:block}}
.stat p{{font-size:.8rem;color:#64748b;letter-spacing:1px;text-transform:uppercase}}
.btn{{display:inline-block;background:var(--accent);color:#fff;padding:.9rem 2rem;border-radius:6px;text-decoration:none;font-weight:700;letter-spacing:1px;font-size:.9rem;transition:.3s}}
.btn:hover{{background:#ea6c10;box-shadow:0 0 30px rgba(249,115,22,.4)}}
.btn-outline{{background:transparent;border:2px solid var(--accent);color:var(--accent)}}
.btn-outline:hover{{background:var(--accent);color:#fff}}
section{{padding:5rem 2rem}}
.container{{max-width:1100px;margin:0 auto}}
.section-title{{font-family:'Orbitron';font-size:1.8rem;margin-bottom:3rem;position:relative;display:inline-block}}
.section-title::after{{content:'';position:absolute;bottom:-8px;left:0;width:40px;height:3px;background:var(--accent)}}
.services-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1.5rem}}
.service-card{{background:var(--card);padding:2rem;border-radius:10px;border:1px solid rgba(249,115,22,.1);transition:.3s}}
.service-card:hover{{border-color:var(--accent);box-shadow:0 0 30px rgba(249,115,22,.1);transform:translateY(-4px)}}
.num{{font-family:'Orbitron';font-size:2.5rem;color:rgba(249,115,22,.2);display:block;margin-bottom:.5rem}}
.service-card h3{{color:#fff;margin-bottom:.5rem;font-size:1.1rem}}
.service-card p{{color:#64748b;font-size:.9rem;line-height:1.6}}
.pricing-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1.5rem;margin-top:3rem}}
.price-card{{background:var(--card);border:1px solid rgba(249,115,22,.15);border-radius:12px;padding:2.5rem;text-align:center;transition:.3s}}
.price-card.featured{{border-color:var(--accent);background:rgba(249,115,22,.05);box-shadow:0 0 40px rgba(249,115,22,.1)}}
.price-card h3{{font-family:'Orbitron';font-size:1rem;letter-spacing:2px;margin-bottom:1.5rem}}
.price-card .price{{font-family:'JetBrains Mono';font-size:2.5rem;color:var(--yellow);margin-bottom:.3rem}}
.price-card .per{{color:#64748b;font-size:.85rem;margin-bottom:2rem}}
.price-features{{list-style:none;text-align:left;margin-bottom:2rem}}
.price-features li{{padding:.5rem 0;border-bottom:1px solid rgba(255,255,255,.05);color:#94a3b8;font-size:.9rem}}
.price-features li::before{{content:'✓ ';color:var(--accent)}}
.coaches{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1.5rem}}
.coach-card{{background:var(--card);border-radius:12px;overflow:hidden;border:1px solid rgba(249,115,22,.1);transition:.3s}}
.coach-card:hover{{transform:translateY(-4px);border-color:var(--accent)}}
.coach-img{{height:180px;background:linear-gradient(135deg,#1e293b,rgba(249,115,22,.2));display:flex;align-items:center;justify-content:center;font-size:4rem}}
.coach-info{{padding:1.5rem}}
.coach-info h3{{color:#fff;margin-bottom:.3rem}}
.coach-info p{{color:var(--accent);font-size:.85rem}}
footer{{background:#0a111a;padding:3rem 2rem;text-align:center;border-top:1px solid rgba(249,115,22,.1)}}
footer .logo{{font-size:1.5rem;margin-bottom:1rem;display:block}}
footer p{{color:#475569;font-size:.9rem;margin:.3rem 0}}
footer a{{color:var(--accent);text-decoration:none}}
.wa-btn{{position:fixed;bottom:2rem;right:2rem;width:60px;height:60px;background:#25D366;border-radius:50%;display:flex;align-items:center;justify-content:center;text-decoration:none;box-shadow:0 4px 20px rgba(37,211,102,.5);z-index:1000}}
.wa-btn svg{{width:32px;height:32px;fill:#fff}}
.hamburger{{display:none;flex-direction:column;gap:5px;cursor:pointer;background:none;border:none;padding:.5rem}}
.hamburger span{{width:25px;height:2px;background:var(--accent);display:block}}
@media(max-width:768px){{.hero-inner{{grid-template-columns:1fr}}.stats-row{{grid-template-columns:repeat(3,1fr)}}.nav-links{{display:none;position:fixed;top:60px;left:0;right:0;background:#0a111a;flex-direction:column;padding:2rem;gap:1.5rem}}.nav-links.open{{display:flex}}.hamburger{{display:flex}}}}
.reveal{{opacity:0;transform:translateY(30px);transition:.6s ease}}
.reveal.visible{{opacity:1;transform:none}}
</style></head><body>
<nav>
  <span class="logo">{n[:12]}</span>
  <ul class="nav-links" id="navLinks">
    <li><a href="#xizmatlar">Xizmatlar</a></li>
    <li><a href="#narxlar">Narxlar</a></li>
    <li><a href="#murabbiylar">Murabbiylar</a></li>
  </ul>
  <button class="hamburger" onclick="document.getElementById('navLinks').classList.toggle('open')"><span></span><span></span><span></span></button>
</nav>
<section class="hero">
  <div class="hero-inner">
    <div class="hero-text">
      <span class="tag">SPORT MARKAZI — TOSHKENT</span>
      <h1>KUCHINGIZNI <span>KASHF</span> ETING</h1>
      <p>Professional murabbiylar va zamonaviy jihozlar bilan maqsadingizga erishing. {n} — bu nafaqat sport zali, bu hayot tarzi.</p>
      <div style="display:flex;gap:1rem;flex-wrap:wrap">
        <a href="{w}" class="btn">Bepul Sinov Darsi</a>
        <a href="tel:{p}" class="btn btn-outline">Qo'ng'iroq</a>
      </div>
    </div>
    <div class="stats-row">
      <div class="stat"><span id="c1">0</span><p>A'zolar</p></div>
      <div class="stat"><span id="c2">0</span><p>Murabbiy</p></div>
      <div class="stat"><span id="c3">0</span><p>Mashg'ulot</p></div>
    </div>
  </div>
</section>
<section id="xizmatlar">
  <div class="container">
    <h2 class="section-title">Xizmatlarimiz</h2>
    <div class="services-grid">{svc_cards}</div>
  </div>
</section>
<section id="narxlar" style="background:#0c1520">
  <div class="container">
    <h2 class="section-title">Narxlar</h2>
    <div class="pricing-grid">
      <div class="price-card reveal"><h3>STARTER</h3><div class="price">299K</div><div class="per">so'm / oy</div><ul class="price-features"><li>10 ta mashg'ulot</li><li>Guruh trenajyor zali</li><li>Kiyinish xonasi</li></ul><a href="{w}" class="btn btn-outline" style="width:100%;text-align:center;display:block">Tanlash</a></div>
      <div class="price-card featured reveal"><h3>PRO ⭐</h3><div class="price">499K</div><div class="per">so'm / oy</div><ul class="price-features"><li>Cheksiz mashg'ulot</li><li>Individual murabbiy</li><li>Ovqatlanish rejasi</li><li>Progress nazorati</li></ul><a href="{w}" class="btn" style="width:100%;text-align:center;display:block">Tanlash</a></div>
      <div class="price-card reveal"><h3>ELITE</h3><div class="price">799K</div><div class="per">so'm / oy</div><ul class="price-features"><li>VIP xizmat</li><li>Shaxsiy murabbiy</li><li>Spa & sauna</li><li>Ovqat tayyorlash</li></ul><a href="{w}" class="btn btn-outline" style="width:100%;text-align:center;display:block">Tanlash</a></div>
    </div>
  </div>
</section>
<section id="murabbiylar">
  <div class="container">
    <h2 class="section-title">Murabbiylarimiz</h2>
    <div class="coaches">
      <div class="coach-card reveal"><div class="coach-img">💪</div><div class="coach-info"><h3>Bobur Xoliqov</h3><p>Kuchlilik va fitnes</p></div></div>
      <div class="coach-card reveal"><div class="coach-img">🥊</div><div class="coach-info"><h3>Sardor Alimov</h3><p>Boks va kardio</p></div></div>
      <div class="coach-card reveal"><div class="coach-img">🧘</div><div class="coach-info"><h3>Zulfiya Nazarova</h3><p>Yoga va stretching</p></div></div>
    </div>
  </div>
</section>
<footer>
  <span class="logo">{n}</span>
  <p>📍 {a}</p>
  <p>📞 <a href="tel:{p}">{p}</a></p>
  <p style="margin-top:1rem;color:#2d3748">© 2025 {n}. Barcha huquqlar himoyalangan.</p>
</footer>
<a href="{w}" class="wa-btn" target="_blank"><svg viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg></a>
<script>
function countUp(id,target){{let n=0;const step=Math.ceil(target/60);const t=setInterval(()=>{{n=Math.min(n+step,target);document.getElementById(id).textContent=n+(target>=100?'+':'');if(n>=target)clearInterval(t)}},30)}}
countUp('c1',500);countUp('c2',12);countUp('c3',30);
document.querySelectorAll('.reveal').forEach(el=>new IntersectionObserver(([e])=>{{if(e.isIntersecting)el.classList.add('visible')}},{{threshold:.2}}).observe(el))
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',e=>{{e.preventDefault();document.querySelector(a.getAttribute('href'))?.scrollIntoView({{behavior:'smooth'}})}}))
</script></body></html>"""

def make_beauty(lead):
    n=lead['name']; p=lead['phone']; a=lead.get('address','Toshkent'); w=wa_link(p,n)
    svcs=lead.get('services',['Soch turmagi','Manikur','Pedikur','Makiyaj'])
    svc_cards=''.join(f'<div class="svc-card reveal"><div class="svc-icon">💅</div><h3>{s}</h3><p>Narxi: {80000+i*20000:,} so\'mdan</p><a href="{w}" class="book-btn">Yozilish</a></div>' for i,s in enumerate(svcs))
    return f"""<!DOCTYPE html><html lang="uz"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{n} — Go'zallik Saloni</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{{--bg:#FDF2F8;--card:#fff;--primary:#831843;--accent:#EC4899;--violet:#8B5CF6;--gold:#d97706}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',sans-serif;background:var(--bg);color:#3b1832}}
nav{{position:fixed;top:0;width:100%;background:rgba(253,242,248,.95);backdrop-filter:blur(12px);border-bottom:1px solid rgba(236,72,153,.1);z-index:999;display:flex;align-items:center;justify-content:space-between;padding:1rem 2rem}}
.logo{{font-family:'Playfair Display';font-style:italic;color:var(--primary);font-size:1.5rem;letter-spacing:1px}}
.nav-links{{display:flex;gap:2rem;list-style:none}}
.nav-links a{{color:#9d4b7a;text-decoration:none;font-size:.9rem}}
.nav-links a:hover{{color:var(--accent)}}
.hero{{min-height:100vh;background:linear-gradient(135deg,#FDF2F8 0%,#fce7f3 50%,#ede9fe 100%);display:flex;align-items:center;padding:6rem 2rem 4rem}}
.hero-inner{{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center}}
.hero-text .tag{{color:var(--accent);font-size:.8rem;letter-spacing:3px;text-transform:uppercase;margin-bottom:1rem;display:block}}
.hero-text h1{{font-family:'Playfair Display';font-size:clamp(2rem,4vw,3.5rem);line-height:1.2;color:var(--primary);margin-bottom:1.5rem}}
.hero-text h1 em{{font-style:italic;color:var(--accent)}}
.hero-text p{{color:#6b4c5a;line-height:1.8;margin-bottom:2rem}}
.booking-card{{background:rgba(255,255,255,.8);backdrop-filter:blur(20px);border:1px solid rgba(236,72,153,.2);border-radius:20px;padding:2.5rem;box-shadow:0 20px 60px rgba(236,72,153,.1)}}
.booking-card h3{{font-family:'Playfair Display';font-style:italic;color:var(--primary);font-size:1.4rem;margin-bottom:1.5rem;text-align:center}}
.form-row{{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem}}
.form-group label{{display:block;font-size:.75rem;font-weight:600;color:#9d4b7a;margin-bottom:.4rem;letter-spacing:1px;text-transform:uppercase}}
.form-group input,.form-group select{{width:100%;padding:.75rem 1rem;border:1.5px solid rgba(236,72,153,.2);border-radius:10px;font-family:'Inter';font-size:.9rem;background:rgba(255,255,255,.7);color:#3b1832;transition:.2s}}
.form-group input:focus,.form-group select:focus{{outline:none;border-color:var(--accent);background:#fff}}
.btn{{display:inline-block;background:linear-gradient(135deg,var(--accent),var(--violet));color:#fff;padding:.85rem 2rem;border-radius:50px;text-decoration:none;font-weight:600;font-size:.9rem;transition:.3s;border:none;cursor:pointer}}
.btn:hover{{transform:translateY(-2px);box-shadow:0 8px 30px rgba(236,72,153,.4)}}
section{{padding:5rem 2rem}}
.container{{max-width:1100px;margin:0 auto}}
.section-title{{font-family:'Playfair Display';font-style:italic;font-size:2.2rem;color:var(--primary);text-align:center;margin-bottom:3rem}}
.section-title::after{{content:'✦';display:block;font-size:1rem;color:var(--accent);margin-top:.5rem;font-style:normal}}
.services-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1.5rem}}
.svc-card{{background:#fff;padding:2rem;border-radius:16px;text-align:center;box-shadow:0 4px 20px rgba(236,72,153,.06);transition:.3s;border:1px solid rgba(236,72,153,.1)}}
.svc-card:hover{{transform:translateY(-6px);box-shadow:0 12px 40px rgba(236,72,153,.15);border-color:var(--accent)}}
.svc-icon{{font-size:2.5rem;margin-bottom:1rem;display:block}}
.svc-card h3{{font-family:'Playfair Display';color:var(--primary);margin-bottom:.5rem}}
.svc-card p{{color:var(--violet);font-weight:600;margin-bottom:1.2rem}}
.book-btn{{display:inline-block;background:linear-gradient(135deg,var(--accent),var(--violet));color:#fff;padding:.5rem 1.5rem;border-radius:50px;text-decoration:none;font-size:.85rem;font-weight:600}}
.masters{{background:linear-gradient(135deg,#fff5f9,#f5f3ff)}}
.masters-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem}}
.master-card{{text-align:center;padding:2rem}}
.master-photo{{width:100px;height:100px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--violet));margin:0 auto 1rem;display:flex;align-items:center;justify-content:center;font-size:2.5rem;border:4px solid rgba(236,72,153,.2)}}
.master-card h3{{font-family:'Playfair Display';color:var(--primary);margin-bottom:.3rem}}
.master-card p{{color:#9d4b7a;font-size:.85rem}}
.reviews-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem}}
.review{{background:#fff;padding:2rem;border-radius:16px;box-shadow:0 4px 20px rgba(236,72,153,.06);border:1px solid rgba(236,72,153,.08)}}
.stars{{color:var(--gold);margin-bottom:.8rem}}
.review p{{color:#6b4c5a;font-style:italic;line-height:1.7;margin-bottom:1rem}}
.review-author{{font-weight:600;color:var(--primary)}}
footer{{background:var(--primary);color:#f9a8d4;padding:3rem 2rem;text-align:center}}
footer .logo{{color:#fff;margin-bottom:1rem;display:block;font-size:1.8rem}}
footer p{{margin:.3rem 0;font-size:.9rem}}
footer a{{color:#f9a8d4;text-decoration:none}}
.wa-btn{{position:fixed;bottom:2rem;right:2rem;width:60px;height:60px;background:#25D366;border-radius:50%;display:flex;align-items:center;justify-content:center;text-decoration:none;box-shadow:0 4px 20px rgba(37,211,102,.5);z-index:1000}}
.wa-btn svg{{width:32px;height:32px;fill:#fff}}
.hamburger{{display:none;flex-direction:column;gap:5px;cursor:pointer;background:none;border:none;padding:.5rem}}
.hamburger span{{width:25px;height:2px;background:var(--accent);display:block}}
@media(max-width:768px){{.hero-inner{{grid-template-columns:1fr}}.form-row{{grid-template-columns:1fr}}.nav-links{{display:none;position:fixed;top:60px;left:0;right:0;background:rgba(253,242,248,.97);flex-direction:column;padding:2rem;gap:1.5rem}}.nav-links.open{{display:flex}}.hamburger{{display:flex}}}}
.reveal{{opacity:0;transform:translateY(30px);transition:.6s ease}}
.reveal.visible{{opacity:1;transform:none}}
</style></head><body>
<nav>
  <span class="logo">{n}</span>
  <ul class="nav-links" id="navLinks">
    <li><a href="#xizmatlar">Xizmatlar</a></li>
    <li><a href="#ustalar">Ustalar</a></li>
    <li><a href="#sharhlar">Sharhlar</a></li>
  </ul>
  <button class="hamburger" onclick="document.getElementById('navLinks').classList.toggle('open')"><span></span><span></span><span></span></button>
</nav>
<section class="hero">
  <div class="hero-inner">
    <div class="hero-text">
      <span class="tag">✨ Go'zallik Saloni · Toshkent</span>
      <h1>Go'zallik — bu <em>san'at</em></h1>
      <p>{n} — sizga eng yaxshi go'zallik xizmatlarini taqdim etadi. Har bir mijoz — bizning asarimiz.</p>
      <a href="{w}" class="btn">Yozilish →</a>
    </div>
    <div class="booking-card">
      <h3>Online Yozilish</h3>
      <div class="form-group" style="margin-bottom:1rem"><label>Xizmat turi</label><select><option>Xizmatni tanlang...</option>{''.join(f'<option>{s}</option>' for s in svcs)}</select></div>
      <div class="form-row">
        <div class="form-group"><label>Ism</label><input type="text" placeholder="Ismingiz"></div>
        <div class="form-group"><label>Telefon</label><input type="tel" placeholder="+998 90..."></div>
      </div>
      <div class="form-group" style="margin-bottom:1.5rem"><label>Sana va vaqt</label><input type="datetime-local"></div>
      <a href="{w}" class="btn" style="width:100%;text-align:center;display:block">Tasdiqlash ✓</a>
    </div>
  </div>
</section>
<section id="xizmatlar">
  <div class="container">
    <h2 class="section-title">Xizmatlarimiz</h2>
    <div class="services-grid">{svc_cards}</div>
  </div>
</section>
<section class="masters" id="ustalar">
  <div class="container">
    <h2 class="section-title">Ustalarimiz</h2>
    <div class="masters-grid">
      <div class="master-card reveal"><div class="master-photo">👩‍🎨</div><h3>Nilufar Yusupova</h3><p>Soch mutaxassisi · 8 yil</p></div>
      <div class="master-card reveal"><div class="master-photo">💄</div><h3>Kamola Rahimova</h3><p>Makiyaj ustasi · 5 yil</p></div>
      <div class="master-card reveal"><div class="master-photo">💅</div><h3>Shahnoza Tosheva</h3><p>Manikur & pedikur · 6 yil</p></div>
    </div>
  </div>
</section>
<section id="sharhlar">
  <div class="container">
    <h2 class="section-title">Mijozlar Fikri</h2>
    <div class="reviews-grid">
      <div class="review reveal"><div class="stars">★★★★★</div><p>"Eng yaxshi salon! Ustalar juda professional va mehribon. Har safar kelaveraman!"</p><span class="review-author">— Dilnoza M.</span></div>
      <div class="review reveal"><div class="stars">★★★★★</div><p>"Manikur va pedikur sifati zo'r. Narxlar ham qulay. Hammaga tavsiya qilaman!"</p><span class="review-author">— Barno K.</span></div>
      <div class="review reveal"><div class="stars">★★★★★</div><p>"Soch turmagi juda chiroyli chiqdi. Usta mening istaklarimni tushunib oldi."</p><span class="review-author">— Feruza T.</span></div>
    </div>
  </div>
</section>
<footer>
  <span class="logo">{n}</span>
  <p>📍 {a}</p>
  <p>📞 <a href="tel:{p}">{p}</a></p>
  <p style="margin-top:1rem;opacity:.5">© 2025 {n}. Barcha huquqlar himoyalangan.</p>
</footer>
<a href="{w}" class="wa-btn" target="_blank"><svg viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg></a>
<script>
document.querySelectorAll('.reveal').forEach(el=>new IntersectionObserver(([e])=>{{if(e.isIntersecting)el.classList.add('visible')}},{{threshold:.2}}).observe(el))
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',e=>{{e.preventDefault();document.querySelector(a.getAttribute('href'))?.scrollIntoView({{behavior:'smooth'}})}}))
</script></body></html>"""

def make_auto(lead):
    n=lead['name']; p=lead['phone']; a=lead.get('address','Toshkent'); w=wa_link(p,n)
    svcs=lead.get('services',['Diagnostika','Moy almashtirish','Tormoz tizimi','Dvigatel ta\'miri'])
    svc_cards=''.join(f'<div class="svc reveal"><span class="svc-num">0{i+1}</span><div><h3>{s}</h3><p>Professional uskunalar bilan tez va sifatli bajariladi</p></div></div>' for i,s in enumerate(svcs))
    return f"""<!DOCTYPE html><html lang="uz"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{n} — Avtoservis</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700;800&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{{--bg:#0F172A;--card:#1E293B;--accent:#059669;--orange:#EA580C;--text:#e2e8f0}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text)}}
nav{{position:fixed;top:0;width:100%;background:rgba(15,23,42,.97);border-bottom:1px solid rgba(5,150,105,.2);z-index:999;display:flex;align-items:center;justify-content:space-between;padding:1rem 2rem}}
.logo{{font-family:'Space Grotesk';font-weight:800;color:#fff;font-size:1.2rem;letter-spacing:1px}}
.logo span{{color:var(--accent)}}
.nav-links{{display:flex;gap:2rem;list-style:none}}
.nav-links a{{color:#94a3b8;text-decoration:none;font-size:.85rem;text-transform:uppercase;letter-spacing:1px;transition:.2s}}
.nav-links a:hover{{color:var(--accent)}}
.hero{{min-height:100vh;background:linear-gradient(135deg,#0F172A 60%,rgba(5,150,105,.08) 100%);display:flex;align-items:center;padding:5rem 2rem}}
.hero-inner{{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:4rem;align-items:center}}
.hero-text .badge{{display:inline-block;background:rgba(5,150,105,.15);border:1px solid rgba(5,150,105,.3);color:var(--accent);padding:.4rem 1rem;border-radius:4px;font-size:.8rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:1.5rem}}
.hero-text h1{{font-family:'Space Grotesk';font-size:clamp(2rem,4vw,3.5rem);font-weight:800;line-height:1.1;margin-bottom:1.5rem}}
.hero-text h1 span{{color:var(--accent)}}
.hero-text p{{color:#94a3b8;line-height:1.7;margin-bottom:2rem}}
.hero-svg{{display:flex;align-items:center;justify-content:center}}
.car-graphic{{width:100%;max-width:400px;height:250px;background:linear-gradient(135deg,var(--card),#0f172a);border-radius:12px;border:1px solid rgba(5,150,105,.2);display:flex;align-items:center;justify-content:center;font-size:8rem;position:relative;overflow:hidden}}
.car-graphic::before{{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,transparent,var(--accent),transparent)}}
.trust-badges{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-top:2rem}}
.badge-item{{background:var(--card);padding:1.2rem;border-radius:8px;text-align:center;border:1px solid rgba(5,150,105,.1)}}
.badge-item .num{{font-family:'Space Grotesk';font-size:1.8rem;font-weight:800;color:var(--accent)}}
.badge-item p{{font-size:.75rem;color:#64748b;text-transform:uppercase;letter-spacing:1px}}
.btn{{display:inline-block;background:var(--accent);color:#fff;padding:.9rem 2rem;border-radius:6px;text-decoration:none;font-weight:700;letter-spacing:1px;font-size:.9rem;transition:.3s;font-family:'Space Grotesk'}}
.btn:hover{{background:#047857;box-shadow:0 0 30px rgba(5,150,105,.3)}}
.btn-orange{{background:var(--orange)}}
.btn-orange:hover{{background:#c2410c}}
section{{padding:5rem 2rem}}
.container{{max-width:1100px;margin:0 auto}}
.section-title{{font-family:'Space Grotesk';font-size:1.8rem;font-weight:800;margin-bottom:3rem;position:relative;padding-bottom:1rem}}
.section-title::after{{content:'';position:absolute;bottom:0;left:0;width:50px;height:3px;background:var(--accent)}}
.services-list{{display:flex;flex-direction:column;gap:1rem}}
.svc{{display:flex;align-items:center;gap:1.5rem;background:var(--card);padding:1.5rem 2rem;border-radius:10px;border:1px solid rgba(5,150,105,.1);transition:.3s}}
.svc:hover{{border-color:var(--accent);transform:translateX(6px)}}
.svc-num{{font-family:'Space Grotesk';font-size:2rem;font-weight:800;color:rgba(5,150,105,.3);min-width:3rem}}
.svc h3{{color:#fff;margin-bottom:.3rem;font-family:'Space Grotesk'}}
.svc p{{color:#64748b;font-size:.9rem}}
.stages{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;background:rgba(5,150,105,.1);border-radius:12px;overflow:hidden}}
.stage{{background:var(--card);padding:2rem;text-align:center}}
.stage-icon{{font-size:2rem;margin-bottom:1rem;display:block}}
.stage h3{{font-size:.9rem;color:var(--accent);font-weight:700;margin-bottom:.5rem}}
.stage p{{font-size:.8rem;color:#64748b}}
.price-calc{{background:var(--card);padding:2.5rem;border-radius:12px;border:1px solid rgba(5,150,105,.2)}}
.price-calc h3{{font-family:'Space Grotesk';color:#fff;margin-bottom:1.5rem}}
.calc-row{{display:flex;align-items:center;gap:1rem;margin-bottom:1rem}}
.calc-row label{{color:#94a3b8;font-size:.9rem;min-width:150px}}
.calc-row input,.calc-row select{{flex:1;background:#0f172a;border:1px solid rgba(5,150,105,.2);border-radius:6px;padding:.7rem 1rem;color:#fff;font-size:.9rem}}
.calc-result{{margin-top:1.5rem;padding:1.5rem;background:rgba(5,150,105,.1);border-radius:8px;text-align:center}}
.calc-result .price{{font-family:'Space Grotesk';font-size:2rem;font-weight:800;color:var(--accent)}}
footer{{background:#060d1a;padding:3rem 2rem;text-align:center;border-top:1px solid rgba(5,150,105,.1)}}
footer .logo{{font-size:1.5rem;margin-bottom:1rem;display:block}}
footer p{{color:#475569;font-size:.9rem;margin:.3rem 0}}
footer a{{color:var(--accent);text-decoration:none}}
.wa-btn{{position:fixed;bottom:2rem;right:2rem;width:60px;height:60px;background:#25D366;border-radius:50%;display:flex;align-items:center;justify-content:center;text-decoration:none;box-shadow:0 4px 20px rgba(37,211,102,.5);z-index:1000}}
.wa-btn svg{{width:32px;height:32px;fill:#fff}}
.hamburger{{display:none;flex-direction:column;gap:5px;cursor:pointer;background:none;border:none;padding:.5rem}}
.hamburger span{{width:25px;height:2px;background:var(--accent);display:block}}
@media(max-width:768px){{.hero-inner{{grid-template-columns:1fr}}.hero-svg{{display:none}}.trust-badges{{grid-template-columns:repeat(3,1fr)}}.calc-row{{flex-direction:column;align-items:stretch}}.calc-row label{{min-width:auto}}.nav-links{{display:none;position:fixed;top:60px;left:0;right:0;background:#060d1a;flex-direction:column;padding:2rem;gap:1.5rem}}.nav-links.open{{display:flex}}.hamburger{{display:flex}}}}
.reveal{{opacity:0;transform:translateY(30px);transition:.6s ease}}
.reveal.visible{{opacity:1;transform:none}}
</style></head><body>
<nav>
  <span class="logo">{n[:14]}<span>.</span></span>
  <ul class="nav-links" id="navLinks">
    <li><a href="#xizmatlar">Xizmatlar</a></li>
    <li><a href="#bosqichlar">Bosqichlar</a></li>
    <li><a href="#narx">Narx</a></li>
  </ul>
  <button class="hamburger" onclick="document.getElementById('navLinks').classList.toggle('open')"><span></span><span></span><span></span></button>
</nav>
<section class="hero">
  <div class="hero-inner">
    <div class="hero-text">
      <span class="badge">✓ Kafolatlangan Xizmat</span>
      <h1>Mashinangiz — <span>Bizning</span> G'amimiz</h1>
      <p>Professional diagnostika va tez ta'mirlash. {n} — Toshkentdagi ishonchli avtoservis.</p>
      <div style="display:flex;gap:1rem;flex-wrap:wrap">
        <a href="{w}" class="btn">Hoziroq Yozing</a>
        <a href="tel:{p}" class="btn btn-orange">📞 {p}</a>
      </div>
      <div class="trust-badges">
        <div class="badge-item"><div class="num">10+</div><p>Yil tajriba</p></div>
        <div class="badge-item"><div class="num">5K+</div><p>Mashina ta'mirlandi</p></div>
        <div class="badge-item"><div class="num">98%</div><p>Mijoz mamnun</p></div>
      </div>
    </div>
    <div class="hero-svg"><div class="car-graphic">🔧</div></div>
  </div>
</section>
<section id="xizmatlar">
  <div class="container">
    <h2 class="section-title">Xizmatlarimiz</h2>
    <div class="services-list">{svc_cards}</div>
  </div>
</section>
<section id="bosqichlar" style="background:#0a1020">
  <div class="container">
    <h2 class="section-title">Ish Bosqichlari</h2>
    <div class="stages">
      <div class="stage"><span class="stage-icon">📋</span><h3>Qabul</h3><p>Mashina qabul qilinadi va muammo aniqlanadi</p></div>
      <div class="stage"><span class="stage-icon">🔍</span><h3>Diagnostika</h3><p>To'liq kompyuter diagnostikasi</p></div>
      <div class="stage"><span class="stage-icon">🔧</span><h3>Ta'mirlash</h3><p>Sifatli ehtiyot qismlar bilan ta'mirlash</p></div>
      <div class="stage"><span class="stage-icon">✅</span><h3>Tekshirish</h3><p>Ishlov berilgandan keyin test</p></div>
      <div class="stage"><span class="stage-icon">🚗</span><h3>Topshirish</h3><p>Kafolat bilan topshirish</p></div>
    </div>
  </div>
</section>
<section id="narx">
  <div class="container">
    <h2 class="section-title">Narx Hisoblash</h2>
    <div class="price-calc">
      <h3>Taxminiy narxni hisoblang</h3>
      <div class="calc-row"><label>Xizmat turi:</label><select id="svcSel"><option value="50000">Diagnostika — 50,000 so'm</option><option value="120000">Moy almashtirish — 120,000 so'm</option><option value="350000">Tormoz tizimi — 350,000 so'm</option><option value="800000">Dvigatel ta'miri — 800,000+ so'm</option></select></div>
      <div class="calc-row"><label>Mashina turi:</label><select id="carSel"><option value="1">Odd (Nexia, Malibu)</option><option value="1.3">O'rta (Gentra, Tracker)</option><option value="1.8">Premium (Damas, Cobalt)</option></select></div>
      <div class="calc-result"><div class="price" id="calcResult">50,000 so'm</div><p style="color:#64748b;font-size:.85rem;margin-top:.5rem">Taxminiy narx. Aniq narx diagnostikadan keyin</p></div>
      <a href="{w}" class="btn" style="margin-top:1.5rem;display:inline-block">Yozilish →</a>
    </div>
  </div>
</section>
<footer>
  <span class="logo">{n}<span>.</span></span>
  <p>📍 {a}</p>
  <p>📞 <a href="tel:{p}">{p}</a></p>
  <p style="margin-top:1rem;color:#1e293b">© 2025 {n}. Barcha huquqlar himoyalangan.</p>
</footer>
<a href="{w}" class="wa-btn" target="_blank"><svg viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg></a>
<script>
function calcPrice(){{const s=parseFloat(document.getElementById('svcSel').value);const c=parseFloat(document.getElementById('carSel').value);const t=Math.round(s*c/1000)*1000;document.getElementById('calcResult').textContent=t.toLocaleString('uz-UZ')+' so\'m'}}
document.getElementById('svcSel').onchange=calcPrice;
document.getElementById('carSel').onchange=calcPrice;
document.querySelectorAll('.reveal').forEach(el=>new IntersectionObserver(([e])=>{{if(e.isIntersecting)el.classList.add('visible')}},{{threshold:.2}}).observe(el))
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',e=>{{e.preventDefault();document.querySelector(a.getAttribute('href'))?.scrollIntoView({{behavior:'smooth'}})}}))
</script></body></html>"""

def make_generic(lead, niche_label="Biznes"):
    """Fallback for Hotel, Construction, Dentistry, Clinic, and any unknown niche."""
    n=lead['name']; p=lead['phone']; a=lead.get('address','Toshkent'); w=wa_link(p,n)
    niche=lead.get('niche','Biznes')
    svcs=lead.get('services',['Asosiy xizmat 1','Asosiy xizmat 2','Asosiy xizmat 3'])
    colors=lead.get('colors',{})
    primary=colors.get('primary','#0a1628')
    accent=colors.get('accent','#00b4d8')

    # pick emoji per niche
    icons={'Hotel':'🏨','Construction':'🏗️','Dentistry':'🦷','Clinic':'🏥','Restaurant':'🍽️'}.get(niche,'🏢')
    svc_cards=''.join(f'<div class="svc-card reveal"><div class="svc-icon">{icons}</div><h3>{s}</h3><p>Professional xizmat kafolati bilan</p></div>' for s in svcs)

    return f"""<!DOCTYPE html><html lang="uz"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{n}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
:root{{--primary:{primary};--accent:{accent};--bg:#f8fafc;--dark:#0f172a}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Inter',sans-serif;background:var(--bg);color:#1e293b}}
nav{{position:fixed;top:0;width:100%;background:rgba(255,255,255,.95);backdrop-filter:blur(10px);border-bottom:1px solid #e2e8f0;z-index:999;display:flex;align-items:center;justify-content:space-between;padding:1rem 2rem;box-shadow:0 1px 20px rgba(0,0,0,.06)}}
.logo{{font-weight:800;color:var(--primary);font-size:1.2rem}}
.nav-links{{display:flex;gap:2rem;list-style:none}}
.nav-links a{{color:#64748b;text-decoration:none;font-size:.9rem;transition:.2s}}
.nav-links a:hover{{color:var(--accent)}}
.hero{{min-height:100vh;background:linear-gradient(135deg,var(--primary) 0%,{accent}33 100%);display:flex;align-items:center;justify-content:center;text-align:center;padding:6rem 2rem 4rem}}
.hero-content .tag{{display:inline-block;background:rgba(255,255,255,.15);color:rgba(255,255,255,.9);padding:.4rem 1.2rem;border-radius:50px;font-size:.8rem;letter-spacing:2px;text-transform:uppercase;margin-bottom:1.5rem;border:1px solid rgba(255,255,255,.2)}}
.hero-content h1{{font-size:clamp(2rem,5vw,4rem);color:#fff;font-weight:800;line-height:1.15;margin-bottom:1.5rem;text-shadow:0 2px 20px rgba(0,0,0,.3)}}
.hero-content p{{color:rgba(255,255,255,.85);font-size:1.1rem;max-width:600px;margin:0 auto 2.5rem;line-height:1.7}}
.hero-btns{{display:flex;gap:1rem;justify-content:center;flex-wrap:wrap}}
.btn{{display:inline-block;background:#fff;color:var(--primary);padding:.9rem 2.2rem;border-radius:8px;text-decoration:none;font-weight:700;font-size:.95rem;transition:.3s}}
.btn:hover{{transform:translateY(-3px);box-shadow:0 10px 30px rgba(0,0,0,.2)}}
.btn-outline{{background:transparent;border:2px solid rgba(255,255,255,.6);color:#fff}}
.btn-outline:hover{{background:rgba(255,255,255,.1)}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:2rem;max-width:600px;margin:3rem auto 0;padding:2rem;background:rgba(255,255,255,.1);border-radius:12px;border:1px solid rgba(255,255,255,.15)}}
.stat-num{{font-size:2rem;font-weight:800;color:#fff}}
.stat-label{{font-size:.8rem;color:rgba(255,255,255,.7);text-transform:uppercase;letter-spacing:1px}}
section{{padding:5rem 2rem}}
.container{{max-width:1100px;margin:0 auto}}
.section-title{{font-size:2rem;font-weight:800;color:var(--dark);text-align:center;margin-bottom:3rem}}
.section-title span{{color:var(--accent)}}
.svc-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1.5rem}}
.svc-card{{background:#fff;padding:2rem;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,.06);transition:.3s;border:1px solid #f1f5f9;text-align:center}}
.svc-card:hover{{transform:translateY(-6px);box-shadow:0 12px 40px rgba(0,0,0,.1);border-color:var(--accent)}}
.svc-icon{{font-size:2.5rem;margin-bottom:1rem;display:block}}
.svc-card h3{{font-weight:700;margin-bottom:.5rem;color:var(--dark)}}
.svc-card p{{color:#64748b;font-size:.9rem;line-height:1.6}}
.why-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem}}
.why-item{{text-align:center;padding:1.5rem}}
.why-icon{{width:60px;height:60px;background:linear-gradient(135deg,var(--primary),var(--accent));border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.5rem;margin:0 auto 1rem}}
.why-item h3{{font-weight:700;margin-bottom:.5rem}}
.why-item p{{color:#64748b;font-size:.9rem}}
.reviews-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem}}
.review{{background:#fff;padding:2rem;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,.06)}}
.stars{{color:#f59e0b;margin-bottom:.8rem}}
.review p{{color:#475569;font-style:italic;line-height:1.7;margin-bottom:1rem}}
.review-author{{font-weight:700;color:var(--dark)}}
.cta-section{{background:linear-gradient(135deg,var(--primary),{accent});text-align:center;padding:5rem 2rem}}
.cta-section h2{{font-size:2.2rem;color:#fff;font-weight:800;margin-bottom:1rem}}
.cta-section p{{color:rgba(255,255,255,.85);margin-bottom:2.5rem;font-size:1.1rem}}
footer{{background:var(--dark);color:#94a3b8;padding:3rem 2rem;text-align:center}}
footer .logo{{color:#fff;font-size:1.4rem;margin-bottom:1rem;display:block}}
footer a{{color:var(--accent);text-decoration:none}}
.wa-btn{{position:fixed;bottom:2rem;right:2rem;width:60px;height:60px;background:#25D366;border-radius:50%;display:flex;align-items:center;justify-content:center;text-decoration:none;box-shadow:0 4px 20px rgba(37,211,102,.5);z-index:1000;animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{box-shadow:0 4px 20px rgba(37,211,102,.5)}}50%{{box-shadow:0 4px 40px rgba(37,211,102,.8)}}}}
.wa-btn svg{{width:32px;height:32px;fill:#fff}}
.hamburger{{display:none;flex-direction:column;gap:5px;cursor:pointer;background:none;border:none;padding:.5rem}}
.hamburger span{{width:25px;height:2px;background:var(--primary);display:block}}
@media(max-width:768px){{.stats{{grid-template-columns:repeat(3,1fr)}}.nav-links{{display:none;position:fixed;top:60px;left:0;right:0;background:#fff;flex-direction:column;padding:2rem;gap:1.5rem;border-bottom:1px solid #e2e8f0}}.nav-links.open{{display:flex}}.hamburger{{display:flex}}}}
.reveal{{opacity:0;transform:translateY(30px);transition:.6s ease}}
.reveal.visible{{opacity:1;transform:none}}
</style></head><body>
<nav>
  <span class="logo">{n}</span>
  <ul class="nav-links" id="navLinks">
    <li><a href="#xizmatlar">Xizmatlar</a></li>
    <li><a href="#nega-biz">Nega Biz?</a></li>
    <li><a href="#sharhlar">Sharhlar</a></li>
    <li><a href="#bog-lanish">Bog'lanish</a></li>
  </ul>
  <button class="hamburger" onclick="document.getElementById('navLinks').classList.toggle('open')"><span></span><span></span><span></span></button>
</nav>
<section class="hero">
  <div class="hero-content">
    <span class="tag">{niche} · Toshkent</span>
    <h1>{n}</h1>
    <p>Sifatli xizmat va professional yondashuv bilan sizning ehtiyojlaringizni qondiramiz.</p>
    <div class="hero-btns">
      <a href="{w}" class="btn">WhatsApp orqali Yozish</a>
      <a href="tel:{p}" class="btn btn-outline">📞 Qo'ng'iroq</a>
    </div>
    <div class="stats">
      <div><div class="stat-num">5+</div><div class="stat-label">Yil tajriba</div></div>
      <div><div class="stat-num">1K+</div><div class="stat-label">Mijozlar</div></div>
      <div><div class="stat-num">100%</div><div class="stat-label">Kafolat</div></div>
    </div>
  </div>
</section>
<section id="xizmatlar">
  <div class="container">
    <h2 class="section-title">Bizning <span>Xizmatlarimiz</span></h2>
    <div class="svc-grid">{svc_cards}</div>
  </div>
</section>
<section id="nega-biz" style="background:#f1f5f9">
  <div class="container">
    <h2 class="section-title">Nega <span>Bizni</span> Tanlashadi?</h2>
    <div class="why-grid">
      <div class="why-item reveal"><div class="why-icon">⚡</div><h3>Tez Xizmat</h3><p>Sizning vaqtingizni qadrlashimiz</p></div>
      <div class="why-item reveal"><div class="why-icon">✅</div><h3>Sifat Kafolati</h3><p>Har bir xizmatga kafolat beramiz</p></div>
      <div class="why-item reveal"><div class="why-icon">💰</div><h3>Qulay Narxlar</h3><p>Sifatni arzon narxda taklif qilamiz</p></div>
      <div class="why-item reveal"><div class="why-icon">🤝</div><h3>Ishonch</h3><p>1000+ mamnun mijozlarimiz bor</p></div>
    </div>
  </div>
</section>
<section id="sharhlar">
  <div class="container">
    <h2 class="section-title">Mijozlar <span>Fikri</span></h2>
    <div class="reviews-grid">
      <div class="review reveal"><div class="stars">★★★★★</div><p>"Juda yaxshi xizmat, professional munosabat. Hammaga tavsiya qilaman!"</p><span class="review-author">— Aziz T.</span></div>
      <div class="review reveal"><div class="stars">★★★★★</div><p>"Narx-navo adolatli, xizmat sifati zo'r. Mamnun qoldim!"</p><span class="review-author">— Malika R.</span></div>
      <div class="review reveal"><div class="stars">★★★★★</div><p>"Tez va sifatli. Bu yerga har doim murojaat qilaman."</p><span class="review-author">— Jahon S.</span></div>
    </div>
  </div>
</section>
<section class="cta-section" id="bog-lanish">
  <h2>Bugun Bog'laning!</h2>
  <p>📍 {a}<br>Ish vaqti: Du–Yak, 09:00 – 19:00</p>
  <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">
    <a href="{w}" class="btn">WhatsApp</a>
    <a href="tel:{p}" class="btn btn-outline">📞 {p}</a>
  </div>
</section>
<footer>
  <span class="logo">{n}</span>
  <p>📍 {a}</p>
  <p>📞 <a href="tel:{p}">{p}</a></p>
  <p style="margin-top:1rem;color:#334155">© 2025 {n}. Barcha huquqlar himoyalangan.</p>
</footer>
<a href="{w}" class="wa-btn" target="_blank"><svg viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg></a>
<script>
document.querySelectorAll('.reveal').forEach(el=>new IntersectionObserver(([e])=>{{if(e.isIntersecting)el.classList.add('visible')}},{{threshold:.2}}).observe(el))
document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',e=>{{e.preventDefault();document.querySelector(a.getAttribute('href'))?.scrollIntoView({{behavior:'smooth'}})}}))
</script></body></html>"""

GENERATORS = {
    'Restaurant': make_restaurant,
    'Fitness': make_fitness,
    'Beauty': make_beauty,
    'Auto': make_auto,
}

def generate_site(lead):
    s = lead.get('slug') or slug(lead['name'])
    out = OUTPUT_DIR / f"{s}.html"
    if out.exists():
        return False, s
    niche = lead.get('niche', '')
    fn = GENERATORS.get(niche, make_generic)
    html = fn(lead)
    out.write_text(html, encoding='utf-8')
    return True, s

def main():
    import sys
    use_real = '--real' in sys.argv

    if use_real:
        files = [ROOT / 'pipeline' / 'real_leads.json']
        print("📂 Mode: REAL leads from 2GIS")
    else:
        files = [
            ROOT / 'pipeline' / 'dental_clinic_leads.json',
            ROOT / 'pipeline' / 'new_leads_100.json',
            ROOT / 'pipeline' / 'seed_leads.json',
        ]

    leads = []
    for f in files:
        if f.exists():
            leads.extend(json.load(open(f, encoding='utf-8')))
        else:
            print(f"⚠ Not found: {f}")

    niche_filter = next((a for a in sys.argv[1:] if not a.startswith('-')), None)
    if niche_filter:
        leads = [l for l in leads if l.get('niche','').lower() == niche_filter.lower()]

    generated, skipped = 0, 0
    niches = {}
    for i, lead in enumerate(leads, 1):
        ok, s = generate_site(lead)
        niche = lead.get('niche','?')
        if ok:
            generated += 1
            niches[niche] = niches.get(niche, 0) + 1
            print(f"[{i:3d}] ✅ {lead['name']} ({niche}) → {s}.html")
        else:
            skipped += 1
            print(f"[{i:3d}] ⏭  Skip: {s}.html")

    print(f"\n{'='*50}")
    print(f"✅ Generated: {generated}  ⏭ Skipped: {skipped}  Total: {len(leads)}")
    print(f"\nNiches generated:")
    for niche, count in sorted(niches.items()):
        print(f"  {niche}: {count}")
    print(f"\n🌐 Sites at: {OUTPUT_DIR}/")

if __name__ == '__main__':
    main()
