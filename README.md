# 🛗 Asansör Bakım Takip Uygulaması

Bu proje, Google Sheets veya yerel CSV verilerini okuyarak asansörlerin bakım durumlarını takip eden, yeni bakım kayıtları giren ve bakım ekipleri için dinamik **QR Kod (Karekod)** üreten modern bir Streamlit uygulamasıdır.

Proje, özellikle **sütun ismi uyuşmazlığı hatalarını (KeyError / IndexError)** ve **macOS üzerindeki sanal ortam (.venv) modül algılama sorunlarını** kökten çözmek için yapılandırılmıştır.

---

## 🛠️ Çözülen Teknik Sorunlar

### 1. Dinamik Sütun Eşleştirme (KeyError: 'ID' Çözümü)
Uygulama, CSV dosyanızdaki sütun başlıklarını (örneğin `Asansör_ID`, `Bina_Lokasyon` gibi Türkçe karakterli veya farklı isimdeki başlıkları) akıllı arama algoritması ile **otomatik olarak algılar**. 
* Eğer otomatik algılama yanlış olursa, uygulamanın solundaki **Sütun Eşleştirme Ayarı** panelinden hangi sütunun neyi temsil ettiğini seçebilirsiniz.
* Bu sayede kod asla `KeyError` veya `IndexError` vererek çökmez.

### 2. macOS Sanal Ortam (.venv) ve Yol Sorunları Çözümü
macOS üzerinde terminal oturumlarının `.venv` ortamını kaybetmesi veya yanlış Python yoluna bakması çok sık karşılaşılan bir durumdur. Bu sorunu aşmak için aşağıdaki kesin çözümleri uygulayabilirsiniz.

---

## 🚀 Kesin ve Kalıcı Kurulum Rehberi (macOS)

Terminalde sanal ortam aktivasyon sorunlarını tamamen aşmak için **"Doğrudan Yol (Direct Path)"** yöntemini kullanacağız. Bu yöntem, ortamı `source` komutuyla aktive etmemiş olsanız bile **%100 çalışır**.

### Adım 1: Proje Dizinine Gidin
Terminalinizi açın ve projenin bulunduğu klasöre geçiş yapın:
```bash
cd /Users/peterbilt/.gemini/antigravity/scratch/elevator_app
```

### Adım 2: Sanal Ortamı (.venv) Oluşturun
Eğer henüz sanal ortam oluşturmadıysanız, sıfırdan temiz bir ortam kuralım:
```bash
python3 -m venv .venv
```

### Adım 3: Bağımlılıkları Kurun (Hatasız Yöntem)
`ModuleNotFoundError: No module named 'qrcode'` veya `streamlit` hatalarını engellemek için, pip kurulumunu **doğrudan sanal ortamın içindeki Python ile** çalıştırın:
```bash
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```
*Bu komut, sistemdeki diğer Python sürümlerini tamamen devre dışı bırakır ve paketleri kesinlikle `.venv` içerisine kurar.*

### Adım 4: Uygulamayı Çalıştırın (Hatasız Yöntem)
Streamlit'i çalıştırırken terminalin global `streamlit` yoluna bakıp "no such file or directory" demesini önlemek için yine sanal ortamın kendi streamlit executable'ını tetikleyin:
```bash
./.venv/bin/streamlit run app.py
```
Uygulamanız tarayıcıda otomatik olarak açılacaktır! 🚀

---

## 💻 VS Code Kullananlar İçin Kalıcı Entegrasyon (Önerilir)

Eğer kod editörü olarak VS Code kullanıyorsanız, terminali her açtığınızda sanal ortamın otomatik aktif olması için:

1. VS Code'da `elevator_app` klasörünü açın.
2. `Cmd + Shift + P` tuşlarına basarak Komut Paletini (Command Palette) açın.
3. **"Python: Select Interpreter"** (Python: Yorumlayıcı Seç) yazın ve seçin.
4. Listeden yanında **`('.venv': venv)`** yazan sanal ortam seçeneğini seçin.
5. VS Code'daki mevcut terminali kapatıp (çöp kutusu simgesine basarak) yeni bir terminal açın (`Ctrl + \``).
6. Terminalinizin başında `(.venv)` ibaresini göreceksiniz. Artık doğrudan `streamlit run app.py` yazarak da çalıştırabilirsiniz!

---

## 📁 Proje Dosyaları
* **`app.py`**: Dinamik sütun eşleştirmeli, QR kod destekli ana Streamlit kodu.
* **`elevator_data.csv`**: Türkçe başlıklara sahip örnek veri tabanı şablonu.
* **`requirements.txt`**: Gerekli kütüphane listesi.
* **`README.md`**: Bu kılavuz kılavuzu.
