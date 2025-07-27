import requests

def test_tts():
    url = "http://localhost:8001/api/voice/tts"
    params = {'query': '你好，世界'}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        print("Test Passed: Received audio response.")
    else:
        print(f"Test Failed: Status code {response.status_code}")

if __name__ == "__main__":
    test_tts()