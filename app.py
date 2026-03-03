import streamlit as st
import pandas as pd
import json
import os
import urllib.parse
from datetime import datetime
import time
import random

# --- 1. AYARLAR & VERİ SİSTEMİ ---
VERI_DOSYASI = "nida_v57_final.json"
HOCA_TEL = "905307368072"
KONU_BARAJI = 150 

def veri_yukle():
    if os.path.exists(VERI_DOSYASI):
        try:
            with open(VERI_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {"ogrenciler": {}, "gunluk_mod": {}}
    return {"ogrenciler": {}, "gunluk_mod": {}}

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
st.set_page_config(page_title="Nida Akademi v57", layout="wide")
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
            st.title(f"📊 {sec} Analizi")
            
            # DUYGUSAL DURUM GÖSTERİMİ
            if "gunluk_puanlar" in o and o["gunluk_puanlar"]:
                st.subheader("🧠 Bugün Nasıl Hissediyor?")
                son_mod = o["gunluk_puanlar"][-1]
                st.info(f"Tarih: {son_mod['Tarih']} | Puan: {son_mod['Puan']}/10 | Mod: {son_mod['Mod']}")
                if son_mod['Not']: st.write(f"Öğrenci Notu: {son_mod['Not']}")

            # MÜFREDAT ANALİZİ
            if not df.empty:
                konu_ozet = df.groupby(['Ders', 'Konu'])['Toplam'].sum().reset_index()
                for d_adi, konular in (M_LGS if o["sinav"] == "LGS" else M_YKS).items():
                    st.subheader(f"📘 {d_adi}")
                    coz_t = konu_ozet[konu_ozet['Ders'] == d_adi]['Toplam'].sum()
                    st.write(f"Toplam Çözülen: {coz_t} Soru")
                    st.progress(min(int(coz_t/(len(konular)*KONU_BARAJI)*100), 100)/100)

                bugun = datetime.now().strftime("%d/%m")
                b_df = df[df['Tarih'].str.contains(bugun)]
                v_msg = f"Sayın Veli, {sec} bugün {b_df['Sure'].sum()} dk çalıştı. {b_df['Toplam'].sum()} soru çözdü. Modu: {o['gunluk_puanlar'][-1]['Mod'] if o.get('gunluk_puanlar') else 'Belirtilmedi'} - Nida GÖMCELİ"
                st.markdown(f'<a href="https://wa.me/{o["v_tel"]}?text={urllib.parse.quote(v_msg)}" target="_blank" style="background-color:#25D366; color:white; padding:15px; text-decoration:none; border-radius:10px;">📱 VELİYE RAPOR AT</a>', unsafe_allow_html=True)

    # --- 6. ÖĞRENCİ PANELİ ---
    else:
        u = st.session_state["user"]; o = st.session_state.db["ogrenciler"][u]
        m = M_LGS if o["sinav"] == "LGS" else M_YKS
        st.title(f"Selam {u} ✨")
        
        # --- HOCAMA BİLDİR & KRONOMETRE ---
        with st.expander("📩 Nida Hocama Mesaj Gönder"):
            msg = st.text_area("Mesajın...")
            if st.button("WhatsApp ile Gönder"):
                w_url = f"https://wa.me/{HOCA_TEL}?text={urllib.parse.quote(f'Hocam Ben {u}: {msg}')}"
                st.markdown(f'<a href="{w_url}" target="_blank" style="color:white; background:blue; padding:10px;">Gönder</a>', unsafe_allow_html=True)

        st.subheader("⏱️ Canlı Kronometre")
        if 'elapsed_time' not in st.session_state: st.session_state.elapsed_time = 0
        if 'running' not in st.session_state: st.session_state.running = False
        c1, c2, c3 = st.columns(3)
        if c1.button("▶️ Başlat"): st.session_state.start_time = time.time() - st.session_state.elapsed_time; st.session_state.running = True
        if c2.button("⏸️ Durdur"): st.session_state.running = False
        if c3.button("🔄 Sıfırla"): st.session_state.elapsed_time = 0; st.session_state.running = False
        if st.session_state.running: st.session_state.elapsed_time = time.time() - st.session_state.start_time
        mins, secs = divmod(int(st.session_state.elapsed_time), 60)
        st.header(f"{mins:02d}:{secs:02d}")
        if st.session_state.running: time.sleep(1); st.rerun()

        t1, t2, t3, t4, t5 = st.tabs(["🌟 Bugün Nasıldım?", "📝 Çalışma", "📊 Müfredat", "🏆 Deneme", "🧮 Puan"])

        with t1:
            st.subheader("🌈 Günlük Değerlendirme")
            g_puan = st.slider("Bugün kendine kaç puan veriyorsun?", 1, 10, 5)
            g_mod = st.select_slider("Şu anki modun nasıl?", options=["Çok Kötü", "Yorgun", "Normal", "Enerjik", "Harika!"])
            g_not = st.text_area("Hocana bugünün özeti olarak ne söylemek istersin?")
            if st.button("Günümü Kaydet"):
                if "gunluk_puanlar" not in o: o["gunluk_puanlar"] = []
                o["gunluk_puanlar"].append({
                    "Tarih": datetime.now().strftime("%d/%m"),
                    "Puan": g_puan, "Mod": g_mod, "Not": g_not
                })
                veri_kaydet(st.session_state.db); st.success("Bugün tarihe not düşüldü! 💪")

        with t2:
            tur = st.selectbox("Tür", ["Soru Çözümü", "Video", "Özel Ders", "Kitap"])
            d = st.selectbox("Ders", list(m.keys())); k = st.selectbox("Konu", m[d])
            soru = st.number_input("Soru", 0); sure = st.number_input("Süre (dk)", value=mins)
            if st.button("Çalışmayı Kaydet"):
                o["soru"].append({"Tarih": datetime.now().strftime("%d/%m %H:%M"), "Tür": tur, "Ders": d, "Konu": k, "Toplam": soru, "Sure": sure})
                veri_kaydet(st.session_state.db); st.success("Kaydedildi!")

        with t3:
            df_std = pd.DataFrame(o["soru"])
            if not df_std.empty:
                k_oz = df_std.groupby(['Ders', 'Konu'])['Toplam'].sum().reset_index()
                for d_adi, konular in m.items():
                    with st.expander(f"{d_adi}"):
                        for kn in konular:
                            coz = k_oz[(k_oz['Ders'] == d_adi) & (k_oz['Konu'] == kn)]['Toplam'].sum()
                            yuz = min(int((coz / KONU_BARAJI) * 100), 100)
                            st.write(f"*{kn}*: %{yuz} ({coz} Soru)"); st.progress(yuz / 100)

        with t4:
            st.subheader("🏆 Deneme Branş Analizi")
            deneme_verisi = {"Eksikler": []}
            for ders_adi in m.keys():
                st.write(f"--- *{ders_adi}* ---")
                col1, col2 = st.columns(2)
                d_s = col1.number_input(f"{ders_adi} D", 0, key=f"d_{ders_adi}")
                y_s = col2.number_input(f"{ders_adi} Y", 0, key=f"y_{ders_adi}")
                eksik = st.multiselect(f"{ders_adi} Yanlış Konuların", m[ders_adi], key=f"e_{ders_adi}")
                deneme_verisi[ders_adi] = {"D": d_s, "Y": y_s}
                deneme_verisi["Eksikler"].extend(eksik)
            if st.button("Denemeyi İşle"):
                deneme_verisi["Tarih"] = datetime.now().strftime("%d/%m")
                o["denemeler"].append(deneme_verisi); veri_kaydet(st.session_state.db); st.success("Kaydedildi!")

        with t5:
            st.subheader("🧮 Net Hesapla")
            total_net = 0
            for ders_adi in m.keys():
                col1, col2 = st.columns(2)
                d_r = col1.number_input(f"{ders_adi} Doğru", 0, key=f"p_d_{ders_adi}")
                y_r = col2.number_input(f"{ders_adi} Yanlış", 0, key=f"p_y_{ders_adi}")
                total_net += d_r - (y_r/3 if o["sinav"]=="LGS" else y_r/4)
            st.write(f"## Toplam Net: {round(total_net, 2)}")
