import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import plotly.express as px
import random

# --- 1. AYARLAR ---
VERI_DOSYASI = "nida_v42_lgs_pro.json"
HOCA_TEL = "905307368072"
SITE_URL = "https://egitimkocunidagomceli.streamlit.app"

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
M_LGS = {
    "Matematik": ["Çarpanlar Katlar", "Üslü", "Kareköklü", "Veri Analizi", "Olasılık", "Cebirsel", "Denklemler", "Eşitsizlikler", "Üçgenler", "Eşlik Benzerlik", "Dönüşüm", "Geometrik Cisimler"],
    "Fen Bilimleri": ["Mevsimler", "DNA", "Basınç", "Madde", "Basit Makineler", "Enerji", "Elektrik"],
    "Türkçe": ["Fiilimsiler", "Ögeler", "Anlam Bilgisi", "Paragraf", "Yazım-Noktalama"],
    "İnkılap Tarihi": ["Milli Uyanış", "Ya İstiklal Ya Ölüm", "Atatürkçülük"],
    "Din Kültürü": ["Kader", "Zekat", "Din ve Hayat"],
    "İngilizce": ["Friendship", "Teen Life", "Kitchen", "Phone"]
}
M_YKS = {"Matematik": ["TYT", "AYT", "Geometri"], "Türkçe/Ed": ["Paragraf", "Dil Bilgisi", "Edebiyat"], "Fen/Sos": ["Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya"]}

# --- 3. TASARIM ---
st.set_page_config(page_title="Nida Akademi v42", layout="wide")
st.markdown("<style>.stApp { background-color: #0d1117; color: white; }</style>", unsafe_allow_html=True)

# --- 4. GİRİŞ ---
if "logged_in" not in st.session_state:
    st.title("🎓 Nida Akademi LGS-YKS Koçluk")
    u = st.text_input("Ad Soyad")
    p = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        if u == "admin" and p == "nida2024":
            st.session_state.update({"logged_in": True, "role": "admin"})
            st.rerun()
        elif u in st.session_state.db.get("ogrenciler", {}) and st.session_state.db["ogrenciler"][u].get("sifre") == p:
            st.session_state.update({"logged_in": True, "role": "ogrenci", "user": u})
            st.rerun()
        else: st.error("Hatalı!")
else:
    # --- 5. ADMIN ---
    if st.session_state["role"] == "admin":
        st.sidebar.title("Nida Hocam")
        menu = st.sidebar.radio("Menü", ["Kayıt", "Raporlar"])
        if st.sidebar.button("Çıkış"): del st.session_state["logged_in"]; st.rerun()

        if menu == "Kayıt":
            with st.expander("👤 Öğrenci Ekle"):
                ad = st.text_input("Ad Soyad"); grp = st.selectbox("Grup", ["LGS", "YKS"])
                o_t = st.text_input("Öğrenci Tel"); v_t = st.text_input("Veli Tel"); h = st.number_input("Hedef", 100)
                if st.button("Kaydet"):
                    s = str(random.randint(1000, 9999))
                    if "ogrenciler" not in st.session_state.db: st.session_state.db["ogrenciler"] = {}
                    st.session_state.db["ogrenciler"][ad] = {"soru": [], "denemeler": [], "sinav": grp, "hedef": h, "o_tel": o_t, "v_tel": v_t, "sifre": s}
                    veri_kaydet(st.session_state.db); st.success(f"Şifre: {s}")

        elif menu == "Raporlar":
            sec = st.selectbox("Öğrenci", list(st.session_state.db.get("ogrenciler", {}).keys()))
            o = st.session_state.db["ogrenciler"][sec]
            df = pd.DataFrame(o["soru"])
            h_toplam = df['Toplam'].sum() if not df.empty else 0
            st.subheader(f"📊 {sec} - Hedef: {h_toplam} / {o['hedef']}")
            
            if o["denemeler"]:
                d_df = pd.DataFrame(o["denemeler"])
                st.table(d_df[['Tarih', 'Puan', 'Yanlis_Listesi']])
                son_p = d_df.iloc[-1]['Puan']
                son_y = d_df.iloc[-1]['Yanlis_Listesi']
                
                v_msg = f"Sayın Veli, {sec} bu hafta {h_toplam} soru çözdü. Son deneme puanı: {son_p}. Yanlış konular: {son_y}. - Nida GÖMCELİ"
                st.markdown(f'<a href="https://wa.me/{o["v_tel"]}?text={urllib.parse.quote(v_msg)}" target="_blank" style="background-color:#25D366; color:white; padding:15px; text-decoration:none; border-radius:10px;">📱 VELİYE RAPOR AT</a>', unsafe_allow_html=True)

    # --- 6. ÖĞRENCİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        m = M_LGS if o.get("sinav") == "LGS" else M_YKS
        st.title(f"Selam {u} ✨")
        t1, t2 = st.tabs(["📝 Soru Girişi", "🏆 Deneme Analizi"])

        with t1:
            ders = st.selectbox("Ders", list(m.keys())); konu = st.selectbox("Konu", m[ders])
            d_s = st.number_input("Doğru", 0); y_s = st.number_input("Yanlış", 0)
            if st.button("Kaydet"):
                o["soru"].append({"Tarih": datetime.now().strftime("%d/%m"), "Ders": ders, "Konu": konu, "Toplam": d_s + y_s})
                veri_kaydet(st.session_state.db); st.success("Kaydedildi!")

        with t2:
            st.subheader("LGS/YKS Puan Hesaplama (3 Yanlış 1 Doğruyu Götürür)")
            with st.expander("Netlerini Gir"):
                c1, c2, c3 = st.columns(3)
                if o.get("sinav") == "LGS":
                    mt_d = c1.number_input("Mat D", 0); mt_y = c1.number_input("Mat Y", 0)
                    tr_d = c2.number_input("Türkçe D", 0); tr_y = c2.number_input("Türkçe Y", 0)
                    fn_d = c3.number_input("Fen D", 0); fn_y = c3.number_input("Fen Y", 0)
                    i_d = c1.number_input("İnkılap D", 0); i_y = c1.number_input("İnkılap Y", 0)
                    d_d = c2.number_input("Din D", 0); d_y = c2.number_input("Din Y", 0)
                    in_d = c3.number_input("İng D", 0); in_y = c3.number_input("İng Y", 0)
                    
                    # MEB LGS Ham Puan Formülü
                    m_n = mt_d - (mt_y/3); t_n = tr_d - (tr_y/3); f_n = fn_d - (fn_y/3)
                    ink_n = i_d - (i_y/3); din_n = d_d - (d_y/3); ing_n = in_d - (in_y/3)
                    puan = 194 + (m_n * 4.9) + (t_n * 4.3) + (f_n * 4.0) + (ink_n * 1.6) + (din_n * 1.6) + (ing_n * 1.6)
                else:
                    tyt_d = c1.number_input("TYT D", 0); tyt_y = c1.number_input("TYT Y", 0)
                    ayt_d = c2.number_input("AYT D", 0); ayt_y = c2.number_input("AYT Y", 0)
                    puan = 100 + ((tyt_d - tyt_y/4) * 1.3) + ((ayt_d - ayt_y/4) * 3.0)

            y_ders = st.selectbox("Yanlış Ders", list(m.keys()))
            y_konu = st.multiselect("Yanlış Konuların", m[y_ders])
            
            if st.button("Denemeyi İşle"):
                o["denemeler"].append({"Tarih": datetime.now().strftime("%d/%m"), "Puan": round(puan, 2), "Yanlis_Listesi": f"{y_ders}: {', '.join(y_konu)}"})
                veri_kaydet(st.session_state.db); st.success(f"Hesaplanan Puan: {round(puan, 2)}")
