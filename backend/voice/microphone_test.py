"""Hardware microphone diagnostic for Offspace."""


def test_microphone():
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        return {"status": "available", "devices": devices}
    except Exception as error:
        return {"status": "error", "message": str(error)}


if __name__ == "__main__":
    print(test_microphone())
