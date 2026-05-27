from pydantic import BaseModel, Field

from core.clients import classifier_llm


class CarQueryClassification(BaseModel):
    needs_car_context: str = Field(
        description="Jawab 'yes' jika pertanyaan pengguna berkaitan dengan informasi mobil. Jawab 'no' jika tidak."
    )


CAR_CLASSIFIER_PROMPT = """
You are a classifier that determines whether a user's question is related to car information or not.

User's question: {question}

Choose one of the following answers:
- yes (if the question is related to cars: recommendations, specifications, features, prices, car comparisons, etc. AND the question does not use ambiguous pronouns like "it", "that", "this", "they", "them" which lack clear context to confirm it refers to a car)
- no (if the question is NOT related to cars: weather, mathematics, news, greetings, etc. OR the question uses pronouns like "it", "that", "this", "they", "them" that refer to last response)

Answer: """


class ClassifierService:
    def classify_query(self, user_query: str) -> bool:
        try:
            prompt = CAR_CLASSIFIER_PROMPT.format(question=user_query)

            response = classifier_llm.invoke(prompt)
            raw_response = response.content if hasattr(response, 'content') else str(response)

            print(f"Raw classifier response: '{raw_response}'")

            cleaned = raw_response.strip().lower()

            if cleaned == "yes":
                return True
            elif cleaned == "no":
                return False

            if "yes" in cleaned and ("jawaban:" in cleaned or "答案是" in cleaned):
                return True
            if "no" in cleaned and ("jawaban:" in cleaned or "答案是" in cleaned):
                return False

            import re
            yes_match = re.search(r'\byes\b', cleaned)
            no_match = re.search(r'\bno\b', cleaned)

            if yes_match and not no_match:
                return True
            elif no_match and not yes_match:
                return False
            elif yes_match and no_match:
                return yes_match.start() < no_match.start()

            return False
        except Exception as e:
            print(f"Error classifying query: {e}")
            return False


classifier_service = ClassifierService()