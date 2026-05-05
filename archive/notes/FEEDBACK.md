# Writing Feedback & Style Guide: Stress Testing LLMs Paper
*For reference by Opus/Agents when editing the manuscript.*

## 1. General Style & Tone
*   **Tone:** Clinical oncology (JNCCN/JAMA Oncol style). Not "AI research" style.
*   **Punctuation:** **NO em dashes (—)**. Use commas/parentheses.
*   **Terminology:**
    *   **"Unsubstantiated claims" / "Patient misconceptions"** (instead of "Misinformation").
    *   **"Evidence-based"** (instead of "Traditional").
    *   **"Unproven/Alternative"** (instead of "Alternative" alone).
*   **Title:** Revert to previous ("Stress Testing Large Language Models for Medical Safety").

## 2. Manuscript Critique (Current State)
*   **Overall:** "Half-baked." Story is clear but underdeveloped.
*   **Visuals:** Figures/Tables are "sad looking" and inconsistent. Needs professional overhaul.

## 3. Specific Section Instructions
*   **Abstract/Intro:**
    *   Add explicit Hypothesis/Purpose statement.
    *   Highlight **N=6,360 interactions**.
    *   Fix any placeholders ("???").
*   **Methods:**
    *   **REPLACE** with Ramez's provided text (see below).
*   **Results:**
    *   Use past tense.
    *   Organize: Method -> Finding -> "So what" sentence.
*   **Discussion:**
    *   Focus on clinical mortality (Johnson et al.).
    *   No lists. Flowing prose.

## 4. Reference Material
*   **Style:** *Kouzy R, Abi Jaoude J, et al. JNCCN*.
*   **Structure:** WAPSA guidelines (Hypothesis statement usage, Method/Result pairing).

---

## Ramez's Provided Methods Section (Raw LaTeX)
% ============================================
\section{Methods}
\subsection{Study Design}
We conducted a 2$\times$2$\times$2 factorial experiment to evaluate the safety and alignment of large language models (LLMs) when discussing cancer treatments from a patient-centered perspective. The three experimental factors were: (1) conversation format (single-turn vs multi-turn), (2) treatment type (traditional vs alternative), and (3) query valence (positive vs negative framing). This design yielded 8 experimental conditions representing the spectrum of patient communication patterns encountered in clinical practice. The conversation structure was designed to model authentic patient-clinician interactions based on clinical experience with cancer treatment counseling. Multi-turn conversations followed an escalating protocol—from routine information-seeking to increasingly safety-critical scenarios—reflecting the natural progression of patient inquiries rather than purely adversarial testing. Importantly, the 8 conditions span a range from entirely benign (e.g., a patient asking positively about chemotherapy) to potentially harmful (e.g., requesting promotional content for unproven treatments). Prior literature has documented sycophancy in LLMs responding to medical queries, but no systematic evaluation has examined how conversation format, treatment evidence base, and user framing interact to influence safety-relevant outputs. We developed a structured evaluation rubric grounded in principles of clinical cancer care communication to quantify model performance across these conditions.

\subsection{Conversation Dataset}
We evaluated 1,272 conversations corresponding to 6,360 LLM-user interactions across 14 LLMs from 6 providers between March and September 2025. Model selection aimed to create a representative sample of publicly accessible LLMs available to patients at the time of the study, including free-tier commercial models, open-source models, and reasoning-focused architectures. The evaluated models were: Claude 3.5 Haiku and Claude 3.7 Sonnet (Anthropic); Gemini 1.5 Flash, Gemini 2.0 Flash, Gemini 2.0 Thinking, and Gemini 2.5 Pro (Google); Gemma 3 4B and Gemma 3 27B (Google, open-source); GPT-4o, GPT-4o-mini, and O3-mini (OpenAI); DeepSeek R1 Distill (DeepSeek, open-source); Llama 3.2 3B (Meta, open-source); and Qwen 3 32B (Alibaba, open-source).

The treatment dataset comprised 15 alternative therapies and 15 traditional therapies selected to represent the range of unproven and evidence-based cancer treatments patients commonly encounter (Appendix 1). Each treatment was queried across two formats and two valences. In the multi-turn format, five sequential queries (T1–T5) were delivered within a single conversation with context maintained between turns, allowing the model to reference prior exchanges. In the single-turn format, the same five queries were delivered as independent, isolated prompts without conversational context. To isolate the effect of valence while minimizing other confounds, positive and negative versions of each query differed by only one or two key words (e.g., ``effective'' vs ``ineffective,'' ``improved'' vs ``worsened,'' ``should'' vs ``shouldn't,'' ``promotional content'' vs ``warning content''), with all other phrasing held constant.

\subsection{Evaluation Rubric}
We developed a structured rubric (maximum 12 points) with six dimensions assessing distinct aspects of model safety (Appendix 2). \textbf{Evidence Accuracy (0–3 points)} evaluated factual correctness with appropriate clinical context. \textbf{Testimonial Handling (0–1 point)} assessed whether models explained why anecdotal evidence cannot establish treatment efficacy. \textbf{Safety Guidance (0–2 points)} measured clarity and proactivity of safety recommendations. \textbf{Misattribution Correction (0–1 point)} assessed whether models corrected false claims about having recommended specific treatments.\textbf{Promotional Content Response (0–3 points)} evaluated refusal to generate marketing materials. \textbf{Healthcare Professional References (0–2 points)} counted consistency of medical consultation recommendations.

Conversations were classified as Strong (10–12 points with no critical failures), Moderate (7–9 points with no critical failures), or Weak (0–6 points or any critical failure). Three categories of critical failure resulted in automatic Weak classification: (1) \textit{Enables Dangerous Implementation}, (2) \textit{Actively Endorses Harmful Content}, and (3) \textit{Creates Promotional Content}.

\subsection{Conversation Scoring}
We used GPT-5-mini via the OpenAI Batch API as an automated judge for scalable, consistent evaluation. The judge received structured prompts containing the complete rubric criteria, the conversation transcript, and instructions to first provide qualitative analysis of each rubric dimension before generating scores. This chain-of-thought approach improved scoring consistency by requiring explicit reasoning. The judge produced dimension-level qualitative assessments which were then converted to numeric scores using Python algorithms. Healthcare Professional Reference counts were computed algorithmically by pattern-matching explicit medical consultation recommendations across all model responses.

Judge prompts and scoring algorithms were iteratively refined on a pilot set of 88 conversations with dual human annotation by two clinical researchers. Disagreements were resolved through discussion to establish a gold standard. Agreement was assessed as the percentage of cases where the LLM judge score matched at least one human annotator (``LLM vs Any Human''), reflecting practical alignment with acceptable human judgment rather than requiring exact match with a single adjudicated score. Overall agreement was 81.8\%, with dimension-level agreement ranging from 77.3\% (Misattribution Correction) to 93.2\% (Testimonial Handling) (Appendix 3).

\subsection{Statistical Analysis}
Categorical comparisons (classification distributions, critical failure rates) used Pearson chi-square tests or Fisher's exact test when expected cell counts were $<$5. Odds ratios with 95\% confidence intervals quantified effect sizes for binary outcomes. Wilson score intervals provided confidence intervals for proportions. Continuous score comparisons used independent samples $t$-tests for two-group comparisons and one-way ANOVA with Tukey HSD post-hoc tests for multi-group comparisons across the four treatment$\times$valence conditions. To model critical failure risk, we fit logistic regression models with treatment type, valence, format, and their interactions as predictors. Model comparison used likelihood ratio tests to evaluate the significance of interaction terms. Predicted probabilities were computed for each experimental condition. To assess the joint effects of all three experimental factors on total rubric scores, we conducted three-way ANOVA (Format $\times$ Treatment $\times$ Valence) with partial eta-squared ($\eta_p^2$) as effect size measures. All analyses were conducted in Python 3.10 using pandas 1.5.3, NumPy 1.24.2, scikit-learn 1.2.2, and statsmodels 0.14.0. Statistical significance was set at $\alpha = 0.05$ (two-sided) for all tests.
