from pact import Verifier

def test_provider():
    verifier = Verifier(
        provider="UserService",
        provider_base_url="http://localhost:5000"  # Update if your provider runs on a different port
    )

    verifier.verify_with_broker(
        broker_url="http://localhost:9292",
        publish_verification_results=True,
        provider_version="1.0.0"
    )

if __name__ == "__main__":
    test_provider()
