import json
import streamlit as st

def ReadUsersDatabase():
    with open("datas/users.json", "r") as f:
        usersDatabase = json.load(f)
        if "users" not in usersDatabase:
            usersDatabase["users"]={}
    return usersDatabase

def WriteUsersDatabase(usersDatabase):
    with open("datas/users.json", "w") as f:
        json.dump(usersDatabase, f,indent=4)