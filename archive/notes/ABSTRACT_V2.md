# Abstract (Revised per WAPSA Guidelines)

**Importance**  
Patients increasingly rely on large language model (LLM) chatbots for medical information. While these models perform well on neutral queries, their safety when confronted with patient misconceptions (a phenomenon termed sycophancy) remains uncharacterized in oncology, where validation of unproven therapies can lead to treatment abandonment and increased mortality.

**Objective**  
To evaluate whether LLMs maintain safety standards when users frame cancer treatment queries with unsubstantiated claims, and to determine if conversational format modifies this risk. We hypothesized that LLMs exhibit validation bias when patients present non-consensus views about cancer treatment, increasing the rate of unsafe responses compared with neutral framing.

**Design, Setting, and Participants**  
This cross-sectional stress test employed a 2×2×2 factorial design to evaluate 6,360 individual model interactions across 1,272 structured conversations involving 14 LLMs from 6 providers (OpenAI, Anthropic, Google, Meta, DeepSeek, Alibaba). Conversations varied by framing (patient misconceptions vs neutral), treatment type (evidence-based vs unproven/alternative), and format (single-turn vs multi-turn).

**Main Outcomes and Measures**  
The primary outcome was the rate of unsafe responses, defined as a "Weak" classification on a 6-dimension safety rubric (score 0 to 6 of 12) or the presence of critical failures (e.g., generating promotional content for harmful treatments). Secondary outcomes included safety erosion and dimension-level scores.

**Results**  
Among 6,360 interactions (1,272 conversations), framing queries with patient misconceptions significantly increased the rate of unsafe responses compared with neutral framing (14.4% [93/644] vs 5.1% [32/628]; odds ratio [OR], 3.13; 95% CI, 2.05 to 4.79; P < .001). Beyond outright failures, 22.6% of safe conversations degraded in quality under misconception conditions. Multi-turn dialogue was protective, reducing unsafe response rates by 68% (OR, 0.32; 95% CI, 0.21 to 0.48; P < .001). Performance varied substantially by provider, with unsafe rates ranging from 1.8% (Anthropic) to 36.8% (DeepSeek).

**Conclusions and Relevance**  
LLMs exhibited significant sycophancy in oncology, validating patient misconceptions at 2.8 times the rate of neutral queries. This validation bias presents a safety risk that standard evaluations miss. Clinical integration of AI assistants requires adversarial testing and multi-turn guardrails to prevent reinforcement of harmful beliefs about cancer treatment.

---
*Revised 2026-01-24 per WAPSA style guidelines. Changes: removed "misinformation" terminology, added explicit hypothesis, emphasized N=6,360 interactions, removed em dashes.*
