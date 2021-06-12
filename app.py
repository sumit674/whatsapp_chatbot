from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import re
from enum import Enum, IntEnum
import validators

# from paramiko import SSHClient
# from scp import SCPClient

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

HANDLE_ANY_TXT = "Hello! Welcome to Anti-Casting\nThis is an automated service to register your details.\nText \"Hi\" to register"
GREET = "Hello! Welcome to Anti-Casting\nThis is an automated service to register your details.\nYour registration starts:\n "
ASK_DETAIL_START = " "
ASK_NAME = "Please enter your full name [Firstname LastName] e.g Manoj Kumar"
ASK_GENDER = "Enter your gender [M/F/O]"
ASK_VALID_GENDER = "Enter gender like [M/F/O]"
ASK_BIRTH_YEAR = "Year of Birth [XXXX]"
ASK_VALID_BIRTH_YEAR = "Enter Year of Birth like [XXXX] e.g 1984"
ASK_ETHINICITY = "Ethnicity [State of origin] e.g. Odisha"
ASK_LOCATION = "Current Location - [City] e.g. Bhopal"
ASK_IMAGE = "Submit a Headshot like above"
ASK_VIDEO = "Submit a Intro Video like below:\nhttp://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4"
# ASK_VIDEO = "Submit a Intro Video:\n"
DATA_SUBMITTED = "Thank you for submitting your profile\nYou are registered with Anti-Casting\nTo get more details plz visit www.anticasting.in"

ALREADY_REGISTERED = "Your profile is already registered "

ASK_FOR_UPDATE = "please enter\n"
ASK_FOR_UPDATE += "0 if update done\n1 to update Name\n2 to update gender\n3 to update Birth Year\n4 to update Ethinicity\n"
ASK_FOR_UPDATE += "5 to update Location\n6 to update Headshot\n7 to update Intro Video\nEnter *OK* to submit"

ask_dict = {
    1: ASK_NAME,
    2: ASK_GENDER,
    3: ASK_BIRTH_YEAR,
    4: ASK_ETHINICITY,
    5: ASK_LOCATION,
    6: ASK_IMAGE,
    7: ASK_VIDEO,
    9: DATA_SUBMITTED,
    10: ASK_FOR_UPDATE
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
    ask_name = 1
    ask_gender = 2
    ask_birth_year = 3
    ask_ethinicity = 4
    ask_location = 5
    ask_headshot_image = 6
    ask_intro_video = 7
    confirm_data = 8
    data_submitted = 9
    ask_for_update = 10

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
        self.wrong_entry = 0
        self.update_state = False

def is_valid_url(url_data):
    return validators.url(url_data)

def is_valid_birth_year(year):
    if re.match(r"^[ ]*[0-9]{4}[ ]*$", year):
        return True
    else:
        return False


def ask_from_user(sender_number):
    ask_statement = GREET
    if sender_number not in user_data:
        user_data[sender_number] = UserData()
    ask_state = user_data[sender_number].ask_state
    if ask_state <= int(AskState.ask_intro_video):
        ask_statement += "1/7: "+ ask_dict[ask_state]
    return ask_statement

def valid_name_check(name):
    single_name_re = r"^[ ]*[a-z|A-Z]+[ ]*$"
    full_name_re = r"^[ ]*[a-z|A-Z]+[ ]+[a-z|A-Z]+[ ]*$"
    if re.match(full_name_re, name):
        return True, ""
    elif re.match(single_name_re, name):
        return False, "Please enter [Firstname LastName]"
    else:
        return False, "Please enter [Firstname LastName]"


def confirm_data(sender_number):
    #confirm data
    reply = "Enter *1* to submit and *2* to edit:\nFollowing are your data:\n"
    data = user_data[sender_number]
    reply += "Name: " + data.name +"\n"
    reply += "Gender: " + data.gender +"\n"
    reply += "Birth Year: " + data.birth_year +"\n"
    reply += "Ethinicity: " + data.ethinicity +"\n"
    reply += "Location: " + data.location

    return reply

def save_to_database(sender_number):
    data = user_data[sender_number]
    # connect to my sql and save data

def update_sender_data(sender_number, msg):
    reply = ""
    if msg == "0":
        user_data[sender_number].update_state = False
        reply = confirm_data(sender_number)
        user_data[sender_number].ask_state = AskState.confirm_data
    elif msg == "1":
        user_data[sender_number].ask_state = AskState.ask_name
        reply = ASK_NAME
    elif msg == "2":
        pass
    elif msg == "3":
        pass
    elif msg == "4":
        pass
    elif msg == "5":
        pass
    elif msg == "6":
        pass
    elif msg == "7":
        pass
    elif msg.lower() == "ok":
        pass

    return reply


def update_user_data(sender_number, ask_state, msg):
    reply = ""
    if ask_state == AskState.ask_name and not user_data[sender_number].update_state:
        is_name_valid, reply = valid_name_check(msg)
        if is_name_valid:
            user_data[sender_number].name = msg
            user_data[sender_number].ask_state = AskState.ask_gender
            reply = "2/7: "
            reply += ask_dict[int(user_data[sender_number].ask_state)]
    elif ask_state == AskState.ask_gender and not user_data[sender_number].update_state:
        if msg == "M" or msg == "m" or msg == "f" or msg == "f" or msg == "o" or msg == "O":
            user_data[sender_number].gender = msg
            user_data[sender_number].ask_state = AskState.ask_birth_year
            reply = "3/7: "
            reply += ask_dict[int(user_data[sender_number].ask_state)]
        else:
            reply = ASK_VALID_GENDER
    elif ask_state == AskState.ask_birth_year and not user_data[sender_number].update_state:
        if is_valid_birth_year(msg):
            user_data[sender_number].birth_year = msg
            user_data[sender_number].ask_state = AskState.ask_ethinicity
            reply = "4/7: "
            reply += ask_dict[int(user_data[sender_number].ask_state)]
        else:
            reply = ASK_VALID_BIRTH_YEAR
    elif ask_state == AskState.ask_ethinicity and not user_data[sender_number].update_state:
        user_data[sender_number].ethinicity = msg
        user_data[sender_number].ask_state = AskState.ask_location
        reply = "5/7: "
        reply += ask_dict[int(user_data[sender_number].ask_state)]
    elif ask_state == AskState.ask_location and not user_data[sender_number].update_state:
        user_data[sender_number].location = msg
        user_data[sender_number].ask_state = AskState.ask_headshot_image
        reply = "6/7: "
        reply += ask_dict[int(user_data[sender_number].ask_state)]
    elif ask_state == AskState.ask_headshot_image and not user_data[sender_number].update_state:
        user_data[sender_number].headshot_image = msg
        user_data[sender_number].ask_state = AskState.ask_intro_video
        reply = "7/7: "
        reply += ask_dict[int(user_data[sender_number].ask_state)]
    elif ask_state == AskState.ask_intro_video and not user_data[sender_number].update_state:
        user_data[sender_number].intro_video = msg
        reply = confirm_data(sender_number)
        user_data[sender_number].ask_state = AskState.confirm_data
    elif ask_state == AskState.confirm_data and not user_data[sender_number].update_state:
        reply = ""
        if msg == "1":
            save_to_database(sender_number)
            user_data[sender_number].ask_state = AskState.data_submitted
            reply = ask_dict[int(user_data[sender_number].ask_state)]
        else:
            user_data[sender_number].ask_state = AskState.ask_for_update
            reply = ask_dict[int(user_data[sender_number].ask_state)]
            user_data[sender_number].update_state = True
    elif ask_state == AskState.ask_for_update and user_data[sender_number].update_state:
        reply = update_sender_data(sender_number, msg)
        if not reply:
            reply = ask_dict[int(user_data[sender_number].ask_state)]

    return reply


def check_user_from_database(sender_number):
    return False


def check_user_message(sender_number, msg):
    reply = ""
    if sender_number in user_data:
        ask_state = user_data[sender_number].ask_state
        if int(ask_state) >= 1 and int(ask_state) <= 10:
            reply = update_user_data(sender_number, ask_state, msg)
    else:
        reply = HANDLE_ANY_TXT

    return reply


def decide_on_message(sender_number, msg):
    reply = ""
    user_present = check_user_from_database(sender_number)
    if msg.lower() == "hi" or msg.lower() == "hello" or msg.lower() == "hey":
        # check mobile no. in data base if not present then go from fresh registraton
        # else ask for what he wants to update
        if not user_present:
            reply = ask_from_user(sender_number)
        else:
            pass
    else:
        reply = check_user_message(sender_number, msg)

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
    # if msg.lower() == "hi" or msg.lower() == "hello" or msg.lower() == "hey":
    #     response = f"*Hi! {sender_name}, Welcome to Anticasting*\n\n"
    #     response += "Please text your details like following format:\n----------------------------------------------------------\n"
    #     response += f"Name: {sender_name}, Age: <age in years>, Ethinicity: <State you belongs to>, Gender: <m/f/o>, Location: <Current city/town>\n"
    #     response += ("\n*As an example below:*\n"
    #                 + f"Name: Mohan Kumar, Age: 23, Ethinicity: Maharashtra, Gender: m, Location: Pune\n\n"
    #                 + "*Note:* For *male* type *m*, for female type *f* and for *other* type *o*"
    #     )
    #     # greet_from_user = True
    #     insert_user_data_type(sender_name, STATE, State.ASK_USER_DATA)

    # elif get_user_data_type(sender_name, STATE) == State.ASK_USER_DATA:
    #     if re.match(pattern, msg):
    #         match = re.search(pattern, msg).groups()
    #         if len(match) != 5:
    #             response = (
    #                 "Please text your details in proper format like following example:\n"
    #                 + "----------------------------------------------------------------\n"
    #                 + f"*Name: Mohan Kumar, Age: 23, Ethinicity: Maharashtra, Gender: m, Location: Pune*\n\n"
    #                 + "*Note:* For *male* type *m*, for female type *f* and for *other* type *o*"
    #             )
    #         else:
    #             add_data_to_user_info(sender_number, match)
    #             response = "Please attach your head shot image like below:\n"
    #             media_file = ""  # add headshot file path
    #             insert_user_data_type(sender_name, STATE, State.ASK_HEAD_SHOT)
    #     else:
    #         response = (
    #             "Please text your details in proper format like following example:\n"
    #             + "----------------------------------------------------------------\n"
    #             + f"*Name: Mohan Kumar, Age: 23, Ethinicity: Maharashtra, Gender: m, Location: Pune*\n\n"
    #             + "*Note:* For *male* type *m*, for female type *f* and for *other* type *o*"
    #         )

    # elif get_user_data_type(sender_name, STATE) == State.ASK_HEAD_SHOT and media_content_type == "image/jpeg":
    #     response = "Please attach your intro video like attached sample or send youtube link of intro video"
    #     media_file = ""  # add intro sample file path
    #     insert_user_data_type(sender_name, STATE, State.ASK_INTRO_VIDEO)

    # elif get_user_data_type(sender_name, STATE) == State.ASK_INTRO_VIDEO and media_content_type == "video/mp4":
    #     response = 'You can text your other work reel in youtube or\ncan text "Bye" to complete submission'
    #     insert_user_data_type(sender_name, STATE, State.INTRO_VIDEO_RECEIVED)
    # elif is_valid_url(msg):
    #     response = 'You can text more work reel in youtube or\ncan text "Bye" to complete submission'
    #     insert_user_data_type(sender_name, STATE, State.WORK_REEL_RECEIVED)
    ########### Response start
    # if (
    #     get_user_data_type(sender_name, STATE) == State.ASK_USER_DATA
    #     or is_valid_url(msg)
    #     or (msg.lower() != "bye" and get_user_data_type(sender_name, STATE) == State.WORK_REEL_RECEIVED)
    #     or (msg.lower() != "bye" and get_user_data_type(sender_name, STATE) == State.INTRO_VIDEO_RECEIVED)
    # ):
    #     resp.message(response)
    # elif (
    #     get_user_data_type(sender_name, STATE) == State.ASK_HEAD_SHOT
    #     or get_user_data_type(sender_name, STATE) == State.ASK_INTRO_VIDEO
    # ):
    #     resp.message(response)
    #     # resp.message(response).media(media_file)
    # elif msg.lower() == "bye" and (
    #     get_user_data_type(sender_name, STATE) == State.INTRO_VIDEO_RECEIVED
    #     or get_user_data_type(sender_name, STATE) == State.WORK_REEL_RECEIVED
    # ):
    #     resp.message(f"Thanks {sender_name}! to submit your profile\nFor more info please visit anticating.in")
    # else:
    #     resp.message(
    #         f'Hi {sender_name}!,\nHow I can help you?\nTo submit profile please text "Hi" here\nFor more info please visit anticating.in'
    #     )


    if sender_number in user_data:
        print("user_data[sender_number].ask_state")
        print(user_data[sender_number].ask_state)
    response = decide_on_message(sender_number, msg)
    res = resp.message(response)
    if sender_number in user_data and user_data[sender_number].ask_state == AskState.ask_headshot_image:
        res.media("https://images.unsplash.com/photo-1518717758536-85ae29035b6d?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80")
    # elif sender_number in user_data and user_data[sender_number].ask_state == AskState.ask_intro_video:
    #     print("########$$$$$$$$$$$$$$$$$$$$$$$$$888888888888888888")
    #     res.media_url("http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4")
    print(resp)
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
