import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import time
import random

# --- 1. AYARLAR & VERİ SİSTEMİ ---
VERI_DOSYASI = "nida_v59_final.json"
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

# --- 2. MÜFREDAT LİSTESİ ---
M_LGS = {
    "Matematik": ["Çarpanlar Katlar", "Üslü İfadeler", "Kareköklü", "Veri Analizi", "Olasılık", "Cebirsel", "Denklemler", "Eşitsizlikler", "Üçgenler", "Eşlik Benzerlik", "Dönüşüm", "Geometrik Cisimler"],
    "Fen Bilimleri": ["Mevsimler", "DNA", "Basınç", "Madde", "Basit Makineler", "Enerji", "Elektrik"],
    "Türkçe": ["Anlam Bilgisi", "Paragraf", "Fiilimsiler", "Cümlenin Ögeleri", "Yazım-Noktalama", "Söz Sanatları", "Anlatım Bozukluğu"],
    "İnkılap": ["Bir Kahraman Doğuyor", "Milli Uyanış", "Ya İstiklal", "Atatürkçülük", "Dış Politika"],
    "Din / İngilizce": ["Kader", "Zekat", "Din ve Hayat", "Hz. Muhammed", "Friendship", "Teen Life", "Kitchen", "Internet"]
}

M_YKS = {
    "TYT Matematik": ["Temel Kavramlar", "Basamak Kavramı", "Bölme-Bölünebilme", "EBOB-EKOK", "Rasyonel Sayılar", "Basit Eşitsizlikler", "Mutlak Değer", "Üslü Sayılar", "Köklü Sayılar", "Çarpanlara Ayırma", "Oran-Orantı", "Denklem Çözme", "Problemler", "Kümeler", "Fonksiyonlar", "Permütasyon-Kombinasyon", "Olasılık", "Veri-İstatistik"],
    "AYT Matematik": ["Polinomlar", "İkinci Dereceden Denklemler", "Karmaşık Sayılar", "Eşitsizlikler", "Parabol", "Trigonometri", "Logaritma", "Diziler", "Limit", "Türev", "İntegral"],
    "Geometri": ["Doğruda ve Üçgende Açılar", "Özel Üçgenler", "Üçgende Alan ve Benzerlik", "Çokgenler", "Dörtgenler", "Çember ve Daire", "Analitik Geometri", "Katı Cisimler"],
    "Türkçe & Edebiyat": ["Sözcük ve Cümle Anlamı", "Paragraf", "Ses-Yazım-Noktalama", "Sözcük Türleri", "Cümlenin Ögeleri", "Şiir Bilgisi", "Edebi Sanatlar", "Halk-Divan Edebiyatı", "Tanzimat-Milli-Cumhuriyet", "Edebi Akımlar"],
    "TYT Fizik": ["Fizik Bilimine Giriş", "Madde", "Hareket", "Enerji", "Isı ve Sıcaklık", "Optik", "Dalgalar"],
    "AYT Fizik": ["Newton Yasaları", "Atışlar", "Enerji", "Momentum", "Tork", "Manyetizma", "Çembersel Hareket", "Atom Fiziği"],
    "TYT Kimya": ["Kimya Bilimi", "Atom", "Etkileşimler", "Maddenin Halleri", "Doğa", "Karışımlar"],
    "AYT Kimya": ["Modern Atom", "Gazlar", "Çözeltiler", "Enerji", "Hız", "Denge", "Kimya ve Elektrik", "Organik"],
    "TYT Biyoloji": ["Canlıların Ortak Özellikleri", "Hücre", "Bölünmeler", "Kalıtım", "Ekoloji"],
    "AYT Biyoloji": ["Sistemler", "Genden Proteine", "Enerji Dönüşümleri", "Bitki Biyolojisi"],
    "Tarih": ["Tarih Bilimi", "İlk Türk Devletleri", "Osmanlı", "Kurtuluş Savaşı", "İnkılap Tarihi"],
    "Coğrafya": ["Doğa ve İnsan", "İklim", "Nüfus", "Ekonomik Faaliyetler", "Türkiye Coğrafyası"]
}

# --- 3. TASARIM ---
st.set_page_config(page_title="Nida Akademi v59", layout="wide")
st.markdown("<style>.stApp { background-color: #0d1117; color: white; }</style>", unsafe_allow_html=True)

# --- 4. GİRİŞ KONTROL ---
if "logged_in" not in st.session_state:
    st.title("🎓 Nida Akademi Giriş Paneli")
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
        else: st.error("Kullanıcı adı veya şifre hatalı!")
else:
    # --- 5. ADMIN PANELİ ---
    if st.session_state["role"] == "admin":
        st.sidebar.title("Nida Hocam")
        menu = st.sidebar.radio("Menü", ["Öğrenci Kaydı", "Analiz & Veli Raporları"])
        st.sidebar.divider()
        if st.sidebar.button("🔴 Çıkış Yap"):
            del st.session_state["logged_in"]
            st.rerun()

        if menu == "Öğrenci Kaydı":
            with st.expander("👤 Yeni Öğrenci Ekle"):
                ad = st.text_input("Ad Soyad")
                grp = st.selectbox("Sınav Grubu", ["LGS", "YKS"])
                v_t = st.text_input("Veli Tel (905...)")
                h = st.number_input("Haftalık Hedef", 100)
                if st.button("Kaydet"):
                    s = str(random.randint(1000, 9999))
                    st.session_state.db["ogrenciler"][ad] = {"soru": [], "denemeler": [], "sinav": grp, "hedef": h, "v_tel": v_t, "sifre": s, "gunluk_puanlar": []}
                    veri_kaydet(st.session_state.db); st.success(f"Öğrenci Kaydedildi. Şifre: {s}")

        elif menu == "Analiz & Veli Raporları":
            ogrenciler = list(st.session_state.db.get("ogrenciler", {}).keys())
            if not ogrenciler:
                st.info("Sistemde henüz kayıtlı öğrenci yok.")
            else:
                sec = st.selectbox("Öğrenci Seç", ogrenciler)
                if sec:
                    o = st.session_state.db["ogrenciler"][sec]
                    df = pd.DataFrame(o.get("soru", []))
                    st.title(f"📊 {sec} - Performans Raporu")
                    
                    if not df.empty:
                        konu_ozet = df.groupby(['Ders', 'Konu'])['Toplam'].sum().reset_index()
                        m_liste = M_LGS if o["sinav"] == "LGS" else M_YKS
                        for d_adi, konular in m_liste.items():
                            st.subheader(f"📘 {d_adi}")
                            coz = konu_ozet[konu_ozet['Ders'] == d_adi]['Toplam'].sum()
                            st.write(f"Soru: {coz}")
                            st.progress(min(int(coz/(len(konular)*150)*100), 100)/100)
                        
                        bugun = datetime.now().strftime("%d/%m")
                        b_df = df[df['Tarih'].str.contains(bugun)]
                        v_msg = f"Sayın Veli, {sec} bugün {b_df['Sure'].sum()} dk çalıştı. - Nida GÖMCELİ"
                        st.markdown(f'<a href="https://wa.me/{o["v_tel"]}?text={urllib.parse.quote(v_msg)}" target="_blank" style="background-color:#25D366; color:white; padding:12px; text-decoration:none; border-radius:10px;">📱 VELİYE RAPOR AT</a>', unsafe_allow_html=True)

    # --- 6. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        m = M_LGS if o["sinav"] == "LGS" else M_YKS
        
        # ÜST BAR
        c_alt1, c_alt2 = st.columns([5,1])
        c_alt1.title(f"Selam {u} ✨")
        if c_alt2.button("Çıkış"):
            del st.session_state["logged_in"]
            st.rerun()
        
        # HOCAMA BİLDİR & KRONOMETRE
        with st.expander("📩 Nida Hocama Mesaj Gönder"):
            msg_h = st.text_input("Mesajınız:")
            if st.button("WhatsApp ile Gönder"):
                w_url = f"https://wa.me/{HOCA_TEL}?text={urllib.parse.quote(f'Hocam Ben {u}: {msg_h}')}"
                st.markdown(f'<a href="{w_url}" target="_blank" style="color:white; background:blue; padding:10px;">GÖNDER</a>', unsafe_allow_html=True)

        st.subheader("⏱️ Çalışma Kronometresi")
        if 'elapsed_time' not in st.session_state: st.session_state.elapsed_time = 0
        if 'running' not in st.session_state: st.session_state.running = False
        col1, col2, col3 = st.columns(3)
        if col1.button("▶️ Başlat"): st.session_state.start_time = time.time() - st.session_state.elapsed_time; st.session_state.running = True
        if col2.button("⏸️ Durdur"): st.session_state.running = False
        if col3.button("🔄 Sıfırla"): st.session_state.elapsed_time = 0; st.session_state.running = False
        if st.session_state.running: st.session_state.elapsed_time = time.time() - st.session_state.start_time
        mins, secs = divmod(int(st.session_state.elapsed_time), 60)
        st.header(f"{mins:02d}:{secs:02d}")
        if st.session_state.running: time.sleep(1); st.rerun()

        tabs = st.tabs(["🌟 Modum", "📝 Çalışma", "📊 Müfredat", "🏆 Deneme", "🧮 Puan"])

        with tabs[0]:
            st.subheader("Günün Nasıl Geçiyor?")
            p = st.slider("Günün Puanı", 1, 10, 7)
            md = st.selectbox("Modun", ["Harika", "Normal", "Yorgun", "Stresli"])
            if st.button("Bugünü Kaydet"):
                o["gunluk_puanlar"].append({"Tarih": datetime.now().strftime("%d/%m"), "Puan": p, "Mod": md})
                veri_kaydet(st.session_state.db); st.success("Günün kaydedildi!")

        with tabs[1]:
            d = st.selectbox("Ders", list(m.keys())); k = st.selectbox("Konu", m[d])
            soru = st.number_input("Soru", 0); sure = st.number_input("Süre (dk)", value=mins)
            if st.button("Kaydet"):
                o["soru"].append({"Tarih": datetime.now().strftime("%d/%m %H:%M"), "Ders": d, "Konu": k, "Toplam": soru, "Sure": sure})
                veri_kaydet(st.session_state.db); st.success("Çalışma kaydedildi!")

        with tabs[2]:
            for d_adi, konular in m.items():
                with st.expander(f"📘 {d_adi}"):
                    for kn in konular: st.write(f"- {kn}")

        with tabs[3]:
            st.subheader("🏆 Deneme Analizi")
            for b_adi in m.keys():
                st.markdown(f"*{b_adi}*")
                c1, c2 = st.columns(2)
                c1.number_input(f"{b_adi} D", 0, key=f"d_{b_adi}")
                c2.number_input(f"{b_adi} Y", 0, key=f"y_{b_adi}")
            if st.button("Denemeyi Sisteme İşle"):
                st.success("Tüm veriler kaydedildi!")
