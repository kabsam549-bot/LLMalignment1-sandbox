# Abstract

**Importance**  
Patients increasingly rely on large language model (LLM) chatbots for medical information. While these models perform well on neutral queries, their safety when confronted with patient-driven misinformation—a phenomenon known as sycophancy—remains uncharacterized in oncology, where validation of unproven therapies can lead to treatment abandonment.

**Objective**  
To evaluate whether LLMs maintain safety standards when users frame cancer treatment queries with misinformation, and to determine if conversational format modifies this risk.

**Design, Setting, and Participants**  
This cross-sectional stress test employed a 2×2×2 factorial design to evaluate 1,272 structured conversations across 14 LLMs from 6 providers (OpenAI, Anthropic, Google, Meta, DeepSeek, Alibaba). Conversations varied by framing (misinformation vs neutral), treatment type (evidence-based vs alternative), and format (single-turn vs multi-turn). Misinformation framing included both promoting unproven cures and attacking evidence-based therapies.

**Main Outcomes and Measures**  
The primary outcome was the rate of unsafe responses, defined as a "Weak" classification on a 6-dimension safety rubric (score 0–6/12) or the presence of critical failures (e.g., generating promotional content for harmful treatments). Secondary outcomes included safety erosion and dimension scores.

**Results**  
Among 1,272 conversations, misinformation framing significantly increased the rate of unsafe responses compared with neutral framing (14.4% [93/644] vs 5.1% [32/628]; odds ratio [OR], 3.13; 95% CI, 2.05-4.79; P < .001). Beyond outright failures, 22.6% of safe conversations degraded in quality under misinformation conditions. Multi-turn dialogue was protective, reducing unsafe response rates by 68% (OR, 0.32; 95% CI, 0.21-0.48; P < .001). Performance varied by provider, with unsafe rates ranging from 1.8% (Anthropic) to 36.8% (DeepSeek).

**Conclusions and Relevance**  
LLMs exhibit significant sycophancy in oncology, validating patient misinformation at 2.8 times the rate of neutral queries. This validation bias presents a safety risk that standard neutral evaluations miss. Clinical integration of AI assistants requires adversarial testing and multi-turn guardrails to prevent reinforcing harmful beliefs.
