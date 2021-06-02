from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import re
from enum import Enum, IntEnum
import validators

app = Flask(__name__)


user_info = {}

user_data = {}

INTRO_VIDEO = "intro_video"
SNAP_SHOT = "snap_shot"
NAME = "Name"
BIRTH_YEAR = "birth_year"
ETHINICITY = "Ethinicity"
GENDER = "Gender"
LOCATION = "Location"
STATE = "state"
ASK_SATATE_VALUE = "ask_state_value"


class State(Enum):
    ASK_USER_DATA = 1
    ASK_HEAD_SHOT = 2
    HEAD_SHOT_RECEIVED = 3
    ASK_INTRO_VIDEO = 4
    INTRO_VIDEO_RECEIVED = 5
    WORK_REEL_RECEIVED = 6

GREET = "Hello! Welcome to Anti-Casting\nThis is an automated service to register your details.\nTo register "
ASK_DETAIL_START = " "
ASK_NAME = "please enter your full name [Firstname LastName] e.g Manoj Kumar"
ASK_GENDER = "Enter your gender [M/F/O]"
ASK_BIRTH_YEAR = "Year of Birth [XXXX]"
ASK_ETHINICITY = "Ethnicity [State of origin] e.g. Odisha"
ASK_LOCATION = "Current Location - [City] e.g. Bhopal"
ASK_IMAGE = "Submit a Headshot"
ASK_VIDEO = "Submit a Intro Video"
ASK_DETAIL_END = "Thank you for submitting your profile"

ASK_FOR_UPDATE = "Your profile is already registered, please enter\n"
ASK_FOR_UPDATE += "1 to update Name\n2 to update Birth Year\n3 to update Ethinicity\n"
ASK_FOR_UPDATE += "4 to update Location\n5 to update Headshot\n6 to update Intro Video"

ask_dict = {
    1: GREET + ASK_NAME,
    2: ASK_GENDER,
    3: ASK_BIRTH_YEAR,
    4: ASK_ETHINICITY,
    5: ASK_LOCATION,
    6: ASK_IMAGE,
    7: ASK_VIDEO,
    8: ASK_FOR_UPDATE
}

update_dict = {
    1: ASK_NAME,
    2: ASK_BIRTH_YEAR,
    3: ASK_ETHINICITY,
    4: ASK_LOCATION,
    5: ASK_IMAGE,
    6: ASK_VIDEO
}

class AskState(IntEnum):
    say_hi = 1
    ask_name = 1 << 1
    ask_gender = 1 << 2
    ask_birth_year = 1 << 3
    ask_ethinicity = 1 << 4
    ask_location = 1 << 5
    ask_headshot_image = 1 << 6
    ask_intro_video = 1 << 7

class UserData:
    def __init__(self):
        self.name = ""
        self.gender = ""
        self.birth_year = ""
        self.ethinicity = ""
        self.location = ""
        self.headshot_image = ""
        self.intro_video = ""
        self.ask_state = 1

def is_valid_url(url_data):
    return validators.url(url_data)


def ask_from_user(sender_number):
    ask_statement = ""
    if sender_number not in user_data:
        user_data[sender_number] = UserData()
    ask_state = user_data[sender_number].ask_state
    if ask_state <= 7:
        ask_statement = ask_dict[ask_state]
    return ask_statement

def check_user_from_database(sender_number):
    return False

def decide_on_message(sender_number, msg):
    reply = ""
    user_present = check_user_from_database(sender_number)
    if msg.lower() == "hi" or msg.lower() == "hello" or msg.lower() == "hey":
        # check mobile no. in data base if not present then go from fresh registraton
        # else ask for what he wants to update
        if not user_present:
            reply = ask_from_user(sender_number)
        else:

    return reply

def add_data_to_user_info(sender_number, data):
    for info in data:
        if sender_number not in user_info:
            user_info[sender_number] = {}

        infos = info.split(":")
        if infos[0].strip(" ") == NAME:
            user_info[sender_number].update({NAME: infos[1].strip(" ")})
        elif infos[0].strip(" ") == BIRTH_YEAR:
            user_info[sender_number].update({BIRTH_YEAR: infos[1].strip(" ")})
        elif infos[0].strip(" ") == ETHINICITY:
            user_info[sender_number].update({ETHINICITY: infos[1].strip(" ")})
        elif infos[0].strip(" ") == GENDER:
            user_info[sender_number].update({GENDER: infos[1].strip(" ")})
        elif infos[0].strip(" ") == LOCATION:
            user_info[sender_number].update({LOCATION: infos[1].strip(" ")})


def is_user_data_present(sender_number):
    if sender_number in user_info:
        if NAME in user_info[sender_number]:
            return True
    else:
        return False


def is_data_type_present(sender_number, data):
    present = False
    if sender_number in user_info:
        if data in user_info[sender_number]:
            present = True
    return present


def get_user_data_type(sender_number, data_type):
    state_data = None
    if sender_number in user_info:
        if data_type in user_info[sender_number]:
            state_data = user_info[sender_number][data_type]

    return state_data


def insert_user_data_type(sender_number, data_type, data):
    if sender_number not in user_info:
        user_info[sender_number] = {}
    user_info[sender_number].update({data_type: data})


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/sms", methods=["POST"])
def sms_reply():
    """Respond to incoming calls with a simple text message."""
    # Fetch the message
    msg = request.form.get("Body")
    sender_name = request.form.get("ProfileName")
    sender_number = request.form.get("WaId")
    media_url = request.form.get("MediaUrl0")
    print(f"media_url: {media_url}")

    media_content_type = request.form.get("MediaContentType0")

    print("$$$$$ request.form $$$$$")
    print(request.form)
    print("$$$$$ request.form end $$$$$")

    # Create reply
    resp = MessagingResponse()
    response = ""
    pattern = r"(Name[ ]*:[ ]*[A-Z|a-z|_|+| ]+)[ ]*,[ ]*(Age[ ]*:[ ]*[0-9]{1,2})[ ]*,[ ]*(Ethinicity[ ]*:[ ]*[A-Z|a-z|_|+ ]+)[ ]*,[ ]*(Gender[ ]*:[ ][m|M|f|F|o|O]),[ ]*(Location[ ]*:[ ]*[A-Z|a-z|_|+| ]+)"
    media_file = ""

    # greet_from_user = False
    if msg.lower() == "hi" or msg.lower() == "hello" or msg.lower() == "hey":
        response = f"*Hi! {sender_name}, Welcome to Anticasting*\n\n"
        response += "Please text your details like following format:\n----------------------------------------------------------\n"
        response += f"Name: {sender_name}, Age: <age in years>, Ethinicity: <State you belongs to>, Gender: <m/f/o>, Location: <Current city/town>\n"
        response += ("\n*As an example below:*\n"
                    + f"Name: Mohan Kumar, Age: 23, Ethinicity: Maharashtra, Gender: m, Location: Pune\n\n"
                    + "*Note:* For *male* type *m*, for female type *f* and for *other* type *o*"
        )
        # greet_from_user = True
        insert_user_data_type(sender_name, STATE, State.ASK_USER_DATA)

    elif get_user_data_type(sender_name, STATE) == State.ASK_USER_DATA:
        if re.match(pattern, msg):
            match = re.search(pattern, msg).groups()
            if len(match) != 5:
                response = (
                    "Please text your details in proper format like following example:\n"
                    + "----------------------------------------------------------------\n"
                    + f"*Name: Mohan Kumar, Age: 23, Ethinicity: Maharashtra, Gender: m, Location: Pune*\n\n"
                    + "*Note:* For *male* type *m*, for female type *f* and for *other* type *o*"
                )
            else:
                add_data_to_user_info(sender_number, match)
                response = "Please attach your head shot image like below:\n"
                media_file = ""  # add headshot file path
                insert_user_data_type(sender_name, STATE, State.ASK_HEAD_SHOT)
        else:
            response = (
                "Please text your details in proper format like following example:\n"
                + "----------------------------------------------------------------\n"
                + f"*Name: Mohan Kumar, Age: 23, Ethinicity: Maharashtra, Gender: m, Location: Pune*\n\n"
                + "*Note:* For *male* type *m*, for female type *f* and for *other* type *o*"
            )

    elif get_user_data_type(sender_name, STATE) == State.ASK_HEAD_SHOT and media_content_type == "image/jpeg":
        response = "Please attach your intro video like attached sample or send youtube link of intro video"
        media_file = ""  # add intro sample file path
        insert_user_data_type(sender_name, STATE, State.ASK_INTRO_VIDEO)

    elif get_user_data_type(sender_name, STATE) == State.ASK_INTRO_VIDEO and media_content_type == "video/mp4":
        response = 'You can text your other work reel in youtube or\ncan text "Bye" to complete submission'
        insert_user_data_type(sender_name, STATE, State.INTRO_VIDEO_RECEIVED)
    elif is_valid_url(msg):
        response = 'You can text more work reel in youtube or\ncan text "Bye" to complete submission'
        insert_user_data_type(sender_name, STATE, State.WORK_REEL_RECEIVED)
    ########### Response start
    if (
        get_user_data_type(sender_name, STATE) == State.ASK_USER_DATA
        or is_valid_url(msg)
        or (msg.lower() != "bye" and get_user_data_type(sender_name, STATE) == State.WORK_REEL_RECEIVED)
        or (msg.lower() != "bye" and get_user_data_type(sender_name, STATE) == State.INTRO_VIDEO_RECEIVED)
    ):
        resp.message(response)
    elif (
        get_user_data_type(sender_name, STATE) == State.ASK_HEAD_SHOT
        or get_user_data_type(sender_name, STATE) == State.ASK_INTRO_VIDEO
    ):
        resp.message(response)
        # resp.message(response).media(media_file)
    elif msg.lower() == "bye" and (
        get_user_data_type(sender_name, STATE) == State.INTRO_VIDEO_RECEIVED
        or get_user_data_type(sender_name, STATE) == State.WORK_REEL_RECEIVED
    ):
        resp.message(f"Thanks {sender_name}! to submit your profile\nFor more info please visit anticating.in")
    else:
        resp.message(
            f'Hi {sender_name}!,\nHow I can help you?\nTo submit profile please text "Hi" here\nFor more info please visit anticating.in'
        )

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
