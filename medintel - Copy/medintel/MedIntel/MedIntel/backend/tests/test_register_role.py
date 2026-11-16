from app.schemas import RegisterRequest


def test_register_request_accepts_selected_role():
    payload = RegisterRequest(
        full_name="Dr. Jane Doe",
        email="jane@example.com",
        password="Password123",
        role="doctor",
    )

    assert payload.role == "doctor"
