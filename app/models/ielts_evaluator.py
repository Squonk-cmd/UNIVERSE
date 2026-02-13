import os
import json
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class IELTSEvaluator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDXfw9eGeYkT8dE5oiXaRF7Fy7TAFGnzKE")
        genai.configure(api_key=api_key)
        
        system_instruction = (
            "You are a senior, supportive IELTS Writing Examiner. Provide a human-centric evaluation. "
            "Be lenient and favor the higher half-band if the communication is clear. "
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
        TASK 1 TEXT: {t1}
        TASK 2 TEXT: {t2}

        Return a JSON object with keys "task1" and "task2". 
        Inside the "errors" list for each task, you MUST provide objects with this exact structure:
        {{
            "original": "the exact text from the student's essay",
            "correction": "the improved/corrected version",
            "explanation": "why it was wrong and the grammatical rule involved"
        }}

        JSON Schema:
        {{
          "task1": {{
            "band_score": float,
            "criteria_scores": {{ "task_achievement": float, "coherence_cohesion": float, "lexical_resource": float, "grammatical_range": float }},
            "detailed_feedback": "string",
            "errors": [ {{ "original": "...", "correction": "...", "explanation": "..." }} ],
            "suggestions": ["string"]
          }},
          "task2": {{
            "band_score": float,
            "criteria_scores": {{ "task_response": float, "coherence_cohesion": float, "lexical_resource": float, "grammatical_range": float }},
            "detailed_feedback": "string",
            "errors": [ {{ "original": "...", "correction": "...", "explanation": "..." }} ],
            "suggestions": ["string"]
          }}
        }}
        """