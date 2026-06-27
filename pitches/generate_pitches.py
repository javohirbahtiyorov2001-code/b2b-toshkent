#!/usr/bin/env python3
"""Generate personalized sales pitches (RU + UZ) for all 50 leads."""
import json, pathlib, textwrap

ROOT = pathlib.Path(__file__).parent.parent

# ── Niche-specific pitch templates ─────────────────────────────────────────
# Each entry: pain_ru, pain_uz, benefit_ru, benefit_uz, proof_ru, proof_uz, cta_ru, cta_uz

NICHE = {
"Restaurant": {
    "pain_ru": "Большинство клиентов ищут кафе и рестораны через телефон — но вас не найти в Google.",
    "pain_uz": "Ko'pchilik mijozlar telefondan restoran qidiradi — lekin Google'da siz yo'qsiz.",
    "benefit_ru": "Ваш сайт покажет меню, акции и фото зала — клиент решит прийти ещё до входа.",
    "benefit_uz": "Saytingiz menyu, aksiyalar va zal rasmlarini ko'rsatadi — mijoz kirmasdan oldin kelishga qaror qiladi.",
    "proof_ru": "Рестораны с сайтом получают на 40% больше бронирований через WhatsApp.",
    "proof_uz": "Saytli restoranlar WhatsApp orqali 40% ko'proq bron oladi.",
    "usp_ru": "Онлайн-меню с ценами, форма бронирования стола, Google-карта входа.",
    "usp_uz": "Narxli online menyu, stol band qilish formasi, kirish uchun Google xarita.",
},
"Clinic": {
    "pain_ru": "Пациенты не могут найти ваш номер — звонят конкурентам.",
    "pain_uz": "Bemorlar raqamingizni topa olmaydi — raqiblarga qo'ng'iroq qilishadi.",
    "benefit_ru": "Сайт показывает врачей, услуги и цены — пациент записывается онлайн.",
    "benefit_uz": "Sayt shifokorlar, xizmatlar va narxlarni ko'rsatadi — bemor onlayn yoziladi.",
    "proof_ru": "Клиники с сайтом получают на 60% больше первичных обращений.",
    "proof_uz": "Saytli klinikalar 60% ko'proq birlamchi murojaat oladi.",
    "usp_ru": "Список врачей с фото, прайс-лист, онлайн-запись, адрес и режим работы.",
    "usp_uz": "Rasmli shifokorlar ro'yxati, narxlar, onlayn yozilish, manzil va ish vaqti.",
},
"Construction": {
    "pain_ru": "Заказчики ищут строителей в Instagram — но там нет ни портфолио, ни доверия.",
    "pain_uz": "Buyurtmachilar Instagram'da quruvchi qidiradi — lekin u yerda portfolio ham, ishonch ham yo'q.",
    "benefit_ru": "Сайт с портфолио объектов, командой и отзывами — закрывает сделки до звонка.",
    "benefit_uz": "Ob'ektlar portfoliosi, jamoa va sharhlar bilan sayt — qo'ng'iroqdan oldin bitimni yopadi.",
    "proof_ru": "Строительные компании с сайтом берут заказы на 2-3× дороже.",
    "proof_uz": "Saytli qurilish kompaniyalari buyurtmalarni 2-3× qimmatroq oladi.",
    "usp_ru": "Галерея объектов, перечень услуг, калькулятор стоимости, форма заявки.",
    "usp_uz": "Ob'ektlar galereyasi, xizmatlar ro'yxati, narx kalkulyatori, ariza formasi.",
},
"Auto Service": {
    "pain_ru": "Клиенты выбирают автосервис по рекомендациям — но вас никто не может передать по ссылке.",
    "pain_uz": "Mijozlar avtosервисni tavsiya bo'yicha tanlaydi — lekin sizni havola orqali uzatib bo'lmaydi.",
    "benefit_ru": "Сайт с услугами, ценами и отзывами — клиент доверяет и едет к вам.",
    "benefit_uz": "Xizmatlar, narxlar va sharhlar bilan sayt — mijoz ishonadi va sizga keladi.",
    "proof_ru": "Автосервисы с сайтом получают на 35% больше постоянных клиентов.",
    "proof_uz": "Saytli avtoservicelar 35% ko'proq doimiy mijoz oladi.",
    "usp_ru": "Прайс по маркам авто, онлайн-запись, фото мастеров, форма обратного звонка.",
    "usp_uz": "Avto markalari bo'yicha narxlar, onlayn yozilish, ustalar rasmi, qayta qo'ng'iroq formasi.",
},
"Dentistry": {
    "pain_ru": "Люди боятся стоматологов — но сайт с командой и фото кабинета снимает страх.",
    "pain_uz": "Odamlar stomatologdan qo'rqadi — lekin jamoa va kabinet rasmlari bilan sayt qo'rquvni yo'qotadi.",
    "benefit_ru": "Пациент видит врача, оборудование и отзывы — записывается без тревоги.",
    "benefit_uz": "Bemor shifokor, uskunalar va sharhlarni ko'radi — tashvishsiz yoziladi.",
    "proof_ru": "Стоматологии с сайтом на 70% меньше теряют пациентов из-за страха.",
    "proof_uz": "Saytli stomatologiyalar qo'rquv sababli 70% kamroq bemor yo'qotadi.",
    "usp_ru": "Портфолио работ «до/после», запись онлайн, видео о клинике, сертификаты.",
    "usp_uz": "'Oldin/keyin' ishlari portfoliosi, onlayn yozilish, klinika haqida video, sertifikatlar.",
},
"Logistics": {
    "pain_ru": "Корпоративные клиенты не работают без официального сайта — они просто уходят.",
    "pain_uz": "Korporativ mijozlar rasmiy saytisiz ishlamaydi — ular shunchaki ketishadi.",
    "benefit_ru": "Сайт с тарифами, маршрутами и формой заявки привлекает B2B-клиентов.",
    "benefit_uz": "Tariflar, yo'nalishlar va ariza formasi bilan sayt B2B mijozlarni jalb qiladi.",
    "proof_ru": "Логисты с сайтом заключают контракты с корпоративными клиентами в 3× чаще.",
    "proof_uz": "Saytli logistlar korporativ mijozlar bilan 3× tez-tez shartnoma tuzadi.",
    "usp_ru": "Калькулятор доставки, карта маршрутов, форма заявки, корпоративный раздел.",
    "usp_uz": "Yetkazib berish kalkulyatori, yo'nalishlar xaritasi, ariza formasi, korporativ bo'lim.",
},
"Education": {
    "pain_ru": "Родители выбирают курсы по сарафанному радио — но сайт охватывает весь город.",
    "pain_uz": "Ota-onalar kurslarni og'izdan og'izga tanlab oladi — lekin sayt butun shaharni qamrab oladi.",
    "benefit_ru": "Сайт с программой, преподавателями и результатами выпускников — конверсия растёт.",
    "benefit_uz": "Dastur, o'qituvchilar va bitiruvchilar natijalari bilan sayt — konversiya o'sadi.",
    "proof_ru": "Учебные центры с сайтом набирают группы на 50% быстрее.",
    "proof_uz": "Saytli o'quv markazlari guruhlarni 50% tezroq to'ldiradi.",
    "usp_ru": "Расписание курсов, онлайн-запись на пробный урок, видео-отзывы, сертификаты.",
    "usp_uz": "Kurslar jadvali, sinov darsiga onlayn yozilish, video sharhlar, sertifikatlar.",
},
"Hotel": {
    "pain_ru": "Гости бронируют через OTA и платят 20% комиссии — сайт даёт прямые бронирования.",
    "pain_uz": "Mehmonlar OTA orqali band qiladi va 20% komissiya to'laydi — sayt to'g'ridan-to'g'ri bron beradi.",
    "benefit_ru": "Сайт с номерами, ценами и онлайн-бронью экономит до 20% комиссии.",
    "benefit_uz": "Xonalar, narxlar va onlayn bron bilan sayt 20% gacha komissiyani tejaydi.",
    "proof_ru": "Отели с сайтом получают 30% бронирований напрямую — без комиссии.",
    "proof_uz": "Saytli mehmonxonalar bronlarning 30%ini to'g'ridan-to'g'ri — komissiyasiz oladi.",
    "usp_ru": "Фото номеров, онлайн-бронирование, галерея, карта, форма вопросов.",
    "usp_uz": "Xonalar rasmlari, onlayn bron, galereya, xarita, savol formasi.",
},
"Fitness": {
    "pain_ru": "Потенциальные клиенты смотрят зал в Instagram — но не знают цену и не записываются.",
    "pain_uz": "Potensial mijozlar zalga Instagram'da qarashadi — lekin narxni bilishmaydi va yozilishmaydi.",
    "benefit_ru": "Сайт с ценами, расписанием и пробным занятием — конвертирует подписчиков в клиентов.",
    "benefit_uz": "Narxlar, jadval va sinov dars bilan sayt — obunachilari mijozlarga aylantiradi.",
    "proof_ru": "Фитнес-центры с сайтом продают абонементы в 2× быстрее.",
    "proof_uz": "Saytli fitness markazlar abonementlarni 2× tezroq sotadi.",
    "usp_ru": "Расписание тренировок, тарифы, онлайн-запись на пробное, тренеры, фото зала.",
    "usp_uz": "Mashg'ulotlar jadvali, tariflar, sinov uchun onlayn yozilish, trenerlar, zal rasmlari.",
},
"Retail": {
    "pain_ru": "Покупатели хотят узнать наличие товара онлайн — а не ехать и проверять.",
    "pain_uz": "Xaridorlar tovar mavjudligini onlayn bilishni xohlaydi — borib tekshirishni emas.",
    "benefit_ru": "Сайт-витрина с каталогом и ценами — клиент приходит уже готовый купить.",
    "benefit_uz": "Katalog va narxlar bilan vitrina-sayt — mijoz sotib olishga tayyor holda keladi.",
    "proof_ru": "Магазины с сайтом увеличивают средний чек на 25%.",
    "proof_uz": "Saytli do'konlar o'rtacha chekni 25% oshiradi.",
    "usp_ru": "Каталог с ценами, фото товаров, карта магазина, WhatsApp-заказ.",
    "usp_uz": "Narxli katalog, tovar rasmlari, do'kon xaritasi, WhatsApp buyurtma.",
},
"Real Estate": {
    "pain_ru": "Покупатели объектов требуют официальный сайт — без него сделки срываются.",
    "pain_uz": "Ob'ekt xaridorlari rasmiy sayt talab qiladi — unisiz bitimlar buziladi.",
    "benefit_ru": "Сайт с базой объектов, фото и ценами — клиент приходит уже выбрав.",
    "benefit_uz": "Ob'ektlar bazasi, rasmlar va narxlar bilan sayt — mijoz allaqachon tanlab keladi.",
    "proof_ru": "Агентства с сайтом закрывают сделки на 45% быстрее.",
    "proof_uz": "Saytli agentliklar bitimlarni 45% tezroq yopadi.",
    "usp_ru": "База объектов с фильтрами, 3D-туры, калькулятор ипотеки, форма заявки.",
    "usp_uz": "Filtrli ob'ektlar bazasi, 3D-turlar, ipoteka kalkulyatori, ariza formasi.",
},
"Electronics Repair": {
    "pain_ru": "Клиенты боятся мошенников — сайт с отзывами и гарантией снимает этот страх.",
    "pain_uz": "Mijozlar firibgarlardan qo'rqadi — sharhlar va kafolat bilan sayt bu qo'rquvni yo'qotadi.",
    "benefit_ru": "Сайт с прайсом, гарантией и реальными отзывами — доверие растёт, клиентов больше.",
    "benefit_uz": "Narxlar, kafolat va haqiqiy sharhlar bilan sayt — ishonch o'sadi, mijozlar ko'payadi.",
    "proof_ru": "Сервисные мастерские с сайтом берут на 30% больше заказов.",
    "proof_uz": "Saytli ta'mirlash ustaxonalari 30% ko'proq buyurtma oladi.",
    "usp_ru": "Прайс по устройствам, статус ремонта онлайн, гарантия, реальные фото работ.",
    "usp_uz": "Qurilmalar bo'yicha narxlar, ta'mirlash holati onlayn, kafolat, haqiqiy ish rasmlari.",
},
"Furniture": {
    "pain_ru": "Покупатели мебели часами едут по магазинам — сайт экономит их время и ваши ресурсы.",
    "pain_uz": "Mebel xaridorlari do'konlarga soatlab boradi — sayt vaqtlarini va resurslaringizni tejaydi.",
    "benefit_ru": "Каталог с 3D-фото и ценами — клиент приходит с конкретным выбором.",
    "benefit_uz": "3D rasmlari va narxlar bilan katalog — mijoz aniq tanlov bilan keladi.",
    "proof_ru": "Мебельные магазины с сайтом увеличивают выручку на 40%.",
    "proof_uz": "Saytli mebel do'konlari tushumni 40% oshiradi.",
    "usp_ru": "3D-каталог, конфигуратор цвета/размера, расчёт доставки, портфолио интерьеров.",
    "usp_uz": "3D-katalog, rang/o'lcham konfiguratoru, yetkazib berish hisobi, interer portfoliosi.",
},
"Printing": {
    "pain_ru": "Корпоративные заказчики хотят скачать макеты и оформить заказ онлайн — без поездки.",
    "pain_uz": "Korporativ buyurtmachilar maketlarni yuklab olishni va onlayn buyurtma berishni xohlaydi.",
    "benefit_ru": "Сайт с онлайн-калькулятором и загрузкой макетов — автоматизирует продажи.",
    "benefit_uz": "Onlayn kalkulyator va maket yuklash bilan sayt — sotuvlarni avtomatlashtiradi.",
    "proof_ru": "Типографии с сайтом обрабатывают заказы в 3× быстрее.",
    "proof_uz": "Saytli bosmaxonalar buyurtmalarni 3× tezroq qayta ishlaydi.",
    "usp_ru": "Онлайн-калькулятор тиража, загрузка макета, каталог продукции, корпоративный раздел.",
    "usp_uz": "Tiraj onlayn kalkulyatori, maket yuklash, mahsulot katalogu, korporativ bo'lim.",
},
"Bakery": {
    "pain_ru": "Торты на заказ — но клиент не знает ваши цены и портфолио до звонка.",
    "pain_uz": "Buyurtmaga tortlar — lekin mijoz qo'ng'iroqqa qadar narxlaringizni va portfoliongizni bilmaydi.",
    "benefit_ru": "Сайт с галереей тортов, ценами и формой заказа — продажи без звонков.",
    "benefit_uz": "Tortlar galereyasi, narxlar va buyurtma formasi bilan sayt — qo'ng'iroqsiz sotuvlar.",
    "proof_ru": "Кондитерские с сайтом получают в 2× больше заказов на торты.",
    "proof_uz": "Saytli qandolatxonalar 2× ko'proq tort buyurtmasi oladi.",
    "usp_ru": "Галерея работ, калькулятор торта по весу, форма заказа, отзывы с фото.",
    "usp_uz": "Ishlar galereyasi, og'irlik bo'yicha tort kalkulyatori, buyurtma formasi, rasmlі sharhlar.",
},
"Landscaping": {
    "pain_ru": "Владельцы дач и офисов не знают, кому доверить озеленение — портфолио решает это.",
    "pain_uz": "Dachalar va ofislar egalari yashillashtirish ishonib topshirish bilmaydi — portfolio bu muammoni hal qiladi.",
    "benefit_ru": "Сайт с фото объектов до/после и ценами — клиент звонит уже убеждённый.",
    "benefit_uz": "Oldin/keyin ob'ekt rasmlari va narxlar bilan sayt — mijoz allaqachon ishongan holda qo'ng'iroq qiladi.",
    "proof_ru": "Ландшафтные компании с сайтом берут заказы дороже на 50%.",
    "proof_uz": "Saytli landshaft kompaniyalari buyurtmalarni 50% qimmatroq oladi.",
    "usp_ru": "Портфолио объектов, каталог растений, форма заявки, сезонные акции.",
    "usp_uz": "Ob'ektlar portfoliosi, o'simliklar katalogu, ariza formasi, mavsum aksiyalari.",
},
"Wholesale": {
    "pain_ru": "Оптовые партнёры требуют прайс-лист — без сайта вы не выглядите серьёзно.",
    "pain_uz": "Ulgurji hamkorlar narxlar ro'yxatini talab qiladi — saytisiz siz jiddiy ko'rinmaysiz.",
    "benefit_ru": "Сайт с каталогом оптовых цен и формой заявки — привлекает крупных партнёров.",
    "benefit_uz": "Ulgurji narxlar katalogi va ariza formasi bilan sayt — yirik hamkorlarni jalb qiladi.",
    "proof_ru": "Оптовые компании с сайтом привлекают партнёров в 4× быстрее.",
    "proof_uz": "Saytli ulgurji kompaniyalar hamkorlarni 4× tezroq jalb qiladi.",
    "usp_ru": "Каталог с оптовыми ценами, условия сотрудничества, форма партнёра, документы.",
    "usp_uz": "Ulgurji narxlар katalogu, hamkorlik shartlari, hamkor formasi, hujjatlar.",
},
"Kindergarten": {
    "pain_ru": "Родители выбирают детсад по фото и отзывам — без сайта они идут к конкуренту.",
    "pain_uz": "Ota-onalar bog'chani rasmlar va sharhlarga qarab tanlaydi — saytisiz ular raqibga boradi.",
    "benefit_ru": "Сайт с фото воспитателей, программой и видео — родители записываются онлайн.",
    "benefit_uz": "Tarbiyachilar rasmlari, dastur va video bilan sayt — ota-onalar onlayn yoziladi.",
    "proof_ru": "Детские сады с сайтом заполняют места на 60% быстрее.",
    "proof_uz": "Saytli bog'chalar o'rinlarni 60% tezroq to'ldiradi.",
    "usp_ru": "Команда воспитателей, программа, фотогалерея, онлайн-запись, отзывы родителей.",
    "usp_uz": "Tarbiyachilar jamoasi, dastur, fotogalereya, onlayn yozilish, ota-onalar sharhlari.",
},
"Laundry": {
    "pain_ru": "Клиенты сравнивают цены и удобство — сайт с онлайн-заказом выигрывает этот выбор.",
    "pain_uz": "Mijozlar narxlar va qulaylikni solishtiради — onlayn buyurtma bilan sayt bu tanlovda g'alaba qiladi.",
    "benefit_ru": "Сайт с прайсом, онлайн-заказом и доставкой — клиент выбирает вас, не выходя из дома.",
    "benefit_uz": "Narxlar, onlayn buyurtma va yetkazib berish bilan sayt — mijoz uydan chiqmay sizni tanlaydi.",
    "proof_ru": "Химчистки с сайтом увеличивают заказы на 45%.",
    "proof_uz": "Saytli kimyoviy tozalashlar buyurtmalarni 45% oshiradi.",
    "usp_ru": "Онлайн-заказ с доставкой, прайс по типу ткани, статус заказа, акции.",
    "usp_uz": "Yetkazib berishli onlayn buyurtma, mato turi bo'yicha narxlar, buyurtma holati, aksiyalar.",
},
"Event Hall": {
    "pain_ru": "Пары выбирают зал по фото в Instagram — но бронируют только тех, у кого есть сайт.",
    "pain_uz": "Juftliklar zalga Instagram rasmlariga qarab tanlaydi — lekin faqat saytlilarni band qiladi.",
    "benefit_ru": "Сайт с галереей залов, ценами и онлайн-бронью закрывает даты на месяц вперёд.",
    "benefit_uz": "Zallar galereyasi, narxlar va onlayn bron bilan sayt sanalarni bir oy oldin band qiladi.",
    "proof_ru": "Той-залы с сайтом бронируют даты на 80% заполнением уже в начале года.",
    "proof_uz": "Saytli to'y zallari sanalarni yil boshidayoq 80% band qiladi.",
    "usp_ru": "Галерея залов, ценовые пакеты, онлайн-бронь дат, отзывы пар, видео торжеств.",
    "usp_uz": "Zallar galereyasi, narx paketlari, sanalar onlayn bron, juftliklar sharhlari, tantanalar videosi.",
},
"Electrical": {
    "pain_ru": "Клиенты не доверяют электрику без рекомендации — сайт с сертификатами меняет это.",
    "pain_uz": "Mijozlar tavsiyasiz elektrikka ishonmaydi — sertifikatlar bilan sayt buni o'zgartiradi.",
    "benefit_ru": "Сайт с лицензиями, выполненными работами и ценами — клиент звонит уверенно.",
    "benefit_uz": "Litsenziyalar, bajarilgan ishlar va narxlar bilan sayt — mijoz ishonch bilan qo'ng'iroq qiladi.",
    "proof_ru": "Электро-монтажные компании с сайтом берут заказы дороже на 35%.",
    "proof_uz": "Saytli elektr montaj kompaniyalari buyurtmalarni 35% qimmatroq oladi.",
    "usp_ru": "Портфолио объектов, сертификаты и лицензии, прайс по работам, форма вызова.",
    "usp_uz": "Ob'ektlar portfoliosi, sertifikat va litsenziyalar, ishlar bo'yicha narxlar, chaqiruv formasi.",
},
"Pharmacy": {
    "pain_ru": "Пациенты ищут наличие лекарств онлайн — без сайта они едут к конкуренту.",
    "pain_uz": "Bemorlar dori mavjudligini onlayn qidiradi — saytisiz ular raqibga boradi.",
    "benefit_ru": "Сайт с каталогом препаратов, адресом и режимом работы — клиент идёт к вам.",
    "benefit_uz": "Dorilar katalogu, manzil va ish vaqti bilan sayt — mijoz sizga keladi.",
    "proof_ru": "Аптеки с сайтом увеличивают посещаемость на 30%.",
    "proof_uz": "Saytli dorixonalar tashrif buyuruvchilikni 30% oshiradi.",
    "usp_ru": "Поиск препаратов, каталог с ценами, адрес на карте, онлайн-запрос наличия.",
    "usp_uz": "Dori qidirish, narxli katalog, xaritada manzil, mavjudligi haqida onlayn so'rov.",
},
"Beauty": {
    "pain_ru": "Клиентки выбирают мастера по Instagram — но записываются через сайт.",
    "pain_uz": "Mijoz ayollar ustani Instagram'da tanlaydi — lekin sayt orqali yoziladi.",
    "benefit_ru": "Сайт с портфолио, прайсом и онлайн-записью — загрузка мастеров растёт.",
    "benefit_uz": "Portfolio, narxlar va onlayn yozilish bilan sayt — ustalar band bo'lishi o'sadi.",
    "proof_ru": "Салоны красоты с сайтом заполняют расписание на 2 недели вперёд.",
    "proof_uz": "Saytli go'zallik salonlari jadvalni 2 hafta oldin to'ldiradi.",
    "usp_ru": "Портфолио работ, онлайн-запись, прайс по услугам, команда мастеров, акции.",
    "usp_uz": "Ishlar portfoliosi, onlayn yozilish, xizmatlar narxi, ustalar jamoasi, aksiyalar.",
},
"Travel": {
    "pain_ru": "Туристы сравнивают туры онлайн — без сайта вас просто нет в их выборе.",
    "pain_uz": "Sayyohlar turlarni onlayn solishtiradi — saytisiz siz ularnng tanlovida yo'qsiz.",
    "benefit_ru": "Сайт с турами, ценами и онлайн-оплатой — продажи идут даже ночью.",
    "benefit_uz": "Turlar, narxlar va onlayn to'lov bilan sayt — kechasi ham sotuvlar boradi.",
    "proof_ru": "Туристические агентства с сайтом увеличивают продажи туров в 3× раз.",
    "proof_uz": "Saytli turizm agentliklari tur sotuvlarini 3× oshiradi.",
    "usp_ru": "Каталог туров с ценами, онлайн-заявка, визовые услуги, отзывы туристов.",
    "usp_uz": "Narxli turlar katalogu, onlayn ariza, viza xizmatlari, sayyohlar sharhlari.",
},
"Auto Glass": {
    "pain_ru": "Водители ищут авто-стекольщиков срочно — сайт с адресом и телефоном находят первым.",
    "pain_uz": "Haydovchilar shoshilinch avto-shishachi qidiradi — manzil va telefon bilan sayt birinchi topiladi.",
    "benefit_ru": "Сайт с прайсом по маркам авто и онлайн-записью — клиент едет к вам сразу.",
    "benefit_uz": "Avto markalari bo'yicha narxlar va onlayn yozilish bilan sayt — mijoz darhol sizga keladi.",
    "proof_ru": "Авто-стекольщики с сайтом получают на 40% больше экстренных вызовов.",
    "proof_uz": "Saytli avto-shishachi ustalar 40% ko'proq shoshilinch chaqiruv oladi.",
    "usp_ru": "Прайс по маркам, выезд на место, онлайн-запись, гарантия на стекло.",
    "usp_uz": "Markalar bo'yicha narxlar, joyga chiqish, onlayn yozilish, shishaga kafolat.",
},
"Bridal": {
    "pain_ru": "Невесты планируют свадьбу за полгода — сайт с портфолио захватывает их в начале пути.",
    "pain_uz": "Kelinlar to'yni yarim yil oldin rejalashtiradi — portfolio bilan sayt ularni yo'lning boshida ushlaydi.",
    "benefit_ru": "Сайт с коллекцией платьев, ценами и онлайн-примеркой — бронирования растут.",
    "benefit_uz": "Ko'ylaklar kolleksiyasi, narxlar va onlayn kiyib ko'rish bilan sayt — bronlar o'sadi.",
    "proof_ru": "Свадебные салоны с сайтом бронируются на 3 месяца вперёд.",
    "proof_uz": "Saytli kelin salonlari 3 oy oldin band bo'ladi.",
    "usp_ru": "Коллекция платьев, онлайн-запись на примерку, пакеты услуг, отзывы невест.",
    "usp_uz": "Ko'ylaklar kolleksiyasi, kiyib ko'rishga onlayn yozilish, xizmat paketlari, kelinlar sharhlari.",
},
"Metalwork": {
    "pain_ru": "Корпоративные заказчики ищут металлообработку с сертификатами — без сайта вы не в игре.",
    "pain_uz": "Korporativ buyurtmachilar sertifikatlі metallni qayta ishlashni qidiradi — saytisiz siz o'yinda yo'qsiz.",
    "benefit_ru": "Сайт с портфолио изделий, характеристиками и формой заявки — B2B-продажи растут.",
    "benefit_uz": "Buyumlar portfoliosi, xarakteristikalar va ariza formasi bilan sayt — B2B sotuvlar o'sadi.",
    "proof_ru": "Металлообрабатывающие предприятия с сайтом получают заказы дороже на 60%.",
    "proof_uz": "Saytli metallni qayta ishlash korxonalari buyurtmalarni 60% qimmatroq oladi.",
    "usp_ru": "Портфолио изделий, технические характеристики, форма заявки, сроки изготовления.",
    "usp_uz": "Buyumlar portfoliosi, texnik xarakteristikalar, ariza formasi, ishlab chiqarish muddatlari.",
},
"Gas Station": {
    "pain_ru": "Водители заправляются там, где знают цены заранее — сайт с тарифами привлекает постоянных клиентов.",
    "pain_uz": "Haydovchilar oldindan narxlarni biladigan joyga yoqilg'i to'ldiradi — tariflar bilan sayt doimiy mijozlarni jalb qiladi.",
    "benefit_ru": "Сайт с актуальными ценами, картой проезда и акциями — трафик растёт.",
    "benefit_uz": "Joriy narxlar, yo'l xaritasi va aksiyalar bilan sayt — trafik o'sadi.",
    "proof_ru": "АЗС с сайтом увеличивают трафик на 20% за счёт лояльных клиентов.",
    "proof_uz": "Saytli benzin quyish stansiyalari sadoqatli mijozlar hisobiga trafini 20% oshiradi.",
    "usp_ru": "Актуальные цены на топливо, карта АЗС, программа лояльности, акции дня.",
    "usp_uz": "Joriy yoqilg'i narxlari, BQS xaritasi, sadoqat dasturi, kun aksiyalari.",
},
"Accounting": {
    "pain_ru": "Бизнес ищет бухгалтера в поисковике — без сайта вас просто не видят.",
    "pain_uz": "Biznes qidiruv tizimida buxgalter qidiradi — saytisiz sizi ko'rishmaydi.",
    "benefit_ru": "Сайт с услугами, ценами и отзывами клиентов — входящие заявки растут.",
    "benefit_uz": "Xizmatlar, narxlar va mijozlar sharhlari bilan sayt — kiruvchi arizalar o'sadi.",
    "proof_ru": "Бухгалтерские компании с сайтом привлекают на 55% больше клиентов из поиска.",
    "proof_uz": "Saytli buxgalteriya kompaniyalari qidiruvdan 55% ko'proq mijoz jalb qiladi.",
    "usp_ru": "Перечень услуг, онлайн-расчёт стоимости, отзывы клиентов, форма заявки.",
    "usp_uz": "Xizmatlar ro'yxati, narxni onlayn hisoblash, mijozlar sharhlari, ariza formasi.",
},
"IT Services": {
    "pain_ru": "IT-компании должны сами иметь сайт — иначе это выглядит странно.",
    "pain_uz": "IT kompaniyalarning o'zlari saytga ega bo'lishi kerak — aks holda bu g'alati ko'rinadi.",
    "benefit_ru": "Сайт с кейсами, командой и услугами — привлекает корпоративных клиентов.",
    "benefit_uz": "Keyslar, jamoa va xizmatlar bilan sayt — korporativ mijozlarni jalb qiladi.",
    "proof_ru": "IT-компании с сайтом заключают корпоративные контракты в 5× раз чаще.",
    "proof_uz": "Saytli IT kompaniyalar korporativ shartnomalarni 5× tez-tez tuzadi.",
    "usp_ru": "Портфолио кейсов, команда разработчиков, прайс-лист, форма брифа, блог.",
    "usp_uz": "Keyslar portfoliosi, dasturchilar jamoasi, narxlar, bref formasi, blog.",
},
"Photography": {
    "pain_ru": "Фотографы живут в Instagram — но продают через сайт с портфолио и прайсом.",
    "pain_uz": "Fotogaraflar Instagram'da yashaydi — lekin portfolio va narxlar bilan sayt orqali sotadi.",
    "benefit_ru": "Сайт-портфолио с пакетами услуг и онлайн-бронью — календарь заполняется быстрее.",
    "benefit_uz": "Xizmat paketlari va onlayn bron bilan portfolio-sayt — kalendar tezroq to'ladi.",
    "proof_ru": "Фотографы с сайтом берут заказы дороже на 40% и полностью загружены.",
    "proof_uz": "Saytli fotogaraflar buyurtmalarni 40% qimmatroq oladi va to'liq band bo'ladi.",
    "usp_ru": "Портфолио по жанрам, пакеты съёмки, онлайн-бронь дат, отзывы клиентов.",
    "usp_uz": "Janrlar bo'yicha portfolio, suratga olish paketlari, sanalar onlayn bron, mijozlar sharhlari.",
},
"Cleaning": {
    "pain_ru": "Клиенты боятся пускать незнакомых в дом — сайт с отзывами и командой снимает этот страх.",
    "pain_uz": "Mijozlar notanishlarni uyga kiritishdan qo'rqadi — sharhlar va jamoa bilan sayt bu qo'rquvni yo'qotadi.",
    "benefit_ru": "Сайт с тарифами, командой и гарантией — клиент решается заказать.",
    "benefit_uz": "Tariflar, jamoa va kafolat bilan sayt — mijoz buyurtma berishga qaror qiladi.",
    "proof_ru": "Клининговые компании с сайтом получают на 50% больше заявок онлайн.",
    "proof_uz": "Saytli tozalash kompaniyalari onlayn 50% ko'proq ariza oladi.",
    "usp_ru": "Тарифы по типу уборки, команда с фото, онлайн-расчёт, форма заявки.",
    "usp_uz": "Tozalash turi bo'yicha tariflar, rasмli jamoa, onlayn hisob, ariza formasi.",
},
"Elevators": {
    "pain_ru": "УК и застройщики требуют официальный сайт для тендеров — без него вы вне конкурса.",
    "pain_uz": "UK va quruvchilar tenderlar uchun rasmiy sayt talab qiladi — unisiz siz tanlovdan tashqarida.",
    "benefit_ru": "Сайт с лицензиями, линейкой лифтов и кейсами — участвуйте в тендерах.",
    "benefit_uz": "Litsenziyalar, liftlar assortimenti va keyslar bilan sayt — tenderlarda ishtirok eting.",
    "proof_ru": "Лифтовые компании с сайтом выигрывают тендеры в 4× чаще.",
    "proof_uz": "Saytli lift kompaniyalari tenderlarda 4× tez-tez g'alaba qiladi.",
    "usp_ru": "Каталог лифтов, технические характеристики, лицензии, кейсы, форма запроса.",
    "usp_uz": "Liftlar katalogu, texnik xarakteristikalar, litsenziyalar, keyslar, so'rov formasi.",
},
"Flowers": {
    "pain_ru": "Цветы заказывают в последний момент онлайн — без сайта вы теряете эти продажи.",
    "pain_uz": "Gullarni so'nggi daqiqada onlayn buyurtma qilishadi — saytisiz bu sotuvlarni yo'qotasiz.",
    "benefit_ru": "Сайт с каталогом букетов, ценами и доставкой — заказы приходят 24/7.",
    "benefit_uz": "Guldastalar katalogu, narxlar va yetkazib berish bilan sayt — buyurtmalar 24/7 keladi.",
    "proof_ru": "Цветочные магазины с сайтом увеличивают онлайн-продажи в 3× раз.",
    "proof_uz": "Saytli gul do'konlari onlayn sotuvlarni 3× oshiradi.",
    "usp_ru": "Каталог с ценами, онлайн-заказ, доставка за 2 часа, персонализация букетов.",
    "usp_uz": "Narxli katalog, onlayn buyurtma, 2 soatda yetkazish, guldastalarni personalizatsiya.",
},
"Courier": {
    "pain_ru": "Интернет-магазины ищут курьерские сервисы онлайн — без сайта вы не в их списке.",
    "pain_uz": "Internet-do'konlar onlayn kuryer xizmatini qidiradi — saytisiz siz ularning ro'yxatida yo'qsiz.",
    "benefit_ru": "Сайт с тарифами, зонами доставки и формой заявки — B2B-клиенты приходят сами.",
    "benefit_uz": "Tariflar, yetkazib berish zonalari va ariza formasi bilan sayt — B2B mijozlar o'zlari keladi.",
    "proof_ru": "Курьерские службы с сайтом заключают контракты с магазинами в 3× быстрее.",
    "proof_uz": "Saytli kuryer xizmatlari do'konlar bilan shartnomalarni 3× tezroq tuzadi.",
    "usp_ru": "Тарифы по зонам, калькулятор стоимости, форма B2B-договора, трекинг статус.",
    "usp_uz": "Zonalar bo'yicha tariflar, narx kalkulyatori, B2B-shartnoma formasi, kuzatuv holati.",
},
"Funeral": {
    "pain_ru": "В трудную минуту семьи ищут информацию онлайн — сайт даёт ответы, не требуя звонка.",
    "pain_uz": "Qiyin daqiqada oilalar onlayn ma'lumot qidiradi — sayt qo'ng'iroqsiz javob beradi.",
    "benefit_ru": "Сайт с услугами, ценами и контактами — семья находит вас в нужный момент.",
    "benefit_uz": "Xizmatlar, narxlar va kontaktlar bilan sayt — oila kerakli daqiqada sizni topadi.",
    "proof_ru": "Ритуальные службы с сайтом получают на 40% больше обращений.",
    "proof_uz": "Saytli dafn xizmatlari 40% ko'proq murojaat oladi.",
    "usp_ru": "Перечень услуг, прайс-лист, контакты 24/7, карта, форма обратного звонка.",
    "usp_uz": "Xizmatlar ro'yxati, narxlar, 24/7 kontaktlar, xarita, qayta qo'ng'iroq formasi.",
},
"Building Materials": {
    "pain_ru": "Строители ищут поставщиков онлайн — без сайта вы теряете их ещё на этапе поиска.",
    "pain_uz": "Quruvchilar onlayn yetkazib beruvchi qidiradi — saytisiz ularni qidiruv bosqichdayoq yo'qotasiz.",
    "benefit_ru": "Сайт с каталогом материалов и оптовыми ценами — строители выбирают вас.",
    "benefit_uz": "Materiallar katalogu va ulgurji narxlar bilan sayt — quruvchilar sizni tanlaydi.",
    "proof_ru": "Поставщики стройматериалов с сайтом увеличивают оборот на 35%.",
    "proof_uz": "Saytli qurilish materiallari yetkazib beruvchilar aylanmani 35% oshiradi.",
    "usp_ru": "Каталог с ценами, опт от объёма, форма заявки, доставка на объект.",
    "usp_uz": "Narxli katalog, hajm bo'yicha ulgurji, ariza formasi, ob'ektga yetkazish.",
},
"HVAC": {
    "pain_ru": "Клиенты выбирают кондиционер летом срочно — сайт с наличием и ценой решает вопрос за минуту.",
    "pain_uz": "Mijozlar yozda shoshilinch konditsioner tanlaydi — mavjudlik va narx bilan sayt masalani bir daqiqada hal qiladi.",
    "benefit_ru": "Сайт с каталогом, монтажными ценами и онлайн-заявкой — заказы идут 24/7.",
    "benefit_uz": "Katalog, o'rnatish narxlari va onlayn ariza bilan sayt — buyurtmalar 24/7 keladi.",
    "proof_ru": "HVAC-компании с сайтом увеличивают продажи кондиционеров на 45% в сезон.",
    "proof_uz": "Saytli HVAC kompaniyalar mavsumda konditsioner sotuvlarini 45% oshiradi.",
    "usp_ru": "Каталог техники, монтаж под ключ, сезонные акции, форма заявки, гарантия.",
    "usp_uz": "Texnika katalogu, kalit ostida montaj, mavsum aksiyalari, ariza formasi, kafolat.",
},
"Logistics": {
    "pain_ru": "Корпоративные клиенты не работают без официального сайта — они просто уходят.",
    "pain_uz": "Korporativ mijozlar rasmiy saytisiz ishlamaydi — ular shunchaki ketishadi.",
    "benefit_ru": "Сайт с тарифами, маршрутами и формой заявки привлекает B2B-клиентов.",
    "benefit_uz": "Tariflar, yo'nalishlar va ariza formasi bilan sayt B2B mijozlarni jalb qiladi.",
    "proof_ru": "Логисты с сайтом заключают контракты с корпоративными клиентами в 3× чаще.",
    "proof_uz": "Saytli logistlar korporativ mijozlar bilan 3× tez-tez shartnoma tuzadi.",
    "usp_ru": "Калькулятор доставки, карта маршрутов, форма заявки, корпоративный раздел.",
    "usp_uz": "Yetkazib berish kalkulyatori, yo'nalishlar xaritasi, ariza formasi, korporativ bo'lim.",
},
"Auto Sales": {
    "pain_ru": "Покупатели авто просматривают десятки сайтов перед визитом — вас там нет.",
    "pain_uz": "Avto xaridorlari tashrif oldidan o'nlab saytni ko'rib chiqadi — siz u yerda yo'qsiz.",
    "benefit_ru": "Сайт с каталогом авто, ценами и онлайн-заявкой на тест-драйв — трафик в салон растёт.",
    "benefit_uz": "Avto katalogu, narxlar va test-drayvga onlayn ariza bilan sayt — salonga trafik o'sadi.",
    "proof_ru": "Автосалоны с сайтом получают в 4× больше запросов на тест-драйв.",
    "proof_uz": "Saytli avtosalonlar test-drayvga 4× ko'proq so'rov oladi.",
    "usp_ru": "Каталог авто с фото, онлайн-заявка на тест-драйв, калькулятор рассрочки, сравнение.",
    "usp_uz": "Rasmli avto katalogu, test-drayvga onlayn ariza, bo'lib to'lash kalkulyatori, solishtirish.",
},
}

def get_niche_data(niche: str) -> dict:
    # Fallback for any niche not in dict
    return NICHE.get(niche, NICHE.get("Retail", {}))

def make_pitch(lead: dict) -> dict:
    n = get_niche_data(lead["niche"])
    name = lead["name"]
    phone = lead["phone"]
    wa = phone.replace("+", "").replace(" ", "")
    slug = lead["slug"]

    # ── Russian pitch
    ru_whatsapp = f"""Здравствуйте! 👋

Я представляю веб-студию в Ташкенте. Я заметил, что у *{name}* пока нет сайта — и это упущенная прибыль каждый день.

🔍 *Проблема:* {n.get('pain_ru','')}

💡 *Решение:* {n.get('benefit_ru','')}

✅ *Что получите:*
{n.get('usp_ru','')}

📊 *Факт:* {n.get('proof_ru','')}

🎁 Мы уже подготовили *демо-сайт* специально для {name} — вы можете посмотреть прямо сейчас по ссылке:
🔗 https://your-domain.netlify.app/{slug}

💰 Стоимость: от *5 000 000 сум* (разово). Запуск за 3 дня.

Удобно поговорить сегодня? 📞"""

    ru_call = f"""Добрый день! Меня зовут [Имя], я из веб-студии в Ташкенте.

Звоню по поводу {name} — вижу, что у вас пока нет сайта. {n.get('pain_ru','')}

Мы уже подготовили демо-сайт именно для вашего бизнеса. Если вам удобно, я могу прислать ссылку прямо сейчас в WhatsApp — посмотрите сами, как это выглядит. Это займёт 2 минуты.

{n.get('benefit_ru','')} {n.get('proof_ru','')}

Когда вам удобно встретиться на 15 минут?"""

    ru_formal = f"""Уважаемое руководство {name}!

Компания WebStudio Tashkent предлагает профессиональный веб-сайт для вашего бизнеса.

{n.get('pain_ru','')} {n.get('benefit_ru','')}

Что включает сайт:
{n.get('usp_ru','')}

{n.get('proof_ru','')}

Специально для вас мы разработали демонстрационную версию сайта, которую вы можете оценить по ссылке.

Стоимость: от 5 000 000 сум. Запуск: 3 рабочих дня. Гарантия: 1 год поддержки.

С уважением,
WebStudio Tashkent
+998 90 000 00 00"""

    # ── Uzbek pitch
    uz_whatsapp = f"""Assalomu alaykum! 👋

Men Toshkentdagi veb-studiyani vakiliman. Men *{name}* da hali sayt yo'qligini ko'rdim — bu har kuni yo'qolayotgan foyda.

🔍 *Muammo:* {n.get('pain_uz','')}

💡 *Yechim:* {n.get('benefit_uz','')}

✅ *Nima olasiz:*
{n.get('usp_uz','')}

📊 *Fakt:* {n.get('proof_uz','')}

🎁 Biz {name} uchun maxsus *demo-sayt* tayyorladik — hoziroq havoladan ko'rishingiz mumkin:
🔗 https://your-domain.netlify.app/{slug}

💰 Narx: *5 000 000 so'mdan* (bir martalik). Ishga tushirish: 3 kun.

Bugun gaplashishga qulayми? 📞"""

    uz_call = f"""Assalomu alaykum! Ismim [Ism], Toshkentdagi veb-studiyadan qo'ng'iroq qilyapman.

{name} haqida qo'ng'iroq qilyapman — sizda hali sayt yo'qligini ko'rdim. {n.get('pain_uz','')}

Biz sizning biznesingiz uchun maxsus demo-sayt tayyorladik. Agar qulay bo'lsa, havolani hoziroq WhatsApp'ga jo'nataman — o'zingiz ko'rasiz, bu qanday ko'rinishda. Bu 2 daqiqa oladi.

{n.get('benefit_uz','')} {n.get('proof_uz','')}

15 daqiqaga uchrashish uchun qachon qulay?"""

    uz_formal = f"""Hurmatli {name} rahbariyati!

WebStudio Tashkent kompaniyasi sizning biznesingiz uchun professional veb-sayt taklif qiladi.

{n.get('pain_uz','')} {n.get('benefit_uz','')}

Saytga nima kiradi:
{n.get('usp_uz','')}

{n.get('proof_uz','')}

Siz uchun maxsus demo-versiyasini ishlab chiqdik, uni havola orqali baholashingiz mumkin.

Narx: 5 000 000 so'mdan. Ishga tushirish: 3 ish kuni. Kafolat: 1 yil qo'llab-quvvatlash.

Hurmat bilan,
WebStudio Tashkent
+998 90 000 00 00"""

    return {
        "id": lead["id"],
        "name": name,
        "niche": lead["niche"],
        "slug": slug,
        "phone": phone,
        "wa_number": wa,
        "colors": lead["colors"],
        "ru": {
            "whatsapp": ru_whatsapp,
            "call_script": ru_call,
            "formal_letter": ru_formal,
            "pain": n.get("pain_ru",""),
            "benefit": n.get("benefit_ru",""),
            "proof": n.get("proof_ru",""),
            "usp": n.get("usp_ru",""),
        },
        "uz": {
            "whatsapp": uz_whatsapp,
            "call_script": uz_call,
            "formal_letter": uz_formal,
            "pain": n.get("pain_uz",""),
            "benefit": n.get("benefit_uz",""),
            "proof": n.get("proof_uz",""),
            "usp": n.get("usp_uz",""),
        }
    }

def main():
    with open(ROOT / "pipeline/seed_leads.json") as f:
        leads = json.load(f)

    pitches = [make_pitch(l) for l in leads]

    out = ROOT / "pitches/pitches.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(pitches, f, ensure_ascii=False, indent=2)

    print(f"✅ Generated {len(pitches)} pitches → {out}")

if __name__ == "__main__":
    main()
