import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import plotly.express as px
import random

# --- 1. AYARLAR ---
VERI_DOSYASI = "nida_v39_final_data.json"
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

# --- 2. MÜFREDAT (LGS & YKS) ---
M_LGS = {
    "Matematik": ["Çarpanlar Katlar", "Üslü İfadeler", "Kareköklü", "Veri Analizi", "Olasılık", "Cebirsel", "Denklemler", "Eşitsizlikler", "Üçgenler", "Eşlik Benzerlik", "Dönüşüm", "Geometrik Cisimler"],
    "Fen Bilimleri": ["Mevsimler", "DNA", "Basınç", "Madde", "Basit Makineler", "Enerji Dönüşümleri", "Elektrik"],
    "Türkçe": ["Fiilimsiler", "Cümlenin Ögeleri", "Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Yazım-Noktalama", "Söz Sanatları"],
    "İnkılap Tarihi": ["Milli Uyanış", "Ya İstiklal Ya Ölüm", "Atatürkçülük"],
    "Din Kültürü": ["Kader İnancı", "Zekat ve Sadaka", "Din ve Hayat"],
    "İngilizce": ["Friendship", "Teen Life", "In the Kitchen"]
}
M_YKS = {
    "TYT Matematik": ["Temel Kavramlar", "Problemler", "Fonksiyonlar", "Geometri"],
    "AYT Matematik": ["Trigonometri", "Logaritma", "Türev", "İntegral"],
    "Türkçe/Edebiyat": ["Paragraf", "Dil Bilgisi", "Edebiyat Akımları"],
    "YKS Fen": ["Fizik", "Kimya", "Biyoloji"],
    "YKS Sosyal": ["Tarih", "Coğrafya", "Felsefe"]
}

# --- 3. TASARIM ---
st.set_page_config(page_title="Nida Akademi v39", layout="wide")
st.markdown("<style>.stApp { background-color: #0d1117; color: white; }</style>", unsafe_allow_html=True)

# --- 4. GİRİŞ SİSTEMİ ---
if "logged_in" not in st.session_state:
    st.title("🎓 Nida Akademi Koçluk Portalı")
    user_input = st.text_input("Ad Soyad")
    pass_input = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        if user_input == "admin" and pass_input == "nida2024":
            st.session_state.update({"logged_in": True, "role": "admin"})
            st.rerun()
        elif user_input in st.session_state.db.get("ogrenciler", {}) and st.session_state.db["ogrenciler"][user_input].get("sifre") == pass_input:
            st.session_state.update({"logged_in": True, "role": "ogrenci", "user": user_input})
            st.rerun()
        else:
            st.error("Giriş bilgileri hatalı veya öğrenci eklenmemiş.")

else:
    # --- 5. ADMIN PANELİ ---
    if st.session_state["role"] == "admin":
        st.sidebar.title("Nida Hocam")
        menu = st.sidebar.radio("Menü", ["Öğrenci Kaydı", "Gelişim Analizi"])
        if st.sidebar.button("Çıkış Yap"):
            del st.session_state["logged_in"]
            st.rerun()

        if menu == "Öğrenci Kaydı":
            with st.expander("👤 Yeni Öğrenci Ekle"):
                ad = st.text_input("Ad Soyad")
                grup = st.selectbox("Grup", ["LGS", "YKS"])
                o_tel = st.text_input("Öğrenci Tel (905...)")
                v_tel = st.text_input("Veli Tel (905...)")
                hedef = st.number_input("Haftalık Hedef", 100)
                if st.button("Kaydet"):
                    sifre = str(random.randint(1000, 9999))
                    if "ogrenciler" not in st.session_state.db: st.session_state.db["ogrenciler"] = {}
                    st.session_state.db["ogrenciler"][ad] = {"soru": [], "denemeler": [], "sinav": grup, "hedef": hedef, "o_tel": o_tel, "v_tel": v_tel, "sifre": sifre}
                    veri_kaydet(st.session_state.db)
                    st.success(f"Kaydedildi! Şifre: {sifre}")

            st.subheader("📋 Mevcut Öğrenciler")
            for isim, d in st.session_state.db.get("ogrenciler", {}).items():
                c1, c2 = st.columns([3, 1])
                c1.write(f"*{isim}* (Grup: {d['sinav']} | Şifre: {d['sifre']})")
                msg = f"Selam {isim}, Nida Akademi giriş şifren: {d['sifre']}\nLink: {SITE_URL}"
                c2.markdown(f'[📲 Gönder](https://wa.me/{d["o_tel"]}?text={urllib.parse.quote(msg)})')

        elif menu == "Gelişim Analizi":
            ogrenciler = list(st.session_state.db.get("ogrenciler", {}).keys())
            if not ogrenciler:
                st.warning("Henüz öğrenci eklenmemiş.")
            else:
                secilen = st.selectbox("Öğrenci Seç", ogrenciler)
                o = st.session_state.db["ogrenciler"][secilen]
                df = pd.DataFrame(o["soru"])
                
                st.title(f"📊 {secilen} Analiz")
                h_toplam = df['Toplam'].sum() if not df.empty else 0
                st.subheader(f"Hedef: {h_toplam} / {o['hedef']}")
                st.progress(min(h_toplam / o['hedef'], 1.0) if o['hedef'] > 0 else 0)

                if not df.empty:
                    st.plotly_chart(px.pie(df, values='Toplam', names='Ders', title="Ders Dağılımı"))
                    st.subheader("📚 Konu Bazlı Detay")
                    st.dataframe(df.groupby(['Ders', 'Konu'])['Toplam'].sum().reset_index(), use_container_width=True)

                if o["denemeler"]:
                    st.subheader("🏆 Denemeler")
                    st.table(pd.DataFrame(o["denemeler"])[['Tarih', 'Yayin', 'Puan', 'Yanlis_Konular']])

                v_msg = f"Sayın Velimiz, {secilen} bu hafta {h_toplam} soru çözmüştür. - Nida GÖMCELİ"
                st.markdown(f'<a href="https://wa.me/{o["v_tel"]}?text={urllib.parse.quote(v_msg)}" target="_blank" style="background-color:#25D366; color:white; padding:10px; text-decoration:none; border-radius:5px;">Veliye Rapor Gönder</a>', unsafe_allow_html=True)

    # --- 6. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]
        o = st.session_state.db["ogrenciler"][u]
        m = M_LGS if o.get("sinav") == "LGS" else M_YKS
        
        st.title(f"Selam {u} ✨")
        t1, t2, t3 = st.tabs(["📝 Çalışma Girişi", "🏆 Deneme Analizi", "📊 Gelişimim"])
        
        with t1:
            ders = st.selectbox("Ders", list(m.keys()))
            konu = st.selectbox("Konu", m[ders])
            tur = st.selectbox("Tür", ["Soru Çözümü", "Özel Ders", "Video/Tekrar"])
            if tur == "Soru Çözümü":
                d_n = st.number_input("Doğru", 0, key="d_key")
                y_n = st.number_input("Yanlış", 0, key="y_key")
                if st.button("Kaydet", key="btn_soru"):
                    o["soru"].append({"Tarih": datetime.now().strftime("%d/%m"), "Ders": ders, "Konu": konu, "Toplam": d_n + y_n})
                    veri_kaydet(st.session_state.db)
                    st.success("Kaydedildi!")
            else:
                birim = st.number_input("Dakika", 10, key="dk_key")
                if st.button("Kaydet", key="btn_calisma"):
                    o["soru"].append({"Tarih": datetime.now().strftime("%d/%m"), "Ders": ders, "Konu": konu, "Toplam": 0, "Detay": f"{birim} dk {tur}"})
                    veri_kaydet(st.session_state.db)
                    st.success("Çalışma kaydedildi!")

        with t2:
            yay = st.text_input("Deneme Yayını", key="yay_key")
            c1, c2 = st.columns(2)
            if o.get("sinav") == "LGS":
                t_net = c1.number_input("Türkçe Net", 0.0, key="tn_key")
                m_net = c2.number_input("Mat Net", 0.0, key="mn_key")
                f_net = c1.number_input("Fen Net", 0.0, key="fn_key")
                puan = 200 + (m_net*5) + (f_net*4) + (t_net*4)
            else:
                tyt_n = c1.number_input("TYT Net", 0.0, key="tyt_key")
                ayt_n = c2.number_input("AYT Net", 0.0, key="ayt_key")
                puan = 100 + (tyt_n*1.5) + (ayt_n*3)
            yanlislar = st.text_area("Hangi konularda yanlış yaptın?", key="y_alan")
            if st.button("Denemeyi İşle", key="btn_deneme"):
                o["denemeler"].append({"Tarih": datetime.now().strftime("%d/%m"), "Yayin": yay, "Puan": round(puan, 2), "Yanlis_Konular": yanlislar})
                veri_kaydet(st.session_state.db)
                st.success(f"Puan: {round(puan, 2)}")

        with t3:
            df_o = pd.DataFrame(o["soru"])
            if not df_o.empty:
                st.plotly_chart(px.bar(df_o.groupby("Ders")["Toplam"].sum().reset_index(), x="Ders", y="Toplam", color="Ders"))
            st.markdown(f'<a href="https://wa.me/{HOCA_TEL}?text=Raporum Hazır Hocam!" target="_blank" style="background-color:#007bff; color:white; padding:10px; text-decoration:none; border-radius:5px;">Hocama Rapor Gönder</a>', unsafe_allow_html=True)