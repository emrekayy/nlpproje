# AI Product Intelligence Assistant

Apple iPhone modelleri için gerçek kullanıcı yorumlarına dayalı, kanıt odaklı bir ürün zekâsı asistanı. Bu proje; ürün kataloğu, inceleme özeti, kronik sorun analizi ve semantik arama destekli sohbet arayüzünü tek bir monorepo altında birleştirir.

## Proje Amacı

Kullanıcıların iPhone satın alma kararlarını desteklemek için dağınık kullanıcı yorumlarını yapılandırılmış, aranabilir ve güvenilir bir bilgi katmanına dönüştürmek.

Asistan; spekülasyon yerine gerçek inceleme parçalarına dayanarak kamera, pil, ısınma, performans ve günlük kullanım gibi konularda yanıt üretir.

## Problem Tanımı

E-ticaret ve topluluk platformlarındaki iPhone yorumları:

- farklı kaynaklarda dağınık biçimde bulunur,
- model ve konu bazında filtrelenmesi zordur,
- genel LLM yanıtları gerçek kullanıcı deneyimini yansıtmayabilir,
- kanıtsız veya kapsam dışı cevaplar (halüsinasyon) güvenilirliği düşürür.

Bu proje, yorum verisini normalize ederek semantik arama ve kanıt tabanlı yanıt üretimi ile daha güvenilir bir karar destek deneyimi sunar.

## Özellikler

- iPhone 11–16 ailesi için ürün kataloğu ve detay sayfaları
- Canlı arama ve filtreleme
- Teknik özellikler, inceleme özeti ve olumlu/olumsuz yönler
- Kronik sorun analizi ve güven skorları
- Kanıt parçacıkları (evidence snippets) listesi
- Semantik arama destekli sohbet paneli
- Gerçek CSV kullanıcı yorumu içe aktarma ve normalizasyon
- Kapsam dışı sorular için filtreleme
- Kanıt sayısı ve kaynak gösterimi ile şeffaf yanıtlar

## Kullanılan Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| Frontend | Next.js 15, React 19, TypeScript, Tailwind CSS |
| Backend | FastAPI, Pydantic, Uvicorn |
| NLP / Arama | Sentence Transformers, NumPy |
| Veri | JSON seed dosyaları, CSV inceleme içe aktarma |
| Mimari | Monorepo (`apps/` + `packages/`) |

## NLP Yaklaşımı

Proje, klasik anahtar kelime eşleştirmesinin ötesine geçerek **anlamsal benzerlik (semantic similarity)** tabanlı bir bilgi getirme (retrieval) hattı kullanır.

### Semantik Getirme ve Embedding

- **Sentence Transformer** tabanlı bir embedding modeli (`all-MiniLM-L6-v2`) ile sorgular ve inceleme parçaları vektör uzayına dönüştürülür.
- **We used a BERT-based Sentence Transformer embedding model for semantic similarity.**
- Kosinüs benzerliği ile en alakalı inceleme, kanıt ve ürün açıklama parçaları seçilir.
- Niyet (intent) profilleri, günlük kullanım, oyun, kamera, pil ve ısınma gibi konulara göre sıralamayı iyileştirir.

### Kanıt Tabanlı Yanıt Üretimi

Sohbet servisi, seçilen parçalardan:

- kısa bir karar özeti,
- destekleyici kanıt cümleleri,
- kaynak ve benzerlik skorları

üretir. Yanıtlar doğrudan LLM uydurması yerine getirilen veri parçalarına dayanır.

### Halüsinasyon Azaltma

- Yanıtlar yalnızca getirilen inceleme ve katalog parçalarından türetilir.
- Kanıt sayısı düşük olduğunda ifade tonu daha temkinli hale getirilir.
- Kullanıcıya gösterilen kanıt parçacıkları ham metin yerine temizlenmiş özetler içerir.

### Kapsam Filtreleme

Hava durumu, siyaset, tarif, kod yazma gibi ürün bilgisi dışındaki sorular tespit edilir ve asistan kapsam dışı yanıt döner. Böylece model, iPhone ürün zekâsı alanı dışına taşmaz.

## Gerçek Kullanıcı İnceleme Veri Seti Kullanımı

Backend, `data/raw/reviews/` altındaki CSV dosyalarını okuyarak farklı kaynak şemalarını tek bir iç formata normalize eder:

```text
id, model, source, rating, review_text, review_title, date, country,
verified_purchase, sentiment, aspect, source_url
```

Temizlenmiş çıktı `data/processed/reviews/real_reviews.json` dosyasına yazılır. Gerçek incelemeler semantik arama hattına dahil edilir; bir model için gerçek veri yoksa mock topluluk yorumları yedek olarak kullanılır.

## Kurulum

### Gereksinimler

- Node.js 18+
- Python 3.11+
- npm

### Backend

```bash
cd apps/api
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload
```

API adresi: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Sağlık kontrolü: `curl http://127.0.0.1:8000/health`

Swagger dokümantasyonu: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

Web uygulaması: [http://localhost:3000](http://localhost:3000)

İsteğe bağlı ortam değişkenleri için `apps/web/.env.example` dosyasını `.env.local` olarak kopyalayın.

### Monorepo (Kök Dizin)

Kök dizinden de çalıştırabilirsiniz:

```bash
npm install
npm run dev:web
npm run build:web
```

## Örnek Sorular

Asistan panelinde deneyebileceğiniz örnek sorular:

- "iPhone 15 Pro kamera gece çekimlerinde nasıl?"
- "Günlük kullanım için iPhone 13 pil ömrü yeterli mi?"
- "iPhone 14 Pro Max ısınma sorunu var mı?"
- "Oyun oynarken iPhone 16 Pro ısınıyor mu?"
- "Instagram ve TikTok için hangi iPhone daha iyi?"
- "iPhone 12 hâlâ alınır mı?"
- "iPhone 15 ile iPhone 14 arasında kamera farkı nedir?"

## Proje Klasör Yapısı

```text
ai-product-intelligence/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── app/
│   │   │   ├── routes/         # HTTP endpoint'leri
│   │   │   ├── services/       # İş mantığı, retrieval, chat
│   │   │   ├── repositories/   # Veri erişimi
│   │   │   └── schemas/        # Pydantic modelleri
│   │   └── requirements.txt
│   └── web/                    # Next.js frontend
│       ├── app/                # App Router sayfaları
│       ├── components/         # Paylaşılan UI bileşenleri
│       ├── features/           # Özellik modülleri (chat, search, issues)
│       └── services/           # API istemcisi
├── packages/                   # Paylaşılan paket iskeletleri
│   ├── shared-types/
│   ├── prompts/
│   ├── retrieval/
│   ├── review-analysis/
│   └── issue-engine/
├── data/
│   ├── seeds/                  # Katalog ve mock inceleme seed'leri
│   ├── raw/reviews/            # Ham CSV inceleme dosyaları
│   └── processed/reviews/      # Normalize edilmiş inceleme çıktıları
├── docs/                       # Mimari notları
├── .gitignore
└── README.md
```

## Ekran Görüntüleri

<!-- Aşağıya proje ekran görüntülerini ekleyin -->

| Ana Sayfa | Ürün Detayı | Sohbet Paneli |
|-----------|-------------|---------------|
| _placeholder_ | _placeholder_ | _placeholder_ |

## Gelecek İyileştirmeler

- PostgreSQL + pgvector ile kalıcı vektör depolama
- ABSA (Aspect-Based Sentiment Analysis) ile konu bazlı duygu analizi
- Sorun kümeleme ve şiddet skorlama
- Zengin atıf (citation) destekli RAG sohbet katmanı
- Değerlendirme veri setleri ile retrieval ve yanıt kalitesi ölçümü
- Otomatik testler (API, servis ve sayfa düzeyi)
- Sesli asistan katmanı

## API Endpoint'leri

| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/api/products` | Ürün listesi |
| GET | `/api/products/{slug}` | Ürün detayı |
| GET | `/api/products/{slug}/summary` | İnceleme özeti |
| GET | `/api/products/{slug}/issues` | Kronik sorunlar |
| POST | `/api/chat` | Kanıt tabanlı sohbet |

## Lisans

Bu depo eğitim ve araştırma amaçlı bir NLP / ürün zekâsı projesidir.
