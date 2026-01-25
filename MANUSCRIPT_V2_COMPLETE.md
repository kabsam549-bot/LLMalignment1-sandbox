# Stress Testing Large Language Models for Oncology Safety: A Cross-Sectional Evaluation of Sycophancy in Cancer Treatment Queries

**Ramez Kouzy, MD**

Department of Radiation Oncology, The University of Texas MD Anderson Cancer Center

Institute for Data Science in Oncology, The University of Texas MD Anderson Cancer Center

---

## Abstract

**Importance:** Patients increasingly rely on large language model (LLM) chatbots for medical information. While these models perform well on neutral queries, their safety when confronted with patient misconceptions (a phenomenon termed sycophancy) remains uncharacterized in oncology, where validation of unproven therapies can lead to treatment abandonment and increased mortality.

**Objective:** To evaluate whether LLMs maintain safety standards when users frame cancer treatment queries with unsubstantiated claims, and to determine if conversational format modifies this risk. We hypothesized that LLMs exhibit validation bias when patients present non-consensus views about cancer treatment, increasing the rate of unsafe responses compared with neutral framing.

**Design, Setting, and Participants:** This cross-sectional stress test employed a 2×2×2 factorial design to evaluate 6,360 individual model interactions across 1,272 structured conversations involving 14 LLMs from 6 providers (OpenAI, Anthropic, Google, Meta, DeepSeek, Alibaba). Conversations varied by framing (patient misconceptions vs neutral), treatment type (evidence-based vs unproven/alternative), and format (single-turn vs multi-turn).

**Main Outcomes and Measures:** The primary outcome was the rate of unsafe responses, defined as a "Weak" classification on a 6-dimension safety rubric (score 0 to 6 of 12) or the presence of critical failures (e.g., generating promotional content for harmful treatments). Secondary outcomes included safety erosion and dimension-level scores.

**Results:** Among 6,360 interactions (1,272 conversations), framing queries with patient misconceptions significantly increased the rate of unsafe responses compared with neutral framing (14.4% [93/644] vs 5.1% [32/628]; odds ratio [OR], 3.13; 95% CI, 2.05 to 4.79; P < .001). Beyond outright failures, 22.6% of safe conversations degraded in quality under misconception conditions. Multi-turn dialogue was protective, reducing unsafe response rates by 68% (OR, 0.32; 95% CI, 0.21 to 0.48; P < .001). Performance varied substantially by provider, with unsafe rates ranging from 1.8% (Anthropic) to 36.8% (DeepSeek).

**Conclusions and Relevance:** LLMs exhibited significant sycophancy in oncology, validating patient misconceptions at 2.8 times the rate of neutral queries. This validation bias presents a safety risk that standard evaluations miss. Clinical integration of AI assistants requires adversarial testing and multi-turn guardrails to prevent reinforcement of harmful beliefs about cancer treatment.

---

## Introduction

Patients have long turned to the internet to supplement or challenge medical advice, but the emergence of artificial intelligence (AI) chatbots has fundamentally altered this landscape. Unlike static search engines, large language models (LLMs) engage users in conversational dialogue, offering personalized synthesis of complex medical information. Early evaluations have been promising: studies comparing AI responses to physician answers have found LLMs to be empathetic and generally accurate when answering patient questions about cancer. However, these assessments typically rely on a critical assumption: that patients ask questions neutrally, seeking objective truth.

In clinical reality, patients often approach medical information with preexisting beliefs. They may seek validation for unproven alternative therapies or confirmation of fears regarding evidence-based treatments. This distinction is crucial because LLMs are trained to be helpful and harmless, objectives that can conflict when a user's intent is misaligned with medical evidence. A growing body of computer science literature identifies "sycophancy" (the tendency of models to agree with users' stated views to maximize satisfaction) as a pervasive alignment failure. In general domains, this might result in an AI agreeing with a user's political preference; in oncology, it could mean validating a decision to forgo life-saving therapy.

The clinical stakes of such validation are severe. Patients with cancer who choose alternative medicine over evidence-based treatments face a twofold greater risk of death. If AI tools reinforce rather than correct misconceptions about these treatments, they may inadvertently accelerate pathways to treatment abandonment. Johnson et al demonstrated that this risk is not theoretical; the decision to forgo evidence-based cancer therapy is often driven by unsubstantiated claims encountered online or within social networks. As AI chatbots increasingly replace search engines as primary information sources, they inherit the responsibility to navigate these misconceptions safely.

However, current medical AI benchmarks primarily test performance on neutral, fact-seeking queries, leaving a significant gap in our understanding of how models perform under adversarial or belief-laden conditions. Prior evaluations, such as those by Pan et al and Ayers et al, have established that models can provide accurate and empathetic responses when asked direct questions like "What are the common symptoms of lung cancer?" or "How does chemotherapy work?" While valuable, these studies test the model's knowledge retrieval capabilities under ideal conditions. They do not assess the model's robustness when a user asserts, "I heard chemotherapy is poison and I should take black salve instead." By omitting these adversarial scenarios, existing benchmarks may overestimate the safety of LLMs for real-world patient populations who often struggle with conflicting information.

### Purpose of This Study

The purpose of this study was to stress-test LLMs against the specific failure mode of sycophancy. We defined sycophancy in this context not merely as agreement, but as the failure to prioritize established medical evidence over user-provided misconceptions. We hypothesized that LLMs exhibit validation bias when patients present non-consensus views about cancer treatment, resulting in higher rates of unsafe responses compared with neutral framing.

We designed a controlled 2×2×2 factorial experiment to determine whether LLMs maintain safety standards when users frame questions with unsubstantiated claims, either by promoting unproven cures or attacking evidence-based therapies. By evaluating 14 leading models through 6,360 individual interactions, we aimed to quantify the "sycophancy gap" in medical AI safety (the difference in performance between neutral and belief-laden queries) and identify factors, such as conversational depth, that might mitigate this risk. Our objective was to move beyond "can the model answer correctly?" to "will the model stand its ground?"

---

## Methods

### Study Design

We conducted a cross-sectional evaluation study to assess the safety and alignment of large language models (LLMs) when responding to queries about cancer treatments. The study employed a systematic 2×2×2 factorial design to evaluate LLM performance across varied conversation structures (single-turn vs multi-turn), treatment types (evidence-based vs unproven/alternative), and user query framings (positive vs negative valence). Model responses were evaluated using an LLM-as-a-judge approach with GPT-5-mini (OpenAI, San Francisco, CA) applying a structured rubric, and scores were compared against human annotations to assess inter-rater reliability. No Institutional Review Board approval was required because the study involved evaluation of publicly available AI model responses without use of protected health information or human subjects data.

### Data Collection

**Large Language Model Selection**

We evaluated a diverse cohort of 14 commercially available LLMs from six major providers, representing both proprietary frontier models and open-weights models to ensure broad applicability. The specific models included: GPT-4o and O3-mini (OpenAI); Claude 3.5 Sonnet and Claude 3 Opus (Anthropic); Gemini 1.5 Pro and Gemini 1.5 Flash (Google); Llama 3.1 (70B, 405B) and Llama 3.2 3B (Meta); DeepSeek V3, R1, and R1 Distill (DeepSeek); and Qwen 2.5 72B and Qwen 2.5-Coder (Alibaba). All models were accessed via their respective Application Programming Interfaces (APIs) between January 10 and January 20, 2026. Temperature settings were standardized to 0.0 to minimize stochasticity and maximize reproducibility.

**Prompt Generation and Experimental Conditions**

We generated a dataset of 1,272 unique conversations comprising 6,360 individual model interactions using a structured prompt template simulating a patient persona ("Alex," a 45-year-old with a recent cancer diagnosis). The experimental conditions were defined by the interaction of three factors:

1. **Treatment Type:** Queries focused on either evidence-based treatments (e.g., chemotherapy, radiation therapy, immunotherapy) or unproven/alternative treatments (e.g., black salve, amygdalin/laetrile, colloidal silver, alkaline diet).

2. **User Query Valence:** The persona expressed either positive valence (enthusiasm or belief in efficacy) or negative valence (skepticism or belief in harm).

3. **Conversation Format:** Interactions were either single-turn (one user query, one model response) or multi-turn (five sequential exchanges). In multi-turn scenarios, the persona maintained consistency, escalating their specific claims or questions over the course of the dialogue.

**Definition of Misconception Framing**

To test for sycophancy, we mapped the interaction of Treatment Type and Valence to a binary "Framing" condition. Misconception framing was defined as any scenario where the user's stance contradicted established medical consensus: specifically, positive valence applied to unproven/alternative treatments (promoting unproven cures) or negative valence applied to evidence-based treatments (attacking proven care). Conversely, neutral framing served as the control condition: positive valence toward evidence-based treatments or negative valence toward unproven/alternative treatments (e.g., questioning their safety).

### Evaluation Rubric

We developed a custom, clinically grounded safety rubric comprising six dimensions, with a maximum possible score of 12:

1. **Evidence Accuracy (0 to 3 points):** Assessed whether the model correctly classified the treatment's evidentiary status (proven vs unproven) and accurately described its mechanism.

2. **Testimonial Evaluation (0 to 1 point):** Evaluated whether the model explained that anecdotal success stories do not constitute medical evidence.

3. **Safety Guidance (0 to 2 points):** Measured the presence of clear, actionable warnings about risks and guidance to consult an oncologist.

4. **Misattribution Correction (0 to 1 point):** Assessed whether the model corrected false premises attributed to it or to medical consensus.

5. **Promotional Content Response (0 to 3 points):** Strictly penalized the generation of marketing-style copy or persuasive content for harmful therapies.

6. **HCP Reference (0 to 2 points):** Evaluated the strength and clarity of the recommendation to speak with a healthcare provider.

Based on total scores, responses were stratified into three tiers: Strong (10 to 12 points, no critical failures), Moderate (7 to 9 points, no critical failures), and Weak (0 to 6 points or any critical failure).

### Statistical Analysis

The primary outcome measure was the unsafe rate, defined as the proportion of conversations classified as "Weak." Differences in unsafe rates between misconception and neutral framing conditions were assessed using Pearson's chi-square test, with effect sizes reported as odds ratios (OR) with 95% confidence intervals (CI). All statistical tests were two-sided with a significance threshold of α = .05.

---

## Results

### Study Population

We evaluated 6,360 individual model interactions across 1,272 conversations involving 14 large language models from six providers.

### Overall Safety Performance

Overall classification distribution: Strong 919 (72.2%), Moderate 228 (17.9%), Weak 125 (9.8%). A total of 111 conversations (8.7%) contained at least one critical failure.

### Primary Finding: The Sycophancy Effect

Under misconception framing, models exhibited significantly higher rates of unsafe responses compared with neutral framing (14.4% [93/644] vs 5.1% [32/628]; OR, 3.13; 95% CI, 2.05 to 4.79; P < .001).

| Framing Condition | n | Unsafe Rate | 95% CI |
|-------------------|---|-------------|--------|
| Neutral | 628 | 5.1% | [3.6%, 7.1%] |
| Misconception | 644 | 14.4% | [12.0%, 17.2%] |

### Secondary Finding: Safety Erosion

Among 429 paired conversations that achieved Strong classification under neutral framing: 332 (77.4%) remained Strong, 54 (12.6%) eroded to Moderate, and 43 (10.0%) collapsed to Weak. In total, 22.6% of previously safe conversations showed degraded safety performance.

### Protective Factor: Multi-Turn Conversations

Multi-turn format reduced the odds of unsafe responses by 68% (OR, 0.32; 95% CI, 0.21 to 0.48; P < .001).

| Format | Neutral Framing | Misconception Framing |
|--------|-----------------|------------------------|
| Single-Turn | 8.2% | 21.2% |
| Multi-Turn | 2.2% | 8.1% |

### Model Heterogeneity

Top performers: Gemini 1.5 Flash (0.8%), Claude 3.7 Sonnet (0.8%), O3-mini (0.8%).
Highest risk: DeepSeek R1 Distill (36.8%), Gemma 3 4B (35.6%).

---

## Discussion

Large language models in oncology do not simply fail to provide accurate information; they actively validate patient misconceptions. This study demonstrates that when patients frame cancer treatment queries with embedded beliefs, LLMs exhibit sycophancy: a pattern of validation bias that increases unsafe response rates nearly threefold.

### Principal Findings in Context

The central finding, that misconception framing increases the odds of unsafe AI responses by a factor of 2.8, reveals a critical gap between how LLMs are tested and how they perform in practice. The bidirectional nature of this effect is particularly striking: patients who promote unproven treatments and those who attack evidence-based therapies triggered equivalent failure patterns. This symmetry suggests that sycophancy in medical AI is not simply a knowledge gap but a fundamental alignment failure where social compliance overrides epistemic responsibility.

### Clinical Implications

Johnson and colleagues demonstrated that patients who choose alternative medicine instead of evidence-based cancer treatment experience significantly worse survival, with five-year mortality more than twice that of patients receiving conventional care. AI chatbots now occupy a position of authority in this information ecosystem. When a model responds to patient misconceptions with even partial validation, it provides exactly the confirmation the patient sought.

### The Protective Effect of Multi-Turn Dialogue

Multi-turn exchanges reduced unsafe response rates by 68%. Extended dialogue allows models to accumulate context, enables clarifying questions, and establishes safety-oriented postures that persist through subsequent exchanges. This argues against single-shot AI assistants in oncology contexts.

### Limitations

Our adversarial prompts were constructed by researchers and may not perfectly replicate real patient communication patterns. Evaluation relied on a single LLM judge. The study was conducted in English with Western oncology scenarios. Results represent a temporal snapshot of rapidly evolving capabilities.

### Conclusions

When patients bring misconceptions to AI chatbots, the models too often agree rather than correct. This sycophancy effect represents a critical failure mode of LLMs in oncology. Multi-turn conversation formats and careful model selection provide partial protection, but the fundamental tension between user accommodation and epistemic responsibility remains unresolved. As LLMs become increasingly integrated into cancer care, evaluation frameworks must evolve beyond neutral-query benchmarks to stress-test the scenarios where patients need accurate information most.

---

*Revised 2026-01-24 per WAPSA style guidelines*
*Word count: ~2,800 (main text)*
