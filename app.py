import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime, timedelta
import plotly.express as px
import random

# --- 1. VERİ YÖNETİMİ ---
VERI_DOSYASI = "nida_v48_final.json"
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
    "Matematik": ["Çarpanlar Katlar", "Üslü İfadeler", "Kareköklü İfadeler", "Veri Analizi", "Olasılık", "Cebirsel İfadeler", "Denklemler", "Eşitsizlikler", "Üçgenler", "Eşlik Benzerlik", "Dönüşüm", "Geometrik Cisimler"],
    "Fen Bilimleri": ["Mevsimler", "DNA", "Basınç", "Madde ve Endüstri", "Basit Makineler", "Enerji Dönüşümleri", "Elektrik"],
    "Türkçe": ["Sözcük-Cümle Anlam", "Paragraf", "Fiilimsiler", "Ögeler", "Yazım-Noktalama", "Söz Sanatları", "Anlatım Bozukluğu"],
    "İnkılap": ["Bir Kahraman Doğuyor", "Milli Uyanış", "Ya İstiklal Ya Ölüm", "Atatürkçülük", "Dış Politika"],
    "Din / İngilizce": ["Kader İnancı", "Zekat", "Din ve Hayat", "Friendship", "Teen Life", "Kitchen", "Internet"]
}
M_YKS = {"Matematik": ["TYT Mat", "AYT Mat", "Geometri"], "Türkçe/Ed": ["Dil Bilgisi", "Paragraf", "Edebiyat"], "Fen": ["Fizik", "Kimya", "Biyoloji"], "Sosyal": ["Tarih", "Coğrafya", "Felsefe"]}

# --- 3. TASARIM ---
st.set_page_config(page_title="Nida Akademi v48", layout="wide")
st.markdown("<style>.stApp { background-color: #0d1117; color: white; }</style>", unsafe_allow_html=True)

# --- 4. GİRİŞ ---
if "logged_in" not in st.session_state:
    st.title("🎓 Nida Akademi Koçluk")
    u = st.text_input("Ad Soyad"); p = st.text_input("Şifre", type="password")
    if st.button("Giriş"):
        if u == "admin" and p == "nida2024": st.session_state.update({"logged_in": True, "role": "admin"}); st.rerun()
        elif u in st.session_state.db.get("ogrenciler", {}):
            if st.session_state.db["ogrenciler"][u].get("sifre") == p:
                st.session_state.update({"logged_in": True, "role": "ogrenci", "user": u}); st.rerun()
        else: st.error("Hatalı!")
else:
    # --- 5. ADMIN PANELİ ---
    if st.session_state["role"] == "admin":
        st.sidebar.title("Nida Hocam")
        menu = st.sidebar.radio("Menü", ["Öğrenci Kaydı", "Gelişmiş Analiz Paneli"])
        if st.sidebar.button("Çıkış"): del st.session_state["logged_in"]; st.rerun()

        if menu == "Öğrenci Kaydı":
            with st.expander("👤 Öğrenci Ekle"):
                ad = st.text_input("Ad Soyad"); grp = st.selectbox("Grup", ["LGS", "YKS"])
                v_t = st.text_input("Veli Tel (905...)"); h = st.number_input("Haftalık Hedef", 100)
                if st.button("Kaydet"):
                    s = str(random.randint(1000, 9999))
                    if "ogrenciler" not in st.session_state.db: st.session_state.db["ogrenciler"] = {}
                    st.session_state.db["ogrenciler"][ad] = {"soru": [], "denemeler": [], "sinav": grp, "hedef": h, "v_tel": v_t, "sifre": s, "biten_konular": []}
                    veri_kaydet(st.session_state.db); st.success(f"Şifre: {s}")

        elif menu == "Gelişmiş Analiz Paneli":
            sec = st.selectbox("Öğrenci Seç", list(st.session_state.db.get("ogrenciler", {}).keys()))
            o = st.session_state.db["ogrenciler"][sec]
            df = pd.DataFrame(o["soru"])
            
            st.title(f"🚀 {sec} - Detaylı Analiz")
            
            # 📈 GÖRSEL İSTATİSTİKLER
            c1, c2, c3 = st.columns(3)
            h_toplam = df['Toplam'].sum() if not df.empty else 0
            s_toplam = df['Sure'].sum() if not df.empty and 'Sure' in df.columns else 0
            c1.metric("Haftalık Soru", f"{h_toplam} / {o['hedef']}")
            c2.metric("Toplam Çalışma", f"{s_toplam} dk")
            c3.metric("Müfredat", f"%{int((len(o.get('biten_konular', []))/100)*100)}") # Basit hesap

            # KONU BAZLI ANALİZ TABLOSU
            if not df.empty:
                st.subheader("📊 Ders & Konu Dağılımı")
                fig = px.sunburst(df, path=['Ders', 'Konu'], values='Toplam', color='Ders')
                st.plotly_chart(fig, use_container_width=True)

            # VELİYE RAPOR (GÜNLÜK ÖZET)
            bugun = datetime.now().strftime("%d/%m")
            bugun_soru = df[df['Tarih'].str.contains(bugun)]['Toplam'].sum() if not df.empty else 0
            v_msg = f"Sayın Veli, {sec} bugün {bugun_soru} soru çözdü, toplam {s_toplam} dakika çalıştı. - Nida GÖMCELİ"
            st.markdown(f'<a href="https://wa.me/{o["v_tel"]}?text={urllib.parse.quote(v_msg)}" target="_blank" style="background-color:#25D366; color:white; padding:15px; text-decoration:none; border-radius:10px;">📱 GÜNLÜK RAPORU AT</a>', unsafe_allow_html=True)

    # --- 6. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        m = M_LGS if o["sinav"] == "LGS" else M_YKS
        st.title(f"Selam {u} ✨")
        t1, t2, t3 = st.tabs(["📝 Çalışma Girişi", "🏆 Deneme Analizi", "✅ Müfredat"])

        with t1:
            st.subheader("Bugünkü Emeklerin")
            c1, c2 = st.columns(2)
            d = c1.selectbox("Ders", list(m.keys())); k = c2.selectbox("Konu", m[d])
            dog = c1.number_input("Doğru", 0); yan = c2.number_input("Yanlış", 0)
            sure = st.slider("Kaç Dakika Çalıştın?", 0, 240, 30)
            if st.button("Kaydet"):
                o["soru"].append({"Tarih": datetime.now().strftime("%d/%m %H:%M"), "Ders": d, "Konu": k, "Toplam": dog+yan, "Sure": sure})
                veri_kaydet(st.session_state.db); st.success("Veri İşlendi!")

        with t2:
            st.subheader("Deneme Netleri (3Y 1D)")
            col1, col2, col3 = st.columns(3)
            if o["sinav"] == "LGS":
                m_d = col1.number_input("Mat D", 0); m_y = col1.number_input("Mat Y", 0)
                f_d = col2.number_input("Fen D", 0); f_y = col2.number_input("Fen Y", 0)
                t_d = col3.number_input("Türk D", 0); t_y = col3.number_input("Türk Y", 0)
                # İnkılap/Din/İng toplu net girişi (Hız için)
                s_d = st.number_input("Sözel (İnk/Din/İng) Toplam D", 0)
                s_y = st.number_input("Sözel (İnk/Din/İng) Toplam Y", 0)
                puan = 194 + (m_d-m_y/3)*4.9 + (f_d-f_y/3)*4.0 + (t_d-t_y/3)*4.3 + (s_d-s_y/3)*1.6
            else:
                tyt_d = col1.number_input("TYT Doğru", 0); tyt_y = col1.number_input("TYT Yanlış", 0)
                puan = 100 + (tyt_d - tyt_y/4)*1.3
            
            y_konu = st.multiselect("Yanlış Konuların", m[d])
            if st.button("Deneme Kaydet"):
                o["denemeler"].append({"Tarih": datetime.now().strftime("%d/%m"), "Puan": round(puan, 2), "Yanlislar": ", ".join(y_konu)})
                veri_kaydet(st.session_state.db); st.success(f"Puan: {round(puan, 2)}")

        with t3:
            st.subheader("Konu Tamamlama")
            biten = o.get("biten_konular", [])
            yeni_biten = []
            for d_adi, konular in m.items():
                with st.expander(f"{d_adi}"):
                    for kn in konular:
                        if st.checkbox(kn, value=(kn in biten), key=f"chk_{kn}"): yeni_biten.append(kn)
            if st.button("Müfredatı Güncelle"):
                o["biten_konular"] = yeni_biten
                veri_kaydet(st.session_state.db); st.success("Müfredat Güncellendi!")
