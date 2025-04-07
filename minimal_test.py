# minimal_test.py
import os
import google.generativeai as genai
from dotenv import load_dotenv
import traceback # Hata detayları için eklendi

print("Minimal test script başlatılıyor...")
print("------------------------------------")

print("1. .env dosyası yükleniyor...")
loaded = load_dotenv()
if loaded:
    print("   .env dosyası yüklendi.")
else:
    print("   UYARI: .env dosyası yüklenemedi veya bulunamadı!")

print("2. API Anahtarı ortam değişkeninden alınıyor...")
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("   HATA: GOOGLE_API_KEY ortam değişkeninde bulunamadı!")
    exit()
else:
    # Anahtarı yazdırmayın, sadece bulunduğunu belirtin
    print(f"   API Anahtarı bulundu.")

try:
    print("3. Genai kütüphanesi yapılandırılıyor...")
    genai.configure(api_key=api_key)
    print("   Genai yapılandırıldı.")

    print("4. Model örneği oluşturuluyor (gemini-pro)...")
    # Daha basit ve yaygın bir model kullanalım
    model = genai.GenerativeModel('gemini-pro')
    print("   Model örneği oluşturuldu.")

    print("5. İçerik üretme denemesi...")
    # Basit bir istek gönderelim
    response = model.generate_content("Tek cümlede kuantum fiziğini açıkla.")
    print("   İstek gönderildi.")

    print("\n--- BAŞARILI ---")
    print("Alınan Cevap:")
    print(response.text)

except Exception as e:
    print(f"\n--- BİR HATA OLUŞTU ---")
    print(f"Hata Tipi: {type(e)}")
    print(f"Hata Detayları: {e}")
    print("\nTraceback:")
    traceback.print_exc() # Hatanın tam kaynağını görmek için

print("\n------------------------------------")
print("Minimal test script tamamlandı.")