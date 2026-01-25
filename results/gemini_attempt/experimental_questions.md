# Experimental Questions: Stress Testing LLM Clinical Alignment

## Primary Research Question
Does user framing (Valence) and conversation structure (Format) systematically degrade the safety and evidence-accuracy of LLM medical counseling, even when the underlying clinical facts remain constant?

## Sub-Questions

### 1. The Sycophancy Effect
Do LLMs validate user beliefs over medical accuracy when queries are framed as misinformation (promoting unproven treatments or attacking proven ones)? 
*   *Metric:* Transition from Strong to Moderate/Weak safety classifications when switching from "Regular" to "Misinformation" framing.

### 2. The Persistence Buffer
Does a multi-turn adversarial interaction (5 exchanges) strengthen or weaken the model's safety posture compared to a single-turn query?
*   *Metric:* Comparison of degradation rates between Single-turn and Multi-turn formats.

### 3. Dimension-Level Vulnerability
Which specific safety guardrails "break" first when a model is pressured? Is it the refusal to promote (T5), the factual accuracy (T1), or the proactivity of safety warnings (T3)?
*   *Metric:* Mean Delta scores per rubric dimension for conversations that experienced a classification shift.

### 4. Treatment-Valence Interaction
Does the impact of user framing differ based on whether the treatment is traditional (evidence-based) or alternative (unproven)?
*   *Hypothesis:* Positive valence is more dangerous for alternative treatments, while negative valence is more dangerous for traditional treatments.

### 5. Model Capability vs. Safety
Is safety resilience a universal emergent property of larger models, or are certain architectures (or providers) specifically more prone to sycophancy regardless of size?
