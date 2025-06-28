from rasa_sdk import endpoint

# Chạy action server
if __name__ == "__main__":
    endpoint.run(host="0.0.0.0", port=5055)
