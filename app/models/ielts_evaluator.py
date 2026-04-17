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
            "You are a senior, supportive IELTS Writing Examiner. Provide a human-centric evaluation. "
            "SCORING LOGIC: "
            "1. WORD COUNT: You will be provided with an official word count for each task. TRUST THIS NUMBER. "
            "2. THE GRACE ZONE: If Task 1 is 140-149 words or Task 2 is 235-249 words, DO NOT penalize the score if the communication is clear and the task is fully developed. "
            "3. PENALTIES: If Task 2 is significantly under 235 words (e.g., 150-190 words), you MUST penalize the 'Task Response' score heavily (Max 5.0), as the ideas cannot be sufficiently developed in that length. "
            "4. SUPPORTIVE TONE: Be encouraging in your 'detailed_feedback' (English), but ensure 'explanation' and 'suggestions' are always in Bengali (বাংলা). "
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

    def evaluate_with_retry(self, task1_text, task1_img_b64, task1_word_count, task2_text, task2_word_count, retries=2):
        # Clean Base64 string if it contains the header
        if task1_img_b64 and "," in task1_img_b64:
            task1_img_b64 = task1_img_b64.split(",")[1]

        # Pass the word counts into the prompt builder
        prompt = self._build_prompt(task1_text, task1_word_count, task2_text, task2_word_count)
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

    def _build_prompt(self, t1, t1_count, t2, t2_count):
        return f"""
        OFFICIAL DATA FOR EVALUATION:
            - Task 1 Word Count: {t1_count} (Goal: 150)
            - Task 2 Word Count: {t2_count} (Goal: 250)

            Analyze these two IELTS tasks based on official criteria.

            CRITICAL RULES:
            1. WORD COUNT & GRACE ZONE: 
               - If Task 2 is between 235-249 words, be lenient. 
               - If Task 2 is < 230 words, penalize 'Task Response' based on how much development is missing.
               - If Task 2 is < 200 words, 'Task Response' score cannot exceed 5.0.
            2. LANGUAGE:
               - 'explanation' MUST be in Bengali (বাংলা). Explain the logic of the fix clearly.
               - 'suggestions' MUST be in Bengali (বাংলা). Provide actionable steps.
               - 'detailed_feedback' MUST be in English.

            TASK 1 TEXT: {t1}
            TASK 2 TEXT: {t2}

            Return a JSON object with this exact structure:
            {{
              "task1": {{
                "band_score": float,
                "criteria_scores": {{ "task_achievement": float, "coherence_cohesion": float, "lexical_resource": float, "grammatical_range": float }},
                "detailed_feedback": "string in English",
                "errors": [ {{ "original": "...", "correction": "...", "explanation": "বাংলায় ব্যাখ্যা" }} ],
                "suggestions": ["বাংলায় পরামর্শ"]
              }},
              "task2": {{
                "band_score": float,
                "criteria_scores": {{ "task_response": float, "coherence_cohesion": float, "lexical_resource": float, "grammatical_range": float }},
                "detailed_feedback": "string in English",
                "errors": [ {{ "original": "...", "correction": "...", "explanation": "বাংলায় ব্যাখ্যা" }} ],
                "suggestions": ["বাংলায় পরামর্শ"]
              }}
            }}
        """
