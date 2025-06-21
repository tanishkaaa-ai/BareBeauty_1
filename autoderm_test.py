import base64
import requests
import json

# Step 1: Read and encode your image
with open("autoderm.jpg", "rb") as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

# Step 2: Set up API request
url = "http://autoderm.firstderm.com/v1/query"
headers = {
    "Authorization": "Bearer 1a92e8f9-58d2-4d64-50ac-cf796d03094a",  # Replace if needed
    "Content-Type": "application/json"
}
data = {
    "image": encoded_image
}

# Step 3: Send request to Autoderm API
response = requests.post(url, headers=headers, json=data)

# Step 4: Process the response
if response.status_code == 200:
    result = response.json()
    print("Diagnosis Result:")
    print(json.dumps(result, indent=4))  # Pretty print in terminal

    # Step 5: Save to a file
    with open("diagnosis_result.json", "w") as f:
        json.dump(result, f, indent=4)
    print("✅ Saved response to diagnosis_result.json")

else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)


# import requests

# try:
#     r = requests.get("https://www.google.com")
#     print("HTTPS Request to Google successful ✅")
# except Exception as e:
#     print("HTTPS Request failed ❌")
#     print(e)


