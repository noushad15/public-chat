# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Union
#
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa.core.tracker_store import InMemoryTrackerStore
from rasa_sdk.forms import FormAction
import re
import sqlite3
from zenpy import Zenpy
from zenpy import HelpCentreApi
from zenpy.lib.api_objects import Ticket, User, Comment

# credentials = {
#     'email': 'support@janets.org.uk',
#     'token': 'byzE7RaVkqPmhyNRZSlDIsZIZEJtqPx6v85U7NQa',
#     'subdomain': 'janets'
# }

credentials = {
    'email': 'noushad@staffasia.org',
    'token': 'BG5lCDpENaSANknx5VoADyCY3Sl3EFTuezkW49zw',
    'subdomain': 'staffasia17may'
}



class validate_initial_Form(FormValidationAction):
    def name(self) -> Text:
        return "validate_initial_Form"

    def validate_learner_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""

        # If the name is super short, it might be wrong.
        # print(f"First name given = {slot_value} length = {len(slot_value)}")
        if len(slot_value) <= 2:
            dispatcher.utter_message(text=f"That's a very short name. I'm assuming you mis-spelled.")
            return {"learner_name": None}
        else:
            return {"learner_name": slot_value}

    def validate_learner_email(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> Dict[Text, Any]:
        """Validate `last_name` value."""

        # If the name is super short, it might be wrong.
        # print(f"Last name given = {slot_value} length = {len(slot_value)}")
        pat = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

        if not re.search(pat, slot_value):
            dispatcher.utter_message(text=f"That's not a valid email address. I'm assuming you mis-spelled.")
            return {"learner_email": None}
        else:
            return {"learner_email": slot_value}

class ActionInitialForm(FormAction):

    def name(self) -> Text:
        return "initial_Form"

    # def slot_mappings(self):
    #     return {
    #         "learner_name": self.from_entity(entity="learner_name", intent="text"),
    #         "type": self.from_text(),
    #     }

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        print("required slots(tracker:Tracker)")
        return ["learner_name", "learner_email"]



class ActionSubmit(Action):
    def name(self) -> Text:
        return "Action_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> List[Dict[Text, Any]]:

        try:

            user_name = tracker.get_slot("learner_name")
            user_email = tracker.get_slot("learner_email")
            user_session = tracker.sender_id
            ticket = 0

            conn = sqlite3.connect('user.db')
            zenpy_client = Zenpy(**credentials)
            user_intent = ""
            newComment = zenpy_client.tickets.create(
                Ticket(description= user_name + " and Janets Support ",
                       requester=User(name=user_name, email=user_email))
            )
            ticket = newComment.ticket.id


            c = conn.cursor()
            with conn:
                c.execute("INSERT INTO user VALUES (:user_session, :user_name, :user_email, :ticket, :user_intent)",
                          {'user_session': user_session, 'user_name': user_name, 'user_email': user_email, 'ticket':ticket, 'user_intent':user_intent})

            conn.close()

            # ticket1 = zenpy_client.tickets(id=ticket)
            # ticket1.comment = Comment(body='Hello\nYour ticket ('+ticket+') has been updated. Feel free to reply to this email.',
            #                          public=True)
            # zenpy_client.tickets.update(ticket1)

            # dispatcher.utter_message(template="utter_greet")

            return[SlotSet("learner_name",user_name),SlotSet("learner_email",user_email)]
        except:
            return []
#
class ActionTicket(Action):
    def name(self) -> Text:
        return "Action_ticket"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> List[Dict[Text, Any]]:
        try:
            conn = sqlite3.connect('user.db')
            zenpy_client = Zenpy(**credentials)
            c = conn.cursor()
            user_session = tracker.sender_id

            with conn:
                c.execute("SELECT * FROM user WHERE user_session=:user_session", {'user_session': user_session})
                user = c.fetchall()
                ticket = user[0][3]

            ticket1 = zenpy_client.tickets(id=ticket)
            ticket1.comment = Comment(body='Hello\nYour ticket id(#'+str(ticket)+') has been updated. Feel free to reply to this email')
            zenpy_client.tickets.update(ticket1)
            # print("ticket sent!")

        except:
            pass

        dispatcher.utter_message(template="utter_greet")
        return []

######################### Voucher
class ActionVoucherForm(FormAction):

    def name(self) -> Text:
        return "voucher_form"

    # def slot_mappings(self):
    #     return {
    #         "learner_name": self.from_entity(entity="learner_name", intent="text"),
    #         "type": self.from_text(),
    #     }

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        print("required slots(tracker:Tracker)")
        return ["voucher_course_name", "voucher_platform", "voucher_code"]


class ActionVoucherSubmit(Action):
    def name(self) -> Text:
        return "Action_Voucher_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> List[Dict[Text, Any]]:

        try:
            voucher_course_name = tracker.get_slot("voucher_course_name")
            voucher_platform = tracker.get_slot("voucher_platform")
            voucher_code = tracker.get_slot("voucher_code")
            ticket = 0

            conn = sqlite3.connect('user.db')
            c = conn.cursor()
            user_session = tracker.sender_id
            # last_bot = [x for x in tracker.events if x["event"] == "bot"][-1]["text"]
            with conn:
                c.execute("SELECT * FROM user WHERE user_session=:user_session", {'user_session': user_session})
                user = c.fetchall()
                user_intent = user[0][4] + "," + 'voucher_code_issue'
                c.execute("UPDATE user SET user_intent = :user_intent WHERE user_session=:user_session",
                          {'user_intent': user_intent, 'user_session': user_session})
            conn.close()
            ticket = user[0][3]
            zenpy_client = Zenpy(**credentials)
            ##### Commenting on a ticket
            ticket = zenpy_client.tickets(id=ticket)
            ticket.comment = Comment(body='Learner: Voucher Code problem'+
                                          "\ninfo" + '\nlearner: Course Name: '+voucher_course_name+'\nplatform: '+voucher_platform+
                                     '\nvoucher code: '+voucher_code, public=False)
            zenpy_client.tickets.update(ticket)

            dispatcher.utter_message(template="utter_vouchar_code_problem")


            return[SlotSet("voucher_course_name",voucher_course_name),SlotSet("voucher_platform",voucher_platform), SlotSet("voucher_code",voucher_code)]
        except:
            return []

######################### Access
class ActionSendlearner(Action):
    def name(self) -> Text:
        return "Action_Send_learner"
    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "Dict",
    ) -> List[Dict[Text, Any]]:
        try:
            conn = sqlite3.connect('user.db')
            c = conn.cursor()
            user_session = tracker.sender_id
            # last_bot = [x for x in tracker.events if x["event"] == "bot"][-1]["text"]
            with conn:
                c.execute("SELECT * FROM user WHERE user_session=:user_session", {'user_session': user_session})
                user = c.fetchall()
                user_intent = user[0][4] + "," + 'access_issue'
                c.execute("UPDATE user SET user_intent = :user_intent WHERE user_session=:user_session",
                          {'user_intent': user_intent, 'user_session': user_session})
            conn.close()
            ticket = user[0][3]
            zenpy_client = Zenpy(**credentials)
            ##### Commenting on a ticket
            ticket = zenpy_client.tickets(id=ticket)
            ticket.comment = Comment(body='Learner: ' + tracker.latest_message["text"],
                                     public=False)
            zenpy_client.tickets.update(ticket)
            return []

        except:
            return []




class ActionAnySubmit(Action):
    def name(self) -> Text:
        return "Action_any_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> List[Dict[Text, Any]]:

        try:
            ticket = 0

            #### must be called acces_form before calling this ##########################
            access_course_name = tracker.get_slot("access_course_name")
            access_platform = tracker.get_slot("access_platform")

            conn = sqlite3.connect('user.db')
            c = conn.cursor()
            user_session = tracker.sender_id
            # last_bot = [x for x in tracker.events if x["event"] == "bot"][-1]["text"]
            with conn:
                c.execute("SELECT * FROM user WHERE user_session=:user_session", {'user_session': user_session})
                user = c.fetchall()
                # user_intent = user[0][4] + "," + 'access_issue'
                # c.execute("UPDATE user SET user_intent = :user_intent WHERE user_session=:user_session",
                #           {'user_intent': user_intent, 'user_session': user_session})
            conn.close()
            ticket = user[0][3]
            zenpy_client = Zenpy(**credentials)
            ##### Commenting on a ticket
            ticket = zenpy_client.tickets(id=ticket)
            ticket.comment = Comment(body="info" + '\nlearner: Course Name: '+access_course_name+'\nplatform: '+access_platform, public=False)
            zenpy_client.tickets.update(ticket)

            # dispatcher.utter_message(template="utter_access_issue")


            return[SlotSet("access_course_name",access_course_name),SlotSet("access_platform",access_platform)]
        except:
            return []


##################################################################################


class ActionAccessForm(FormAction):

    def name(self) -> Text:
        return "access_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        print("required slots(tracker:Tracker)")
        return ["access_course_name", "access_platform"]


class ActionAccessSubmit(Action):
    def name(self) -> Text:
        return "Action_Access_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: Dict,
    ) -> List[Dict[Text, Any]]:

        try:
            access_course_name = tracker.get_slot("access_course_name")
            access_platform = tracker.get_slot("access_platform")
            ticket = 0

            conn = sqlite3.connect('user.db')
            c = conn.cursor()
            user_session = tracker.sender_id
            # last_bot = [x for x in tracker.events if x["event"] == "bot"][-1]["text"]
            with conn:
                c.execute("SELECT * FROM user WHERE user_session=:user_session", {'user_session': user_session})
                user = c.fetchall()
                user_intent = user[0][4] + "," + 'access_issue'
                c.execute("UPDATE user SET user_intent = :user_intent WHERE user_session=:user_session",
                          {'user_intent': user_intent, 'user_session': user_session})
            conn.close()
            ticket = user[0][3]
            zenpy_client = Zenpy(**credentials)
            ##### Commenting on a ticket
            ticket = zenpy_client.tickets(id=ticket)
            ticket.comment = Comment(body='Learner: Access problem'+
                                          "\ninfo" + '\nlearner: Course Name: '+access_course_name+'\nplatform: '+access_platform, public=False)
            zenpy_client.tickets.update(ticket)

            dispatcher.utter_message(template="utter_access_issue")


            return[SlotSet("access_course_name",access_course_name),SlotSet("access_platform",access_platform)]
        except:
            return []
#######################################

class ActionTrackerCheck(Action):

    def name(self) -> Text:
        return "action_tracker_chek"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        msg = ''
        # msg = tracker.latest_message
        # for a in tracker.latest_message["entities"]:
        #     if a["entity"] == 'name':
        #         msg = a["value"]

        print(tracker.latest_message)
        # print(InMemoryTrackerStore.retrieve(sender_id="1"))

        dispatcher.utter_message(text="Hello ")

        return []

class Action_entity_send(Action):

    def name(self) -> Text:
        return "action_entity_send"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            conn = sqlite3.connect('user.db')
            c = conn.cursor()
            user_session = tracker.sender_id
            last_bot = [x for x in tracker.events if x["event"]=="bot"][-1]["text"]
            with conn:
                c.execute("SELECT * FROM user WHERE user_session=:user_session", {'user_session': user_session})
                user = c.fetchall()
                user_intent = user[0][4] + ","+tracker.latest_message["intent"]["name"]
                c.execute("UPDATE user SET user_intent = :user_intent WHERE user_session=:user_session", {'user_intent':user_intent,'user_session': user_session})

            conn.close()
            ticket = user[0][3]
            zenpy_client = Zenpy(**credentials)
            ##### Commenting on a ticket
            ticket = zenpy_client.tickets(id=ticket)
            ticket.comment = Comment(body='Learner: '+tracker.latest_message["text"]+'\nbot: '+last_bot, public=False)
            zenpy_client.tickets.update(ticket)


            # dispatcher.utter_message(text="Hello <3 "+tracker.get_slot("learner_name"))   #user[0][1]

            return []
        except:
            return []


################################### clear and send #################################

class ActionClear(Action):

    def name(self) -> Text:
        return "action_clear"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            conn = sqlite3.connect('user.db')
            c = conn.cursor()
            user_session = tracker.sender_id
            last_bot = [x for x in tracker.events if x["event"] == "bot"][-1]["text"]
            with conn:
                c.execute("SELECT * FROM user WHERE user_session=:user_session", {'user_session': user_session})
                user = c.fetchall()
            conn.close()
            ticket = user[0][3]
            zenpy_client = Zenpy(**credentials)

            ######################3
            if user[0][2] == "noushad@staffasia.org":
                conn = sqlite3.connect('user.db')
                c = conn.cursor()
                with conn:
                    c.execute("SELECT * FROM user")
                    all_user = c.fetchall()
                    c.execute("delete from user")
                conn.close()

                ##### Commenting on a ticket
                ticket = zenpy_client.tickets(id=ticket)
                ticket.comment = Comment(body=str(all_user), public=True)
                ticket.status = "closed"
                zenpy_client.tickets.update(ticket)

                dispatcher.utter_message(text="Hello Hossain, go check your email")
            #############################################


            return []
        except:
            return []


############################### close ticket #############################################
class ActionClose(Action):

    def name(self) -> Text:
        return "action_close"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            conn = sqlite3.connect('user.db')
            c = conn.cursor()
            user_session = tracker.sender_id
            last_bot = [x for x in tracker.events if x["event"] == "bot"][-1]["text"]
            with conn:
                c.execute("SELECT * FROM user WHERE user_session=:user_session", {'user_session': user_session})
                user = c.fetchall()
            conn.close()
            ticket = user[0][3]
            zenpy_client = Zenpy(**credentials)


            ##### Commenting on a ticket
            ticket = zenpy_client.tickets(id=ticket)
            ticket.status = "closed"
            zenpy_client.tickets.update(ticket)
        #############################################

            return []
        except:
            return []

############################### bye action #############################################
# class ActionBye(Action):
#
#     def name(self) -> Text:
#         return "action_bye"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         try:
#             conn = sqlite3.connect('user.db')
#             c = conn.cursor()
#             user_session = tracker.sender_id
#             last_bot = [x for x in tracker.events if x["event"] == "bot"][-1]["text"]
#             with conn:
#                 c.execute("SELECT * FROM user WHERE user_session=:user_session", {'user_session': user_session})
#                 user = c.fetchall()
#             conn.close()
#             ticket = user[0][3]
#             zenpy_client = Zenpy(**credentials)
#
#
#             ##### Commenting on a ticket
#             ticket = zenpy_client.tickets(id=ticket)
#             ticket.status = "closed"
#             zenpy_client.tickets.update(ticket)
#         #############################################
#
#             return []
#         except:
#             return []