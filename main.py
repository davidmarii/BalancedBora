# ============================================================
# BALANCEDBORA v3.0 — RATION + SUPPLIERS + M-PESA + ADMIN
# Features: NRC 2001, 21 Feeds, 4 Languages, Supplier Directory,
# M-Pesa STK Push, Admin Dashboard, Image Recognition
# ============================================================

import os
import json
import base64
import hashlib
import traceback
import requests
from datetime import datetime
from fastapi import FastAPI, Form, Request
from fastapi.responses import Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import pulp

from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="BalancedBora v3.0")
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ============================================================
# CREDENTIALS
# ============================================================
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "whatsapp:+254703709346")
GOOGLE_API_KEY = os.getenv("GOOGLE_VISION_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# M-Pesa Daraja API
MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")  # Sandbox default
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY", "")
MPESA_ENV = os.getenv("MPESA_ENV", "sandbox")  # sandbox or production
BASE_URL = os.getenv("BASE_URL", "")  # e.g. https://balancedbora.onrender.com

client = Client(TWILIO_SID, TWILIO_TOKEN) if TWILIO_SID else None

# ============================================================
# SESSIONS & ORDERS
# ============================================================
user_sessions = {}
orders_db = {}  # phone -> list of orders

# ============================================================
# SUPPLIER DATABASE (JSON-backed)
# ============================================================
SUPPLIERS_FILE = "suppliers.json"

def load_suppliers():
    if os.path.exists(SUPPLIERS_FILE):
        with open(SUPPLIERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "maize_bran": [
            {"id": "sup_001", "name": "Central Feeds Ltd", "phone": "+254712345678", "region": "Central", "price": 24}
        ],
        "wheat_bran": [
            {"id": "sup_002", "name": "Nakuru Grain Hub", "phone": "+254723456789", "region": "Rift Valley", "price": 19}
        ],
        "cottonseed_cake": [
            {"id": "sup_003", "name": "Eldoret Protein Co", "phone": "+254734567890", "region": "Rift Valley", "price": 58}
        ],
        "napier_grass_fresh": [
            {"id": "sup_004", "name": "Green Pastures Co-op", "phone": "+254745678901", "region": "Central", "price": 4}
        ],
        "soybean_meal": [
            {"id": "sup_005", "name": "Nairobi Agro Suppliers", "phone": "+254756789012", "region": "Nairobi", "price": 72}
        ],
        "dairy_meal_18": [
            {"id": "sup_006", "name": "Unga Feeds Distributor", "phone": "+254767890123", "region": "Central", "price": 53}
        ],
        "limestone": [
            {"id": "sup_007", "name": "Mineral Solutions KE", "phone": "+254778901234", "region": "Nairobi", "price": 14}
        ],
    }

def save_suppliers(data):
    with open(SUPPLIERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

SUPPLIERS_DB = load_suppliers()

# ============================================================
# OPTIONAL AI TRANSLATION ENGINE
# ============================================================
def ai_translate(text, target_lang):
    if not OPENAI_API_KEY:
        return None
    try:
        import openai
        lang_names = {'en': 'English', 'sw': 'Swahili', 'ki': 'Kikuyu', 'mer': 'Kimeru'}
        target = lang_names.get(target_lang, target_lang)
        resp = openai.OpenAI(api_key=OPENAI_API_KEY).chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You translate for Kenyan farmers. Translate to {target}. Keep it short, friendly, and use simple language. Return ONLY the translation."},
                {"role": "user", "content": text}
            ],
            temperature=0.2,
            max_tokens=600
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return None

# ============================================================
# NATIVE TRANSLATION SYSTEM
# ============================================================
LANG_MAP = {'1': 'en', '2': 'sw', '3': 'ki', '4': 'mer'}
LANG_NAME = {'en': 'English', 'sw': 'Kiswahili', 'ki': 'Kikuyu', 'mer': 'Kimeru'}
REGIONS = {
    '1': 'Central', '2': 'Rift Valley', '3': 'Eastern', '4': 'Nairobi',
    '5': 'Western', '6': 'Nyanza', '7': 'Coast', '8': 'North Eastern'
}

MESSAGES = {
    'en': {
        'welcome': "🐄 Welcome to BalancedBora!\n\nI calculate the cheapest balanced ration for your cow using NRC 2001 science.",
        'choose_language': "🌍 Choose your language:\n\n1️⃣ English\n2️⃣ Kiswahili\n3️⃣ Kikuyu\n4️⃣ Kimeru\n\nReply with 1, 2, 3, or 4.",
        'choose_region': "🌍 Choose your region:\n\n1️⃣ Central\n2️⃣ Rift Valley\n3️⃣ Eastern\n4️⃣ Nairobi\n5️⃣ Western\n6️⃣ Nyanza\n7️⃣ Coast\n8️⃣ North Eastern\n\nReply with a number (1-8) or 0 to skip.",
        'choose_animal': "Step 1: Choose your animal by number:\n\n1️⃣ Dairy Cow — High Producer (30L/day)\n2️⃣ Dairy Cow — Medium Producer (20L/day)\n3️⃣ Dairy Cow — Low Producer (10L/day)\n4️⃣ Dry Cow (Late Pregnancy)\n5️⃣ Growing Heifer (300kg)\n\nReply with a number (1-5).",
        'feed_selection': "Step 2: Which feeds do you have?\nSend numbers separated by commas (e.g., 1,6,11,16,18):\n\nENERGY:\n1️⃣ Maize Bran (KES 25/kg)\n2️⃣ Wheat Bran (KES 20/kg)\n3️⃣ Rice Bran (KES 22/kg)\n4️⃣ Cassava Chips (KES 18/kg)\n5️⃣ Molasses (KES 30/kg)\n\nPROTEIN:\n6️⃣ Cottonseed Cake (KES 60/kg)\n7️⃣ Sunflower Cake (KES 55/kg)\n8️⃣ Soybean Meal (KES 75/kg)\n9️⃣ Brewers Grains (KES 15/kg)\n🔟 Fish Meal (KES 120/kg)\n\nFORAGE:\n11️⃣ Napier Grass Fresh (KES 5/kg)\n12️⃣ Napier Grass Silage (KES 8/kg)\n13️⃣ Maize Stover (KES 3/kg)\n14️⃣ Rhodes Grass Hay (KES 10/kg)\n15️⃣ Lucerne Hay (KES 35/kg)\n\nCONCENTRATE:\n16️⃣ Dairy Meal 18% (KES 55/kg)\n17️⃣ Dairy Meal 24% (KES 65/kg)\n\nMINERALS:\n18️⃣ Limestone (KES 15/kg)\n19️⃣ Dicalcium Phosphate (KES 80/kg)\n20️⃣ Mineral Lick (KES 50/kg)\n21️⃣ Salt (KES 20/kg)\n\nTip: Include at least 1 forage + 1 protein source.",
        'ration_optimal': "✅ Your Balanced Ration (NRC 2001)",
        'ration_besteffort': "✅ Your Best Ration (Closest Possible)",
        'profile_label': "🐄",
        'dmi_label': "📊 Daily DM Intake",
        'total_cost_label': "💰 Total Daily Cost",
        'cost_per_kg_label': "💰 Cost per kg DM",
        'mix_header': "MIX THESE INGREDIENTS:",
        'how_to_feed': "How to feed:\n1. Weigh each ingredient accurately\n2. Mix thoroughly before feeding\n3. Divide into 2 portions (AM & PM)\n4. Provide fresh, clean water at all times",
        'start_again': "🔄 Send START for another ration.",
        'best_effort_notice': "ℹ️ Best-Effort Mode: Your feeds couldn't hit every target perfectly, so I found the closest possible mix.",
        'nutrient_low': "⚠️ {nutrient}: {actual} (target {min}-{max}) — slightly LOW",
        'nutrient_high': "⚠️ {nutrient}: {actual} (target {min}-{max}) — slightly HIGH",
        'nfc_ndf_warning': "⚠️ NFC/NDF ratio: {nfc}% NFC vs {ndf}% NDF — add more starch (Cassava #4, Molasses #5)",
        'ai_suggestions': "🤖 To improve next time, try adding:",
        'no_forage_error': "❌ Please add at least one forage (#11-15) for rumen health.",
        'impossible_mins': "❌ IMPOSSIBLE: Your selected feeds must take up {total_min}%, but a ration is only 100%.\nOffenders: {offenders}\n→ Remove one or more feeds with high minimum requirements.",
        'unknown_feeds': "❌ Unknown feeds: {feeds}",
        'select_at_least_2': "Please select at least 2 feeds.\nSend numbers like 1,6,11,16,18",
        'invalid_animal': "Please send a number from 1 to 5.",
        'photo_detected': "📸 I can see: {feeds}\n\nReply YES to use these, or send your own numbers.",
        'photo_not_found': "📸 I could not identify feeds in the photo.",
        'voice_soon': "🎙️ Voice notes coming soon!\n\nPlease type or send a photo.",
        'generic_help': "🐄 Send START to calculate a balanced ration.",
        'yes_confirm': "Reply YES to use these, or send your own numbers.",
        'kg_day': "kg/day",
        'kes_day': "KES",
        'notes_header': "NOTES:",
        'supplier_header': "💼 SUPPLIERS NEAR YOU:",
        'no_supplier': "No registered suppliers yet. Ask your local agrovet.",
        'order_prompt': "\n📦 Reply ORDER to buy these feeds from suppliers.",
        'order_instructions': "Reply with amounts like: 1:5,2:3\n(This means 5kg of feed #1 and 3kg of feed #2 from your ration)",
        'order_invalid': "❌ Invalid format. Use: 1:5,2:3 (feed_number:kg)",
        'order_summary': "📦 ORDER SUMMARY\n\n{items}\nTotal: *KES {total}*\n\nReply with your M-Pesa number to pay.",
        'payment_prompt': "📲 Enter M-Pesa number (e.g. 254712345678):",
        'payment_initiated': "✅ M-Pesa prompt sent to {phone}.\nEnter PIN on your phone to complete payment.",
        'payment_failed': "❌ Payment failed: {reason}\nPlease try again or pay supplier directly.",
        'payment_success': "✅ Payment received!\nSupplier {supplier} will contact you on {phone} for delivery.",
        'mpesa_not_configured': "⚠️ M-Pesa not configured yet.\nCall supplier directly: {phone}",
    },
    'sw': {
        'welcome': "🐄 Karibu BalancedBora!\n\nNakuhesabu chakula bora kwa gharama nafuu kwa ng'ombe wako kwa kutumia sayansi ya NRC 2001.",
        'choose_language': "🌍 Chagua lugha yako:\n\n1️⃣ English\n2️⃣ Kiswahili\n3️⃣ Kikuyu\n4️⃣ Kimeru\n\nJibu kwa 1, 2, 3, au 4.",
        'choose_region': "🌍 Chagua mkoa wako:\n\n1️⃣ Central\n2️⃣ Rift Valley\n3️⃣ Eastern\n4️⃣ Nairobi\n5️⃣ Western\n6️⃣ Nyanza\n7️⃣ Coast\n8️⃣ North Eastern\n\nJibu kwa namba (1-8) au 0 ku-ruka.",
        'choose_animal': "Hatua 1: Chagua mnyama wako kwa namba:\n\n1️⃣ Ng'ombe wa Maziwa — Mzazi Mkubwa (L 30/siku)\n2️⃣ Ng'ombe wa Maziwa — Mzazi wa Kati (L 20/siku)\n3️⃣ Ng'ombe wa Maziwa — Mzazi Mdogo (L 10/siku)\n4️⃣ Ng'ombe wa Kavu (Mimba ya Mwisho)\n5️⃣ Mtoto Ng'ombe (kg 300)\n\nJibu kwa namba (1-5).",
        'feed_selection': "Hatua 2: Chagua chakula ulicho nacho.\nTuma namba zikitenganishwa na koma (mfano, 1,6,11,16,18):\n\nNISHATI:\n1️⃣ Makapi ya Mahindi (KES 25/kg)\n2️⃣ Makapi ya Ngano (KES 20/kg)\n3️⃣ Makapi ya Mchele (KES 22/kg)\n4️⃣ Vipande vya Muhogo (KES 18/kg)\n5️⃣ Mtambo (KES 30/kg)\n\nPROTEINI:\n6️⃣ Keki ya Pamba (KES 60/kg)\n7️⃣ Keki ya Alizeti (KES 55/kg)\n8️⃣ Mlo wa Soya (KES 75/kg)\n9️⃣ Makapi ya Bia (KES 15/kg)\n🔟 Mlo wa Samaki (KES 120/kg)\n\nMAJANI:\n11️⃣ Majani ya Napier Fresh (KES 5/kg)\n12️⃣ Majani ya Napier Silage (KES 8/kg)\n13️⃣ Majani ya Mahindi (KES 3/kg)\n14️⃣ Majani ya Rhodes Hay (KES 10/kg)\n15️⃣ Majani ya Lucerne (KES 35/kg)\n\nCHAKULA CHA KUKAMILISHA:\n16️⃣ Dairy Meal 18% (KES 55/kg)\n17️⃣ Dairy Meal 24% (KES 65/kg)\n\nMADINI:\n18️⃣ Mawe ya Chokaa (KES 15/kg)\n19️⃣ Dicalcium Phosphate (KES 80/kg)\n20️⃣ Chumvi ya Madini (KES 50/kg)\n21️⃣ Chumvi (KES 20/kg)\n\nKidokezo: Weka angalau majani 1 + chakula cha proteini 1.",
        'ration_optimal': "✅ Chakula Chako Bora (NRC 2001)",
        'ration_besteffort': "✅ Chakula Chako Bora Zaidi (Uwezekano wa Karibu)",
        'profile_label': "🐄",
        'dmi_label': "📊 Kula Kavu Kwa Siku",
        'total_cost_label': "💰 Gharama Kuu Kwa Siku",
        'cost_per_kg_label': "💰 Gharama kwa kg Kavu",
        'mix_header': "CHANGANYA VIUNGO HIVI:",
        'how_to_feed': "Jinsi ya Kulisha:\n1. Pima kila kiungo kwa usahihi\n2. Changanya vizuri kabla ya kulisha\n3. Gawanya sehemu 2 (Asubuhi & Jioni)\n4. Toa maji safi na baridi kila wakati",
        'start_again': "🔄 Tuma START kwa chakula kingine.",
        'best_effort_notice': "ℹ️ Hali Bora Zaidi: Chakula chako hakingeweza kufikia kila lengo, kwa hivyo nimepata mchanganyiko wa karibu zaidi.",
        'nutrient_low': "⚠️ {nutrient}: {actual} (lengo {min}-{max}) — CHINI kidogo",
        'nutrient_high': "⚠️ {nutrient}: {actual} (lengo {min}-{max}) — JUU kidogo",
        'nfc_ndf_warning': "⚠️ NFC/NDF: {nfc}% NFC vs {ndf}% NDF — ongeza wanga zaidi (Muhogo #4, Mtambo #5)",
        'ai_suggestions': "🤖 Kuboresha wakati ujao, jaribu kuongeza:",
        'no_forage_error': "❌ Tafadhali ongeza majani angalau moja (#11-15) kwa afya ya rumen.",
        'impossible_mins': "❌ HAIWEZEKANI: Chakula ulichochagua lazima chukue {total_min}%, lakini chakula ni 100% tu.\nWaliokosea: {offenders}\n→ Ondoa chakula kimoja au zaidi chenye mahitaji makubwa ya chini.",
        'unknown_feeds': "❌ Chakula isiyojulikana: {feeds}",
        'select_at_least_2': "Tafadhali chagua angalau chakula 2.\nTuma namba kama 1,6,11,16,18",
        'invalid_animal': "Tafadhali tuma namba kati ya 1 hadi 5.",
        'photo_detected': "📸 Naona: {feeds}\n\nJibu NDIYO kutumia hivi, au tuma namba zako.",
        'photo_not_found': "📸 Sikuweza kutambua chakula katika picha.",
        'voice_soon': "🎙️ Ujumbe wa sauti utakuja hivi karibu!\n\nTafadhali andika au tuma picha.",
        'generic_help': "🐄 Tuma START kuhesabu chakula bora.",
        'yes_confirm': "Jibu NDIYO kutumia hivi, au tuma namba zako.",
        'kg_day': "kg/siku",
        'kes_day': "KES",
        'notes_header': "MAELEZO:",
        'supplier_header': "💼 WAUZAJI KARIBU NA WEWE:",
        'no_supplier': "Hakuna wauzaji waliosajiliwa. Uliza agrovet yako.",
        'order_prompt': "\n📦 Jibu ORDER kununua chakula kutoka kwa wauzaji.",
        'order_instructions': "Jibu na kiasi kama: 1:5,2:3\n(Maana yake kg 5 za chakula #1 na kg 3 za chakula #2)",
        'order_invalid': "❌ Umbizo sio sahihi. Tumia: 1:5,2:3 (namba_chakula:kg)",
        'order_summary': "📦 MUHTASARI WA ORDER\n\n{items}\nJumla: *KES {total}*\n\nJibu na namba yako ya M-Pesa kulipa.",
        'payment_prompt': "📲 Weka namba ya M-Pesa (mfano 254712345678):",
        'payment_initiated': "✅ M-Pesa prompt imetumwa kwa {phone}.\nWeka PIN kwenye simu yako kukamilisha malipo.",
        'payment_failed': "❌ Malipo yameshindwa: {reason}\nJaribu tena au lipa moja kwa moja kwa mchuuzi.",
        'payment_success': "✅ Malipo yamepokelewa!\nMchuuzi {supplier} atawasiliana nawe kwa {phone} kwa delivery.",
        'mpesa_not_configured': "⚠️ M-Pesa bado haijasanidiwa.\nPiga mchuuzi moja kwa moja: {phone}",
    },
    'ki': {
        'welcome': "🐄 Wî mwega BalancedBora!\n\nNîndîrathîrîria irio rîtheru na bei ncheene ya ng'ombe yaku na sayansi ya NRC 2001.",
        'choose_language': "🌍 Thagua rurimi rwaku:\n\n1️⃣ English\n2️⃣ Kiswahili\n3️⃣ Kikuyu\n4️⃣ Kimeru\n\nCokeria na 1, 2, 3, kana 4.",
        'choose_region': "🌍 Thagua gîcigo gîaku:\n\n1️⃣ Central\n2️⃣ Rift Valley\n3️⃣ Eastern\n4️⃣ Nairobi\n5️⃣ Western\n6️⃣ Nyanza\n7️⃣ Coast\n8️⃣ North Eastern\n\nCokeria na namba (1-8) kana 0 kûrega.",
        'choose_animal': "Hatua 1: Thagua nyamû na namba:\n\n1️⃣ Ng'ombe ya Mûrû — Mûtûngi Mûnene (L 30/mûthenya)\n2️⃣ Ng'ombe ya Mûrû — Mûtûngi wa Gatagati (L 20/mûthenya)\n3️⃣ Ng'ombe ya Mûrû — Mûtûngi Mûnini (L 10/mûthenya)\n4️⃣ Ng'ombe Mûkûrû (Ndà Mûthî)\n5️⃣ Kîhîî kia Ng'ombe (kg 300)\n\nCokeria na namba (1-5).",
        'feed_selection': "Hatua 2: Thagua irio ûrî na rîo.\nTûma namba ikîmenyekanithio na koma (kûranî, 1,6,11,16,18):\n\nHOTI:\n1️⃣ Makapi ma Mûbî (KES 25/kg)\n2️⃣ Makapi ma Ngano (KES 20/kg)\n3️⃣ Makapi ma Mûchele (KES 22/kg)\n4️⃣ Muhogo (KES 18/kg)\n5️⃣ Mtambo (KES 30/kg)\n\nPROTEINI:\n6️⃣ Keki ya Pamba (KES 60/kg)\n7️⃣ Keki ya Alizeti (KES 55/kg)\n8️⃣ Mlo wa Soya (KES 75/kg)\n9️⃣ Makapi ma Bia (KES 15/kg)\n🔟 Mlo wa Thamaki (KES 120/kg)\n\nMAJANI:\n11️⃣ Majani ma Napier Fresh (KES 5/kg)\n12️⃣ Majani ma Napier Silage (KES 8/kg)\n13️⃣ Majani ma Mûbî (KES 3/kg)\n14️⃣ Majani ma Rhodes (KES 10/kg)\n15️⃣ Majani ma Lucerne (KES 35/kg)\n\nIRIO RÎA GÛCINIA:\n16️⃣ Dairy Meal 18% (KES 55/kg)\n17️⃣ Dairy Meal 24% (KES 65/kg)\n\nMADINI:\n18️⃣ Mawe ma Chokaa (KES 15/kg)\n19️⃣ Dicalcium Phosphate (KES 80/kg)\n20️⃣ Chumvi ya Madini (KES 50/kg)\n21️⃣ Chumvi (KES 20/kg)\n\nGîcûnio: Ikara majani 1 + irio rîa proteini 1.",
        'ration_optimal': "✅ Irio Rîaku Rîtheru (NRC 2001)",
        'ration_besteffort': "✅ Irio Rîaku Rîtheru Zaidi (Kûgîa Gûtîrî)",
        'profile_label': "🐄",
        'dmi_label': "📊 Kûrîa Kûkû Kwa Mûthenya",
        'total_cost_label': "💰 Bei Kuu Kwa Mûthenya",
        'cost_per_kg_label': "💰 Bei kwa kg Kûkû",
        'mix_header': "CAMBANIA IRIO ICIO:",
        'how_to_feed': "Uria wa Gûcambania:\n1. Pima kîndu o gîothe gîa kûhûthia\n2. Cambania wega mbere ya gûcambania\n3. Gawanîria mîgwanîko 2 (Rûcinî & Hwaîni)\n4. He maa matheru na baridi ihindî o rîa",
        'start_again': "🔄 Tuma START kûgîa irio rîngî.",
        'best_effort_notice': "ℹ️ Hali Bora Zaidi: Irio rîaku rîtingîhîtie kûgîa kîndu o gîothe, nîndîragîa mîcambanîko ya hûgûrû.",
        'nutrient_low': "⚠️ {nutrient}: {actual} (gûtîrî {min}-{max}) — CHINI hûgûrû",
        'nutrient_high': "⚠️ {nutrient}: {actual} (gûtîrî {min}-{max}) — JUU hûgûrû",
        'nfc_ndf_warning': "⚠️ NFC/NDF: {nfc}% NFC vs {ndf}% NDF — ongera wanga (Muhogo #4, Mtambo #5)",
        'ai_suggestions': "🤖 Kûboresha thutha wa gûku, geria kuongeza:",
        'no_forage_error': "❌ Tafadhali ongera majani angalau imwe (#11-15) kûhûthia rumen.",
        'impossible_mins': "❌ HAIWEZEKANI: Irio ûliothegûria lazima cûkue {total_min}%, no irio nî 100%.\nArîa mekosea: {offenders}\n→ Ora irio imwe kana ingî îrî na mahitaji makûnû ma chini.",
        'unknown_feeds': "❌ Irio itarîmenyekana: {feeds}",
        'select_at_least_2': "Tafadhali thagua angalau irio 2.\nTuma namba ta 1,6,11,16,18",
        'invalid_animal': "Tafadhali tuma namba kûranî 1 nginya 5.",
        'photo_detected': "📸 Nîmona: {feeds}\n\nCokeria II kûhûthia icio, kana tuma namba ciaku.",
        'photo_not_found': "📸 Nîndîratambua irio kûranî rûtûni.",
        'voice_soon': "🎙️ Ujumbe wa mûgambo ûgûka hûgûrû!\n\nTafadhali andika kana tuma rûtûni.",
        'generic_help': "🐄 Tuma START kûhûthia irio rîtheru.",
        'yes_confirm': "Cokeria II kûhûthia icio, kana tuma namba ciaku.",
        'kg_day': "kg/mûthenya",
        'kes_day': "KES",
        'notes_header': "MAELEZO:",
        'supplier_header': "💼 ARÎA MEKûGûRA HûGûRû:",
        'no_supplier': "Gûtîrî arîa mekûgûra. Rîria agrovet yaku.",
        'order_prompt': "\n📦 Cokeria ORDER kûgûra irio kuuma kûrîa mekûgûra.",
        'order_instructions': "Cokeria na kîgîrô kîranî: 1:5,2:3\n(Maana yake kg 5 cia irio #1 na kg 3 cia irio #2)",
        'order_invalid': "❌ Kîgîrô gîtarî kûrîa. Tumia: 1:5,2:3 (namba_irio:kg)",
        'order_summary': "📦 MûTHONDO WA ORDER\n\n{items}\nJumla: *KES {total}*\n\nCokeria na namba yaku ya M-Pesa kûrîha.",
        'payment_prompt': "📲 Ikara namba ya M-Pesa (kûranî 254712345678):",
        'payment_initiated': "✅ M-Pesa prompt nîyatumîtwo kûrî {phone}.\nIkera PIN cîaku.",
        'payment_failed': "❌ Kûrîha kûgîa gûtîrî: {reason}\nGeria rîngî kana ûrîhe mûgûrî mûciî.",
        'payment_success': "✅ Kûrîha kwîmûkîrîrwo!\nMûgûrî {supplier} arîkûhûthia kûrî {phone}.",
        'mpesa_not_configured': "⚠️ M-Pesa ndîrî na cîgerio.\nHîa mûgûrî mûciî: {phone}",
    },
    'mer': {
        'welcome': "🐄 Urova BalancedBora!\n\nNtathimana irio theru na bei ncheene ya ng'ombe yaku na sayansi ya NRC 2001.",
        'choose_language': "🌍 Thagua rurimi rwaku:\n\n1️⃣ English\n2️⃣ Kiswahili\n3️⃣ Kikuyu\n4️⃣ Kimeru\n\nCokeria na 1, 2, 3, kana 4.",
        'choose_region': "🌍 Thagua gîcigo gîaku:\n\n1️⃣ Central\n2️⃣ Rift Valley\n3️⃣ Eastern\n4️⃣ Nairobi\n5️⃣ Western\n6️⃣ Nyanza\n7️⃣ Coast\n8️⃣ North Eastern\n\nCokeria na namba (1-8) kana 0 kûrega.",
        'choose_animal': "Hatua 1: Thagua kiama na namba:\n\n1️⃣ Ng'ombe ya Mûrû — Mûtûngi Mûnene (L 30/mûthenya)\n2️⃣ Ng'ombe ya Mûrû — Mûtûngi wa Gatagati (L 20/mûthenya)\n3️⃣ Ng'ombe ya Mûrû — Mûtûngi Mûnini (L 10/mûthenya)\n4️⃣ Ng'ombe Mûkûrû (Ndà Mûthî)\n5️⃣ Kîhîî kia Ng'ombe (kg 300)\n\nCokeria na namba (1-5).",
        'feed_selection': "Hatua 2: Thagua irio ûrî na rîo.\nTûma namba ikîmenyekanithio na koma (kûranî, 1,6,11,16,18):\n\nHOTI:\n1️⃣ Makapi ma Mûbî (KES 25/kg)\n2️⃣ Makapi ma Ngano (KES 20/kg)\n3️⃣ Makapi ma Mûchele (KES 22/kg)\n4️⃣ Muhogo (KES 18/kg)\n5️⃣ Mtambo (KES 30/kg)\n\nPROTEINI:\n6️⃣ Keki ya Pamba (KES 60/kg)\n7️⃣ Keki ya Alizeti (KES 55/kg)\n8️⃣ Mlo wa Soya (KES 75/kg)\n9️⃣ Makapi ma Bia (KES 15/kg)\n🔟 Mlo wa Thamaki (KES 120/kg)\n\nMAJANI:\n11️⃣ Majani ma Napier Fresh (KES 5/kg)\n12️⃣ Majani ma Napier Silage (KES 8/kg)\n13️⃣ Majani ma Mûbî (KES 3/kg)\n14️⃣ Majani ma Rhodes (KES 10/kg)\n15️⃣ Majani ma Lucerne (KES 35/kg)\n\nIRIO RIA GÛCINIA:\n16️⃣ Dairy Meal 18% (KES 55/kg)\n17️⃣ Dairy Meal 24% (KES 65/kg)\n\nMADINI:\n18️⃣ Mawe ma Chokaa (KES 15/kg)\n19️⃣ Dicalcium Phosphate (KES 80/kg)\n20️⃣ Chumvi ya Madini (KES 50/kg)\n21️⃣ Chumvi (KES 20/kg)\n\nGîcûnio: Ikara majani 1 + irio ria proteini 1.",
        'ration_optimal': "✅ Irio Rîaku Rîtheru (NRC 2001)",
        'ration_besteffort': "✅ Irio Rîaku Rîtheru Zaidi (Kûgîa Gûtîrî)",
        'profile_label': "🐄",
        'dmi_label': "📊 Kûrîa Kûkû Kwa Mûthenya",
        'total_cost_label': "💰 Bei Kuu Kwa Mûthenya",
        'cost_per_kg_label': "💰 Bei kwa kg Kûkû",
        'mix_header': "CAMBANIA IRIO ICIO:",
        'how_to_feed': "Uria wa Gûcambania:\n1. Pima kîndu o gîothe gîa kûhûthia\n2. Cambania wega mbere ya gûcambania\n3. Gawanîria mîgwanîko 2 (Rûcinî & Hwaîni)\n4. He maa matheru na baridi ihindî o rîa",
        'start_again': "🔄 Tuma START kûgîa irio rîngî.",
        'best_effort_notice': "ℹ️ Hali Bora Zaidi: Irio rîaku rîtingîhîtie kûgîa kîndu o gîothe, nîntagîa mîcambanîko ya hûgûrû.",
        'nutrient_low': "⚠️ {nutrient}: {actual} (gûtîrî {min}-{max}) — CHINI hûgûrû",
        'nutrient_high': "⚠️ {nutrient}: {actual} (gûtîrî {min}-{max}) — JUU hûgûrû",
        'nfc_ndf_warning': "⚠️ NFC/NDF: {nfc}% NFC vs {ndf}% NDF — ongera wanga (Muhogo #4, Mtambo #5)",
        'ai_suggestions': "🤖 Kûboresha thutha wa gûku, geria kuongeza:",
        'no_forage_error': "❌ Tafadhali ongera majani angalau imwe (#11-15) kûhûthia rumen.",
        'impossible_mins': "❌ HAIWEZEKANI: Irio ûliothegûria lazima cûkue {total_min}%, no irio nî 100%.\nArîa mekosea: {offenders}\n→ Ora irio imwe kana ingî îrî na mahitaji makûnû ma chini.",
        'unknown_feeds': "❌ Irio itarîmenyekana: {feeds}",
        'select_at_least_2': "Tafadhali thagua angalau irio 2.\nTuma namba ta 1,6,11,16,18",
        'invalid_animal': "Tafadhali tuma namba kûranî 1 nginya 5.",
        'photo_detected': "📸 Nîmona: {feeds}\n\nCokeria II kûhûthia icio, kana tuma namba ciaku.",
        'photo_not_found': "📸 Nîndîratambua irio kûranî rûtûni.",
        'voice_soon': "🎙️ Ujumbe wa mûgambo ûgûka hûgûrû!\n\nTafadhali andika kana tuma rûtûni.",
        'generic_help': "🐄 Tuma START kûhûthia irio rîtheru.",
        'yes_confirm': "Cokeria II kûhûthia icio, kana tuma namba ciaku.",
        'kg_day': "kg/mûthenya",
        'kes_day': "KES",
        'notes_header': "MAELEZO:",
        'supplier_header': "💼 ARÎA MEKûGûRA HûGûRû:",
        'no_supplier': "Gûtîrî arîa mekûgûra. Rîria agrovet yaku.",
        'order_prompt': "\n📦 Cokeria ORDER kûgûra irio kuuma kûrîa mekûgûra.",
        'order_instructions': "Cokeria na kîgîrô kîranî: 1:5,2:3\n(Maana yake kg 5 cia irio #1 na kg 3 cia irio #2)",
        'order_invalid': "❌ Kîgîrô gîtarî kûrîa. Tumia: 1:5,2:3 (namba_irio:kg)",
        'order_summary': "📦 MûTHONDO WA ORDER\n\n{items}\nJumla: *KES {total}*\n\nCokeria na namba yaku ya M-Pesa kûrîha.",
        'payment_prompt': "📲 Ikera namba ya M-Pesa (kûranî 254712345678):",
        'payment_initiated': "✅ M-Pesa prompt nîyatumîtwo kûrî {phone}.\nIkera PIN cîaku.",
        'payment_failed': "❌ Kûrîha kûgîa gûtîrî: {reason}\nGeria rîngî kana ûrîhe mûgûrî mûciî.",
        'payment_success': "✅ Kûrîha kwîmûkîrîrwo!\nMûgûrî {supplier} arîkûhûthia kûrî {phone}.",
        'mpesa_not_configured': "⚠️ M-Pesa ndîrî na cîgerio.\nHîa mûgûrî mûciî: {phone}",
    }
}

def get_msg(phone, key, **kwargs):
    """Get translated message. Native first, AI fallback if enabled."""
    lang = user_sessions.get(phone, {}).get('lang', 'en')
    text = MESSAGES.get(lang, MESSAGES['en']).get(key, MESSAGES['en'][key])
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    if lang != 'en' and text == MESSAGES['en'].get(key, text) and OPENAI_API_KEY:
        ai_text = ai_translate(text, lang)
        if ai_text:
            return ai_text
    return text

# ============================================================
# NUMBER -> FEED ID MAPPING (21 feeds)
# ============================================================
FEED_NUMBER_MAP = {
    '1': 'maize_bran', '2': 'wheat_bran', '3': 'rice_bran',
    '4': 'cassava_chips', '5': 'molasses',
    '6': 'cottonseed_cake', '7': 'sunflower_cake', '8': 'soybean_meal',
    '9': 'brewers_grains', '10': 'fish_meal',
    '11': 'napier_grass_fresh', '12': 'napier_grass_silage',
    '13': 'maize_stover', '14': 'rhodes_grass_hay', '15': 'lucerne_hay',
    '16': 'dairy_meal_18', '17': 'dairy_meal_24',
    '18': 'limestone', '19': 'dicalcium_phosphate',
    '20': 'mineral_lick', '21': 'salt',
}

ID_TO_NUMBER = {v: k for k, v in FEED_NUMBER_MAP.items()}

# ============================================================
# COMPLETE FEED DATABASE — NRC 2001
# ============================================================
FEEDS_DB = {
    'maize_bran': {
        'name': 'Maize Bran', 'cp': 10.0, 'me': 2.80, 'ca': 0.05, 'p': 0.35,
        'ndf': 35.0, 'adf': 12.0, 'ee': 3.5, 'ash': 4.0, 'nfc': 42.0,
        'cost_kg': 25, 'min_incl': 5, 'max_incl': 40,
        'category': 'energy', 'notes': 'Good energy, moderate fiber'
    },
    'wheat_bran': {
        'name': 'Wheat Bran', 'cp': 15.0, 'me': 2.60, 'ca': 0.10, 'p': 0.90,
        'ndf': 40.0, 'adf': 14.0, 'ee': 3.0, 'ash': 5.5, 'nfc': 31.0,
        'cost_kg': 20, 'min_incl': 0, 'max_incl': 25,
        'category': 'energy', 'notes': 'High phosphorus, good fiber'
    },
    'rice_bran': {
        'name': 'Rice Bran', 'cp': 13.0, 'me': 2.50, 'ca': 0.08, 'p': 1.40,
        'ndf': 32.0, 'adf': 18.0, 'ee': 12.0, 'ash': 10.0, 'nfc': 25.0,
        'cost_kg': 22, 'min_incl': 0, 'max_incl': 20,
        'category': 'energy', 'notes': 'High fat, rancidity risk if old'
    },
    'cassava_chips': {
        'name': 'Cassava Chips', 'cp': 3.0, 'me': 3.20, 'ca': 0.25, 'p': 0.10,
        'ndf': 10.0, 'adf': 6.0, 'ee': 0.5, 'ash': 2.5, 'nfc': 82.0,
        'cost_kg': 18, 'min_incl': 0, 'max_incl': 30,
        'category': 'energy', 'notes': 'High starch, must be dried (HCN risk)'
    },
    'molasses': {
        'name': 'Molasses', 'cp': 3.0, 'me': 2.90, 'ca': 0.90, 'p': 0.10,
        'ndf': 0.0, 'adf': 0.0, 'ee': 0.0, 'ash': 10.0, 'nfc': 55.0,
        'cost_kg': 30, 'min_incl': 0, 'max_incl': 10,
        'category': 'energy', 'notes': 'Palatability, max 10% (scours)'
    },
    'cottonseed_cake': {
        'name': 'Cottonseed Cake', 'cp': 40.0, 'me': 2.40, 'ca': 0.20, 'p': 1.10,
        'ndf': 30.0, 'adf': 22.0, 'ee': 5.0, 'ash': 6.0, 'nfc': 15.0,
        'cost_kg': 60, 'min_incl': 0, 'max_incl': 15,
        'category': 'protein', 'notes': 'GOSSYPOL: Max 15% for dairy'
    },
    'sunflower_cake': {
        'name': 'Sunflower Cake', 'cp': 35.0, 'me': 2.20, 'ca': 0.40, 'p': 1.00,
        'ndf': 35.0, 'adf': 28.0, 'ee': 10.0, 'ash': 6.0, 'nfc': 12.0,
        'cost_kg': 55, 'min_incl': 0, 'max_incl': 20,
        'category': 'protein', 'notes': 'High fiber, good protein'
    },
    'soybean_meal': {
        'name': 'Soybean Meal', 'cp': 48.0, 'me': 3.20, 'ca': 0.35, 'p': 0.70,
        'ndf': 15.0, 'adf': 8.0, 'ee': 2.0, 'ash': 6.5, 'nfc': 25.0,
        'cost_kg': 75, 'min_incl': 0, 'max_incl': 25,
        'category': 'protein', 'notes': 'Premium protein, high bypass'
    },
    'brewers_grains': {
        'name': 'Brewers Grains', 'cp': 25.0, 'me': 2.10, 'ca': 0.35, 'p': 0.55,
        'ndf': 50.0, 'adf': 24.0, 'ee': 6.0, 'ash': 4.0, 'nfc': 12.0,
        'cost_kg': 15, 'min_incl': 0, 'max_incl': 20,
        'category': 'protein', 'notes': 'Moderate protein, high fiber'
    },
    'fish_meal': {
        'name': 'Fish Meal', 'cp': 65.0, 'me': 2.80, 'ca': 5.50, 'p': 3.00,
        'ndf': 0.0, 'adf': 0.0, 'ee': 8.0, 'ash': 18.0, 'nfc': 0.0,
        'cost_kg': 120, 'min_incl': 0, 'max_incl': 5,
        'category': 'protein', 'notes': 'Very high protein, max 5%'
    },
    'napier_grass_fresh': {
        'name': 'Napier Grass (Fresh)', 'cp': 8.0, 'me': 1.80, 'ca': 0.30, 'p': 0.25,
        'ndf': 65.0, 'adf': 38.0, 'ee': 2.0, 'ash': 10.0, 'nfc': 12.0,
        'cost_kg': 5, 'min_incl': 20, 'max_incl': 60,
        'category': 'forage', 'notes': 'Base forage, quality varies'
    },
    'napier_grass_silage': {
        'name': 'Napier Grass Silage', 'cp': 10.0, 'me': 2.00, 'ca': 0.35, 'p': 0.30,
        'ndf': 60.0, 'adf': 35.0, 'ee': 2.5, 'ash': 8.0, 'nfc': 18.0,
        'cost_kg': 8, 'min_incl': 15, 'max_incl': 50,
        'category': 'forage', 'notes': 'Better than fresh, higher energy'
    },
    'maize_stover': {
        'name': 'Maize Stover', 'cp': 5.0, 'me': 1.60, 'ca': 0.30, 'p': 0.15,
        'ndf': 72.0, 'adf': 45.0, 'ee': 1.5, 'ash': 7.0, 'nfc': 10.0,
        'cost_kg': 3, 'min_incl': 10, 'max_incl': 40,
        'category': 'forage', 'notes': 'Poor quality, needs supplement'
    },
    'rhodes_grass_hay': {
        'name': 'Rhodes Grass Hay', 'cp': 7.0, 'me': 1.70, 'ca': 0.35, 'p': 0.25,
        'ndf': 68.0, 'adf': 40.0, 'ee': 2.0, 'ash': 8.0, 'nfc': 15.0,
        'cost_kg': 10, 'min_incl': 10, 'max_incl': 50,
        'category': 'forage', 'notes': 'Standard hay, moderate quality'
    },
    'lucerne_hay': {
        'name': 'Lucerne (Alfalfa) Hay', 'cp': 18.0, 'me': 2.20, 'ca': 1.40, 'p': 0.25,
        'ndf': 45.0, 'adf': 35.0, 'ee': 2.5, 'ash': 10.0, 'nfc': 22.0,
        'cost_kg': 35, 'min_incl': 5, 'max_incl': 30,
        'category': 'forage', 'notes': 'High protein forage, excellent'
    },
    'dairy_meal_18': {
        'name': 'Dairy Meal (18% CP)', 'cp': 18.0, 'me': 3.00, 'ca': 0.80, 'p': 0.60,
        'ndf': 25.0, 'adf': 14.0, 'ee': 4.0, 'ash': 8.0, 'nfc': 42.0,
        'cost_kg': 55, 'min_incl': 0, 'max_incl': 35,
        'category': 'concentrate', 'notes': 'Balanced commercial feed'
    },
    'dairy_meal_24': {
        'name': 'Dairy Meal (24% CP)', 'cp': 24.0, 'me': 3.00, 'ca': 1.00, 'p': 0.80,
        'ndf': 22.0, 'adf': 12.0, 'ee': 5.0, 'ash': 9.0, 'nfc': 38.0,
        'cost_kg': 65, 'min_incl': 0, 'max_incl': 30,
        'category': 'concentrate', 'notes': 'High protein for early lactation'
    },
    'limestone': {
        'name': 'Limestone', 'cp': 0.0, 'me': 0.0, 'ca': 38.0, 'p': 0.0,
        'ndf': 0.0, 'adf': 0.0, 'ee': 0.0, 'ash': 98.0, 'nfc': 0.0,
        'cost_kg': 15, 'min_incl': 0, 'max_incl': 2,
        'category': 'mineral', 'notes': 'Calcium for milk production'
    },
    'dicalcium_phosphate': {
        'name': 'Dicalcium Phosphate', 'cp': 0.0, 'me': 0.0, 'ca': 24.0, 'p': 18.5,
        'ndf': 0.0, 'adf': 0.0, 'ee': 0.0, 'ash': 95.0, 'nfc': 0.0,
        'cost_kg': 80, 'min_incl': 0, 'max_incl': 2,
        'category': 'mineral', 'notes': 'Ca + P balanced mineral'
    },
    'mineral_lick': {
        'name': 'Mineral Lick', 'cp': 0.0, 'me': 0.0, 'ca': 15.0, 'p': 10.0,
        'ndf': 0.0, 'adf': 0.0, 'ee': 0.0, 'ash': 85.0, 'nfc': 0.0,
        'cost_kg': 50, 'min_incl': 0, 'max_incl': 1,
        'category': 'mineral', 'notes': 'Trace minerals included'
    },
    'salt': {
        'name': 'Common Salt', 'cp': 0.0, 'me': 0.0, 'ca': 0.0, 'p': 0.0,
        'ndf': 0.0, 'adf': 0.0, 'ee': 0.0, 'ash': 100.0, 'nfc': 0.0,
        'cost_kg': 20, 'min_incl': 0, 'max_incl': 1,
        'category': 'mineral', 'notes': 'Sodium source, essential'
    },
}

# ============================================================
# ANIMAL PROFILES
# ============================================================
ANIMAL_PROFILES = {
    '1': {
        'name': 'Dairy Cow — High Producer (30L/day, 600kg)', 'dmi': 22.0,
        'cp': {'min': 17.0, 'max': 19.0}, 'me': {'min': 2.80, 'max': 3.20},
        'ca': {'min': 0.80, 'max': 1.40}, 'p': {'min': 0.45, 'max': 0.70},
        'ndf': {'min': 28.0, 'max': 38.0}, 'adf': {'min': 18.0, 'max': 24.0},
        'ee': {'min': 3.0, 'max': 6.0}, 'ash': {'min': 6.0, 'max': 10.0},
        'nfc': {'min': 35.0, 'max': 45.0},
    },
    '2': {
        'name': 'Dairy Cow — Medium Producer (20L/day, 500kg)', 'dmi': 18.0,
        'cp': {'min': 16.0, 'max': 18.0}, 'me': {'min': 2.65, 'max': 3.00},
        'ca': {'min': 0.65, 'max': 1.10}, 'p': {'min': 0.40, 'max': 0.60},
        'ndf': {'min': 30.0, 'max': 40.0}, 'adf': {'min': 19.0, 'max': 26.0},
        'ee': {'min': 3.0, 'max': 6.0}, 'ash': {'min': 6.0, 'max': 10.0},
        'nfc': {'min': 32.0, 'max': 42.0},
    },
    '3': {
        'name': 'Dairy Cow — Low Producer (10L/day, 400kg)', 'dmi': 14.0,
        'cp': {'min': 14.0, 'max': 16.0}, 'me': {'min': 2.50, 'max': 2.80},
        'ca': {'min': 0.55, 'max': 0.90}, 'p': {'min': 0.35, 'max': 0.50},
        'ndf': {'min': 32.0, 'max': 45.0}, 'adf': {'min': 20.0, 'max': 28.0},
        'ee': {'min': 3.0, 'max': 6.0}, 'ash': {'min': 6.0, 'max': 10.0},
        'nfc': {'min': 30.0, 'max': 40.0},
    },
    '4': {
        'name': 'Dry Cow — Late Pregnancy (500kg)', 'dmi': 12.0,
        'cp': {'min': 12.0, 'max': 14.0}, 'me': {'min': 2.20, 'max': 2.50},
        'ca': {'min': 0.45, 'max': 0.70}, 'p': {'min': 0.30, 'max': 0.45},
        'ndf': {'min': 35.0, 'max': 50.0}, 'adf': {'min': 22.0, 'max': 32.0},
        'ee': {'min': 2.5, 'max': 5.0}, 'ash': {'min': 6.0, 'max': 10.0},
        'nfc': {'min': 25.0, 'max': 35.0},
    },
    '5': {
        'name': 'Growing Heifer (300kg, 0.7kg/day gain)', 'dmi': 10.0,
        'cp': {'min': 14.0, 'max': 16.0}, 'me': {'min': 2.40, 'max': 2.70},
        'ca': {'min': 0.50, 'max': 0.80}, 'p': {'min': 0.35, 'max': 0.50},
        'ndf': {'min': 35.0, 'max': 50.0}, 'adf': {'min': 22.0, 'max': 30.0},
        'ee': {'min': 2.5, 'max': 5.0}, 'ash': {'min': 6.0, 'max': 10.0},
        'nfc': {'min': 28.0, 'max': 38.0},
    },
}

# ============================================================
# AI SUGGESTION ENGINE
# ============================================================
class FeedSuggestionEngine:
    def __init__(self, feeds_db, profiles_db):
        self.feeds = feeds_db
        self.profiles = profiles_db
        self._compute_efficiency_scores()

    def _compute_efficiency_scores(self):
        for fid, data in self.feeds.items():
            data['efficiency'] = {}
            if data['cost_kg'] > 0:
                data['efficiency']['cp'] = data['cp'] / data['cost_kg']
                data['efficiency']['me'] = data['me'] / data['cost_kg']
                data['efficiency']['ca'] = data['ca'] / data['cost_kg']
                data['efficiency']['p'] = data['p'] / data['cost_kg']

    def suggest_for_fix(self, profile_key, current_feeds, low_nutrients, high_nutrients):
        profile = self.profiles[profile_key]
        current_ids = set(current_feeds)
        candidates = []

        for fid, data in self.feeds.items():
            if fid in current_ids:
                continue

            score = 0.0
            reasons = []

            for nutrient in low_nutrients:
                if nutrient in data and data[nutrient] > 0:
                    efficiency = data.get('efficiency', {}).get(nutrient, 0)
                    score += efficiency * 100
                    if efficiency > 0.3:
                        reasons.append(f"adds {nutrient.upper()}")

            for nutrient in high_nutrients:
                if nutrient in data and data[nutrient] < 5:
                    score += 50
                    reasons.append(f"low {nutrient.upper()}")

            current_cats = {self.feeds[f]['category'] for f in current_ids if f in self.feeds}
            if data['category'] not in current_cats:
                if data['category'] == 'protein':
                    score += 100
                    reasons.append("adds PROTEIN")
                elif data['category'] == 'forage':
                    score += 80
                    reasons.append("adds FORAGE")
                elif data['category'] == 'mineral':
                    score += 60
                    reasons.append("adds MINERALS")
                elif data['category'] == 'energy':
                    score += 50
                    reasons.append("adds ENERGY")

            if score > 0:
                candidates.append({
                    'id': fid, 'name': data['name'], 'score': score,
                    'cost': data['cost_kg'], 'category': data['category'],
                    'reasons': reasons[:2], 'notes': data['notes']
                })

        candidates.sort(key=lambda x: x['score'], reverse=True)
        return candidates[:3]

suggestion_engine = FeedSuggestionEngine(FEEDS_DB, ANIMAL_PROFILES)

# ============================================================
# MAIN SOLVER — STRICT + BEST-EFFORT
# ============================================================
def solve_nrc_ration(profile_key, selected_feeds):
    if profile_key not in ANIMAL_PROFILES:
        return None, f"Invalid profile: {profile_key}"

    profile = ANIMAL_PROFILES[profile_key]
    available = {fid: FEEDS_DB[fid] for fid in selected_feeds if fid in FEEDS_DB}
    invalid = [fid for fid in selected_feeds if fid not in FEEDS_DB]

    if invalid:
        return None, f"Unknown feeds: {', '.join(invalid)}"
    if len(available) < 2:
        return None, "Please select at least 2 feeds."

    forage_count = sum(1 for f in available.values() if f['category'] == 'forage')
    if forage_count == 0:
        return None, "NO_FORAGE"

    total_min = sum(FEEDS_DB[fid]['min_incl'] for fid in selected_feeds if fid in FEEDS_DB)
    if total_min > 100:
        offenders = [FEEDS_DB[fid]['name'] + f" (min {FEEDS_DB[fid]['min_incl']}%)"
                     for fid in selected_feeds if fid in FEEDS_DB and FEEDS_DB[fid]['min_incl'] > 0]
        return None, ("IMPOSSIBLE_MINS", total_min, offenders)

    nutrients = ['cp', 'me', 'ca', 'p', 'ndf', 'adf', 'ee', 'ash', 'nfc']

    # STAGE 1: STRICT LP
    prob = pulp.LpProblem(f"NRC_{profile_key}", pulp.LpMinimize)
    feed_vars = pulp.LpVariable.dicts("Feed", available.keys(), lowBound=0, upBound=100)

    prob += pulp.lpSum([feed_vars[fid] * available[fid]['cost_kg'] for fid in available])
    prob += pulp.lpSum([feed_vars[fid] for fid in available]) == 100

    for nutrient in nutrients:
        if nutrient in profile:
            req = profile[nutrient]
            prob += pulp.lpSum([feed_vars[fid] * available[fid][nutrient] for fid in available]) >= req['min'] * 100
            prob += pulp.lpSum([feed_vars[fid] * available[fid][nutrient] for fid in available]) <= req['max'] * 100

    for fid, data in available.items():
        prob += feed_vars[fid] >= data['min_incl']
        prob += feed_vars[fid] <= data['max_incl']

    if profile_key in ['1', '2', '3']:
        prob += pulp.lpSum([feed_vars[fid] * (available[fid]['nfc'] - 1.2 * available[fid]['ndf']) for fid in available]) >= 0

    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    strict_optimal = (pulp.LpStatus[prob.status] == 'Optimal')

    # STAGE 2: BEST-EFFORT LP
    if not strict_optimal:
        prob2 = pulp.LpProblem(f"NRC_{profile_key}_besteffort", pulp.LpMinimize)
        feed_vars2 = pulp.LpVariable.dicts("FeedBE", available.keys(), lowBound=0, upBound=100)

        slack_under = {}
        slack_over = {}
        for nutrient in nutrients:
            if nutrient in profile:
                slack_under[nutrient] = pulp.LpVariable(f"under_{nutrient}", lowBound=0)
                slack_over[nutrient] = pulp.LpVariable(f"over_{nutrient}", lowBound=0)

        dairy_slack = None
        if profile_key in ['1', '2', '3']:
            dairy_slack = pulp.LpVariable("dairy_slack", lowBound=0)

        objective = pulp.lpSum([
            100000 * slack_under[n] + 100000 * slack_over[n]
            for n in slack_under
        ])
        if dairy_slack:
            objective += 100000 * dairy_slack
        objective += pulp.lpSum([feed_vars2[fid] * available[fid]['cost_kg'] for fid in available])

        prob2 += objective
        prob2 += pulp.lpSum([feed_vars2[fid] for fid in available]) == 100

        for fid, data in available.items():
            prob2 += feed_vars2[fid] >= data['min_incl']
            prob2 += feed_vars2[fid] <= data['max_incl']

        for nutrient in nutrients:
            if nutrient in profile:
                req = profile[nutrient]
                prob2 += pulp.lpSum([feed_vars2[fid] * available[fid][nutrient] for fid in available]) + slack_under[nutrient] * 100 >= req['min'] * 100
                prob2 += pulp.lpSum([feed_vars2[fid] * available[fid][nutrient] for fid in available]) - slack_over[nutrient] * 100 <= req['max'] * 100

        if profile_key in ['1', '2', '3']:
            prob2 += pulp.lpSum([feed_vars2[fid] * (available[fid]['nfc'] - 1.2 * available[fid]['ndf']) for fid in available]) + dairy_slack * 100 >= 0

        prob2.solve(pulp.PULP_CBC_CMD(msg=0))
        feed_vars = feed_vars2
        best_effort = True
    else:
        best_effort = False

    # BUILD RESULT
    ration = []
    total_cost = 0
    total_nutrients = {n: 0 for n in nutrients}

    for fid in available:
        qty = feed_vars[fid].varValue
        if qty and qty > 0.05:
            cost = qty * available[fid]['cost_kg']
            total_cost += cost
            ration.append({
                'id': fid,
                'name': available[fid]['name'],
                'percentage': qty,
                'kg_per_day': qty / 100 * profile['dmi'],
                'cost_per_day': cost / 100 * profile['dmi'],
                'category': available[fid]['category'],
            })
            for n in nutrients:
                total_nutrients[n] += qty * available[fid][n]

    for n in total_nutrients:
        total_nutrients[n] /= 100

    verification = {}
    low_nutrients = []
    high_nutrients = []
    all_ok = True

    for n in nutrients:
        if n in profile:
            actual = total_nutrients[n]
            req = profile[n]
            in_range = req['min'] <= actual <= req['max']
            if not in_range:
                all_ok = False
                if actual < req['min']:
                    low_nutrients.append(n)
                else:
                    high_nutrients.append(n)
            verification[n] = {
                'actual': actual, 'min': req['min'], 'max': req['max'],
                'status': '✅' if in_range else '⚠️',
                'unit': '%' if n != 'me' else 'Mcal/kg'
            }

    dairy_ok = True
    if profile_key in ['1', '2', '3']:
        nfc_actual = total_nutrients.get('nfc', 0)
        ndf_actual = total_nutrients.get('ndf', 0)
        if nfc_actual < 1.2 * ndf_actual:
            dairy_ok = False
            all_ok = False

    warnings = []
    if best_effort:
        warnings.append(('best_effort_notice', {}))
        for n in low_nutrients:
            v = verification[n]
            warnings.append(('nutrient_low', {'nutrient': n.upper(), 'actual': f"{v['actual']:.1f}{v['unit']}", 'min': f"{v['min']:.1f}", 'max': f"{v['max']:.1f}"}))
        for n in high_nutrients:
            v = verification[n]
            warnings.append(('nutrient_high', {'nutrient': n.upper(), 'actual': f"{v['actual']:.1f}{v['unit']}", 'min': f"{v['min']:.1f}", 'max': f"{v['max']:.1f}"}))
        if not dairy_ok:
            warnings.append(('nfc_ndf_warning', {'nfc': f"{nfc_actual:.1f}", 'ndf': f"{ndf_actual:.1f}"}))

        ai_sugs = suggestion_engine.suggest_for_fix(profile_key, selected_feeds, low_nutrients, high_nutrients)
        if ai_sugs:
            warnings.append(('ai_suggestions', {}))
            for i, sug in enumerate(ai_sugs, 1):
                num = ID_TO_NUMBER.get(sug['id'], '?')
                reasons = ", ".join(sug['reasons']) if sug['reasons'] else "balanced"
                warnings.append(('ai_item', {'i': i, 'num': num, 'name': sug['name'], 'cost': sug['cost'], 'reasons': reasons}))

    result = {
        'profile': profile['name'], 'dmi': profile['dmi'],
        'total_cost_per_day': total_cost / 100 * profile['dmi'],
        'cost_per_kg_dm': total_cost / 100,
        'ration': ration, 'verification': verification,
        'best_effort': best_effort,
        'warnings': warnings
    }

    return result, None

# ============================================================
# IMAGE RECOGNITION (Google Vision)
# ============================================================
FEED_LABELS = {
    'maize': '1', 'corn': '1', 'grain': '1', 'cereal': '1', 'yellow': '1',
    'cotton': '6', 'seed': '6', 'cake': '6',
    'grass': '11', 'hay': '14', 'fodder': '11', 'green': '11', 'leaf': '11', 'napier': '11',
    'dairy': '16', 'meal': '16', 'concentrate': '16', 'pellet': '16', 'bag': '16',
    'wheat': '2', 'bran': '1',
    'molasses': '5', 'syrup': '5', 'sweet': '5', 'dark': '5',
    'limestone': '18', 'chalk': '18', 'mineral': '20', 'white': '18', 'powder': '18',
    'phosphate': '19', 'dcp': '19',
}

def detect_feeds_from_image(image_url):
    if not GOOGLE_API_KEY:
        return None, "⚠️ Image recognition not configured."
    try:
        img_data = requests.get(image_url, timeout=10).content
        encoded = base64.b64encode(img_data).decode('utf-8')
        vision_url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_API_KEY}"
        payload = {"requests": [{"image": {"content": encoded}, "features": [{"type": "LABEL_DETECTION", "maxResults": 15}]}]}
        resp = requests.post(vision_url, json=payload, timeout=15)
        result = resp.json()
        if 'error' in result:
            return None, f"Vision API error: {result['error']['message']}"
        labels = [a['description'].lower() for a in result['responses'][0].get('labelAnnotations', [])]
        detected = set()
        for label in labels:
            for keyword, feed_num in FEED_LABELS.items():
                if keyword in label:
                    detected.add(feed_num)
        return list(detected), None
    except Exception as e:
        return None, f"Image analysis failed: {str(e)}"


# ============================================================
# M-PESA DARAJA INTEGRATION
# ============================================================
def get_mpesa_access_token():
    """Get M-Pesa access token from Daraja API."""
    if not MPESA_CONSUMER_KEY or not MPESA_CONSUMER_SECRET:
        return None
    try:
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        if MPESA_ENV == "production":
            url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        resp = requests.get(url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET), timeout=10)
        data = resp.json()
        return data.get('access_token')
    except Exception:
        return None

def initiate_stk_push(phone, amount, account_ref, callback_url):
    """Initiate M-Pesa STK Push to farmer's phone."""
    token = get_mpesa_access_token()
    if not token:
        return None, "M-Pesa credentials not configured"

    try:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode()

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        if MPESA_ENV == "production":
            url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

        payload = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": callback_url,
            "AccountReference": account_ref[:12],
            "TransactionDesc": "BalancedBora Feed"
        }

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        data = resp.json()

        if data.get("ResponseCode") == "0":
            return data.get("CheckoutRequestID"), None
        else:
            return None, data.get("ResponseDescription", "Unknown M-Pesa error")
    except Exception as e:
        return None, str(e)


# ============================================================
# SUPPLIER FORMATTING
# ============================================================
def format_suppliers(phone, ration):
    """Format supplier contacts for the ration ingredients."""
    m = lambda k, **kw: get_msg(phone, k, **kw)
    region = user_sessions.get(phone, {}).get('region')

    lines = [f"\n*{m('supplier_header')}*"]

    for item in ration:
        feed_id = item['id']
        suppliers = SUPPLIERS_DB.get(feed_id, [])

        if region and suppliers:
            local = [s for s in suppliers if s['region'] == region]
            others = [s for s in suppliers if s['region'] != region]
            suppliers = local + others

        if suppliers:
            lines.append(f"\n*{item['name']}:*")
            for i, s in enumerate(suppliers[:2], 1):
                lines.append(f"{i}. {s['name']} 📞 {s['phone']} ({s['region']}, KES {s['price']}/kg)")
        else:
            lines.append(f"\n*{item['name']}:* {m('no_supplier')}")

    lines.append(f"\n{m('order_prompt')}")
    return "\n".join(lines)


# ============================================================
# MESSAGE BUILDERS
# ============================================================
def format_ration(phone, result):
    m = lambda k, **kw: get_msg(phone, k, **kw)

    header = m('ration_besteffort') if result.get('best_effort') else m('ration_optimal')

    msg = (
        f"{header}\n"
        f"{m('profile_label')} {result['profile']}\n"
        f"{m('dmi_label')}: {result['dmi']:.1f} {m('kg_day')}\n"
        f"{m('total_cost_label')}: *{m('kes_day')} {result['total_cost_per_day']:.0f}*\n"
        f"{m('cost_per_kg_label')}: {m('kes_day')} {result['cost_per_kg_dm']:.2f}\n\n"
        f"*{m('mix_header')}*\n"
    )
    for item in result['ration']:
        msg += f"• {item['name']}: {item['percentage']:.1f}% ({item['kg_per_day']:.2f} {m('kg_day')}) — {m('kes_day')} {item['cost_per_day']:.0f}\n"

    msg += f"\n{m('how_to_feed')}\n"

    if result.get('warnings'):
        msg += f"\n*{m('notes_header')}*\n"
        for warn_key, warn_kwargs in result['warnings']:
            if warn_key == 'ai_item':
                msg += f"{warn_kwargs['i']}. #{warn_kwargs['num']} {warn_kwargs['name']} ({m('kes_day')} {warn_kwargs['cost']}/kg) — {warn_kwargs['reasons']}\n"
            else:
                msg += m(warn_key, **warn_kwargs) + "\n"

    msg += f"\n{m('start_again')}"

    # ADD SUPPLIERS
    msg += format_suppliers(phone, result['ration'])

    return msg

# ============================================================
# ADMIN DASHBOARD
# ============================================================
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "balancedbora2024")

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>BalancedBora Admin</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            h1 { color: #2c5530; }
            .card { background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { text-align: left; padding: 10px; border-bottom: 1px solid #ddd; }
            th { background: #2c5530; color: white; }
            tr:hover { background: #f9f9f9; }
            input, select { padding: 8px; margin: 5px 0; width: 100%; box-sizing: border-box; }
            button { background: #2c5530; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #1e3d21; }
            .delete-btn { background: #c0392b; }
            .delete-btn:hover { background: #a93226; }
            .nav { margin-bottom: 20px; }
            .nav a { color: #2c5530; text-decoration: none; margin-right: 15px; font-weight: bold; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
            .stat-box { background: #2c5530; color: white; padding: 15px; border-radius: 8px; text-align: center; }
            .stat-box h3 { margin: 0; font-size: 2em; }
            .stat-box p { margin: 5px 0 0; opacity: 0.9; }
        </style>
    </head>
    <body>
        <h1>🐄 BalancedBora Admin Dashboard</h1>
        <div class="nav">
            <a href="/admin">Dashboard</a>
            <a href="/admin/suppliers">Suppliers</a>
            <a href="/admin/add-supplier">Add Supplier</a>
            <a href="/admin/orders">Orders</a>
        </div>
        <div class="stats">
            <div class="stat-box"><h3>""" + str(len(SUPPLIERS_DB)) + """</h3><p>Feed Types with Suppliers</p></div>
            <div class="stat-box"><h3>""" + str(sum(len(v) for v in SUPPLIERS_DB.values())) + """</h3><p>Total Suppliers</p></div>
            <div class="stat-box"><h3>""" + str(len(user_sessions)) + """</h3><p>Active Sessions</p></div>
            <div class="stat-box"><h3>""" + str(len(orders_db)) + """</h3><p>Total Orders</p></div>
        </div>
        <div class="card">
            <h2>Quick Actions</h2>
            <p><a href="/admin/suppliers"><button>Manage Suppliers</button></a></p>
            <p><a href="/admin/add-supplier"><button>Add New Supplier</button></a></p>
        </div>
    </body>
    </html>
    """
    return html

@app.get("/admin/suppliers", response_class=HTMLResponse)
def admin_suppliers():
    rows = ""
    for feed_id, suppliers in SUPPLIERS_DB.items():
        feed_name = FEEDS_DB.get(feed_id, {}).get('name', feed_id)
        for s in suppliers:
            rows += f"""
            <tr>
                <td>{feed_name}</td>
                <td>{s['name']}</td>
                <td>{s['phone']}</td>
                <td>{s['region']}</td>
                <td>KES {s['price']}</td>
                <td>
                    <form method="post" action="/admin/delete-supplier" style="display:inline;">
                        <input type="hidden" name="feed_id" value="{feed_id}">
                        <input type="hidden" name="supplier_id" value="{s['id']}">
                        <button type="submit" class="delete-btn" onclick="return confirm('Delete this supplier?')">Delete</button>
                    </form>
                </td>
            </tr>
            """

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Suppliers - BalancedBora</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            h1 { color: #2c5530; }
            .card { background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { text-align: left; padding: 10px; border-bottom: 1px solid #ddd; }
            th { background: #2c5530; color: white; }
            tr:hover { background: #f9f9f9; }
            button { background: #2c5530; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            .delete-btn { background: #c0392b; padding: 5px 10px; }
            .nav { margin-bottom: 20px; }
            .nav a { color: #2c5530; text-decoration: none; margin-right: 15px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🐄 Suppliers</h1>
        <div class="nav">
            <a href="/admin">Dashboard</a>
            <a href="/admin/suppliers">Suppliers</a>
            <a href="/admin/add-supplier">Add Supplier</a>
            <a href="/admin/orders">Orders</a>
        </div>
        <div class="card">
            <h2>All Registered Suppliers</h2>
            <table>
                <tr><th>Feed</th><th>Name</th><th>Phone</th><th>Region</th><th>Price</th><th>Action</th></tr>
                """ + rows + """
            </table>
        </div>
    </body>
    </html>
    """
    return html

@app.get("/admin/add-supplier", response_class=HTMLResponse)
def admin_add_supplier_form():
    feed_options = ""
    for num, fid in FEED_NUMBER_MAP.items():
        name = FEEDS_DB.get(fid, {}).get('name', fid)
        feed_options += f'<option value="{fid}">{num}. {name}</option>'

    region_options = ""
    for num, reg in REGIONS.items():
        region_options += f'<option value="{reg}">{reg}</option>'

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Supplier - BalancedBora</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            h1 { color: #2c5530; }
            .card { background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            input, select { padding: 10px; margin: 8px 0; width: 100%; box-sizing: border-box; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #2c5530; color: white; padding: 12px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            button:hover { background: #1e3d21; }
            .nav { margin-bottom: 20px; }
            .nav a { color: #2c5530; text-decoration: none; margin-right: 15px; font-weight: bold; }
            label { font-weight: bold; color: #333; }
        </style>
    </head>
    <body>
        <h1>🐄 Add New Supplier</h1>
        <div class="nav">
            <a href="/admin">Dashboard</a>
            <a href="/admin/suppliers">Suppliers</a>
            <a href="/admin/add-supplier">Add Supplier</a>
            <a href="/admin/orders">Orders</a>
        </div>
        <div class="card">
            <form method="post" action="/admin/add-supplier">
                <label>Feed Type</label>
                <select name="feed_id" required>""" + feed_options + """</select>

                <label>Supplier Name</label>
                <input type="text" name="name" placeholder="e.g. Central Feeds Ltd" required>

                <label>Phone Number</label>
                <input type="text" name="phone" placeholder="+254712345678" required>

                <label>Region</label>
                <select name="region" required>""" + region_options + """</select>

                <label>Price per kg (KES)</label>
                <input type="number" name="price" placeholder="25" required>

                <button type="submit">Add Supplier</button>
            </form>
        </div>
    </body>
    </html>
    """
    return html

@app.post("/admin/add-supplier")
def admin_add_supplier_post(
    feed_id: str = Form(...),
    name: str = Form(...),
    phone: str = Form(...),
    region: str = Form(...),
    price: int = Form(...)
):
    import uuid
    supplier = {
        "id": f"sup_{uuid.uuid4().hex[:8]}",
        "name": name,
        "phone": phone,
        "region": region,
        "price": price
    }
    if feed_id not in SUPPLIERS_DB:
        SUPPLIERS_DB[feed_id] = []
    SUPPLIERS_DB[feed_id].append(supplier)
    save_suppliers(SUPPLIERS_DB)

    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html><head><meta http-equiv="refresh" content="2;url=/admin/suppliers"></head>
    <body style="font-family:Arial; text-align:center; padding:50px;">
        <h2 style="color:#2c5530;">✅ Supplier Added Successfully!</h2>
        <p>Redirecting to suppliers list...</p>
    </body></html>
    """)

@app.post("/admin/delete-supplier")
def admin_delete_supplier(feed_id: str = Form(...), supplier_id: str = Form(...)):
    if feed_id in SUPPLIERS_DB:
        SUPPLIERS_DB[feed_id] = [s for s in SUPPLIERS_DB[feed_id] if s['id'] != supplier_id]
        if not SUPPLIERS_DB[feed_id]:
            del SUPPLIERS_DB[feed_id]
        save_suppliers(SUPPLIERS_DB)

    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html><head><meta http-equiv="refresh" content="2;url=/admin/suppliers"></head>
    <body style="font-family:Arial; text-align:center; padding:50px;">
        <h2 style="color:#c0392b;">🗑️ Supplier Deleted</h2>
        <p>Redirecting to suppliers list...</p>
    </body></html>
    """)

@app.get("/admin/orders", response_class=HTMLResponse)
def admin_orders():
    rows = ""
    for phone, orders in orders_db.items():
        for order in orders:
            items = "<br>".join([f"{it['name']}: {it['kg']}kg @ KES {it['price']}/kg" for it in order.get('items', [])])
            status_color = "#2c5530" if order.get('paid') else "#e67e22"
            status_text = "PAID" if order.get('paid') else "PENDING"
            rows += f"""
            <tr>
                <td>{phone}</td>
                <td>{items}</td>
                <td>KES {order.get('total', 0)}</td>
                <td style="color:{status_color}; font-weight:bold;">{status_text}</td>
                <td>{order.get('supplier_phone', 'N/A')}</td>
                <td>{order.get('timestamp', 'N/A')}</td>
            </tr>
            """

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Orders - BalancedBora</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
            h1 { color: #2c5530; }
            .card { background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { text-align: left; padding: 10px; border-bottom: 1px solid #ddd; }
            th { background: #2c5530; color: white; }
            tr:hover { background: #f9f9f9; }
            .nav { margin-bottom: 20px; }
            .nav a { color: #2c5530; text-decoration: none; margin-right: 15px; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>🐄 Orders</h1>
        <div class="nav">
            <a href="/admin">Dashboard</a>
            <a href="/admin/suppliers">Suppliers</a>
            <a href="/admin/add-supplier">Add Supplier</a>
            <a href="/admin/orders">Orders</a>
        </div>
        <div class="card">
            <h2>All Orders</h2>
            <table>
                <tr><th>Farmer</th><th>Items</th><th>Total</th><th>Status</th><th>Supplier</th><th>Time</th></tr>
                """ + (rows if rows else "<tr><td colspan='6' style='text-align:center;'>No orders yet</td></tr>") + """
            </table>
        </div>
    </body>
    </html>
    """
    return html

# ============================================================
# WEBHOOK
# ============================================================
@app.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(default=""),
    From: str = Form(default=""),
    NumMedia: str = Form(default="0"),
    MediaUrl0: str = Form(default=""),
    MediaContentType0: str = Form(default="")
):
    phone = From.replace("whatsapp:", "")
    text = Body.strip().lower()
    num_media = int(NumMedia)

    if phone not in user_sessions:
        user_sessions[phone] = {'step': -1}

    session = user_sessions[phone]
    resp = MessagingResponse()
    msg = resp.message()

    # HANDLE IMAGE
    if num_media > 0 and 'image' in MediaContentType0:
        detected, error = detect_feeds_from_image(MediaUrl0)
        if error:
            msg.body(error + "\n\n" + get_msg(phone, 'choose_language'))
            session['step'] = -1
            return Response(content=str(resp), media_type="application/xml")
        if not detected:
            msg.body(get_msg(phone, 'photo_not_found') + "\n\n" + get_msg(phone, 'feed_selection'))
            session['step'] = 2
            return Response(content=str(resp), media_type="application/xml")
        session['ai_detected_feeds'] = detected
        session['step'] = 2
        feed_names = [FEEDS_DB[FEED_NUMBER_MAP[n]]['name'] for n in detected if n in FEED_NUMBER_MAP]
        msg.body(get_msg(phone, 'photo_detected', feeds=', '.join(feed_names)))
        return Response(content=str(resp), media_type="application/xml")

    # HANDLE VOICE
    if num_media > 0 and 'audio' in MediaContentType0:
        msg.body(get_msg(phone, 'voice_soon') + "\n\n" + get_msg(phone, 'choose_animal'))
        session['step'] = 1
        return Response(content=str(resp), media_type="application/xml")

    # HANDLE TEXT
    if text in ['start', 'hi', 'hello', 'help', '0']:
        session['step'] = -1
        session['profile'] = None
        session['feeds'] = None
        session['region'] = None
        session['last_ration'] = None
        session.pop('ai_detected_feeds', None)
        session.pop('order_items', None)
        msg.body(get_msg(phone, 'choose_language'))
        return Response(content=str(resp), media_type="application/xml")

    # LANGUAGE SELECTION (Step -1)
    if session['step'] == -1:
        if text in LANG_MAP:
            session['lang'] = LANG_MAP[text]
            session['step'] = 0
            msg.body(get_msg(phone, 'choose_region'))
        else:
            msg.body(get_msg(phone, 'choose_language'))
        return Response(content=str(resp), media_type="application/xml")

    # REGION SELECTION (Step 0)
    if session['step'] == 0:
        if text in REGIONS:
            session['region'] = REGIONS[text]
            session['step'] = 1
            msg.body(get_msg(phone, 'welcome') + "\n\n" + get_msg(phone, 'choose_animal'))
        elif text == '0':
            session['region'] = None
            session['step'] = 1
            msg.body(get_msg(phone, 'welcome') + "\n\n" + get_msg(phone, 'choose_animal'))
        else:
            msg.body(get_msg(phone, 'choose_region'))
        return Response(content=str(resp), media_type="application/xml")

    # Confirm AI-detected feeds
    if session.get('step') == 2 and 'ai_detected_feeds' in session and text in ['yes', 'yep', 'sawa', 'correct', 'ndio', 'ii']:
        feed_ids = [FEED_NUMBER_MAP[n] for n in session['ai_detected_feeds'] if n in FEED_NUMBER_MAP]
        try:
            result, error = solve_nrc_ration(session['profile'], feed_ids)
        except Exception as e:
            traceback.print_exc()
            msg.body("❌ Something went wrong calculating your ration. Please try different feeds or send START to restart.")
            session.pop('ai_detected_feeds', None)
            session['step'] = 0
            return Response(content=str(resp), media_type="application/xml")
        session.pop('ai_detected_feeds', None)
        if error:
            if error == "NO_FORAGE":
                msg.body(get_msg(phone, 'no_forage_error'))
            elif isinstance(error, tuple) and error[0] == "IMPOSSIBLE_MINS":
                msg.body(get_msg(phone, 'impossible_mins', total_min=error[1], offenders=', '.join(error[2])))
            else:
                msg.body("❌ " + str(error) + "\n\n" + get_msg(phone, 'start_again'))
            session['step'] = 0
        else:
            session['last_ration'] = result
            msg.body(format_ration(phone, result))
            session['step'] = 3
        return Response(content=str(resp), media_type="application/xml")

    # Step 1: Select animal
    if session['step'] == 1:
        if text in ANIMAL_PROFILES:
            session['profile'] = text
            session['step'] = 2
            msg.body(get_msg(phone, 'feed_selection'))
        else:
            msg.body(get_msg(phone, 'invalid_animal') + "\n\n" + get_msg(phone, 'choose_animal'))
        return Response(content=str(resp), media_type="application/xml")

    # Step 2: Select feeds
    if session['step'] == 2:
        selected_nums = [s.strip() for s in text.split(",") if s.strip() in FEED_NUMBER_MAP]
        if len(selected_nums) < 2:
            msg.body(get_msg(phone, 'select_at_least_2') + "\n\n" + get_msg(phone, 'feed_selection'))
            return Response(content=str(resp), media_type="application/xml")

        feed_ids = [FEED_NUMBER_MAP[n] for n in selected_nums]
        try:
            result, error = solve_nrc_ration(session['profile'], feed_ids)
        except Exception as e:
            traceback.print_exc()
            msg.body("❌ Something went wrong calculating your ration. Please try different feeds or send START to restart.")
            session['step'] = 0
            return Response(content=str(resp), media_type="application/xml")

        if error:
            if error == "NO_FORAGE":
                msg.body(get_msg(phone, 'no_forage_error'))
            elif isinstance(error, tuple) and error[0] == "IMPOSSIBLE_MINS":
                msg.body(get_msg(phone, 'impossible_mins', total_min=error[1], offenders=', '.join(error[2])))
            else:
                msg.body("❌ " + str(error) + "\n\n" + get_msg(phone, 'start_again'))
            session['step'] = 0
        else:
            session['last_ration'] = result
            msg.body(format_ration(phone, result))
            session['step'] = 3

        return Response(content=str(resp), media_type="application/xml")

    # Step 3: Order menu (after ration shown)
    if session['step'] == 3:
        if text == 'order':
            ration = session.get('last_ration', {})
            if not ration or not ration.get('ration'):
                msg.body(get_msg(phone, 'generic_help'))
                return Response(content=str(resp), media_type="application/xml")

            # Build order menu
            lines = [get_msg(phone, 'order_instructions') + "\n"]
            for i, item in enumerate(ration['ration'], 1):
                lines.append(f"{i}. {item['name']}")
            msg.body("\n".join(lines))
            session['step'] = 4
            return Response(content=str(resp), media_type="application/xml")
        else:
            msg.body(get_msg(phone, 'generic_help'))
            return Response(content=str(resp), media_type="application/xml")

    # Step 4: Parse order quantities
    if session['step'] == 4:
        ration = session.get('last_ration', {})
        if not ration or not ration.get('ration'):
            msg.body(get_msg(phone, 'generic_help'))
            session['step'] = 0
            return Response(content=str(resp), media_type="application/xml")

        try:
            order_items = []
            total = 0
            parts = text.split(",")
            for part in parts:
                idx_qty = part.strip().split(":")
                if len(idx_qty) != 2:
                    raise ValueError("Invalid format")
                idx = int(idx_qty[0].strip()) - 1
                qty = float(idx_qty[1].strip())
                if idx < 0 or idx >= len(ration['ration']):
                    raise ValueError("Invalid feed number")

                item = ration['ration'][idx]
                feed_id = item['id']
                # Get supplier price if available, else use default
                suppliers = SUPPLIERS_DB.get(feed_id, [])
                region = session.get('region')
                price = item.get('cost_per_day', 0)  # fallback
                supplier_phone = None
                supplier_name = "Direct"

                if suppliers:
                    # Pick cheapest supplier in region, or cheapest overall
                    if region:
                        local = [s for s in suppliers if s['region'] == region]
                        if local:
                            supplier = min(local, key=lambda x: x['price'])
                        else:
                            supplier = min(suppliers, key=lambda x: x['price'])
                    else:
                        supplier = min(suppliers, key=lambda x: x['price'])
                    price = supplier['price']
                    supplier_phone = supplier['phone']
                    supplier_name = supplier['name']

                cost = qty * price
                total += cost
                order_items.append({
                    'name': item['name'],
                    'kg': qty,
                    'price': price,
                    'cost': cost,
                    'supplier_name': supplier_name,
                    'supplier_phone': supplier_phone,
                    'feed_id': feed_id
                })

            session['order_items'] = order_items
            session['order_total'] = total

            items_str = "\n".join([f"• {it['name']}: {it['kg']}kg x KES {it['price']} = KES {it['cost']:.0f}" for it in order_items])
            msg.body(get_msg(phone, 'order_summary', items=items_str, total=f"{total:.0f}"))
            session['step'] = 5
            return Response(content=str(resp), media_type="application/xml")

        except Exception as e:
            msg.body(get_msg(phone, 'order_invalid'))
            return Response(content=str(resp), media_type="application/xml")

    # Step 5: M-Pesa phone number
    if session['step'] == 5:
        mpesa_phone = text.strip()
        if not mpesa_phone.startswith("254") or len(mpesa_phone) != 12:
            msg.body(get_msg(phone, 'payment_prompt'))
            return Response(content=str(resp), media_type="application/xml")

        order_items = session.get('order_items', [])
        total = session.get('order_total', 0)

        if not MPESA_CONSUMER_KEY or not MPESA_PASSKEY or not BASE_URL:
            # M-Pesa not configured — give supplier direct contact
            supplier_phone = order_items[0].get('supplier_phone') if order_items else None
            msg.body(get_msg(phone, 'mpesa_not_configured', phone=supplier_phone or "your local agrovet"))
            session['step'] = 0
            return Response(content=str(resp), media_type="application/xml")

        # Initiate STK Push
        callback = f"{BASE_URL}/mpesa/callback"
        checkout_id, error = initiate_stk_push(mpesa_phone, total, f"BB{phone[-6:]}", callback)

        if error:
            msg.body(get_msg(phone, 'payment_failed', reason=str(error)))
            session['step'] = 0
            return Response(content=str(resp), media_type="application/xml")

        # Save order pending payment
        order = {
            'items': order_items,
            'total': total,
            'phone': phone,
            'mpesa_phone': mpesa_phone,
            'checkout_id': checkout_id,
            'paid': False,
            'timestamp': datetime.now().isoformat()
        }
        if phone not in orders_db:
            orders_db[phone] = []
        orders_db[phone].append(order)
        session['pending_checkout'] = checkout_id

        msg.body(get_msg(phone, 'payment_initiated', phone=mpesa_phone))
        session['step'] = 6
        return Response(content=str(resp), media_type="application/xml")

    # Step 6: Waiting for payment
    if session['step'] == 6:
        msg.body("⏳ Please check your phone and enter M-Pesa PIN.\nSend START to cancel.")
        return Response(content=str(resp), media_type="application/xml")

    msg.body(get_msg(phone, 'generic_help'))
    return Response(content=str(resp), media_type="application/xml")


# ============================================================
# M-PESA CALLBACK
# ============================================================
@app.post("/mpesa/callback")
async def mpesa_callback(request: Request):
    try:
        data = await request.json()
        result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
        checkout_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')

        # Find order
        for phone, orders in orders_db.items():
            for order in orders:
                if order.get('checkout_id') == checkout_id:
                    if result_code == 0:
                        order['paid'] = True
                        # Notify farmer via Twilio
                        if client:
                            supplier = order['items'][0]['supplier_name'] if order['items'] else "Supplier"
                            supplier_phone = order['items'][0]['supplier_phone'] if order['items'] else ""
                            message = get_msg(phone, 'payment_success', supplier=supplier, phone=supplier_phone)
                            try:
                                client.messages.create(
                                    from_=TWILIO_NUMBER,
                                    to=f"whatsapp:{phone}",
                                    body=message
                                )
                            except Exception:
                                pass
                        # Notify supplier
                        if client and order['items']:
                            sup_phone = order['items'][0].get('supplier_phone')
                            if sup_phone:
                                try:
                                    farmer_order = "\n".join([f"{it['name']}: {it['kg']}kg" for it in order['items']])
                                    client.messages.create(
                                        from_=TWILIO_NUMBER,
                                        to=f"whatsapp:{sup_phone}",
                                        body=f"🐄 NEW ORDER from {phone}\n{farmer_order}\nTotal: KES {order['total']}\nPlease arrange delivery."
                                    )
                                except Exception:
                                    pass
                    else:
                        order['paid'] = False
                        order['failure_reason'] = data.get('Body', {}).get('stkCallback', {}).get('ResultDesc', 'Unknown')
                    break

        return {"ResultCode": 0, "ResultDesc": "Accepted"}
    except Exception:
        return {"ResultCode": 0, "ResultDesc": "Accepted"}