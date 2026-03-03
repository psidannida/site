import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import time
import random

# --- 1. AYARLAR & VERİ SİSTEMİ ---
VERI_DOSYASI = "nida_v62_final.json"
HOCA_TEL = "905307368072"
KONU_BARAJI = 150 

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
M_YKS = {"TYT Matematik": ["Temel Kavramlar", "Sayılar", "Problemler", "Kümeler", "Fonksiyonlar", "Permütasyon-Olasılık"], "AYT Matematik": ["Polinomlar", "Trigonometri", "Logaritma", "Diziler", "Limit", "Türev", "İntegral"], "Türkçe & Edebiyat": ["Paragraf", "Dil Bilgisi", "Şiir Bilgisi", "Edebiyat Akımları", "Dönemler"], "TYT Fizik": ["Madde", "Kuvvet", "Enerji", "Optik", "Dalgalar"], "AYT Fizik": ["Atışlar", "Momentum", "Tork", "Elektrik", "Manyetizma"], "TYT Kimya": ["Atom", "Maddenin Halleri", "Karışımlar"], "AYT Kimya": ["Gazlar", "Enerji", "Denge", "Organik"], "TYT Biyoloji": ["Hücre", "Kalıtım"], "AYT Biyoloji": ["Sistemler", "Genden Proteine", "Bitki Biyolojisi"], "Tarih-Coğrafya": ["Osmanlı", "İnkılap", "İklim", "Nüfus"]}

# --- 3. TASARIM ---
st.set_page_config(page_title="Nida Akademi v62", layout="wide")
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
        else: st.error("Bilgiler hatalı!")
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
                
                a1, a2, a3, a4 = st.tabs(["📊 Müfredat İlerleme", "📝 Çalışma Tablosu", "🧠 Mod Takibi", "🏆 Denemeler"])
                
                with a1:
                    df_ana = pd.DataFrame(o.get("soru", []))
                    m_liste = M_LGS if o["sinav"] == "LGS" else M_YKS
                    for d_adi, konular in m_liste.items():
                        coz = df_ana[df_ana['Ders'] == d_adi]['Toplam'].sum() if not df_ana.empty else 0
                        yuzde = min(int(coz / (len(konular) * KONU_BARAJI) * 100), 100)
                        st.write(f"*{d_adi}* - Toplam Soru: {coz}"); st.progress(yuzde / 100)
                
                with a2:
                    if o["soru"]: st.table(pd.DataFrame(o["soru"]))
                    else: st.info("Veri yok.")

                # --- GELİŞMİŞ VELİ MESAJI OLUŞTURMA ---
                bugun = datetime.now().strftime("%d/%m")
                df_bugun = df_ana[df_ana['Tarih'].str.contains(bugun)] if not df_ana.empty else pd.DataFrame()
                
                if not df_bugun.empty:
                    toplam_soru = df_bugun['Toplam'].sum()
                    konular = ", ".join(df_bugun['Konu'].unique())
                    v_msg = f"Sayın Veli, {sec} bugün toplam {toplam_soru} soru çözdü. Çalıştığı konular: {konular}. - Nida GÖMCELİ"
                else:
                    v_msg = f"Sayın Veli, {sec} bugün henüz soru girişi yapmadı. Bilginize. - Nida GÖMCELİ"

                st.divider()
                st.subheader("📱 Veli Bilgilendirme")
                st.write(f"*Gidecek Mesaj:* {v_msg}")
                st.markdown(f'<a href="https://wa.me/{o["v_tel"]}?text={urllib.parse.quote(v_msg)}" target="_blank" style="background-color:#25D366; color:white; padding:15px; text-decoration:none; border-radius:10px; font-weight:bold;">📱 WHATSAPP RAPORU GÖNDER</a>', unsafe_allow_html=True)

    # --- 6. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        m = M_LGS if o["sinav"] == "LGS" else M_YKS
        st.title(f"Selam {u} ✨")
        if st.button("Çıkış"): del st.session_state["logged_in"]; st.rerun()

        with st.expander("📝 Çalışma Ekle"):
            d = st.selectbox("Ders", list(m.keys())); k = st.selectbox("Konu", m[d])
            soru = st.number_input("Soru Sayısı", 0); sure = st.number_input("Süre (dk)", 0)
            if st.button("Kaydet"):
                o["soru"].append({"Tarih": datetime.now().strftime("%d/%m %H:%M"), "Ders": d, "Konu": k, "Toplam": soru, "Sure": sure})
                veri_kaydet(st.session_state.db); st.success("Kaydedildi!")

        t = st.tabs(["📊 Müfredat", "🏆 Deneme"])
        with t[0]:
            df_st = pd.DataFrame(o.get("soru", []))
            for d_adi, konular in m.items():
                coz = df_st[df_st['Ders'] == d_adi]['Toplam'].sum() if not df_st.empty else 0
                st.write(f"*{d_adi}*: {coz} Soru"); st.progress(min(coz/(len(konular)*KONU_BARAJI), 1.0))
