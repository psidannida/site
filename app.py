import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import plotly.express as px
import random

# --- 1. AYARLAR ---
VERI_DOSYASI = "nida_v45_full_lgs.json"
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
    "Matematik": ["Çarpanlar Katlar", "Üslü İfadeler", "Kareköklü", "Veri Analizi", "Olasılık", "Cebirsel", "Doğrusal Denklemler", "Eşitsizlikler", "Üçgenler", "Eşlik Benzerlik", "Dönüşüm", "Geometrik Cisimler"],
    "Fen Bilimleri": ["Mevsimler", "DNA", "Basınç", "Madde ve Endüstri", "Basit Makineler", "Enerji Dönüşümleri", "Elektrik Yükleri"],
    "Türkçe": ["Fiilimsiler", "Cümlenin Ögeleri", "Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Yazım-Noktalama", "Söz Sanatları"],
    "İnkılap Tarihi": ["Bir Kahraman Doğuyor", "Milli Uyanış", "Ya İstiklal Ya Ölüm", "Atatürkçülük", "Dış Politika"],
    "Din Kültürü": ["Kader İnancı", "Zekat ve Sadaka", "Din ve Hayat", "Hz. Muhammed"],
    "İngilizce": ["Friendship", "Teen Life", "In the Kitchen", "On the Phone", "The Internet"]
}
M_YKS = {"Matematik": ["TYT", "AYT", "Geometri"], "Türkçe/Ed": ["Paragraf", "Dil Bilgisi", "Edebiyat"], "Fen/Sos": ["Fizik", "Kimya", "Biyoloji", "Tarih", "Coğrafya"]}

# --- 3. TASARIM ---
st.set_page_config(page_title="Nida Akademi v45", layout="wide")
st.markdown("<style>.stApp { background-color: #0d1117; color: white; }</style>", unsafe_allow_html=True)

# --- 4. GİRİŞ ---
if "logged_in" not in st.session_state:
    st.title("🎓 Nida Akademi Koçluk Portalı")
    u_in = st.text_input("Ad Soyad")
    p_in = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        if u_in == "admin" and p_in == "nida2024":
            st.session_state.update({"logged_in": True, "role": "admin"})
            st.rerun()
        elif u_in in st.session_state.db.get("ogrenciler", {}) and st.session_state.db["ogrenciler"][u_in].get("sifre") == p_in:
            st.session_state.update({"logged_in": True, "role": "ogrenci", "user": u_in})
            st.rerun()
        else: st.error("Bilgiler hatalı.")
else:
    # --- 5. ADMIN PANELİ ---
    if st.session_state["role"] == "admin":
        st.sidebar.title("Nida Hocam")
        menu = st.sidebar.radio("Menü", ["Öğrenci Kaydı", "Analiz & Rapor"])
        if st.sidebar.button("Çıkış"): del st.session_state["logged_in"]; st.rerun()

        if menu == "Öğrenci Kaydı":
            with st.expander("👤 Yeni Öğrenci Ekle"):
                ad = st.text_input("Ad Soyad")
                grp = st.selectbox("Grup", ["LGS", "YKS"])
                o_tel = st.text_input("Öğrenci Tel")
                v_tel = st.text_input("Veli Tel")
                hedef = st.number_input("Haftalık Hedef", 100)
                if st.button("Kaydet"):
                    sifre = str(random.randint(1000, 9999))
                    if "ogrenciler" not in st.session_state.db: st.session_state.db["ogrenciler"] = {}
                    st.session_state.db["ogrenciler"][ad] = {"soru": [], "denemeler": [], "sinav": grp, "hedef": hedef, "o_tel": o_tel, "v_tel": v_tel, "sifre": sifre}
                    veri_kaydet(st.session_state.db); st.success(f"Kaydedildi! Şifre: {sifre}")

        elif menu == "Analiz & Rapor":
            ogrenciler = list(st.session_state.db.get("ogrenciler", {}).keys())
            if not ogrenciler: st.warning("Öğrenci yok.")
            else:
                secilen = st.selectbox("Öğrenci Seç", ogrenciler)
                o = st.session_state.db["ogrenciler"][secilen]
                df = pd.DataFrame(o["soru"])
                
                st.title(f"📊 {secilen} Analiz")
                h_toplam = df['Toplam'].sum() if not df.empty else 0
                st.subheader(f"Haftalık Hedef: {h_toplam} / {o['hedef']}")
                st.progress(min(h_toplam / o['hedef'], 1.0) if o['hedef'] > 0 else 0)

                if not df.empty:
                    st.subheader("📚 Konu Bazlı Soru Dağılımı")
                    st.table(df.groupby(['Ders', 'Konu'])['Toplam'].sum().reset_index())

                if o["denemeler"]:
                    st.subheader("🏆 Deneme Puanları")
                    st.table(pd.DataFrame(o["denemeler"])[['Tarih', 'Puan', 'Yanlis_Listesi']])
                
                v_msg = f"Sayın Velimiz, {secilen} bu hafta toplam {h_toplam} soru çözmüştür. Son puanı: {o['denemeler'][-1]['Puan'] if o['denemeler'] else '0'}. - Nida GÖMCELİ"
                st.markdown(f'<a href="https://wa.me/{o["v_tel"]}?text={urllib.parse.quote(v_msg)}" target="_blank" style="background-color:#25D366; color:white; padding:15px; text-decoration:none; border-radius:10px;">📱 VELİYE RAPOR GÖNDER</a>', unsafe_allow_html=True)

    # --- 6. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        m = M_LGS if o.get("sinav") == "LGS" else M_YKS
        st.title(f"Selam {u} ✨")
        t1, t2 = st.tabs(["📝 Soru Girişi", "🏆 Deneme Analizi"])
        
        with t1:
            ders = st.selectbox("Ders", list(m.keys()), key="d_s")
            konu = st.selectbox("Konu", m[ders], key="k_s")
            d_n = st.number_input("Doğru", 0, key="d_n")
            y_n = st.number_input("Yanlış", 0, key="y_n")
            if st.button("Kaydet", key="b_k"):
                o["soru"].append({"Tarih": datetime.now().strftime("%d/%m %H:%M"), "Ders": ders, "Konu": konu, "Toplam": d_n + y_n})
                veri_kaydet(st.session_state.db); st.success("Kaydedildi!")

        with t2:
            st.subheader("LGS Puan Hesaplama (3 Yanlış 1 Doğruyu Götürür)")
            c1, c2, c3 = st.columns(3)
            if o.get("sinav") == "LGS":
                # SAYISAL
                m_d = c1.number_input("Mat D", 0); m_y = c1.number_input("Mat Y", 0)
                f_d = c2.number_input("Fen D", 0); f_y = c2.number_input("Fen Y", 0)
                # SÖZEL
                t_d = c3.number_input("Türk D", 0); t_y = c3.number_input("Türk Y", 0)
                i_d = c1.number_input("İnkılap D", 0); i_y = c1.number_input("İnkılap Y", 0)
                d_d = c2.number_input("Din D", 0); d_y = c2.number_input("Din Y", 0)
                ing_d = c3.number_input("İng D", 0); ing_y = c3.number_input("İng Y", 0)
                
                # NET HESAPLAMA
                m_net = m_d - (m_y/3); f_net = f_d - (f_y/3); t_net = t_d - (t_y/3)
                ink_net = i_d - (i_y/3); din_net = d_d - (d_y/3); ing_net = ing_d - (ing_y/3)
                
                # PUAN (MEB Katsayılar)
                puan = 194 + (m_net * 4.9) + (f_net * 4.0) + (t_net * 4.3) + (ink_net * 1.6) + (din_net * 1.6) + (ing_net * 1.6)
            else:
                tyt_d = c1.number_input("TYT D", 0); tyt_y = c1.number_input("TYT Y", 0)
                ayt_d = c2.number_input("AYT D", 0); ayt_y = c2.number_input("AYT Y", 0)
                puan = 100 + (tyt_d - tyt_y/4)*1.3 + (ayt_d - ayt_y/4)*3.0
            
            y_ders = st.selectbox("Yanlış Ders", list(m.keys()), key="y_d")
            y_konu = st.multiselect("Yanlış Konuların", m[y_ders], key="y_k")
            if st.button("Denemeyi İşle", key="b_d"):
                o["denemeler"].append({"Tarih": datetime.now().strftime("%d/%m"), "Puan": round(puan, 2), "Yanlis_Listesi": f"{y_ders}: {', '.join(y_konu)}"})
                veri_kaydet(st.session_state.db); st.success(f"Puan: {round(puan, 2)}")
