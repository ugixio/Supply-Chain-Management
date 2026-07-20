"""
NLP-based supplier risk monitoring using FinBERT and supply chain NER.

Two capabilities:
  1. FinBERT sentiment scoring — financial news and earnings call analysis
     for early-warning supplier financial distress signals.
  2. SCM risk entity extraction — identifies risk entities (disruptions,
     sanctions, force-majeure events, commodity shortages) from news text
     using spaCy NER + rule-based pattern matching.

Pipeline:
    Raw news text
    → FinBERT sentiment (POSITIVE/NEUTRAL/NEGATIVE + confidence)
    → spaCy NER (ORG, GPE, PRODUCT, EVENT)
    → Rule patterns (FORCE_MAJEURE, SANCTION, SHORTAGE, STRIKE, WEATHER)
    → Risk signal aggregation per supplier
    → RiskAlert with severity score

Design notes:
  - FinBERT (ProsusAI/finbert, Apache-2.0) is fine-tuned on financial text;
    outperforms base BERT by ~8pp F1 on FPB benchmark (Malo et al. 2014).
  - For production use, run on a GPU with batch_size=32 for ~50ms/article.
  - Alternatively use DistilBERT (66% size, 97% accuracy) for CPU deployment.
  - spaCy en_core_web_sm is sufficient for ORG/GPE extraction; upgrade to
    en_core_web_trf for higher NER precision on supplier names.

References:
    Araci, "FinBERT: Financial Sentiment Analysis with Pre-trained Language
    Models" (2019), arXiv:1908.10063.
    Malo et al., "Good Debt or Bad Debt" (2014), JASIST.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ArticleRiskSignal:
    """Per-article risk assessment output."""
    text_snippet: str
    sentiment: str              # POSITIVE | NEUTRAL | NEGATIVE
    sentiment_confidence: float
    risk_categories: list[str]  # e.g. ['SANCTION', 'SHORTAGE']
    entities_mentioned: list[str]
    risk_score: float           # 0–1 composite


@dataclass
class SupplierRiskMonitor:
    """Aggregated risk profile for a supplier over a monitoring window."""
    supplier_id: str
    supplier_name: str
    articles_analysed: int
    negative_sentiment_rate: float
    avg_sentiment_confidence: float
    risk_categories_detected: list[str]
    composite_risk_score: float     # 0–1; >0.6 triggers procurement review
    alert_level: str                # LOW | MEDIUM | HIGH | CRITICAL
    signals: list[ArticleRiskSignal] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Risk category patterns (rule-based, fast, language-agnostic)
# ---------------------------------------------------------------------------

_RISK_PATTERNS: dict[str, list[str]] = {
    "FORCE_MAJEURE": [
        r"\bforce\s+majeure\b", r"\bact\s+of\s+god\b",
        r"\bearth\s*quake\b", r"\bflood\b", r"\btyphoon\b", r"\bhurricane\b",
        r"\bpandemic\b", r"\bblackout\b",
    ],
    "SANCTION": [
        r"\bsanction\b", r"\bembargo\b", r"\bofac\b", r"\bexport\s+control\b",
        r"\bblacklist\b", r"\bentity\s+list\b", r"\bdebarment\b",
    ],
    "SHORTAGE": [
        r"\bshortage\b", r"\bsupply\s+crunch\b", r"\ballocation\b",
        r"\bscarcity\b", r"\bcapacity\s+constraint\b", r"\bbacklog\b",
        r"\blead\s+time\s+increas\b",
    ],
    "LABOUR_DISRUPTION": [
        r"\bstrike\b", r"\blabour\s+dispute\b", r"\bunion\b",
        r"\bwork\s+stoppage\b", r"\bwalkout\b",
    ],
    "FINANCIAL_DISTRESS": [
        r"\bbankrupt\b", r"\binsolvenc\b", r"\bliquidat\b",
        r"\bdefault\b", r"\bcredit\s+downgrad\b", r"\bdebt\s+covenant\b",
        r"\bgoing\s+concern\b",
    ],
    "GEOPOLITICAL": [
        r"\bwar\b", r"\bconflict\b", r"\btrade\s+war\b",
        r"\btariff\b", r"\bborder\s+clos\b", r"\bport\s+clos\b",
    ],
    "QUALITY_RECALL": [
        r"\brecall\b", r"\bquality\s+issue\b", r"\bfda\s+warning\b",
        r"\bfda\s+483\b", r"\biso\s+revoc\b", r"\bncr\b",
    ],
}


def _detect_risk_categories(text: str) -> list[str]:
    """Fast regex scan for supply chain risk signals."""
    lower = text.lower()
    detected = []
    for category, patterns in _RISK_PATTERNS.items():
        if any(re.search(p, lower) for p in patterns):
            detected.append(category)
    return detected


# ---------------------------------------------------------------------------
# FinBERT sentiment
# ---------------------------------------------------------------------------

def load_finbert(
    model_name: str = "ProsusAI/finbert",
    device: Optional[str] = None,
) -> tuple:
    """
    Load FinBERT tokenizer and model from HuggingFace Hub.

    Args:
        model_name: HF model id (default ProsusAI/finbert, Apache-2.0)
        device:     'cpu', 'cuda', or auto-detected

    Returns:
        (tokenizer, model) — pass to analyse_article_batch()

    Notes:
        First call downloads ~440 MB to ~/.cache/huggingface/.
        For air-gapped environments, copy the cache and set
        TRANSFORMERS_OFFLINE=1 before calling.
    """
    try:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
    except ImportError as e:
        raise ImportError(
            "transformers and torch required: pip install transformers torch"
        ) from e

    if device is None:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model = model.to(device)
    model.eval()
    return tokenizer, model


def analyse_article_batch(
    texts: list[str],
    tokenizer: Any,
    model: Any,
    max_length: int = 512,
    batch_size: int = 16,
    device: Optional[str] = None,
) -> list[dict]:
    """
    Run FinBERT on a list of article texts.

    Args:
        texts:      list of news snippets or article bodies
        tokenizer:  from load_finbert()
        model:      from load_finbert()
        max_length: token truncation limit (512 for BERT)
        batch_size: GPU batch size (reduce if OOM)
        device:     compute device

    Returns:
        list of {'label': 'positive'|'neutral'|'negative', 'score': float}
    """
    try:
        import torch
        import torch.nn.functional as F
    except ImportError as e:
        raise ImportError("torch required") from e

    if device is None:
        device = next(model.parameters()).device

    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        enc = tokenizer(
            batch, padding=True, truncation=True,
            max_length=max_length, return_tensors="pt",
        )
        enc = {k: v.to(device) for k, v in enc.items()}
        with torch.no_grad():
            logits = model(**enc).logits
        probs = F.softmax(logits, dim=1).cpu().numpy()
        label_map = {0: "positive", 1: "negative", 2: "neutral"}
        for prob_row in probs:
            best_idx = int(prob_row.argmax())
            results.append({
                "label": label_map[best_idx],
                "score": round(float(prob_row[best_idx]), 4),
                "positive": round(float(prob_row[0]), 4),
                "negative": round(float(prob_row[1]), 4),
                "neutral": round(float(prob_row[2]), 4),
            })
    return results


# ---------------------------------------------------------------------------
# NER entity extraction
# ---------------------------------------------------------------------------

def extract_entities(texts: list[str], spacy_model: str = "en_core_web_sm") -> list[list[str]]:
    """
    Extract organisation and geopolitical entities from news texts.

    Args:
        texts:       list of article strings
        spacy_model: spaCy model name (download: python -m spacy download en_core_web_sm)

    Returns:
        list of entity lists, one per article: ['Foxconn', 'Taiwan', ...]
    """
    try:
        import spacy
    except ImportError as e:
        raise ImportError("spacy required: pip install spacy") from e

    try:
        nlp = spacy.load(spacy_model)
    except OSError:
        raise OSError(
            f"spaCy model '{spacy_model}' not found. "
            f"Run: python -m spacy download {spacy_model}"
        )

    all_entities = []
    for doc in nlp.pipe(texts, batch_size=32):
        entities = list({
            ent.text.strip()
            for ent in doc.ents
            if ent.label_ in ("ORG", "GPE", "PRODUCT", "EVENT", "FAC")
        })
        all_entities.append(entities)
    return all_entities


# ---------------------------------------------------------------------------
# Composite risk scoring
# ---------------------------------------------------------------------------

# Risk category severity weights (sum to 1.0 approximately)
_CATEGORY_WEIGHTS: dict[str, float] = {
    "FINANCIAL_DISTRESS": 0.30,
    "SANCTION": 0.25,
    "GEOPOLITICAL": 0.15,
    "FORCE_MAJEURE": 0.10,
    "LABOUR_DISRUPTION": 0.08,
    "SHORTAGE": 0.07,
    "QUALITY_RECALL": 0.05,
}


def score_article(
    text: str,
    sentiment_result: dict,
    entities: list[str],
) -> ArticleRiskSignal:
    """
    Combine FinBERT sentiment + rule-based risk categories into a signal.

    Args:
        text:              raw article text
        sentiment_result:  output from analyse_article_batch() for this article
        entities:          output from extract_entities() for this article

    Returns:
        ArticleRiskSignal with composite risk score.
    """
    categories = _detect_risk_categories(text)
    sentiment_label = sentiment_result["label"].upper()
    sentiment_conf = float(sentiment_result["score"])

    # Base score from sentiment (NEGATIVE = 0.5, NEUTRAL = 0.2, POSITIVE = 0)
    sentiment_base = {"NEGATIVE": 0.5, "NEUTRAL": 0.2, "POSITIVE": 0.0}.get(sentiment_label, 0.2)
    # Category additive penalty
    cat_score = sum(_CATEGORY_WEIGHTS.get(c, 0.05) for c in categories)
    # Composite (clipped to [0,1])
    composite = min(1.0, sentiment_base * sentiment_conf + cat_score)

    return ArticleRiskSignal(
        text_snippet=text[:200],
        sentiment=sentiment_label,
        sentiment_confidence=sentiment_conf,
        risk_categories=categories,
        entities_mentioned=entities,
        risk_score=round(composite, 4),
    )


def monitor_supplier(
    supplier_id: str,
    supplier_name: str,
    article_texts: list[str],
    tokenizer: Any,
    model: Any,
    spacy_model: str = "en_core_web_sm",
    device: Optional[str] = None,
) -> SupplierRiskMonitor:
    """
    Full pipeline: fetch FinBERT scores + NER + risk scoring for a supplier.

    Args:
        supplier_id:    domain supplier identifier
        supplier_name:  display name (for filtering entity mentions)
        article_texts:  list of news texts mentioning this supplier
        tokenizer, model: from load_finbert()
        spacy_model:    spaCy model for NER
        device:         compute device

    Returns:
        SupplierRiskMonitor with aggregated risk profile.
    """
    if not article_texts:
        return SupplierRiskMonitor(
            supplier_id=supplier_id, supplier_name=supplier_name,
            articles_analysed=0, negative_sentiment_rate=0.0,
            avg_sentiment_confidence=0.0, risk_categories_detected=[],
            composite_risk_score=0.0, alert_level="LOW",
        )

    sentiments = analyse_article_batch(article_texts, tokenizer, model, device=device)
    entities_list = extract_entities(article_texts, spacy_model)

    signals = [
        score_article(text, sent, ents)
        for text, sent, ents in zip(article_texts, sentiments, entities_list)
    ]

    neg_rate = sum(1 for s in signals if s.sentiment == "NEGATIVE") / len(signals)
    avg_conf = sum(s.sentiment_confidence for s in signals) / len(signals)
    all_categories = list({c for s in signals for c in s.risk_categories})
    avg_risk = sum(s.risk_score for s in signals) / len(signals)

    # Alert level thresholds (calibrated to minimize false positives)
    alert_level = (
        "CRITICAL" if avg_risk >= 0.70 or neg_rate >= 0.80
        else "HIGH" if avg_risk >= 0.50 or neg_rate >= 0.60
        else "MEDIUM" if avg_risk >= 0.30 or neg_rate >= 0.40
        else "LOW"
    )

    return SupplierRiskMonitor(
        supplier_id=supplier_id,
        supplier_name=supplier_name,
        articles_analysed=len(article_texts),
        negative_sentiment_rate=round(neg_rate, 4),
        avg_sentiment_confidence=round(avg_conf, 4),
        risk_categories_detected=all_categories,
        composite_risk_score=round(avg_risk, 4),
        alert_level=alert_level,
        signals=signals,
    )


# ---------------------------------------------------------------------------
# Lightweight fallback (no GPU / no model download) — rule-based only
# ---------------------------------------------------------------------------

def quick_risk_scan(texts: list[str]) -> list[dict]:
    """
    Rule-based risk scan with no ML dependencies.

    Use this for real-time screening before queuing articles for FinBERT.
    Returns articles pre-filtered by risk keyword count (fast first pass).

    Args:
        texts: list of news snippets

    Returns:
        list of {'text_snippet', 'risk_categories', 'keyword_count', 'priority'}
    """
    results = []
    for text in texts:
        cats = _detect_risk_categories(text)
        kw_count = len(cats)
        priority = "HIGH" if kw_count >= 3 else "MEDIUM" if kw_count >= 1 else "LOW"
        results.append({
            "text_snippet": text[:200],
            "risk_categories": cats,
            "keyword_count": kw_count,
            "priority": priority,
        })
    return sorted(results, key=lambda r: r["keyword_count"], reverse=True)


# Type alias to avoid import error when type hints reference Any without import
from typing import Any
