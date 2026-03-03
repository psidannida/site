import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import time
import random

# --- 1. AYARLAR & VERİ SİSTEMİ ---
VERI_DOSYASI = "nida_v54_final.json"
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

# --- 2. TAM MÜFREDAT LİSTESİ ---
M_LGS = {
    "Matematik": ["Çarpanlar Katlar", "Üslü İfadeler", "Kareköklü", "Veri Analizi", "Olasılık", "Cebirsel", "Denklemler", "Eşitsizlikler", "Üçgenler", "Eşlik Benzerlik", "Dönüşüm", "Geometrik Cisimler"],
    "Fen Bilimleri": ["Mevsimler", "DNA", "Basınç", "Madde", "Basit Makineler", "Enerji", "Elektrik"],
    "Türkçe": ["Anlam Bilgisi", "Paragraf", "Fiilimsiler", "Cümlenin Ögeleri", "Yazım-Noktalama", "Söz Sanatları", "Anlatım Bozukluğu"],
    "İnkılap": ["Bir Kahraman Doğuyor", "Milli Uyanış", "Ya İstiklal", "Atatürkçülük", "Dış Politika"],
    "Din / İngilizce": ["Kader", "Zekat", "Din ve Hayat", "Hz. Muhammed", "Friendship", "Teen Life", "Kitchen", "Internet"]
}

M_YKS = {
    "TYT Matematik": ["Sayılar", "Bölünebilme", "EBOB-EKOK", "Rasyonel", "Basit Eşitsizlik", "Mutlak Değer", "Üslü-Köklü", "Çarpanlara Ayırma", "Oran-Orantı", "Problemler", "Kümeler", "Fonksiyonlar", "Veri-İstatistik", "Permütasyon-Olasılık"],
    "AYT Matematik": ["Polinomlar", "2. Derece Denklemler", "Eşitsizlikler", "Logaritma", "Diziler", "Trigonometri", "Limit", "Türev", "İntegral"],
    "Geometri": ["Üçgende Açılar", "Özel Üçgenler", "Benzerlik-Alan", "Çokgenler", "Daire", "Analitik Geometri", "Katı Cisimler"],
    "Türkçe-Edebiyat": ["Sözcük-Cümle Anlamı", "Paragraf", "Dil Bilgisi", "Yazım-Noktalama", "Şiir Bilgisi", "Sanatlar", "Dönemler", "Yazar-Eser"],
    "Fizik": ["Kuvvet ve Hareket", "Enerji", "Optik", "Dalgalar", "Elektrik", "Modern Fizik"],
    "Kimya": ["Atom", "Mol", "Bağlar", "Enerji", "Hız-Denge", "Çözeltiler", "Organik Kimya"],
    "Biyoloji": ["Hücre", "Kalıtım", "Sistemler", "Bitki Biyolojisi", "Ekoloji"],
    "Sosyal": ["Tarih", "Coğrafya", "Felsefe", "Din Kültürü"]
}

# --- 3. TASARIM ---
st.set_page_config(page_title="Nida Akademi v54 Master", layout="wide")
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
        if st.sidebar.button("Güvenli Çıkış"): del st.session_state["logged_in"]; st.rerun()

        if menu == "Öğrenci Kaydı":
            with st.expander("👤 Yeni Öğrenci Ekle"):
                ad = st.text_input("Ad Soyad")
                grp = st.selectbox("Sınav Grubu", ["LGS", "YKS"])
                v_t = st.text_input("Veli Tel (905...)")
                h = st.number_input("Haftalık Hedef", 100)
                if st.button("Kaydet"):
                    s = str(random.randint(1000, 9999))
                    st.session_state.db["ogrenciler"][ad] = {"soru": [], "denemeler": [], "sinav": grp, "hedef": h, "v_tel": v_t, "sifre": s}
                    veri_kaydet(st.session_state.db); st.success(f"Kaydedildi. Şifre: {s}")

        elif menu == "Analiz & Veli Raporları":
            sec = st.selectbox("Öğrenci Seç", list(st.session_state.db.get("ogrenciler", {}).keys()))
            o = st.session_state.db["ogrenciler"][sec]
            df = pd.DataFrame(o["soru"])
            m = M_LGS if o["sinav"] == "LGS" else M_YKS
            st.title(f"📊 {sec} - Gelişim Raporu")
            
            if not df.empty:
                konu_ozet = df.groupby(['Ders', 'Konu'])['Toplam'].sum().reset_index()
                for d_adi, konular in m.items():
                    st.subheader(f"📘 {d_adi}")
                    cols = st.columns(2)
                    for i, kn in enumerate(konular):
                        cozulen = konu_ozet[(konu_ozet['Ders'] == d_adi) & (konu_ozet['Konu'] == kn)]['Toplam'].sum()
                        yuzde = min(int((cozulen / KONU_BARAJI) * 100), 100)
                        cols[i % 2].write(f"*{kn}*: {cozulen}/{KONU_BARAJI} Soru (%{yuzde})")
                        cols[i % 2].progress(yuzde / 100)

                bugun = datetime.now().strftime("%d/%m")
                b_df = df[df['Tarih'].str.contains(bugun)]
                v_msg = f"Sayın Veli, {sec} bugün {b_df['Sure'].sum()} dk çalıştı. Toplam {b_df['Toplam'].sum()} soru çözdü. - Nida GÖMCELİ"
                st.markdown(f'<a href="https://wa.me/{o["v_tel"]}?text={urllib.parse.quote(v_msg)}" target="_blank" style="background-color:#25D366; color:white; padding:15px; text-decoration:none; border-radius:10px;">📱 VELİYE RAPOR AT</a>', unsafe_allow_html=True)

    # --- 6. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        m = M_LGS if o["sinav"] == "LGS" else M_YKS
        st.title(f"Selam {u} ✨")
        
        # --- HOCAMA BİLDİR (WHATSAPP) ---
        msg_hocam = st.text_input("Nida Hocama Mesaj Yaz:")
        if st.button("📩 Hocama Bildir"):
            w_url = f"https://wa.me/{HOCA_TEL}?text={urllib.parse.quote(f'Hocam Ben {u}: {msg_hocam}')}"
            st.markdown(f'<a href="{w_url}" target="_blank" style="background-color:#007bff; color:white; padding:10px; text-decoration:none; border-radius:5px;">Mesajı WhatsApp ile Gönder</a>', unsafe_allow_html=True)

        # --- KRONOMETRE ---
        st.divider()
        st.subheader("⏱️ Canlı Ders Kronometresi")
        if 'elapsed_time' not in st.session_state: st.session_state.elapsed_time = 0
        if 'running' not in st.session_state: st.session_state.running = False
        
        c1, c2, c3 = st.columns(3)
        if c1.button("▶️ Başlat"): 
            st.session_state.start_time = time.time() - st.session_state.elapsed_time
            st.session_state.running = True
        if c2.button("⏸️ Durdur"): st.session_state.running = False
        if c3.button("🔄 Sıfırla"): st.session_state.elapsed_time = 0; st.session_state.running = False

        if st.session_state.running: st.session_state.elapsed_time = time.time() - st.session_state.start_time
        mins, secs = divmod(int(st.session_state.elapsed_time), 60)
        st.header(f"{mins:02d}:{secs:02d}")
        if st.session_state.running: time.sleep(1); st.rerun()

        # --- TABLAR ---
        t1, t2, t3, t4 = st.tabs(["📝 Çalışma Girişi", "📊 Müfredat", "🏆 Deneme Analizi", "🧮 Puan Robotu"])

        with t1:
            tur = st.selectbox("Tür", ["Soru Çözümü", "Konu Videosu", "Özel Ders", "Kitap Okuma"])
            col1, col2 = st.columns(2)
            d = col1.selectbox("Ders", list(m.keys())); k = col2.selectbox("Konu", m[d])
            soru = col1.number_input("Soru Sayısı", 0); sure = col2.number_input("Süre (dk)", value=mins)
            if st.button("Kaydı Tamamla"):
                o["soru"].append({"Tarih": datetime.now().strftime("%d/%m %H:%M"), "Tür": tur, "Ders": d, "Konu": k, "Toplam": soru, "Sure": sure})
                veri_kaydet(st.session_state.db); st.success("Kaydedildi!")

        with t2:
            df_std = pd.DataFrame(o["soru"])
            if not df_std.empty:
                k_oz = df_std.groupby(['Ders', 'Konu'])['Toplam'].sum().reset_index()
                for d_adi, konular in m.items():
                    with st.expander(f"{d_adi}"):
                        for kn in konular:
                            coz = k_oz[(k_oz['Ders'] == d_adi) & (k_oz['Konu'] == kn)]['Toplam'].sum()
                            yuz = min(int((coz / KONU_BARAJI) * 100), 100)
                            st.write(f"*{kn}*: %{yuz} ({coz} Soru)"); st.progress(yuz / 100)

        with t3:
            st.subheader("Deneme Analizi")
            y_ders = st.selectbox("Eksik Ders Seç", list(m.keys()))
            y_konu = st.multiselect("Eksik Konuları Seç", m[y_ders])
            if st.button("Eksikleri Kaydet"):
                o["denemeler"].append({"Tarih": datetime.now().strftime("%d/%m"), "Eksikler": y_konu})
                veri_kaydet(st.session_state.db); st.success("Analiz eklendi.")

        with t4:
            st.subheader("🧮 Puan Hesaplama Robotu")
            if o["sinav"] == "LGS":
                m_n = st.number_input("Mat Net (D - Y/3)", 0.0)
                f_n = st.number_input("Fen Net (D - Y/3)", 0.0)
                t_n = st.number_input("Türkçe Net (D - Y/3)", 0.0)
                soz_n = st.number_input("Sözel Net Toplam (İnk+Din+İng)", 0.0)
                puan_h = 194 + (m_n * 4.95) + (f_n * 4.07) + (t_n * 4.33) + (soz_n * 1.6)
            else:
                tyt_net = st.number_input("TYT Toplam Net", 0.0)
                puan_h = 100 + (tyt_net * 1.32) + 50 # Örn Diploma
            st.write(f"## Tahmini Puanın: {round(puan_h, 2)}")
