from fastapi import FastAPI
from pydantic import BaseModel
from googlenewsdecoder import gnewsdecoder

app = FastAPI()

class DecodeRequest(BaseModel):
    url: str

@app.post("/decode")
def decode_google_news(req: DecodeRequest):
    fallback_url = req.url.strip() if req.url else ""

    result = {
        "status": "fallback",
        "decoded_url": fallback_url,
        "fallback_url": fallback_url,
        "error": ""
    }

    if not fallback_url:
        result["error"] = "empty_url"
        return result

    try:
        if "news.google.com" not in fallback_url:
            result["status"] = "not_google_news"
            result["decoded_url"] = fallback_url
            return result

        decoded = gnewsdecoder(fallback_url, interval=1)

        if isinstance(decoded, dict):
            decoded_url = decoded.get("decoded_url") or ""
            status = decoded.get("status")
            message = decoded.get("message") or ""

            if status and decoded_url and "news.google.com" not in decoded_url:
                result["status"] = "resolved"
                result["decoded_url"] = decoded_url
                result["error"] = ""
                return result

            result["error"] = message or "decode_failed"
            return result

        result["error"] = "invalid_decoder_response"
        return result

    except Exception as e:
        result["status"] = "fallback"
        result["error"] = str(e)
        return result

@app.get("/")
def health_check():
    return {"status": "ok"}
