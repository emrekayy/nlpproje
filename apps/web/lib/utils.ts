import type { IssueItem, ProductDetail, ReviewSummary } from "@/types/product";

export function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

export function formatConfidenceScore(score: number) {
  return `${Math.round(score * 100)}%`;
}

export function formatRecommendationVerdict(verdict: string) {
  if (verdict === "strong_buy") return "Guclu tercih";
  if (verdict === "buy_with_caveats") return "Dikkatle onerilir";
  if (verdict === "niche_pick") return "Nis kullanim icin uygun";
  return "Degerlendiriliyor";
}

export function getRecommendationTone(
  verdict: string
): "neutral" | "positive" | "negative" | "warning" {
  if (verdict === "strong_buy") return "positive";
  if (verdict === "buy_with_caveats") return "neutral";
  if (verdict === "niche_pick") return "warning";
  return "neutral";
}

export function getScoreColor(score: number): {
  bar: string;
  text: string;
  stripe: string;
} {
  if (score >= 80) return { bar: "bg-emerald-500", text: "text-emerald-600", stripe: "bg-emerald-500" };
  if (score >= 65) return { bar: "bg-amber-500",   text: "text-amber-600",   stripe: "bg-amber-500"   };
  return              { bar: "bg-rose-500",   text: "text-rose-600",   stripe: "bg-rose-500"   };
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}

export function getProductIntelligenceScore(product: ProductDetail) {
  const verdictBase =
    product.decision_support.recommendation_verdict === "strong_buy"
      ? 84
      : product.decision_support.recommendation_verdict === "buy_with_caveats"
        ? 73
        : product.decision_support.recommendation_verdict === "niche_pick"
          ? 64
          : 68;

  const positiveLift = Math.min(product.review_summary.top_positive_aspects.length * 2, 8);
  const negativeDrag = Math.min(product.review_summary.top_negative_aspects.length * 1.5, 6);
  const issueDrag = Math.min(product.common_issues.length * 2.25, 9);
  const evidenceLift = Math.min(product.review_summary.evidence_snippets.length, 4);

  return Math.round(clamp(verdictBase + positiveLift + evidenceLift - negativeDrag - issueDrag, 48, 96));
}

function includesAny(text: string, keywords: string[]) {
  return keywords.some((keyword) => text.includes(keyword));
}

export type IntelligenceScoreMetric = {
  label: string;
  score: number;
};

export function getIntelligenceScoreBreakdown(
  product: ProductDetail,
  overallOverride = getProductIntelligenceScore(product)
) {
  const slug = product.slug.toLowerCase();
  const chipset = product.chipset.toLowerCase();
  const battery = product.battery_summary.toLowerCase();
  const camera = product.camera_summary.toLowerCase();
  const display = product.display_type.toLowerCase();
  const highlights = product.notable_highlights.join(" ").toLowerCase();
  const positives = product.review_summary.top_positive_aspects.join(" ").toLowerCase();
  const negatives = product.review_summary.top_negative_aspects.join(" ").toLowerCase();
  const issues = product.common_issues
    .map((issue) => `${issue.title} ${issue.description}`)
    .join(" ")
    .toLowerCase();

  let performanceScore = 68 + Math.max(0, product.release_year - 2021) * 4;
  if (includesAny(chipset, ["a18"])) performanceScore += 10;
  else if (includesAny(chipset, ["a17"])) performanceScore += 8;
  else if (includesAny(chipset, ["a16"])) performanceScore += 6;
  else if (includesAny(chipset, ["a15"])) performanceScore += 4;
  else if (includesAny(chipset, ["a14"])) performanceScore += 2;
  if (includesAny(chipset, ["pro"])) performanceScore += 4;
  if (display.includes("promotion")) performanceScore += 4;
  performanceScore += Math.min(product.review_summary.top_positive_aspects.length * 2, 8);
  performanceScore -= Math.min(product.common_issues.length * 2, 8);

  let batteryScore = 64;
  if (includesAny(battery, ["referans", "en uzun", "gunu rahat", "dayaniklilik", "uzun", "strong"])) {
    batteryScore += 12;
  } else if (includesAny(battery, ["gunluk", "tutarli", "orta-iyi", "gun sonu", "ongorulebilir"])) {
    batteryScore += 7;
  }
  if (includesAny(slug, ["plus", "max"])) batteryScore += 4;
  if (slug.includes("mini")) batteryScore -= 6;
  if (includesAny(issues, ["pil", "battery", "isinma", "heat"])) batteryScore -= 8;

  let cameraScore = 66;
  if (
    includesAny(camera, [
      "pro kamera",
      "guclu video",
      "zoom",
      "lidar",
      "dusuk isik",
      "sensor shift",
      "photonic",
      "buyuk sensor",
    ])
  ) {
    cameraScore += 12;
  } else if (includesAny(camera, ["dengeli", "cift kamera", "kamera"])) {
    cameraScore += 7;
  }
  if (includesAny(`${highlights} ${positives}`, ["kamera", "video", "fotograf", "zoom"])) {
    cameraScore += 6;
  }
  if (includesAny(issues, ["kamera", "camera", "lens"])) cameraScore -= 6;

  let longevityScore = 60 + Math.max(0, product.release_year - 2020) * 5;
  if (includesAny(chipset, ["a17", "a18", "pro"])) longevityScore += 5;
  if (display.includes("oled")) longevityScore += 2;
  longevityScore += Math.min(product.storage_options.length, 4);
  longevityScore -= Math.min(product.common_issues.length * 2, 8);

  let valueScore = 66 + Math.round((overallOverride - 70) * 0.35);
  if (product.release_year <= 2023) valueScore += 6;
  if (product.release_year >= 2025) valueScore -= 2;
  if (includesAny(slug, ["pro", "max"])) valueScore -= 2;
  if (slug.includes("mini")) valueScore += 2;
  if (product.decision_support.recommendation_verdict === "strong_buy") valueScore += 4;
  if (product.decision_support.recommendation_verdict === "niche_pick") valueScore -= 4;
  if (includesAny(`${negatives} ${issues}`, ["isinma", "pil", "battery"])) valueScore -= 4;

  const metrics: IntelligenceScoreMetric[] = [
    { label: "Performance score", score: clamp(Math.round(performanceScore), 52, 97) },
    { label: "Battery score", score: clamp(Math.round(batteryScore), 48, 95) },
    { label: "Camera score", score: clamp(Math.round(cameraScore), 50, 96) },
    { label: "Longevity score", score: clamp(Math.round(longevityScore), 50, 96) },
    { label: "Value score", score: clamp(Math.round(valueScore), 46, 93) },
  ];

  return {
    overallScore: clamp(Math.round(overallOverride), 45, 98),
    metrics,
  };
}

export function getCommunitySentimentLabel(summary: ReviewSummary) {
  const positive = summary.top_positive_aspects.length;
  const negative = summary.top_negative_aspects.length;

  if (positive >= negative + 2) return "Guclu memnuniyet";
  if (positive > negative) return "Genel olarak olumlu";
  if (positive === negative) return "Dengeli gorus";
  return "Temkinli yorumlar";
}

export function getRiskSignalLabel(issues: IssueItem[]) {
  const averageConfidence =
    issues.length > 0
      ? issues.reduce((total, issue) => total + issue.confidence_score, 0) / issues.length
      : 0;

  if (issues.length >= 3 || averageConfidence >= 0.82) return "Yuksek izleme gerektirir";
  if (issues.length >= 1 || averageConfidence >= 0.58) return "Orta risk seviyesi";
  return "Dusuk risk profili";
}

export function getBuyingVerdictCopy(product: ProductDetail) {
  const score = getProductIntelligenceScore(product);

  if (score >= 82) {
    return "Guncel deneyim, topluluk memnuniyeti ve donanim dengesi birlikte guclu bir satin alma adayi sunuyor.";
  }

  if (score >= 68) {
    return "Dogru beklentiyle secildiginde tatmin edici; ancak kronik sinyaller ve kullanim senaryosu birlikte degerlendirilmeli.";
  }

  return "Ancak belirli bir ihtiyaca net uyuyorsa anlamli; genel kullanici icin daha guclu alternatifler dusunulebilir.";
}

export function getBestForPersonas(product: ProductDetail) {
  const personas = [...product.decision_support.best_for];

  if (product.battery_summary.toLowerCase().includes("all-day") || product.battery_summary.toLowerCase().includes("gun")) {
    personas.push("Gun boyu mobil kullanim isteyenler");
  }

  if (product.camera_summary.toLowerCase().includes("video") || product.camera_summary.toLowerCase().includes("camera")) {
    personas.push("Sosyal medya ve kamera odakli kullananlar");
  }

  if (product.chipset.toLowerCase().includes("pro") || product.chipset.toLowerCase().includes("bionic")) {
    personas.push("Uzun omurlu performans arayanlar");
  }

  return Array.from(new Set(personas)).slice(0, 4);
}
