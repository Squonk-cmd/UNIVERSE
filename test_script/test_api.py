import requests
import base64
import json

def test_production_api():
    # 1. Load a sample image (ensure sample.png exists in your folder)
    try:
        with open("sample.png", "rb") as f:
            img_str = base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError:
        img_str = None
        print("Note: sample.png not found, testing without image.")

    payload = {
        "task1_text": "The graph shows changes in population...",
        "task1_image": img_str,
        "task2_text": "Some believe children should make their own decisions..."
    }

    print("Sending consolidated request to FastAPI...")
    response = requests.post("http://127.0.0.1:8000/analyze", json=payload)
    
    print("\n--- API RESPONSE ---")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_production_api()