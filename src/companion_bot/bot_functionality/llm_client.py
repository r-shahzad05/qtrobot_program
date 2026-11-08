def generate_response(user_text, detected_emotion, conversation_history):
    #call api and get response

    # response = api call
    # emotion = api call

    match emotion:
        case "happy":
            qt_emotion = "QT/happy"
        case "sad":
            qt_emotion = "QT/sad"
        case "angry":
            qt_emotion = "QT/angry"
        case "suprised":
            qt_emotion = "QT/suprised"
        case "Confused":
            qt_emotion = "QT/confused"
        case "neutral":
            qt_emotion = "QT/neutral"
        case "concerned":
            qt_emotion = "QT/concerned"
        case _:
            qt_emotion = "invalid"


    return response, qt_emotion

