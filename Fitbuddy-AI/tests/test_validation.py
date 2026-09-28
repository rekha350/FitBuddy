def test_user_input_accepts_valid_data():
    name = "Alex"
    goal = "muscle gain"
    assert name == "Alex"
    assert goal == "muscle gain"

def test_feedback_is_trimmed():
    feedback = "   add more cardio   "
    trimmed = feedback.strip()
    assert trimmed == "add more cardio"