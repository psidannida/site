import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import plotly.express as px
import random

# --- 1. VERİ YÖNETİMİ ---
VERI_DOSYASI = "nida_v46_ultimate.json"
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

# --- 2. DEV MÜFREDAT LİSTESİ ---
M_LGS = {
    "Matematik": ["Çarpanlar Katlar", "Üslü İfadeler", "Kareköklü", "Veri Analizi", "Olasılık", "Cebirsel", "Doğrusal Denklemler", "Eşitsizlikler", "Üçgenler", "Eşlik Benzerlik", "Dönüşüm", "Geometrik Cisimler"],
    "Fen Bilimleri": ["Mevsimler", "DNA", "Basınç", "Madde ve Endüstri", "Basit Makineler", "Enerji Dönüşümleri", "Elektrik Yükleri"],
    "Türkçe": ["Fiilimsiler", "Cümlenin Ögeleri", "Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Yazım-Noktalama", "Söz Sanatları", "Anlatım Bozukluğu"],
    "İnkılap Tarihi": ["Bir Kahraman Doğuyor", "Milli Uyanış", "Ya İstiklal Ya Ölüm", "Atatürkçülük", "Dış Politika", "Atatürk Ölümü"],
    "Din Kültürü": ["Kader İnancı", "Zekat ve Sadaka", "Din ve Hayat", "Hz. Muhammed'in Örnekliği", "Kur'an ve Özellikleri"],
    "İngilizce": ["Friendship", "Teen Life", "In the Kitchen", "On the Phone", "The Internet", "Adventures", "Tourism"]
}
M_YKS = {
    "TYT Matematik": ["Sayılar", "Bölünebilme", "Rasyonel", "Üslü-Köklü", "Çarpanlara Ayırma", "Denklemler", "Problemler", "Kümeler", "Fonksiyonlar"],
    "AYT Matematik": ["Polinomlar", "2. Derece Denklemler", "Trigonometri", "Logaritma", "Diziler", "Limit", "Türev", "İntegral"],
    "Geometri": ["Üçgenler", "Çokgenler", "Daire", "Analitik Geometri", "Katı Cisimler"],
    "Türkçe/Edebiyat": ["Sözcük/Cümle Anlamı", "Paragraf", "Dil Bilgisi", "Şiir Bilgisi", "Edebiyat Akımları", "Yazarlar Eserler"],
    "Fizik": ["Kuvvet ve Hareket", "Elektrik", "Optik", "Dalgalar", "Modern Fizik"],
    "Kimya": ["Atom", "Mol", "Çözeltiler", "Enerji", "Hız", "Denge", "Organik Kimya"],
    "Biyoloji": ["Hücre", "Kalıtım", "Sistemler", "Bitki Biyolojisi", "Ekoloji"],
    "Tarih/Coğrafya": ["Tarih Bilimi", "Türk Tarihi", "Osmanlı", "İnkılap", "Nüfus", "İklim", "Bölgeler"]
}

# --- 3. TASARIM VE ARAYÜZ ---
st.set_page_config(page_title="Nida Akademi v46", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: white; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #238636; color: white; border: none; }
    .stProgress > div > div > div > div { background-color: #238636; }
</style>
""", unsafe_allow_html=True)

# --- 4. GİRİŞ KONTROLÜ ---
if "logged_in" not in st.session_state:
    st.title("🎓 Nida Akademi Koçluk Portalı")
    user_input = st.text_input("Ad Soyad")
    pass_input = st.text_input("Şifre", type="password")
    if st.button("Sisteme Giriş Yap"):
        if user_input == "admin" and pass_input == "nida2024":
            st.session_state.update({"logged_in": True, "role": "admin"})
            st.rerun()
        elif user_input in st.session_state.db.get("ogrenciler", {}) and st.session_state.db["ogrenciler"][user_input].get("sifre") == pass_input:
            st.session_state.update({"logged_in": True, "role": "ogrenci", "user": user_input})
            st.rerun()
        else: st.error("Bilgiler hatalı veya öğrenci eklenmemiş.")

else:
    # --- 5. ADMIN PANELİ ---
    if st.session_state["role"] == "admin":
        st.sidebar.title("Hoş Geldiniz Nida Hocam")
        menu = st.sidebar.radio("Menü", ["Öğrenci Kaydı & Şifre", "Analiz & Veli Raporu"])
        if st.sidebar.button("Güvenli Çıkış"): del st.session_state["logged_in"]; st.rerun()

        if menu == "Öğrenci Kaydı & Şifre":
            with st.expander("👤 Yeni Öğrenci Kaydet"):
                ad = st.text_input("Öğrenci Ad Soyad")
                grp = st.selectbox("Sınav Grubu", ["LGS", "YKS"])
                o_tel = st.text_input("Öğrenci Tel (905...)")
                v_tel = st.text_input("Veli Tel (905...)")
                hedef = st.number_input("Haftalık Soru Hedefi", 100)
                if st.button("Kaydı Tamamla"):
                    sifre = str(random.randint(1000, 9999))
                    if "ogrenciler" not in st.session_state.db: st.session_state.db["ogrenciler"] = {}
                    st.session_state.db["ogrenciler"][ad] = {"soru": [], "denemeler": [], "sinav": grp, "hedef": hedef, "o_tel": o_tel, "v_tel": v_tel, "sifre": sifre}
                    veri_kaydet(st.session_state.db); st.success(f"{ad} eklendi! Şifre: {sifre}")

            st.subheader("📋 Öğrenci Listesi")
            for isim, d in st.session_state.db.get("ogrenciler", {}).items():
                c1, c2 = st.columns([3, 1])
                c1.write(f"*{isim}* ({d['sinav']}) | Şifre: {d['sifre']} | Hedef: {d['hedef']}")
                msg = f"Selam {isim}, Nida Akademi giriş şifren: {d['sifre']}\nLink: {SITE_URL}"
                c2.markdown(f'[📲 Şifre Gönder](https://wa.me/{d["o_tel"]}?text={urllib.parse.quote(msg)})')

        elif menu == "Analiz & Veli Raporu":
            ogrenciler = list(st.session_state.db.get("ogrenciler", {}).keys())
            if not ogrenciler: st.warning("Henüz öğrenci yok.")
            else:
                secilen = st.selectbox("Öğrenci Seç", ogrenciler)
                o = st.session_state.db["ogrenciler"][secilen]
                df = pd.DataFrame(o["soru"])
                bugun = datetime.now().strftime("%d/%m")
                
                st.title(f"📊 {secilen} Performans Analizi")
                
                # 🎯 HEDEF BAR
                h_toplam = df['Toplam'].sum() if not df.empty else 0
                yuzde = min(h_toplam / o['hedef'], 1.0) if o['hedef'] > 0 else 0
                st.subheader(f"Haftalık Hedef Durumu: {h_toplam} / {o['hedef']}")
                st.progress(yuzde)
                st.write(f"Haftalık hedefin %{int(yuzde*100)} tamamlandı.")

                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📆 Günlük Yapılanlar")
                    if not df.empty: st.dataframe(df.sort_index(ascending=False), use_container_width=True)
                    else: st.info("Çalışma girişi yok.")
                
                with col2:
                    st.subheader("📚 Konu Bazlı Toplam")
                    if not df.empty:
                        konu_ozet = df.groupby(['Ders', 'Konu'])['Toplam'].sum().reset_index()
                        st.table(konu_ozet)
                
                # DENEME ANALİZİ
                if o["denemeler"]:
                    st.subheader("🏆 Deneme Geçmişi")
                    d_df = pd.DataFrame(o["denemeler"])
                    st.table(d_df[['Tarih', 'Puan', 'Yanlis_Listesi']])
                    son_p = d_df.iloc[-1]['Puan']
                    son_y = d_df.iloc[-1]['Yanlis_Listesi']
                else: son_p = 0; son_y = "Henüz girilmedi"

                # 📱 VELİ RAPORU (GÜNLÜK & HAFTALIK ÖZET)
                bugun_toplam = df[df['Tarih'].str.contains(bugun)]['Toplam'].sum() if not df.empty else 0
                v_msg = (f"Sayın Velimiz, {secilen} bugün {bugun_toplam} soru çözmüştür. "
                         f"Haftalık toplamı {h_toplam}/{o['hedef']} seviyesine ulaştı. "
                         f"Son deneme puanı: {son_p}. Yanlış konular: {son_y}. - Nida GÖMCELİ")
                
                st.divider()
                st.markdown(f'<a href="https://wa.me/{o["v_tel"]}?text={urllib.parse.quote(v_msg)}" target="_blank" style="background-color:#25D366; color:white; padding:15px; text-decoration:none; border-radius:10px; font-weight:bold; display:inline-block;">📱 BUGÜNKÜ RAPORU VELİYE GÖNDER</a>', unsafe_allow_html=True)

    # --- 6. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        m = M_LGS if o.get("sinav") == "LGS" else M_YKS
        st.title(f"Selam {u} ✨")
        tab1, tab2, tab3 = st.tabs(["📝 Çalışma Girişi", "🏆 Deneme Analizi", "📊 Gelişimim"])
        
        with tab1:
            st.subheader("Bugün Neler Çalıştın?")
            c1, c2 = st.columns(2)
            ders = c1.selectbox("Ders", list(m.keys()), key="std_d")
            konu = c2.selectbox("Konu", m[ders], key="std_k")
            dogru = c1.number_input("Doğru", 0, key="std_do")
            yanlis = c2.number_input("Yanlış", 0, key="std_ya")
            if st.button("Çalışmayı Kaydet"):
                o["soru"].append({"Tarih": datetime.now().strftime("%d/%m %H:%M"), "Ders": ders, "Konu": konu, "Toplam": dogru + yanlis})
                veri_kaydet(st.session_state.db); st.success("Harika! Veri başarıyla kaydedildi.")

        with tab2:
            st.subheader("Deneme Netlerini Gir (3 Yanlış 1 Doğruyu Götürür)")
            if o.get("sinav") == "LGS":
                col1, col2, col3 = st.columns(3)
                m_d = col1.number_input("Mat D", 0); m_y = col1.number_input("Mat Y", 0)
                f_d = col2.number_input("Fen D", 0); f_y = col2.number_input("Fen Y", 0)
                t_d = col3.number_input("Türk D", 0); t_y = col3.number_input("Türk Y", 0)
                i_d = col1.number_input("İnkılap D", 0); i_y = col1.number_input("İnkılap Y", 0)
                d_d = col2.number_input("Din D", 0); d_y = col2.number_input("Din Y", 0)
                ing_d = col3.number_input("İng D", 0); ing_y = col3.number_input("İng Y", 0)
                # LGS Puan
                m_n = m_d - (m_y/3); f_n = f_d - (f_y/3); t_n = t_d - (t_y/3)
                in_n = i_d - (i_y/3); di_n = d_d - (d_y/3); ig_n = ing_d - (ing_y/3)
                puan = 194 + (m_n*4.9) + (f_n*4.0) + (t_n*4.3) + (in_n*1.6) + (di_n*1.6) + (ig_n*1.6)
            else:
                c1, c2 = st.columns(2)
                tyt_d = c1.number_input("TYT D", 0); tyt_y = c1.number_input("TYT Y", 0)
                ayt_d = c2.number_input("AYT D", 0); ayt_y = c2.number_input("AYT Y", 0)
                puan = 100 + (tyt_d - tyt_y/4)*1.3 + (ayt_d - ayt_y/4)*3.0
            
            st.divider()
            st.subheader("⚠️ Yanlış Yaptığın Konuları Seç")
            y_ders = st.selectbox("Hangi Dersten Yanlışın Var?", list(m.keys()), key="y_ders_std")
            y_konular = st.multiselect("Yanlış Konuların", m[y_ders], key="y_konu_std")
            
            if st.button("Deneme Sonucunu İşle"):
                y_notu = f"{y_ders}: {', '.join(y_konular)}" if y_konular else "Yok"
                o["denemeler"].append({"Tarih": datetime.now().strftime("%d/%m"), "Puan": round(puan, 2), "Yanlis_Listesi": y_notu})
                veri_kaydet(st.session_state.db); st.success(f"Deneme Puanın: {round(puan, 2)} olarak kaydedildi!")

        with tab3:
            df_std = pd.DataFrame(o["soru"])
            if not df_std.empty:
                st.plotly_chart(px.bar(df_std.groupby("Ders")["Toplam"].sum().reset_index(), x="Ders", y="Toplam", color="Ders", title="Ders Bazlı Toplam Soru Sayıların"))
            st.markdown(f'<a href="https://wa.me/{HOCA_TEL}?text=Raporum Hazır Hocam!" target="_blank" style="background-color:#007bff; color:white; padding:10px; text-decoration:none; border-radius:5px; font-weight:bold;">📤 HOCAMA RAPOR GÖNDER</a>', unsafe_allow_html=True)
