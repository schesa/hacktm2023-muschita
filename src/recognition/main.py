import requests

def search_image(image_path):
    # API endpoint URL
    url = "https://api.pimeyes.com/image"

    # Set request headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Referer": "https://pimeyes.com/",
        "Origin": "https://pimeyes.com"
    }

    # Read image file
    with open(image_path, "rb") as file:
        image_data = file.read()

    # Set the request payload with the image data
    files = {"file": image_data}

    # Send POST request to the Pimeyes API
    response = requests.post(url, headers=headers, files=files)

    # Check if the request was successful
    if response.status_code == 200:
        # Retrieve and return the JSON response
        return response.json()
    else:
        # Handle the error case
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Main program
if __name__ == "__main__":
    # Set the path to the image file you want to search
    image_path = "/Users/mihai/Dropbox/Screenshots/munteanu.png"

    # Perform image search
    result = search_image(image_path)

    # Print the result
    if result:
        print("Pimeyes search result:")
        print(result)
