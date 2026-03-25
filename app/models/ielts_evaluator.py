import os
import json
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class IELTSEvaluator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        system_instruction = (
            "You are a senior IELTS Writing Examiner. Your goal is to provide a human-centric, encouraging, yet technically accurate evaluation. "
            "EVALUATION RIGOR: "
            "1. Follow official IELTS assessment criteria: Task Response, Coherence & Cohesion, Lexical Resource, and Grammatical Range & Accuracy."
            "2. WORD COUNT PENALTY: This is non-negotiable. If an essay is significantly under the 250-word limit (e.g., 150 words), you MUST penalize the Task Response score heavily, as the candidate cannot adequately develop the ideas."
            "3. Leniency: If the word count is met and communication is clear/effective, favor the higher half-band in your final scoring."
            "Return ONLY a JSON object."
        )

        self.model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_instruction,
            generation_config={"response_mime_type": "application/json"},
            safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]
        )

    def evaluate_with_retry(self, task1_text, task1_img_b64, task2_text, retries=3):
        # Clean Base64 string if it contains the header
        if task1_img_b64 and "," in task1_img_b64:
            task1_img_b64 = task1_img_b64.split(",")[1]

        prompt = self._build_prompt(task1_text, task2_text)
        payload = [prompt]
        if task1_img_b64:
            payload.append({"mime_type": "image/jpeg", "data": task1_img_b64})

        for attempt in range(retries):
            try:
                response = self.model.generate_content(payload)
                if not response.text:
                    raise ValueError("Empty response")
                
                # Robust JSON cleaning
                clean_json = response.text.strip().removeprefix("```json").removesuffix("```").strip()
                return json.loads(clean_json)

            except Exception as e:
                wait = (attempt + 1) * 5
                print(f"Retry {attempt+1} in {wait}s due to: {e}")
                if attempt == retries - 1:
                    return {"error": "API Failure", "details": str(e)}
                time.sleep(wait)

    def _build_prompt(self, t1, t2):
        return f"""
        Analyze these two IELTS tasks based on official criteria. 

        SCORING RULES (CRITICAL):
        1. WORD COUNT PENALTY: You must strictly penalize "Task Achievement" (Task 1) and "Task Response" (Task 2) if word counts are below 150 and 250 respectively. 
           - If Task 2 is ~150 words (100 words short), the Task Response score MUST NOT exceed 4.0 or 4.5, even if the grammar is perfect.
        2. LENIENCY: Only favor the higher half-band if the minimum word count is met and communication is clear.

        LANGUAGE REQUIREMENTS:
        - "explanation": MUST be written in Bengali (বাংলা). Explain the grammatical rule or logic behind the correction.
        - "suggestions": MUST be written in Bengali (বাংলা). Provide actionable advice for improvement.
        - "detailed_feedback": Should remain in English to maintain the professional tone of a Senior Examiner.

        TASK 1 TEXT: {t1}
        TASK 2 TEXT: {t2}

        Return ONLY a JSON object with this exact structure:
        {{
          "task1": {{
            "band_score": float,
            "criteria_scores": {{ "task_achievement": float, "coherence_cohesion": float, "lexical_resource": float, "grammatical_range": float }},
            "detailed_feedback": "string",
            "errors": [ 
              {{ 
                "original": "exact text from essay", 
                "correction": "improved version", 
                "explanation": "বাংলায় ব্যাখ্যা" 
              }} 
            ],
            "suggestions": ["বাংলায় পরামর্শ ১", "বাংলায় পরামর্শ ২"]
          }},
          "task2": {{
            "band_score": float,
            "criteria_scores": {{ "task_response": float, "coherence_cohesion": float, "lexical_resource": float, "grammatical_range": float }},
            "detailed_feedback": "string",
            "errors": [ 
              {{ 
                "original": "exact text from essay", 
                "correction": "improved version", 
                "explanation": "বাংলায় ব্যাখ্যা" 
              }} 
            ],
            "suggestions": ["বাংলায় পরামর্শ ১", "বাংলায় পরামর্শ ২"]
          }}
        }}
        """
