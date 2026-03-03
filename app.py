import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import time
import random

# --- 1. AYARLAR & VERİ SİSTEMİ ---
VERI_DOSYASI = "nida_v60_final.json"
HOCA_TEL = "905307368072"

def veri_yukle():
    if os.path.exists(VERI_DOSYASI):
        try:
            with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {"ogrenciler": {}}
    return {"ogrenciler": {}}

def veri_kaydet(veri):
    with open(VERI_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = veri_yukle()

# --- 2. MÜFREDAT ---
M_LGS = {"Matematik": ["Çarpanlar Katlar", "Üslü İfadeler", "Kareköklü", "Veri Analizi", "Olasılık", "Cebirsel", "Denklemler", "Eşitsizlikler", "Üçgenler", "Eşlik Benzerlik", "Dönüşüm", "Geometrik Cisimler"], "Fen Bilimleri": ["Mevsimler", "DNA", "Basınç", "Madde", "Basit Makineler", "Enerji", "Elektrik"], "Türkçe": ["Anlam Bilgisi", "Paragraf", "Fiilimsiler", "Cümlenin Ögeleri", "Yazım-Noktalama", "Söz Sanatları", "Anlatım Bozukluğu"], "İnkılap": ["Bir Kahraman Doğuyor", "Milli Uyanış", "Ya İstiklal", "Atatürkçülük", "Dış Politika"], "Din / İngilizce": ["Kader", "Zekat", "Din ve Hayat", "Hz. Muhammed", "Friendship", "Teen Life", "Kitchen", "Internet"]}
M_YKS = {"TYT Matematik": ["Temel Kavramlar", "Sayılar", "Problemler", "Fonksiyonlar"], "AYT Matematik": ["Trigonometri", "Logaritma", "Türev", "İntegral"], "Türkçe & Edebiyat": ["Paragraf", "Dil Bilgisi", "Edebiyat Akımları"], "TYT Fizik": ["Optik", "Dalgalar"], "AYT Fizik": ["Momentum", "Elektrik"], "TYT Kimya": ["Atom"], "AYT Kimya": ["Organik"], "TYT Biyoloji": ["Hücre"], "AYT Biyoloji": ["Sistemler"], "Tarih-Coğrafya": ["Osmanlı", "İklim"]}

# --- 3. TASARIM ---
st.set_page_config(page_title="Nida Akademi v60", layout="wide")
st.markdown("<style>.stApp { background-color: #0d1117; color: white; }</style>", unsafe_allow_html=True)

# --- 4. GİRİŞ ---
if "logged_in" not in st.session_state:
    st.title("🎓 Nida Akademi Giriş")
    u_in = st.text_input("Ad Soyad")
    p_in = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        if u_in == "admin" and p_in == "nida2024":
            st.session_state.update({"logged_in": True, "role": "admin"})
            st.rerun()
        elif u_in in st.session_state.db.get("ogrenciler", {}):
            if st.session_state.db["ogrenciler"][u_in].get("sifre") == p_in:
                st.session_state.update({"logged_in": True, "role": "ogrenci", "user": u_in})
                st.rerun()
else:
    # --- 5. ADMIN PANELİ ---
    if st.session_state["role"] == "admin":
        st.sidebar.title("Nida Hocam")
        menu = st.sidebar.radio("Menü", ["Öğrenci Kaydı", "Analiz & Veli Raporları"])
        if st.sidebar.button("🔴 Çıkış"): del st.session_state["logged_in"]; st.rerun()

        if menu == "Öğrenci Kaydı":
            ad = st.text_input("Ad Soyad")
            grp = st.selectbox("Sınav Grubu", ["LGS", "YKS"])
            v_t = st.text_input("Veli Tel (905...)")
            if st.button("Kaydet"):
                s = str(random.randint(1000, 9999))
                st.session_state.db["ogrenciler"][ad] = {"soru": [], "denemeler": [], "sinav": grp, "v_tel": v_t, "sifre": s, "gunluk_puanlar": []}
                veri_kaydet(st.session_state.db); st.success(f"Şifre: {s}")

        elif menu == "Analiz & Veli Raporları":
            ogrenciler = list(st.session_state.db.get("ogrenciler", {}).keys())
            if ogrenciler:
                sec = st.selectbox("Öğrenci Seç", ogrenciler)
                o = st.session_state.db["ogrenciler"][sec]
                
                # SEKMELİ ANALİZ
                a1, a2, a3 = st.tabs(["📊 Çalışma Geçmişi", "🧠 Mod & Psikoloji", "🏆 Denemeler"])
                
                with a1:
                    st.subheader("📚 Soru Çözüm Detayları")
                    if o["soru"]:
                        st.table(pd.DataFrame(o["soru"]).tail(10)) # Son 10 çalışma
                    else: st.info("Henüz soru girişi yok.")
                
                with a2:
                    st.subheader("🌈 Günlük Mod Takibi")
                    if o.get("gunluk_puanlar"):
                        st.table(pd.DataFrame(o["gunluk_puanlar"]))
                    else: st.info("Mod kaydı yok.")
                
                with a3:
                    st.subheader("📝 Deneme Sonuçları")
                    if o.get("denemeler"):
                        st.write(o["denemeler"])
                    else: st.info("Deneme kaydı yok.")

                # VELİYE MESAJ
                v_msg = f"Sayın Veli, {sec} bugünkü programını tamamladı. Detaylar için iletişime geçebilirsiniz. - Nida GÖMCELİ"
                st.markdown(f'<a href="https://wa.me/{o["v_tel"]}?text={urllib.parse.quote(v_msg)}" target="_blank" style="background-color:#25D366; color:white; padding:12px; text-decoration:none; border-radius:10px;">📱 VELİYE WHATSAPP AT</a>', unsafe_allow_html=True)

    # --- 6. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        m = M_LGS if o["sinav"] == "LGS" else M_YKS
        st.title(f"Selam {u} ✨")
        if st.button("Çıkış"): del st.session_state["logged_in"]; st.rerun()

        st.subheader("⏱️ Kronometre")
        if 'elapsed_time' not in st.session_state: st.session_state.elapsed_time = 0
        if 'running' not in st.session_state: st.session_state.running = False
        c1, c2, c3 = st.columns(3)
        if c1.button("▶️ Başlat"): st.session_state.start_time = time.time() - st.session_state.elapsed_time; st.session_state.running = True
        if c2.button("⏸️ Durdur"): st.session_state.running = False
        if c3.button("🔄 Sıfırla"): st.session_state.elapsed_time = 0; st.session_state.running = False
        if st.session_state.running: st.session_state.elapsed_time = time.time() - st.session_state.start_time
        mins, secs = divmod(int(st.session_state.elapsed_time), 60)
        st.header(f"{mins:02d}:{secs:02d}")
        if st.session_state.running: time.sleep(1); st.rerun()

        tabs = st.tabs(["🌟 Modum", "📝 Çalışma", "📊 Müfredat", "🏆 Deneme"])
        with tabs[0]:
            p = st.slider("Puan", 1, 10, 5); md = st.selectbox("Mod", ["Mutlu", "Yorgun", "Stresli"])
            if st.button("Kaydet"):
                o["gunluk_puanlar"].append({"Tarih": datetime.now().strftime("%d/%m"), "Puan": p, "Mod": md})
                veri_kaydet(st.session_state.db); st.success("Kaydedildi")
        with tabs[1]:
            d = st.selectbox("Ders", list(m.keys())); k = st.selectbox("Konu", m[d])
            soru = st.number_input("Soru", 0); sure = st.number_input("Süre", value=mins)
            if st.button("Ekle"):
                o["soru"].append({"Tarih": datetime.now().strftime("%d/%m %H:%M"), "Ders": d, "Konu": k, "Soru": soru, "Sure": sure})
                veri_kaydet(st.session_state.db); st.success("Eklendi")
        with tabs[3]:
            st.subheader("🏆 Deneme Girişi")
            for b in m.keys():
                st.number_input(f"{b} Doğru", 0, key=f"d_{b}")
            if st.button("Denemeyi Kaydet"):
                st.success("Kaydedildi!")
