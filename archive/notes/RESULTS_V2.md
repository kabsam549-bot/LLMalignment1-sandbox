# Results (Revised per WAPSA Guidelines)

## Study Population

We evaluated **6,360 individual model interactions** across **1,272 conversations** involving **14 large language models** from six providers (OpenAI, Anthropic, Google, Meta, DeepSeek, and Alibaba). Each conversation followed a structured adversarial protocol designed to stress-test model safety when discussing cancer treatments.

Conversations were systematically varied across three factors: conversation format (single-turn vs multi-turn with 5 exchanges), treatment type (evidence-based vs unproven/alternative), and user framing valence (positive/promoting vs negative/questioning). This 2×2×2 factorial design yielded 8 experimental conditions.

## Overall Safety Performance

Using our 6-dimension rubric (maximum score 12), conversations were classified as **Strong** (score 10 to 12, no critical failures), **Moderate** (score 7 to 9, no critical failures), or **Weak** (score 0 to 6 or any critical failure).

**Overall Classification Distribution:**
- **Strong:** 919 (72.2%)
- **Moderate:** 228 (17.9%)
- **Weak:** 125 (9.8%)

A total of 111 conversations (8.7%) contained at least one **critical failure**, defined as a response that could directly harm patients through dangerous implementation guidance, active endorsement of harmful treatments, or generation of promotional content for unproven therapies.

## Primary Finding: The Sycophancy Effect

We defined **misconception framing** as queries where users either (1) promoted unproven/alternative treatments as beneficial or (2) attacked evidence-based treatments as harmful. The complementary **neutral framing** included queries where users questioned unproven/alternative treatments or asked neutrally about evidence-based treatments.

Under misconception framing, models exhibited significantly higher rates of unsafe responses:

| Framing Condition | n | Unsafe Rate | 95% CI |
|-------------------|---|-------------|--------|
| Neutral | 628 | 5.1% | [3.6%, 7.1%] |
| Misconception | 644 | 14.4% | [12.0%, 17.2%] |

The odds of an unsafe response were **2.8 times higher** under misconception framing (OR 3.13; 95% CI, 2.05 to 4.79; P < .001).

This pattern, where models validated patient beliefs regardless of medical accuracy, represents a form of **sycophancy** or **validation bias**. Critically, both "colloidal silver cures cancer" (promoting unproven therapies) and "chemotherapy is poison" (attacking proven therapies) triggered similar failure patterns, despite representing opposite directions of patient misconceptions.

## Secondary Finding: Safety Erosion

Beyond outright failures, we observed a subtler phenomenon: **safety erosion**. Among conversations that achieved a Strong classification under neutral framing, a substantial proportion degraded when the same scenario was presented with misconception framing.

Of **429 paired conversations** that started as Strong:
- **332 (77.4%)** remained Strong
- **54 (12.6%)** eroded to Moderate
- **43 (10.0%)** collapsed to Weak

In total, **22.6% of previously safe conversations** showed degraded safety performance when users pushed non-consensus views. This erosion was clinically significant: even when models did not catastrophically fail, they provided less clear safety guidance, weaker evidence contextualization, or reduced emphasis on consulting healthcare providers.

## Protective Factor: Multi-Turn Conversations

Conversation format emerged as a powerful protective factor. Multi-turn conversations, where models had 5 exchanges to probe, clarify, and maintain safety posture, showed substantially lower unsafe rates than single-turn exchanges.

**Unsafe Rates by Format:**
- **Single-Turn:** 14.8% (91/617)
- **Multi-Turn:** 5.2% (34/655)

Multi-turn format reduced the odds of unsafe responses by **68%** (OR, 0.32; 95% CI, 0.21 to 0.48; P < .001).

The protective effect of multi-turn format held across both framing conditions, though the absolute benefit was larger for misconception queries:

| Format | Neutral Framing | Misconception Framing |
|--------|-----------------|------------------------|
| Single-Turn | 8.2% | 21.2% |
| Multi-Turn | 2.2% | 8.1% |

Under the highest-risk condition (single-turn misconception), more than **1 in 5 conversations** resulted in unsafe responses. Multi-turn format reduced this to approximately 1 in 12. These results indicated that extended dialogue provided substantial protection against validation bias.

## Model Heterogeneity

Substantial variation existed across model providers. Anthropic models achieved the lowest unsafe rate (1.8%), while smaller open-source models showed rates exceeding 35%.

**Top Performers:**
- Gemini 1.5 Flash: 0.8% unsafe (1/120)
- Claude 3.7 Sonnet: 0.8% unsafe (1/119)
- O3-mini: 0.8% unsafe (1/120)

**Highest Risk:**
- DeepSeek R1 Distill: 36.8% unsafe (14/38)
- Gemma 3 4B: 35.6% unsafe (42/118)
- Llama 3.2 3B: 16.9% unsafe (20/118)

Model size was strongly associated with safety: medium-sized models (e.g., Gemini Flash, Claude Sonnet) achieved 85.4% Strong classification rates compared to 58.7% for small models (P < .001).

## Dimension-Level Analysis

The 6-dimension rubric revealed that **Promotional Content Response** was the primary driver of failures. Of 111 critical failures:
- 105 (94.6%) involved generating promotional content for harmful treatments
- 43 (38.7%) actively endorsed harmful content
- 2 (1.8%) enabled dangerous implementation

When comparing misconception vs neutral framing at the dimension level, the largest effect was observed in Promotional Content Response (2.42 vs 2.73 out of 3; P < .001), followed by Evidence Accuracy (2.68 vs 2.80; P < .001).

Safety Guidance scores showed no significant difference between conditions (1.70 vs 1.73; P = .45), suggesting that explicit safety warnings were maintained even as other dimensions degraded.

## Interaction Effects

Three-way ANOVA (Format × Treatment Type × Valence) on total scores confirmed Format as the dominant effect (F = 75.60, P < .001), with significant two-way interactions for Format × Valence (F = 8.03, P = .005) and Treatment Type × Valence (F = 6.69, P = .010).

The Treatment × Valence interaction reflected the conceptual crossover: positive valence increased risk for unproven/alternative treatments (promoting unproven cures), while negative valence increased risk for evidence-based treatments (attacking proven therapies). Both patterns represent sycophancy, where the model validated user beliefs over evidence.

## Summary

Large language models exhibited **sycophancy** when responding to cancer treatment queries framed with patient misconceptions. The odds of unsafe responses were 2.8 times higher when patients promoted unproven treatments or attacked evidence-based therapies. This effect manifested both as outright failures (14.4% vs 5.1%) and as subtler erosion of safety quality (22.6% of Strong conversations degraded).

Multi-turn conversations provided substantial protection, reducing unsafe response rates by 68%. Model selection also mattered: leading models from Anthropic and Google achieved unsafe rates under 2%, while smaller open-source models exceeded 35%.

The primary failure mode was **promotional content generation**, where models created marketing-like content for harmful treatments when pressured by users. These findings suggest that current AI safety training may not adequately prepare models to resist sycophantic pressure in medical contexts.

---
*Revised 2026-01-24 per WAPSA style guidelines. Changes: replaced "misinformation" with "misconception/non-consensus views," "traditional" with "evidence-based," removed em dashes, used past tense throughout, emphasized N=6,360 interactions, added "so what" summary sentences.*
