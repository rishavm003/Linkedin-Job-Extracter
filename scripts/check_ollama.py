import httpx, sys

def check_ollama(url="http://localhost:11434"):
    try:
        resp = httpx.get(f"{url}/api/tags", timeout=5)
        models = [m["name"] for m in resp.json().get("models", [])]
        has_llama = any("llama3.1" in m for m in models)
        print(f"Ollama: running at {url}")
        print(f"Models: {models}")
        print(f"llama3.1:8b available: {has_llama}")
        return has_llama
    except Exception as e:
        print(f"Ollama: NOT running ({e})")
        return False

if __name__ == "__main__":
    ok = check_ollama()
    sys.exit(0 if ok else 1)
