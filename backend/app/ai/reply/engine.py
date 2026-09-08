"""Auto-Reply Engine (TF-IDF + Multiclass Logistic Regression with Real Train/Test Holdout)."""

import re
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


class ReplyIntent(str, Enum):
    """Categorical comment intents."""
    PRICING_INQUIRY = "pricing_inquiry"
    SUPPORT_ISSUE = "support_issue"
    COMPLIMENT_PRAISE = "compliment_praise"
    GENERAL_INQUIRY = "general_inquiry"
    SPAM_TROLL = "spam_troll"
    NEUTRAL_FEEDBACK = "neutral_feedback"


class ReplyAction(str, Enum):
    """Human-in-the-loop routing actions."""
    AUTOMATIC = "automatic"  # Execute reply immediately (confidence >= 0.90)
    APPROVAL_REQUIRED = "approval_required"  # Queue for human review (0.70 <= confidence < 0.90)
    MANUAL = "manual"  # Route to human team inbox (confidence < 0.70 or sensitive issue)
    IGNORE_SPAM = "ignore_spam"  # Flag or hide spam without auto-replying


class AutomationMode(str, Enum):
    """System-level automation policy."""
    MANUAL = "manual"  # Suggestions only
    ASSISTED = "assisted"  # Always require human approval
    AUTOMATIC = "automatic"  # Send automatically when confidence >= auto_threshold


@dataclass
class ReplyClassification:
    """Comment classification output."""
    intent: ReplyIntent
    confidence: float  # 0.0 to 1.0 probability
    all_probabilities: Dict[str, float]
    keywords_detected: List[str]


@dataclass
class ReplySuggestion:
    """Generated reply suggestion and routing."""
    comment_id: str
    comment_text: str
    intent: ReplyIntent
    suggested_reply: str
    confidence: float
    routing_action: ReplyAction
    template_used: str
    requires_human_review: bool


@dataclass
class ReplyConfig:
    """Configurable thresholds and response templates."""
    auto_threshold: float = 0.90
    approval_threshold: float = 0.70
    automation_mode: AutomationMode = AutomationMode.AUTOMATIC
    baseline_accuracy: float = 88.00  # Research paper baseline

    templates: Dict[str, List[str]] = field(default_factory=lambda: {
        ReplyIntent.PRICING_INQUIRY.value: [
            "Thanks for your interest! Pricing plans start with a free trial. Check the link in our bio for full details! 🚀",
            "Hey! You can find our pricing tiers and features at the link in bio. Feel free to DM us with any questions! 🙌",
        ],
        ReplyIntent.SUPPORT_ISSUE.value: [
            "We're sorry to hear you're experiencing an issue! Please send us a DM or email support@aismm.com so our team can resolve this immediately. 🙏",
            "Thank you for letting us know! Please DM us your account details and our support team will help you right away.",
        ],
        ReplyIntent.COMPLIMENT_PRAISE.value: [
            "Thank you so much! We really appreciate your support! ❤️🙌",
            "Thanks for the love! Thrilled to have you in our community! 🚀🎉",
            "Appreciate the kind words! Let us know if you need anything. ✨",
        ],
        ReplyIntent.GENERAL_INQUIRY.value: [
            "Thanks for asking! You can find all the details and links in our bio. Let us know if we can help with anything else! 👍",
            "Great question! Check out our website link in bio for full information. Have a great day! 😊",
        ],
        ReplyIntent.NEUTRAL_FEEDBACK.value: [
            "Thanks for sharing your feedback with us! 👍",
            "Appreciate you taking the time to share your thoughts!",
        ],
    })


class ReplyEngine(ABC):
    """Abstract base contract for reply generation engines."""

    @abstractmethod
    def classify_comment(self, text: str) -> ReplyClassification:
        """Classify incoming comment into intent."""
        pass

    @abstractmethod
    def generate_reply(self, comment_text: str, comment_id: str = "") -> ReplySuggestion:
        """Generate response and determine routing action."""
        pass


class TFIDFReplyEngine(ReplyEngine):
    """Research Baseline: TF-IDF (n-grams 1,2) + Multinomial Logistic Regression."""

    TRAINING_CORPUS: List[Tuple[str, str]] = [
        # Pricing inquiries
        ("How much does this cost?", ReplyIntent.PRICING_INQUIRY.value),
        ("What is the price for the monthly subscription?", ReplyIntent.PRICING_INQUIRY.value),
        ("Where can I check pricing plans?", ReplyIntent.PRICING_INQUIRY.value),
        ("Is there a free trial or discount coupon available?", ReplyIntent.PRICING_INQUIRY.value),
        ("What are your subscription rates?", ReplyIntent.PRICING_INQUIRY.value),
        ("Cost for enterprise license?", ReplyIntent.PRICING_INQUIRY.value),
        ("how much is this?", ReplyIntent.PRICING_INQUIRY.value),
        ("price please", ReplyIntent.PRICING_INQUIRY.value),
        ("how much to buy?", ReplyIntent.PRICING_INQUIRY.value),
        ("Can you share your annual pricing breakdown?", ReplyIntent.PRICING_INQUIRY.value),
        ("Do you offer student discounts or non-profit rates?", ReplyIntent.PRICING_INQUIRY.value),
        ("Is the starter plan billed monthly or annually?", ReplyIntent.PRICING_INQUIRY.value),
        ("What is the cost per social account?", ReplyIntent.PRICING_INQUIRY.value),
        ("Any promotional discount codes available for new accounts?", ReplyIntent.PRICING_INQUIRY.value),
        ("How expensive is the pro plan?", ReplyIntent.PRICING_INQUIRY.value),

        # Support issues
        ("My account is locked and not working properly.", ReplyIntent.SUPPORT_ISSUE.value),
        ("I encountered a bug when uploading video files.", ReplyIntent.SUPPORT_ISSUE.value),
        ("App crashed and failed to publish my post.", ReplyIntent.SUPPORT_ISSUE.value),
        ("Need refund, payment charged twice by mistake.", ReplyIntent.SUPPORT_ISSUE.value),
        ("I cannot login to my dashboard, getting 500 error.", ReplyIntent.SUPPORT_ISSUE.value),
        ("This is broken, please fix it.", ReplyIntent.SUPPORT_ISSUE.value),
        ("Error code 400 when connecting my account.", ReplyIntent.SUPPORT_ISSUE.value),
        ("Customer support is not answering my ticket.", ReplyIntent.SUPPORT_ISSUE.value),
        ("Posts are failing to publish to Facebook automatically.", ReplyIntent.SUPPORT_ISSUE.value),
        ("My OAuth connection disconnected unexpectedly.", ReplyIntent.SUPPORT_ISSUE.value),
        ("The analytics charts are showing 0 data since yesterday.", ReplyIntent.SUPPORT_ISSUE.value),
        ("Password reset email never arrived in my inbox.", ReplyIntent.SUPPORT_ISSUE.value),
        ("Billing failure error code 402 on card renewal.", ReplyIntent.SUPPORT_ISSUE.value),
        ("Unable to delete scheduled post, getting server timeout.", ReplyIntent.SUPPORT_ISSUE.value),

        # Compliments & praise
        ("Amazing product, love the new UI update! ❤️", ReplyIntent.COMPLIMENT_PRAISE.value),
        ("This is fantastic! Super clean and powerful.", ReplyIntent.COMPLIMENT_PRAISE.value),
        ("Great job team, this saves me hours of work! 🚀", ReplyIntent.COMPLIMENT_PRAISE.value),
        ("Awesome feature release, absolutely love it!", ReplyIntent.COMPLIMENT_PRAISE.value),
        ("Best social media management tool on the market.", ReplyIntent.COMPLIMENT_PRAISE.value),
        ("Brilliant work! Congrats on the launch! 🎉", ReplyIntent.COMPLIMENT_PRAISE.value),
        ("So cool, keep it up!", ReplyIntent.COMPLIMENT_PRAISE.value),
        ("Huge fan of the new scheduling engine features!", ReplyIntent.COMPLIMENT_PRAISE.value),
        ("The AI caption optimizer is unbelievably accurate and helpful! 🔥", ReplyIntent.COMPLIMENT_PRAISE.value),
        ("Love the dark mode interface and responsiveness.", ReplyIntent.COMPLIMENT_PRAISE.value),
        ("Incredible platform, recommended it to all my colleagues. 🙌", ReplyIntent.COMPLIMENT_PRAISE.value),
        ("Kudos to the developers for this fantastic release.", ReplyIntent.COMPLIMENT_PRAISE.value),

        # General inquiries
        ("Where can I download the latest release?", ReplyIntent.GENERAL_INQUIRY.value),
        ("When will you support TikTok and YouTube shorts?", ReplyIntent.GENERAL_INQUIRY.value),
        ("What is the link to the documentation website?", ReplyIntent.GENERAL_INQUIRY.value),
        ("How do I connect my Facebook page to this dashboard?", ReplyIntent.GENERAL_INQUIRY.value),
        ("Is there a mobile app available on iOS or Android?", ReplyIntent.GENERAL_INQUIRY.value),
        ("Where can I find more information?", ReplyIntent.GENERAL_INQUIRY.value),
        ("Can you explain how this works?", ReplyIntent.GENERAL_INQUIRY.value),
        ("Do you provide a public REST API or webhooks for developers?", ReplyIntent.GENERAL_INQUIRY.value),
        ("How many team members can share one workspace?", ReplyIntent.GENERAL_INQUIRY.value),
        ("Where is the user settings configuration page located?", ReplyIntent.GENERAL_INQUIRY.value),
        ("Can I schedule carousel posts on LinkedIn?", ReplyIntent.GENERAL_INQUIRY.value),

        # Spam & troll
        ("Check out my bio for free money and crypto gains 💰", ReplyIntent.SPAM_TROLL.value),
        ("Follow for follow back guaranteed immediately!", ReplyIntent.SPAM_TROLL.value),
        ("Earn 5000 dollars a day working from home click here", ReplyIntent.SPAM_TROLL.value),
        ("DM me to grow your followers fast 100k cheap", ReplyIntent.SPAM_TROLL.value),
        ("Free gift cards click link on my page", ReplyIntent.SPAM_TROLL.value),
        ("Get rich quick with my forex trading telegram signals link", ReplyIntent.SPAM_TROLL.value),
        ("Hot singles in your area click the link in bio", ReplyIntent.SPAM_TROLL.value),
        ("Buy verified blue checkmark badges cheap DM now", ReplyIntent.SPAM_TROLL.value),

        # Neutral comments
        ("Interesting perspective on social media trends.", ReplyIntent.NEUTRAL_FEEDBACK.value),
        ("Noticed this today as well.", ReplyIntent.NEUTRAL_FEEDBACK.value),
        ("Standard update for the industry.", ReplyIntent.NEUTRAL_FEEDBACK.value),
        ("Okay, noted.", ReplyIntent.NEUTRAL_FEEDBACK.value),
        ("Just reading through the release notes.", ReplyIntent.NEUTRAL_FEEDBACK.value),
        ("Seen similar approaches before in data science.", ReplyIntent.NEUTRAL_FEEDBACK.value),
        ("Following along with the progress.", ReplyIntent.NEUTRAL_FEEDBACK.value),
    ]

    def __init__(self, config: Optional[ReplyConfig] = None):
        self.config = config or ReplyConfig()
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=5000,
            sublinear_tf=True,
        )
        self.classifier = LogisticRegression(
            max_iter=1000,
            C=5.0,
            random_state=42,
        )
        self.heldout_test_data: Optional[Tuple[List[str], List[str]]] = None
        self.evaluated_metrics: Dict[str, float] = {}
        self._is_trained = False
        self._train_baseline_model()

    def _train_baseline_model(self) -> None:
        """Train classifier on train split and evaluate on held-out test split."""
        texts = [item[0] for item in self.TRAINING_CORPUS]
        labels = [item[1] for item in self.TRAINING_CORPUS]

        # 80/20 Train-Test split for out-of-sample evaluation
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.20, random_state=42, stratify=labels
        )

        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        self.classifier.fit(X_train_tfidf, y_train)
        self.heldout_test_data = (X_test, y_test)

        # Compute real out-of-sample performance
        X_test_tfidf = self.vectorizer.transform(X_test)
        y_pred = self.classifier.predict(X_test_tfidf)

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
        rec = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
        f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

        self.evaluated_metrics = {
            "accuracy": round(acc * 100, 2),
            "precision": round(prec * 100, 2),
            "recall": round(rec * 100, 2),
            "f1_score": round(f1 * 100, 2),
            "test_samples": len(X_test),
        }
        self._is_trained = True

    def evaluate_on_heldout(self) -> Dict[str, float]:
        """Evaluate classifier on held-out test split and return live computed metrics."""
        if not self.heldout_test_data:
            return {"status": "not_evaluated"}

        X_test, y_test = self.heldout_test_data
        X_test_tfidf = self.vectorizer.transform(X_test)
        y_pred = self.classifier.predict(X_test_tfidf)

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
        rec = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
        f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

        return {
            "accuracy": round(acc * 100, 2),
            "precision": round(prec * 100, 2),
            "recall": round(rec * 100, 2),
            "f1_score": round(f1 * 100, 2),
            "test_samples": len(X_test),
        }

    def classify_comment(self, text: str) -> ReplyClassification:
        """Classify incoming comment into intent with confidence distribution."""
        clean_text = text or ""
        if not clean_text.strip():
            return ReplyClassification(
                intent=ReplyIntent.NEUTRAL_FEEDBACK,
                confidence=1.0,
                all_probabilities={ReplyIntent.NEUTRAL_FEEDBACK.value: 1.0},
                keywords_detected=[],
            )

        vec = self.vectorizer.transform([clean_text])
        probabilities = self.classifier.predict_proba(vec)[0]
        classes = self.classifier.classes_

        prob_dict = {classes[i]: round(float(probabilities[i]), 4) for i in range(len(classes))}
        best_class_idx = int(np.argmax(probabilities))
        best_intent_str = classes[best_class_idx]
        best_confidence = float(probabilities[best_class_idx])

        # Rule-based regex boosting for high-precision intents
        keywords_detected = []
        if re.search(r"\b(cost|price|pricing|how much|rate|subscription|discount)\b", clean_text, re.I):
            keywords_detected.append("pricing")
            best_intent_str = ReplyIntent.PRICING_INQUIRY.value
            best_confidence = max(0.85, min(0.99, best_confidence + 0.35))

        if re.search(r"\b(error|bug|broken|crash|not working|issue|refund|help|locked)\b", clean_text, re.I):
            keywords_detected.append("support")
            best_intent_str = ReplyIntent.SUPPORT_ISSUE.value
            best_confidence = max(0.85, min(0.99, best_confidence + 0.35))

        if re.search(r"\b(love|awesome|amazing|great|fantastic|fire|brilliant|helpful|best|❤️|🔥|🎉|✨|🙌)\b", clean_text, re.I):
            keywords_detected.append("compliment")
            best_intent_str = ReplyIntent.COMPLIMENT_PRAISE.value
            best_confidence = max(0.85, min(0.99, best_confidence + 0.35))

        if re.search(r"\b(crypto|free money|earn \d+|follow for follow|gift card)\b", clean_text, re.I):
            keywords_detected.append("spam")
            best_intent_str = ReplyIntent.SPAM_TROLL.value
            best_confidence = 0.98

        try:
            intent = ReplyIntent(best_intent_str)
        except ValueError:
            intent = ReplyIntent.NEUTRAL_FEEDBACK

        return ReplyClassification(
            intent=intent,
            confidence=round(best_confidence, 4),
            all_probabilities=prob_dict,
            keywords_detected=keywords_detected,
        )

    def generate_reply(self, comment_text: str, comment_id: str = "") -> ReplySuggestion:
        """Generate response and determine routing action based on confidence and mode."""
        classification = self.classify_comment(comment_text)
        intent = classification.intent
        conf = classification.confidence

        # Handle Spam
        if intent == ReplyIntent.SPAM_TROLL:
            return ReplySuggestion(
                comment_id=comment_id,
                comment_text=comment_text,
                intent=intent,
                suggested_reply="",
                confidence=conf,
                routing_action=ReplyAction.IGNORE_SPAM,
                template_used="none_spam",
                requires_human_review=False,
            )

        # Select template
        templates = self.config.templates.get(intent.value, ["Thank you for reaching out!"])
        idx = len(comment_text) % len(templates)
        selected_reply = templates[idx]

        # Determine human-in-the-loop action
        if self.config.automation_mode == AutomationMode.MANUAL:
            action = ReplyAction.MANUAL
            review_required = True
        elif self.config.automation_mode == AutomationMode.ASSISTED:
            action = ReplyAction.APPROVAL_REQUIRED
            review_required = True
        else:  # Automatic mode
            if intent == ReplyIntent.SUPPORT_ISSUE:
                action = ReplyAction.APPROVAL_REQUIRED
                review_required = True
            elif conf >= self.config.auto_threshold:
                action = ReplyAction.AUTOMATIC
                review_required = False
            elif conf >= self.config.approval_threshold:
                action = ReplyAction.APPROVAL_REQUIRED
                review_required = True
            else:
                action = ReplyAction.MANUAL
                review_required = True

        return ReplySuggestion(
            comment_id=comment_id,
            comment_text=comment_text,
            intent=intent,
            suggested_reply=selected_reply,
            confidence=conf,
            routing_action=action,
            template_used=f"{intent.value}_template_{idx}",
            requires_human_review=review_required,
        )
