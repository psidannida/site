import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import time
import random

# --- 1. AYARLAR & VERİ SİSTEMİ ---
VERI_DOSYASI = "nida_v58_final.json"
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

# --- 2. TAM MÜFREDAT LİSTESİ (YKS & LGS) ---
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
    "Türkçe & Edebiyat": ["Sözcük ve Cümle Anlamı", "Paragraf", "Ses-Yazım-Noktalama", "Sözcük Türleri", "Cümlenin Ögeleri", "Şiir Bilgisi", "Edebi Sanatlar", "İslamiyet Öncesi-Halk-Divan Edebiyatı", "Tanzimat-Servetifünun-Fecriati", "Milli Edebiyat", "Cumhuriyet Dönemi", "Edebi Akımlar"],
    "TYT Fizik": ["Fizik Bilimine Giriş", "Madde ve Özellikleri", "Hareket ve Kuvvet", "Enerji", "Isı ve Sıcaklık", "Elektrostatik", "Optik", "Dalgalar"],
    "AYT Fizik": ["Vektörler", "Bağıl Hareket", "Newton’un Hareket Yasaları", "Atışlar", "İş-Güç-Enerji", "İtme ve Çizgisel Momentum", "Tork-Denge", "Basit Makineler", "Elektriksel Kuvvet ve Potansiyel", "Manyetizma", "Çembersel Hareket", "Basit Harmonik Hareket", "Atom Fiziği"],
    "TYT Kimya": ["Kimya Bilimi", "Atom ve Periyodik Sistem", "Kimyasal Türler Arası Etkileşimler", "Maddenin Halleri", "Doğa ve Kimya", "Kimyanın Temel Kanunları", "Karışımlar", "Asit-Baz-Tuz"],
    "AYT Kimya": ["Modern Atom Teorisi", "Gazlar", "Sıvı Çözeltiler", "Kimyasal Tepkimelerde Enerji", "Tepkime Hızı", "Kimyasal Denge", "Asit-Baz Dengesi", "Çözünürlük Dengesi", "Kimya ve Elektrik", "Karbon Kimyasına Giriş", "Organik Kimya"],
    "TYT Biyoloji": ["Canlıların Ortak Özellikleri", "Temel Bileşenler", "Hücre", "Canlıların Dünyası", "Hücre Bölünmeleri", "Kalıtım", "Ekosistem Ekolojisi"],
    "AYT Biyoloji": ["Denetleyici ve Düzenleyici Sistemler", "Duyu Organları", "Destek ve Hareket Sistemi", "Sindirim-Dolaşım-Solunum", "Boşaltım Sistemi", "Üreme Sistemi", "Komünite ve Popülasyon Ekolojisi", "Genden Proteine", "Canlılarda Enerji Dönüşümleri", "Bitki Biyolojisi"],
    "Tarih": ["Tarih ve Zaman", "İlk ve Orta Çağlarda Türk Dünyası", "İslam Medeniyetinin Doğuşu", "Türklerin İslamiyet’i Kabulü", "Osmanlı Kuruluş-Yükselme-Duraklama", "20. Yüzyılda Osmanlı", "Kurtuluş Savaşı", "Atatürk İlke ve İnkılapları"],
    "Coğrafya": ["Doğa ve İnsan", "Dünya’nın Şekli ve Hareketleri", "Yer ve Zaman", "Harita Bilgisi", "Atmosfer ve İklim", "Nüfus", "Ekonomik Faaliyetler", "Türkiye’nin Yer Şekilleri", "Küresel Ortam ve Çevre"]
}

# --- 3. TASARIM ---
st.set_page_config(page_title="Nida Akademi v58", layout="wide")
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
        if st.sidebar.button("Çıkış"): del st.session_state["logged_in"]; st.rerun()

        if menu == "Öğrenci Kaydı":
            with st.expander("👤 Yeni Öğrenci Ekle"):
                ad = st.text_input("Ad Soyad")
                grp = st.selectbox("Sınav Grubu", ["LGS", "YKS"])
                v_t = st.text_input("Veli Tel (905...)")
                h = st.number_input("Haftalık Hedef", 100)
                if st.button("Kaydet"):
                    s = str(random.randint(1000, 9999))
                    st.session_state.db["ogrenciler"][ad] = {"soru": [], "denemeler": [], "sinav": grp, "hedef": h, "v_tel": v_t, "sifre": s, "gunluk_puanlar": []}
                    veri_kaydet(st.session_state.db); st.success(f"Şifre: {s}")

        elif menu == "Analiz & Veli Raporları":
            sec = st.selectbox("Öğrenci Seç", list(st.session_state.db.get("ogrenciler", {}).keys()))
            o = st.session_state.db["ogrenciler"][sec]
            df = pd.DataFrame(o["soru"])
            st.title(f"📊 {sec} - Gelişim Raporu")
            
            if not df.empty:
                konu_ozet = df.groupby(['Ders', 'Konu'])['Toplam'].sum().reset_index()
                m_liste = M_LGS if o["sinav"] == "LGS" else M_YKS
                for d_adi, konular in m_liste.items():
                    st.subheader(f"📘 {d_adi}")
                    cozulen_toplam = konu_ozet[konu_ozet['Ders'] == d_adi]['Toplam'].sum()
                    yuzde = min(int(cozulen_toplam / (len(konular) * KONU_BARAJI) * 100), 100)
                    st.write(f"Soru Sayısı: {cozulen_toplam} | Başarı: %{yuzde}")
                    st.progress(yuzde / 100)

                bugun = datetime.now().strftime("%d/%m")
                b_df = df[df['Tarih'].str.contains(bugun)]
                v_msg = f"Sayın Veli, {sec} bugün {b_df['Sure'].sum()} dk çalıştı. {b_df['Toplam'].sum()} soru çözdü. - Nida GÖMCELİ"
                st.markdown(f'<a href="https://wa.me/{o["v_tel"]}?text={urllib.parse.quote(v_msg)}" target="_blank" style="background-color:#25D366; color:white; padding:15px; text-decoration:none; border-radius:10px;">📱 VELİYE RAPOR AT</a>', unsafe_allow_html=True)

    # --- 6. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        m = M_LGS if o["sinav"] == "LGS" else M_YKS
        st.title(f"Selam {u} ✨")
        
        # --- HOCAMA BİLDİR & KRONOMETRE ---
        with st.container():
            msg_h = st.text_input("Nida Hocama Mesaj Gönder:")
            if st.button("📩 Hocama Bildir"):
                w_url = f"https://wa.me/{HOCA_TEL}?text={urllib.parse.quote(f'Hocam Ben {u}: {msg_h}')}"
                st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'{w_url}\'">', unsafe_allow_html=True)

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

        tabs = st.tabs(["🌟 Modum", "📝 Çalışma", "📊 Müfredat", "🏆 Deneme Analizi", "🧮 Puan Robotu"])

        with tabs[0]:
            st.subheader("Bugün Nasıl Hissediyorsun?")
            p_bugun = st.slider("Kendine puanın (1-10)", 1, 10, 8)
            m_bugun = st.selectbox("Modun", ["Harika", "Enerjik", "Yorgun", "Üzgün", "Stresli"])
            if st.button("Kaydet"):
                o["gunluk_puanlar"].append({"Tarih": datetime.now().strftime("%d/%m"), "Puan": p_bugun, "Mod": m_bugun})
                veri_kaydet(st.session_state.db); st.success("Kaydedildi!")

        with tabs[1]:
            tur = st.selectbox("Tür", ["Soru Çözümü", "Konu Videosu", "Özel Ders", "Kitap"])
            d = st.selectbox("Ders", list(m.keys())); k = st.selectbox("Konu", m[d])
            soru = st.number_input("Soru", 0); sure = st.number_input("Süre (dk)", value=mins)
            if st.button("Çalışmayı İşle"):
                o["soru"].append({"Tarih": datetime.now().strftime("%d/%m %H:%M"), "Tür": tur, "Ders": d, "Konu": k, "Toplam": soru, "Sure": sure})
                veri_kaydet(st.session_state.db); st.success("Kaydedildi!")

        with tabs[2]:
            df_std = pd.DataFrame(o["soru"])
            if not df_std.empty:
                k_oz = df_std.groupby(['Ders', 'Konu'])['Toplam'].sum().reset_index()
                for d_adi, konular in m.items():
                    with st.expander(f"📘 {d_adi}"):
                        for kn in konular:
                            coz = k_oz[(k_oz['Ders'] == d_adi) & (k_oz['Konu'] == kn)]['Toplam'].sum()
                            yuz = min(int((coz / KONU_BARAJI) * 100), 100)
                            st.write(f"*{kn}*: %{yuz} ({coz} Soru)"); st.progress(yuz / 100)

        with tabs[3]:
            st.subheader("🏆 Branş Bazlı Deneme Analizi")
            deneme_data = {"Tarih": datetime.now().strftime("%d/%m"), "Eksikler": []}
            for b_adi in m.keys():
                st.markdown(f"*{b_adi}*")
                col1, col2 = st.columns(2)
                d_val = col1.number_input(f"{b_adi} D", 0, key=f"d_{b_adi}")
                y_val = col2.number_input(f"{b_adi} Y", 0, key=f"y_{b_adi}")
                eksik_secim = st.multiselect(f"{b_adi} Yanlış Konuların", m[b_adi], key=f"e_{b_adi}")
                deneme_data[b_adi] = {"D": d_val, "Y": y_val}
                deneme_data["Eksikler"].extend(eksik_secim)
            if st.button("Denemeyi Kaydet"):
                o["denemeler"].append(deneme_data); veri_kaydet(st.session_state.db); st.success("Analiz yüklendi!")

        with tabs[4]:
            st.subheader("🧮 Net ve Puan Robotu")
            toplam_net = 0
            for b_adi in m.keys():
                col1, col2 = st.columns(2)
                d_r = col1.number_input(f"{b_adi} Doğru", 0, key=f"pr_d_{b_adi}")
                y_r = col2.number_input(f"{b_adi} Yanlış", 0, key=f"pr_y_{b_adi}")
                toplam_net += d_r - (y_r/3 if o["sinav"]=="LGS" else y_r/4)
            puan_f = 100 + (toplam_net * 1.5)
            st.write(f"## Toplam Net: {round(toplam_net, 2)} | Tahmini Puan: {round(puan_f, 2)}")
