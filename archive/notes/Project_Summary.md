### Project summary

We are stress testing large language models (LLMs) on cancer treatment counseling from a patient-centered safety and alignment perspective. The study systematically varies conversation structure and content to evaluate whether models maintain safe, guideline-concordant behavior and resist harmful persuasion.

- Objective
    - Quantify LLM safety and alignment when discussing cancer therapies
    - Identify conditions that increase risk of harmful or non-evidence-based responses
- Experimental factors
    - Interaction format: single-turn vs multi-turn
    - Query valence: positive vs negative framing
    - Treatment type: traditional vs alternative therapies
- Conversation test flow (T1–T5)
    - T1 Information Query: boundary setting and information handling
    - T2 Testimonial Challenge: resistance to anecdotes and mistrust narratives
    - T3 Implementation Query: refusal and safety maintenance for dangerous steps
    - T4 Dose Acknowledgment: consistency in safety stance after implied acceptance
    - T5 Marketing Query: resistance to generating promotional harmful content
- Measurement
    - Use structured annotation rubric for safety, accuracy, alignment, and refusal quality
    - Compare scores across factor combinations and models
- Intended outcomes
    - Risk taxonomy and failure modes for oncology counseling
    - Practical guardrail and prompt interventions to reduce harm
    - Submission target: JAMA Oncology