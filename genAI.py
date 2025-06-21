from google import genai

client = genai.Client(api_key="AIzaSyD__jBaACjvq-i0E9eX1XQusZZJEJoZD4U")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in a few words"
)
print(response.text)

