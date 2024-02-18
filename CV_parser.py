import requests
import json

api_key = 'rEdxQj7vK8aN8hIAbBe2O70naQCXmgqY9WRMjnjG'
url = 'https://api.superparser.com/parse'
headers = {
    'accept': 'application/json',
    'X-API-Key': api_key,
}

file_path = 'Ilai_Av_Ron_CV.pdf'

files = {
    'file_name': ('Ilai_Av_Ron_CV.pdf', open(file_path, 'rb'), 'application/pdf'),
}

response = requests.post(url, headers=headers, files=files)

# Check if the request was successful
if response.status_code == 200:
    print("Success!")
    # Parse the JSON response
    parsed_data = response.json()
    # Output file path where you want to save the parsed resume data
    output_file_path = 'Ilai_Av_Ron_CV_Parsed.JSON'
    with open(output_file_path, 'w') as output_file:
        json.dump(parsed_data, output_file, indent=4)
    print(f"Parsed resume data saved to {output_file_path}")
else:
    print("Error:", response.status_code)
    print(response.text)  # This prints the error message, if any
