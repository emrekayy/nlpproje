import { writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const PRODUCT_SPECS = [
  { slug: "iphone-11", name: "iPhone 11", year: 2019, chipset: "A13 Bionic", display: "Liquid Retina HD", size: '6.1"', battery: "Gunluk kullanimda rahat bir gunu cikarabilen pil performansi", camera: "Cift arka kamera ile dengeli fotograf ve video paketi", storage: ["64 GB", "128 GB", "256 GB"], weight: "194 g", highlights: ["Renkli tasarim", "Dengeli performans", "Guclu video stabilizasyonu"], desc: "Serinin erisilebilir giris modeli; hala dengeli bir temel deneyim sunuyor." },
  { slug: "iphone-11-pro", name: "iPhone 11 Pro", year: 2019, chipset: "A13 Bionic", display: "Super Retina XDR OLED", size: '5.8"', battery: "Kompakt sinifa gore guclu dayaniklilik", camera: "Uc arka kamera ile premium kadraj esnekligi", storage: ["64 GB", "256 GB", "512 GB"], weight: "188 g", highlights: ["Kompakt premium govde", "Telefoto lens", "Parlak OLED panel"], desc: "Kucuk boyutta amiral gemisi hissi arayanlar icin premium iPhone yorumu." },
  { slug: "iphone-11-pro-max", name: "iPhone 11 Pro Max", year: 2019, chipset: "A13 Bionic", display: "Super Retina XDR OLED", size: '6.5"', battery: "Serisinin en uzun giden pillerinden biri", camera: "Uc arka kamera ile guclu video ve zoom deneyimi", storage: ["64 GB", "256 GB", "512 GB"], weight: "226 g", highlights: ["Uzun pil omru", "Buyuk ekran", "Premium kamera sistemi"], desc: "11 serisinin en uzun omurlu ve en kapsamli modeli." },
  { slug: "iphone-12", name: "iPhone 12", year: 2020, chipset: "A14 Bionic", display: "Super Retina XDR OLED", size: '6.1"', battery: "5G kullaniminda orta-iyi seviye pil dengesi", camera: "Gece cekimlerinde daha guclu cift kamera sistemi", storage: ["64 GB", "128 GB", "256 GB"], weight: "164 g", highlights: ["Ceramic Shield", "OLED ekran", "Daha ince kasa"], desc: "Modern tasarim diline gecis yapan dengeli ana model." },
  { slug: "iphone-12-mini", name: "iPhone 12 mini", year: 2020, chipset: "A14 Bionic", display: "Super Retina XDR OLED", size: '5.4"', battery: "Kompakt form faktoru nedeniyle sinirli ama verimli pil davranisi", camera: "Mini boyutta tam iPhone 12 kamera deneyimi", storage: ["64 GB", "128 GB", "256 GB"], weight: "135 g", highlights: ["Cok kompakt boyut", "Hafiflik", "OLED ekran"], desc: "Kucuk telefon sevenler icin nadir bulunan guclu bir secenek." },
  { slug: "iphone-12-pro", name: "iPhone 12 Pro", year: 2020, chipset: "A14 Bionic", display: "Super Retina XDR OLED", size: '6.1"', battery: "Premium segment icin istikrarli gun sonu performansi", camera: "LiDAR destekli gelismis pro kamera paketi", storage: ["128 GB", "256 GB", "512 GB"], weight: "189 g", highlights: ["LiDAR", "Paslanmaz celik govde", "ProRAW hazirligi"], desc: "Profesyonel cekim ve premium malzeme isteyenler icin gelistirilmis 12." },
  { slug: "iphone-12-pro-max", name: "iPhone 12 Pro Max", year: 2020, chipset: "A14 Bionic", display: "Super Retina XDR OLED", size: '6.7"', battery: "Serinin en guclu pil performansi", camera: "Daha buyuk sensor avantajiyla daha guclu dusuk isik performansi", storage: ["128 GB", "256 GB", "512 GB"], weight: "228 g", highlights: ["En buyuk 12 serisi ekran", "Daha buyuk ana sensor", "Uzun pil"], desc: "12 ailesinin kamera ve pil odakli en guclu secenegi." },
  { slug: "iphone-13", name: "iPhone 13", year: 2021, chipset: "A15 Bionic", display: "Super Retina XDR OLED", size: '6.1"', battery: "11 ve 12'ye gore belirgin iyilesen pil sureleri", camera: "Sensor shift sabitleme ile daha guclu ana kamera", storage: ["128 GB", "256 GB", "512 GB"], weight: "174 g", highlights: ["Daha iyi pil", "Parlak ekran", "Guclu video"], desc: "Genel denge acisindan cok genis kitleye hitap eden ana model." },
  { slug: "iphone-13-mini", name: "iPhone 13 mini", year: 2021, chipset: "A15 Bionic", display: "Super Retina XDR OLED", size: '5.4"', battery: "Mini segment icinde anlamli sekilde iyilesmis dayaniklilik", camera: "Kompakt boyutta guclu cift kamera", storage: ["128 GB", "256 GB", "512 GB"], weight: "141 g", highlights: ["Kompakt amiral gemisi", "Daha iyi pil", "Guclu islemci"], desc: "Kucuk govdede ust duzey deneyimi en olgun haliyle sunan mini." },
  { slug: "iphone-13-pro", name: "iPhone 13 Pro", year: 2021, chipset: "A15 Bionic", display: "ProMotion Super Retina XDR OLED", size: '6.1"', battery: "120 Hz ekrana ragmen guclu optimizasyonla gunu rahat tamamlama", camera: "Makro ve sinematik video dahil cok yonlu pro kamera", storage: ["128 GB", "256 GB", "512 GB", "1 TB"], weight: "204 g", highlights: ["120 Hz ProMotion", "Makro cekim", "Premium performans"], desc: "ProMotion ile iPhone deneyiminde hissedilir akicilik sunan premium secenek." },
  { slug: "iphone-13-pro-max", name: "iPhone 13 Pro Max", year: 2021, chipset: "A15 Bionic", display: "ProMotion Super Retina XDR OLED", size: '6.7"', battery: "Apple tarafinda referans sayilan uzun pil omru", camera: "Pro seviyede video ve buyuk ekran avantajini birlestiriyor", storage: ["128 GB", "256 GB", "512 GB", "1 TB"], weight: "240 g", highlights: ["Cok uzun pil omru", "120 Hz ekran", "Pro kamera"], desc: "Pil ve ekran oncelikli kullanicilar icin halen guclu bir kriter cihaz." },
  { slug: "iphone-14", name: "iPhone 14", year: 2022, chipset: "A15 Bionic", display: "Super Retina XDR OLED", size: '6.1"', battery: "Gundelik kullanimda tutarli ve ongorulebilir pil performansi", camera: "Photonic Engine ile daha guclu dusuk isik ciktilari", storage: ["128 GB", "256 GB", "512 GB"], weight: "172 g", highlights: ["Photonic Engine", "Crash Detection", "Dengeli kullanim"], desc: "13 uzerine daha rafine bir deneyim ve guvenlik odagi ekliyor." },
  { slug: "iphone-14-plus", name: "iPhone 14 Plus", year: 2022, chipset: "A15 Bionic", display: "Super Retina XDR OLED", size: '6.7"', battery: "Pro Max olmadan buyuk ekran ve uzun pil isteyenlere hitap ediyor", camera: "Ana kamera deneyimi buyuk ekran formatinda sunuluyor", storage: ["128 GB", "256 GB", "512 GB"], weight: "203 g", highlights: ["Buyuk ekran", "Uzun pil", "Hafif buyuk govde"], desc: "Pro fiyatina cikmadan buyuk ekran ve dayaniklilik isteyenler icin." },
  { slug: "iphone-14-pro", name: "iPhone 14 Pro", year: 2022, chipset: "A16 Bionic", display: "ProMotion Super Retina XDR OLED", size: '6.1"', battery: "Yuksek parlaklik ve AOD'ye ragmen iyi optimize pil dengesi", camera: "48 MP ana sensor ile daha detayli cekim kabiliyeti", storage: ["128 GB", "256 GB", "512 GB", "1 TB"], weight: "206 g", highlights: ["Dynamic Island", "48 MP ana kamera", "AOD"], desc: "Yeni arayuz dili ve 48 MP gecisiyle belirgin bir pro nesil siramasi." },
  { slug: "iphone-14-pro-max", name: "iPhone 14 Pro Max", year: 2022, chipset: "A16 Bionic", display: "ProMotion Super Retina XDR OLED", size: '6.7"', battery: "Yuksek parlaklikli buyuk ekrana ragmen cok guclu pil", camera: "48 MP kamera ve buyuk ekranla premium medya ve cekim deneyimi", storage: ["128 GB", "256 GB", "512 GB", "1 TB"], weight: "240 g", highlights: ["Dynamic Island", "Uzun pil", "48 MP kamera"], desc: "14 serisinin en kapsamli ekran, pil ve kamera kombinasyonu." },
  { slug: "iphone-15", name: "iPhone 15", year: 2023, chipset: "A16 Bionic", display: "Super Retina XDR OLED", size: '6.1"', battery: "USB-C donusumu ve verimli performansla dengeli kullanim suresi", camera: "48 MP ana kamera ana seri icin buyuk bir sicrama sunuyor", storage: ["128 GB", "256 GB", "512 GB"], weight: "171 g", highlights: ["USB-C", "48 MP kamera", "Dynamic Island"], desc: "Ana seri tarafinda modernlesen baglanti ve kamera paketi sunuyor." },
  { slug: "iphone-15-plus", name: "iPhone 15 Plus", year: 2023, chipset: "A16 Bionic", display: "Super Retina XDR OLED", size: '6.7"', battery: "Serinin en guclu standart model pil performanslarindan biri", camera: "48 MP ana kamera buyuk ekran deneyimiyle destekleniyor", storage: ["128 GB", "256 GB", "512 GB"], weight: "201 g", highlights: ["Uzun pil", "USB-C", "Buyuk ekran"], desc: "Pro olmayan sinifta pil odakli en guclu seceneklerden biri." },
  { slug: "iphone-15-pro", name: "iPhone 15 Pro", year: 2023, chipset: "A17 Pro", display: "ProMotion Super Retina XDR OLED", size: '6.1"', battery: "Titanyum kasaya gecisle hafifleyen premium modelde dengeli pil", camera: "Gelismis hesaplamali cekim ve pro video imkanlari", storage: ["128 GB", "256 GB", "512 GB", "1 TB"], weight: "187 g", highlights: ["Titanyum kasa", "A17 Pro", "Action Button"], desc: "Daha hafif premium govde ve oyun odakli silikonla yeni nesil pro cihaz." },
  { slug: "iphone-15-pro-max", name: "iPhone 15 Pro Max", year: 2023, chipset: "A17 Pro", display: "ProMotion Super Retina XDR OLED", size: '6.7"', battery: "Buyuk ekran ve guclu verimlilikle cok iyi dayaniklilik", camera: "Tetraprism zoom ile serinin en esnek kamera sistemi", storage: ["256 GB", "512 GB", "1 TB"], weight: "221 g", highlights: ["5x optical zoom", "Titanyum kasa", "A17 Pro"], desc: "Kamera esnekligi ve buyuk ekran isteyenler icin 15 serisinin vitrini." },
  { slug: "iphone-16", name: "iPhone 16", year: 2024, chipset: "A18", display: "Super Retina XDR OLED", size: '6.1"', battery: "Verimlilik iyilesmeleriyle daha tutarli gunluk dayaniklilik", camera: "Camera Control ile cekime hizli erisim sunan rafine ana paket", storage: ["128 GB", "256 GB", "512 GB"], weight: "170 g", highlights: ["A18", "Camera Control", "Apple Intelligence hazirligi"], desc: "Yeni kontrol katmani ve daha modern AI hazirligi ile guncel ana model." },
  { slug: "iphone-16-plus", name: "iPhone 16 Plus", year: 2024, chipset: "A18", display: "Super Retina XDR OLED", size: '6.7"', battery: "Buyuk govdede rahat gun sonu hatta ertesi gun kullanim potansiyeli", camera: "Standart seri icin guclu ama sadelestirilmis kamera deneyimi", storage: ["128 GB", "256 GB", "512 GB"], weight: "199 g", highlights: ["Buyuk ekran", "A18", "Camera Control"], desc: "Ana seri icinde buyuk ekran ve uzun pil arayanlar icin guncel secenek." },
  { slug: "iphone-16-pro", name: "iPhone 16 Pro", year: 2024, chipset: "A18 Pro", display: "ProMotion Super Retina XDR OLED", size: '6.3"', battery: "Yeni termal ve verimlilik ayarlariyla daha istikrarli premium pil davranisi", camera: "Guclu video, hizli odak ve pro workflows icin optimize sistem", storage: ["128 GB", "256 GB", "512 GB", "1 TB"], weight: "199 g", highlights: ["A18 Pro", "6.3 in ekran", "Gelistirilmis termal yapi"], desc: "Daha buyuyen ekran ve AI-era donanimi ile guncel pro giris noktasi." },
  { slug: "iphone-16-pro-max", name: "iPhone 16 Pro Max", year: 2024, chipset: "A18 Pro", display: "ProMotion Super Retina XDR OLED", size: '6.9"', battery: "Serinin en iddiali pil ve buyuk ekran kombinasyonu", camera: "En ust seviye zoom, video ve hesaplamali cekim dengesi", storage: ["256 GB", "512 GB", "1 TB"], weight: "227 g", highlights: ["6.9 in ekran", "A18 Pro", "En genis pro paket"], desc: "16 ailesinin ekran, pil ve kamera odakli tepe modeli." }
];

const buildReviewSummary = (product) => {
  const compact = product.slug.includes("mini") || product.display.startsWith("Liquid");
  const pro = product.slug.includes("pro");
  const maxModel = product.slug.includes("max") || product.slug.includes("plus");

  const positives = [
    `${product.chipset} ile akici performans`,
    `${product.display} panelin sundugu kaliteli ekran deneyimi`,
    product.camera
  ];

  const negatives = [
    !pro ? "Yuksek yenileme hizinin yalnizca Pro modellerde olmasi" : "Uzun kullanimda agirlik ve elde yoruculuk",
    "Baz model depolama seceneklerinin hizla dolabilmesi",
    "Nesil yenilendikce fiyat performans algisinin modele gore degismesi"
  ];

  if (compact) {
    negatives[0] = "Kompakt govde nedeniyle pil beklentisinin daha sinirli kalmasi";
  }

  if (maxModel) {
    positives[1] = "Buyuk ekranin medya ve okuma deneyimini guclendirmesi";
  }

  return {
    overall_sentiment_summary: `${product.name} genel olarak olumlu algilaniyor; kullanicilar performans, kamera ve ekran tarafini guclu bulurken bazi geri bildirimler agirlik, pil siniri veya fiyat hissi uzerinde yogunlasiyor.`,
    top_positive_aspects: positives,
    top_negative_aspects: negatives,
    evidence_snippets: [
      { source: "Reddit digest", text: `Kullanicilar ${product.name} icin en cok ${positives[0].toLowerCase()} ve kamera tutarliligini ovuyor.` },
      { source: "Forum synthesis", text: `Uzun donem yorumlarda ${product.battery.toLowerCase()} ifadesi tekrar ediyor.` },
      { source: "Review rollup", text: `Elestiriler daha cok ${negatives[0].toLowerCase()} ve depolama tercihleri etrafinda toplaniyor.` }
    ],
    chatbot_ready_summary: `Topluluktan derlenen sinyaller ${product.name} modelinin guclu performans, guvenilir kamera ve genel kullanim dengesi sundugunu gosteriyor.`
  };
};

const buildIssues = (product) => {
  const issues = [
    {
      title: "Pil sagligi kaybi algisi",
      description: `Kullanicilar uzun donem yogun kullanimda ${product.name} icin pil sagliginin beklenenden hizli dustugunu belirtebiliyor.`,
      confidence_score: product.slug.includes("16") ? 0.65 : 0.74
    },
    {
      title: "Isinma ve termal his",
      description: `Oyun, kamera veya navigasyon gibi yuksek yukte ${product.name} kasasinda hissedilir isinma yorumlari bulunuyor.`,
      confidence_score: product.year >= 2024 ? 0.58 : 0.69
    }
  ];

  if (product.slug.includes("mini")) {
    issues[0] = {
      title: "Kompakt kasa nedeniyle pil beklentisi",
      description: `${product.name} sahipleri, kucuk govde nedeniyle yogun kullanim gunlerinde sarj takviyesi ihtiyacinin arttigini soyluyor.`,
      confidence_score: 0.82
    };
  }

  if (product.slug.includes("pro-max") || product.slug.includes("plus")) {
    issues[1] = {
      title: "Buyuk govde ergonomisi",
      description: `Bazi kullanicilar ${product.name} modelinin tek elle kullanimda agir ve hacimli hissettirdigini belirtiyor.`,
      confidence_score: 0.71
    };
  }

  return issues;
};

const products = PRODUCT_SPECS.map((spec, index) => ({
  id: `iphone-${String(index + 1).padStart(2, "0")}`,
  slug: spec.slug,
  name: spec.name,
  family: `iPhone ${spec.year - 2008} Series`,
  release_year: spec.year,
  chipset: spec.chipset,
  display_type: spec.display,
  display_size: spec.size,
  battery_summary: spec.battery,
  camera_summary: spec.camera,
  storage_options: spec.storage,
  weight: spec.weight,
  notable_highlights: spec.highlights,
  short_description: spec.desc,
  analysis: {
    review_summary: buildReviewSummary(spec),
    common_issues: buildIssues(spec)
  }
}));

const filePath = join(dirname(fileURLToPath(import.meta.url)), "iphone_catalog.json");
writeFileSync(filePath, JSON.stringify({ products }, null, 2), "utf8");
