import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import random

# --- 1. AYARLAR VE VERİ YÖNETİMİ ---
VERI_DOSYASI = "nida_v51_master.json"
KONU_BARAJI = 150  # Bir YKS konusunun %100 dolması için gereken soru (İsteğe göre değiştirin)

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

# --- 2. DEV MÜFREDAT (LGS & YKS AYRIMI) ---
M_LGS = {
    "Matematik": ["Çarpanlar Katlar", "Üslü İfadeler", "Kareköklü", "Veri Analizi", "Olasılık", "Cebirsel", "Denklemler", "Eşitsizlikler", "Üçgenler", "Eşlik Benzerlik", "Dönüşüm", "Geometrik Cisimler"],
    "Fen Bilimleri": ["Mevsimler", "DNA", "Basınç", "Madde", "Basit Makineler", "Enerji", "Elektrik"],
    "Türkçe": ["Sözcük-Cümle Anlam", "Paragraf", "Fiilimsiler", "Ögeler", "Yazım-Noktalama", "Söz Sanatları"],
    "İnkılap": ["Bir Kahraman Doğuyor", "Milli Uyanış", "Ya İstiklal Ya Ölüm", "Atatürkçülük", "Dış Politika"],
    "Din / İngilizce": ["Kader", "Zekat", "Din ve Hayat", "Friendship", "Teen Life", "Kitchen", "Internet"]
}

M_YKS = {
    "Matematik (TYT)": ["Temel Kavramlar", "Sayı Basamakları", "Bölme-Bölünebilme", "EBOB-EKOK", "Rasyonel Sayılar", "Basit Eşitsizlikler", "Mutlak Değer", "Üslü Sayılar", "Köklü Sayılar", "Çarpanlara Ayırma", "Oran-Orantı", "Denklem Çözme", "Problemler", "Kümeler", "Fonksiyonlar", "Polinomlar", "İstatistik"],
    "Matematik (AYT)": ["2. Derece Denklemler", "Karmaşık Sayılar", "Parabol", "Eşitsizlikler", "Logaritma", "Diziler", "Trigonometri", "Limit", "Türev", "İntegral"],
    "Geometri": ["Doğruda ve Üçgende Açılar", "Özel Üçgenler", "Üçgende Alan", "Üçgende Benzerlik", "Çokgenler", "Dörtgenler", "Çember ve Daire", "Analitik Geometri", "Katı Cisimler"],
    "Türkçe & Edebiyat": ["Sözcük-Cümle Anlamı", "Paragraf", "Dil Bilgisi", "Yazım-Noktalama", "Şiir Bilgisi", "Edebi Sanatlar", "İslamiyet Öncesi-Halk-Divan", "Tanzimat-Servetifünun", "Cumhuriyet Dönemi"],
    "Fizik": ["Kuvvet ve Hareket", "Enerji", "Elektrik ve Manyetizma", "Optik", "Dalgalar", "Modern Fizik"],
    "Kimya": ["Kimya Bilimi", "Atom ve Periyodik Sistem", "Mol Kavramı", "Çözeltiler", "Enerji-Hız-Denge", "Organik Kimya"],
    "Biyoloji": ["Hücre", "Canlıların Temel Bileşenleri", "Kalıtım", "Sistemler", "Bitki Biyolojisi", "Ekoloji"],
    "Tarih & Coğrafya": ["Tarih Bilimi", "Osmanlı Tarihi", "İnkılap Tarihi", "Doğa ve İnsan", "İklim Bilgisi", "Nüfus ve Yerleşme", "Ekonomik Faaliyetler"]
}

# --- 3. TASARIM ---
st.set_page_config(page_title="Nida Akademi v51 Master", layout="wide")
st.markdown("<style>.stApp { background-color: #0d1117; color: white; }</style>", unsafe_allow_html=True)

# --- 4. GİRİŞ KONTROLÜ ---
if "logged_in" not in st.session_state:
    st.title("🎓 Nida Akademi Eğitim Koçu")
    u = st.text_input("Ad Soyad"); p = st.text_input("Şifre", type="password")
    if st.button("Giriş Yap"):
        if u == "admin" and p == "nida2024": st.session_state.update({"logged_in": True, "role": "admin"}); st.rerun()
        elif u in st.session_state.db.get("ogrenciler", {}):
            if st.session_state.db["ogrenciler"][u].get("sifre") == p:
                st.session_state.update({"logged_in": True, "role": "ogrenci", "user": u}); st.rerun()
        else: st.error("Bilgiler hatalı!")
else:
    # --- 5. ADMIN PANELİ ---
    if st.session_state["role"] == "admin":
        st.sidebar.title("Nida Hocam")
        menu = st.sidebar.radio("Menü", ["Öğrenci Kaydı", "Analiz & Otomatik Müfredat"])
        if st.sidebar.button("Çıkış"): del st.session_state["logged_in"]; st.rerun()

        if menu == "Öğrenci Kaydı":
            with st.expander("👤 Yeni Öğrenci Ekle"):
                ad = st.text_input("Ad Soyad")
                grp = st.selectbox("Sınav Grubu", ["LGS", "YKS"])
                v_t = st.text_input("Veli Tel (905...)")
                h = st.number_input("Haftalık Soru Hedefi", 100)
                if st.button("Kaydet"):
                    s = str(random.randint(1000, 9999))
                    st.session_state.db["ogrenciler"][ad] = {"soru": [], "denemeler": [], "sinav": grp, "hedef": h, "v_tel": v_t, "sifre": s}
                    veri_kaydet(st.session_state.db); st.success(f"{ad} için Şifre: {s}")

        elif menu == "Analiz & Otomatik Müfredat":
            ogrenciler = list(st.session_state.db.get("ogrenciler", {}).keys())
            if not ogrenciler: st.warning("Henüz öğrenci yok.")
            else:
                sec = st.selectbox("Öğrenci Seç", ogrenciler)
                o = st.session_state.db["ogrenciler"][sec]
                df = pd.DataFrame(o["soru"])
                m = M_LGS if o["sinav"] == "LGS" else M_YKS
                
                st.title(f"📊 {sec} - {o['sinav']} Gelişim Analizi")
                
                # OTOMATİK MÜFREDAT GÖSTERİMİ
                if not df.empty:
                    konu_ozet = df.groupby(['Ders', 'Konu'])['Toplam'].sum().reset_index()
                    for d_adi, konular in m.items():
                        st.subheader(f"📘 {d_adi}")
                        cols = st.columns(2)
                        for i, kn in enumerate(konular):
                            cozulen = konu_ozet[(konu_ozet['Ders'] == d_adi) & (konu_ozet['Konu'] == kn)]['Toplam'].sum()
                            yuzde = min(int((cozulen / KONU_BARAJI) * 100), 100)
                            r = "🔴" if yuzde < 30 else "🟡" if yuzde < 70 else "🟢"
                            cols[i % 2].write(f"{r} *{kn}*: {cozulen}/{KONU_BARAJI} Soru (%{yuzde})")
                            cols[i % 2].progress(yuzde / 100)
                
                # VELİYE RAPOR
                bugun = datetime.now().strftime("%d/%m")
                b_df = df[df['Tarih'].str.contains(bugun)] if not df.empty else pd.DataFrame()
                v_msg = f"Sayın Veli, {sec} bugün {b_df['Toplam'].sum() if not b_df.empty else 0} soru çözdü ve {b_df['Sure'].sum() if not b_df.empty else 0} dk çalıştı. - Nida GÖMCELİ"
                st.markdown(f'<a href="https://wa.me/{o["v_tel"]}?text={urllib.parse.quote(v_msg)}" target="_blank" style="background-color:#25D366; color:white; padding:15px; text-decoration:none; border-radius:10px;">📱 VELİYE BUGÜNKÜ RAPORU AT</a>', unsafe_allow_html=True)

    # --- 6. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        m = M_LGS if o["sinav"] == "LGS" else M_YKS
        st.title(f"Selam {u} ✨")
        t1, t2 = st.tabs(["📝 Çalışma Girişi", "📊 Müfredat Durumum"])

        with t1:
            tur = st.selectbox("Çalışma Türü", ["Soru Çözümü", "Konu Videosu", "Özel Ders", "Etüt", "Kitap Okuma"])
            c1, c2 = st.columns(2)
            d = c1.selectbox("Ders", list(m.keys())); k = c2.selectbox("Konu", m[d])
            soru = c1.number_input("Soru Sayısı", 0); sure = c2.number_input("Süre (Dakika)", 15, step=15)
            if st.button("Kaydet"):
                o["soru"].append({"Tarih": datetime.now().strftime("%d/%m %H:%M"), "Tür": tur, "Ders": d, "Konu": k, "Toplam": soru, "Sure": sure})
                veri_kaydet(st.session_state.db); st.success("Harika! Veriler işlendi ve müfredatın güncellendi.")

        with t2:
            st.subheader("🎯 Konu Bazlı İlerleme Durumun")
            df_std = pd.DataFrame(o["soru"])
            if not df_std.empty:
                konu_ozet_std = df_std.groupby(['Ders', 'Konu'])['Toplam'].sum().reset_index()
                for d_adi, konular in m.items():
                    with st.expander(f"{d_adi} İlerlemesi"):
                        for kn in konular:
                            cozulen = konu_ozet_std[(konu_ozet_std['Ders'] == d_adi) & (konu_ozet_std['Konu'] == kn)]['Toplam'].sum()
                            yuzde = min(int((cozulen / KONU_BARAJI) * 100), 100)
                            st.write(f"*{kn}*: {cozulen} Soru")
                            st.progress(yuzde / 100)
            else: st.info("Henüz çalışma girmemişsin, haydi masaya! 💪")
