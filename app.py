import streamlit as st
import google.generativeai as genai
import json
import re
import os
from dotenv import load_dotenv

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="🎓 AURCC Smart College Chatbot", page_icon="🤖")

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


SYSTEM_PROMPT = """
You are the official assistant for Anna University Regional Campus, Coimbatore.

Rules:
- Use the provided college dataset first.
- If dataset gives a valid answer, use it — no modification.
- If dataset doesn't have info, then use your own knowledge (Gemini).
- For requests of HOD, Principal, phone, email, room number — give dataset value only.
- Replies must be short and factual.
"""

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# -----------------------------
# DATASET
# -----------------------------
college_data = {
  "college_name": "Anna University Regional Campus, Coimbatore",
  "general_info": {
    "principal_name": "Dr. R. Saravan Kumar",
    "college_location": "Navavoor, Coimbatore, Tamil Nadu",
    "contact_email": "cseaurcc@aurcc.edu.in",
    "college_phone": "0422-1234567",
    "working_hours": "9:00 AM to 4:30 PM (Monday to Friday)",
    "website": "https://aurcc.edu.in",
    "motto": "Progress Through Knowledge"
  },

  "departments": {
    "CSE": {
      "hod": {
        "name": "Dr. K. Manisekaran",
        "room_no": "218",
        "phone": "9442450955",
        "email": "manisekaran@aurcc.edu.in"
      },
      "office_room_no": "207",
      "courses": {
        "B.E Computer Science and Engineering": {
          "semesters": {
            "1st_semester": {
              "subjects": ["Mathematics I", "Physics", "Chemistry", "Engineering Graphics", "Programming in Python", "English"],
              "timetable": {
                "Monday": ["Mathematics I(1,2)", "Physics(3,4)", "Programming in Python(5,6)", "English(7)"],
                "Tuesday": ["Chemistry(1,2)", "Physics(3,4)", "Engineering Graphics(5,6,7)"],
                "Wednesday": ["Programming in Python(1,2,3,4)", "English(5)", "Mathematics I(6,7)"],
                "Thursday": ["Physics(1,2)", "Chemistry(3,4)", "Programming in Python(5,6,7)"],
                "Friday": ["Engineering Graphics(1,2,3,4)", "English(5,6)", "Tutorials(7)"]
              }
            },

            "2nd_semester": {
              "subjects": ["Mathematics II", "Data Structures", "BEEE", "English", "Tamil", "Physics"],
              "timetable": {
                "Monday": ["Mathematics II(1,2)", "Data Structures(3,4)", "English(5,6)", "Physics(7)"],
                "Tuesday": ["BEEE(1,2)", "Tamil(3,4)", "Data Structures(5,6,7,8)"],
                "Wednesday": ["Tamil(1,2)", "Physics(3,4)", "Data Structures(5)", "Mathematics II(6,7)"],
                "Thursday": ["BEEE(1,2)", "Data Structures(3,4)", "English(5,6)", "Tamil(7)"],
                "Friday": ["Mathematics II(1,2)", "Tamil(3,4)", "Physics(5,6,7)"]
              }
            }
          }
        }
      }
    }
  },

  "procedures": {
    "on_duty": "Collect OD form from department office, get faculty + advisor + HOD signature, submit to office.",
    "leave": "Submit leave letter to class advisor or upload in portal before leave date."
  }
}

# -----------------------------
# SEARCH KEYWORDS
# -----------------------------
PRINCIPAL_SYNS = ["principal"]
HOD_SYNS = ["hod"]
SUBJECT_SYNS = ["subjects"]
TIMETABLE_SYNS = ["timetable"]

def contains_any(q, keywords):
    return any(k in q for k in keywords)

# -----------------------------
# SEARCH DATASET
# -----------------------------
def search_dataset(query, data):
    q = query.lower().strip()

    if contains_any(q, PRINCIPAL_SYNS):
        return data["general_info"]["principal_name"]

    if contains_any(q, HOD_SYNS):
        if "cse" in q:
            return data["departments"]["CSE"]["hod"]["name"]

    if contains_any(q, SUBJECT_SYNS):
        return data["departments"]["CSE"]["courses"]["B.E Computer Science and Engineering"]["semesters"]["1st_semester"]["subjects"]

    if contains_any(q, TIMETABLE_SYNS):
        return data["departments"]["CSE"]["courses"]["B.E Computer Science and Engineering"]["semesters"]["1st_semester"]["timetable"]

    return None

# -----------------------------
# MODEL REPLY
# -----------------------------
def build_reply(user_q, dataset_ans):
    if dataset_ans is not None:
        prompt = f"User asked: {user_q}\nAnswer: {dataset_ans}\nReply short."
        return model.generate_content(prompt).text.strip()

    return model.generate_content(user_q).text.strip()

# -----------------------------
# UI
# -----------------------------
st.title("🎓 AURCC Smart College Chatbot")

if "chat" not in st.session_state:
    st.session_state.chat = []

for m in st.session_state.chat:
    st.chat_message(m["role"]).markdown(m["msg"])

user_q = st.chat_input("Ask your question...")

if user_q:
    st.session_state.chat.append({"role": "user", "msg": user_q})
    st.chat_message("user").markdown(user_q)

    data_answer = search_dataset(user_q, college_data)
    reply = build_reply(user_q, data_answer)

    st.session_state.chat.append({"role": "assistant", "msg": reply})
    st.chat_message("assistant").markdown(reply)
