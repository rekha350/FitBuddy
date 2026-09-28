from functools import lru_cache

from google import genai
from google.genai import types

from app.config import get_settings


class GeminiService:
    """
    Central service for all Gemini operations.
    """

    def __init__(self):

        settings = get_settings()

        if not settings.gemini_api_key:

            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Create a .env file and add your Gemini API key."
            )

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        self.workout_model = settings.workout_model

        self.nutrition_model = settings.nutrition_model

    def _generate(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 5000,
    ) -> str:

        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=max_tokens,
            ),
        )

        text = response.text

        if not text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return text.strip()

    def generate_workout(
        self,
        *,
        name: str,
        age: int,
        weight: float,
        goal: str,
        intensity: str,
    ) -> str:

        prompt = f"""
You are FitBuddy, an AI fitness planning assistant.

Create a practical personalized 7-day workout plan.

User information:

Name: {name}
Age: {age}
Weight: {weight} kg
Fitness goal: {goal}
Workout intensity: {intensity}

The plan must contain exactly seven labeled days.

For every day include:

1. Day name
2. Workout focus
3. Warm-up lasting approximately 5-10 minutes
4. Main workout
5. Exercise names
6. Sets and repetitions or duration
7. Suggested rest periods
8. Cool-down or recovery guidance

Include at least one recovery/rest-focused day.

The intensity must match the requested intensity.

The plan should be practical for a general adult user and should not prescribe
dangerous extreme exercise.

Do not diagnose medical conditions.

Do not prescribe medications.

Do not prescribe medical treatment.

Do not recommend dangerous training practices.

At the end include this safety guidance:

"Safety note: This is general wellness information, not medical advice.
If you have an injury, medical condition, are pregnant, or experience
concerning symptoms, consult an appropriate qualified professional before
starting or modifying an exercise program."

Return plain text.

Do not return JSON.

Do not use a markdown table.
"""

        return self._generate(
            model=self.workout_model,
            prompt=prompt,
            max_tokens=6000,
        )

    def generate_nutrition_tip(
        self,
        *,
        goal: str,
    ) -> str:

        prompt = f"""
You are FitBuddy's nutrition and recovery assistant.

Give one concise and practical nutrition or recovery recommendation
for a fitness user whose goal is:

{goal}

Keep the response between 3 and 5 sentences.

Focus on sustainable habits such as:

- hydration
- balanced meals
- adequate protein from ordinary foods
- fruits and vegetables
- sleep
- recovery

Do not diagnose medical conditions.

Do not prescribe medications.

Do not prescribe supplements as medical treatment.

Return plain text only.
"""

        return self._generate(
            model=self.nutrition_model,
            prompt=prompt,
            max_tokens=700,
        )

    def update_workout(
        self,
        *,
        original_plan: str,
        feedback: str,
        goal: str,
        intensity: str,
    ) -> str:

        prompt = f"""
You are FitBuddy's workout-plan revision assistant.

The user's fitness goal is:

{goal}

The requested workout intensity is:

{intensity}

Here is the ORIGINAL PLAN:

---------------- ORIGINAL PLAN ----------------

{original_plan}

---------------- END ORIGINAL PLAN ------------

Here is the USER FEEDBACK:

---------------- USER FEEDBACK -----------------

{feedback}

---------------- END USER FEEDBACK -------------

Create a complete revised 7-day workout plan.

Do not return a diff.

Return the entire revised plan.

Apply the user's feedback where it is safe and reasonable.

Keep the original fitness goal.

Keep the requested intensity.

If the user requests something unsafe, do not follow the unsafe portion.

The revised plan must include:

- seven labeled days
- workout focus
- warm-up
- exercises
- sets/repetitions or duration
- rest periods
- cooldown/recovery
- at least one recovery/rest-focused day

Do not diagnose medical conditions.

Do not prescribe medication.

Do not provide dangerous training recommendations.

At the end include:

"Safety note: This is general wellness information, not medical advice.
If you have an injury, medical condition, are pregnant, or experience
concerning symptoms, consult an appropriate qualified professional."

Return plain text only.

Do not return JSON.

Do not use a markdown table.
"""

        return self._generate(
            model=self.workout_model,
            prompt=prompt,
            max_tokens=6000,
        )


@lru_cache
def get_gemini_service() -> GeminiService:

    return GeminiService()