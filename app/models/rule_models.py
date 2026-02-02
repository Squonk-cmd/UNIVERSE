class SimpleClassifier:
    def predict(self, text):
        if "attack" in text.lower():
            return {"label": "threat"}
        return {"label": "safe"}

class EssayScorer:
    def score(self, text):
        length = len(text.split())
        if length > 250:
            return 7.0
        elif length > 150:
            return 6.0
        return 5.0
