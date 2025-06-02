from rasa_sdk.endpoint import endpoint_app

# Chạy action server
if __name__ == "__main__":
    endpoint_app.run(host="0.0.0.0", port=5055)
