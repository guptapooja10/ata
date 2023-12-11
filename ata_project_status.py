import streamlit as st
import pandas as pd
import io
from PIL import Image
from google.cloud import firestore
from google.oauth2 import service_account
import os

image = Image.open('logo_ata.png')
st.image(image, caption='Ata Logo', use_column_width=True)


# Navigation bar
def navigation_bar():
    apps = {
        "Login page": "https://credentials-page.streamlit.app/",
        "Project Instantiation": "https://ata-app-navigator.streamlit.app/",
        "VK-ST-0": "https://vk-st-0.streamlit.app/",
        "VK-0": "https://ata-vk-0.streamlit.app/",
        "Deckung": "https://deckung.streamlit.app/",

    }

    st.sidebar.title('Navigation')

    for app_name, app_url in apps.items():
        st.sidebar.markdown(f"[{app_name}]({app_url})")


key_dict = st.secrets["textkey"]
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)


def get_all_collections(db):
    excluded_collections = {'operators', 'posts', 'projects'}
    collections = db.collections()
    return [collection.id for collection in collections if collection.id not in excluded_collections]


def get_all_document_ids(collection_name):
    docs = db.collection(collection_name).stream()
    return [doc.id for doc in docs]


# Function to get total number of fields in a document
def get_total_fields(collection_name, document_id):
    doc_ref = db.collection(collection_name).document(document_id)
    document = doc_ref.get()

    def count_fields(data):
        total_fields = 0
        for key, value in data.items():
            total_fields += 1
            if isinstance(value, dict):
                total_fields += count_fields(value)
        return total_fields

    if document.exists:
        return count_fields(document.to_dict())
    else:
        return 0


def get_populated_fields_count(collection_name, document_id):
    doc_ref = db.collection(collection_name).document(document_id)
    document = doc_ref.get()

    def count_populated_fields(data):
        count = 0
        for value in data.values():
            if isinstance(value, dict):
                count += count_populated_fields(value)
            elif value is not None:
                count += 1
        return count

    if document.exists:
        return count_populated_fields(document.to_dict())
    else:
        return 0


# Streamlit app
def main():
    st.title('Project Status App')

    # Display the navigation bar
    navigation_bar()

    # Get all collection IDs
    all_collections = get_all_collections(db)

    # Allow the user to select a collection using a dropdown
    selected_collection = st.selectbox('Select Collection:', all_collections)

    # Get all document IDs for the selected collection
    document_ids = get_all_document_ids(selected_collection)

    # Display total number of fields for each document in the selected collection
    st.header(f"Total Number of Fields in Documents of {selected_collection} Collection:")
    for doc_id in document_ids:
        total_fields = get_total_fields(selected_collection, doc_id)
        st.write(f"{doc_id}: {total_fields} fields")
        st.write(f"Total fields in {doc_id}: {total_fields}")
        populated_fields_count = get_populated_fields_count(selected_collection, doc_id)
        st.write(f"{doc_id}: {populated_fields_count} populated fields")
        st.write(f"Populated fields count in {doc_id}: {populated_fields_count}")


if __name__ == '__main__':
    main()

# import streamlit as st
# from google.cloud import firestore
# import json
# import datetime as dt
# from streamlit_calendar import calendar
# from google.oauth2 import service_account
#
# # Authenticate to Firestore with the JSON account key.
# key_dict = st.secrets["textkey"]
# creds = service_account.Credentials.from_service_account_info(key_dict)
# db = firestore.Client(credentials=creds)
#
# st.set_page_config(page_title="ATA-Dashboard-App",layout="wide")
# st.write("### Welcome to the ATA-Dashboard-App")
# st.markdown("* Use the sidebar for Overall Project Data *")
# # Sidebar
# st.sidebar.title("Project Overview")
#
# st.header("Project Status App")
#
# # Create a reference to the projects
# project_ref = db.collection("projects")
# projects = list(project_ref.stream())  # Fetch data once and convert to a list
#
# project_name_list = []
#
# for project in projects:
#     project_data = project.to_dict()
#     project_name = project_data.get("name")
#     project_name_list.append(project_name)
#
# selected_project = st.selectbox("Select a project", project_name_list)
#
# # Get details of the selected project
# selected_project_query = project_ref.where("name", "==", selected_project).stream()
#
# # Calculate progress for all projects
# total_completed_tasks = 0
# total_num_tasks = 0
# total_projects = len(projects)
# # Display overall progress in the sidebar
# st.sidebar.subheader("Overall Progress")
# st.sidebar.metric("Total Number of Projects", total_projects)
# for proj in projects:
#     project_data = proj.to_dict()
#     total_completed_tasks += project_data.get("num_completed_tasks",0)
#     total_num_tasks += project_data.get("num_tasks",0)
#
# # Calculate delta
# delta = total_num_tasks - total_completed_tasks
# st.sidebar.metric(
#     "Total Completed Tasks",
#     total_completed_tasks,
#     total_num_tasks, delta_color="normal"
# )
# # Calculate progress ratio
# progress_ratio = total_completed_tasks / total_num_tasks
# # Display total completed tasks as a progress bar in the sidebar
# st.sidebar.write(f"Over Progress Ratio: {progress_ratio * 100:.2f}%")
# st.sidebar.write(f"Total Tasks Delta: {delta}")
#
# for proj in selected_project_query:
#     selected_project_data = proj.to_dict()
#
#     # Project data
#     current_progress_ratio = selected_project_data.get("current_progress_ratio")
#     num_completed_tasks = selected_project_data.get("num_completed_tasks")
#     num_tasks = selected_project_data.get("num_tasks")
#     project_name = selected_project_data.get("name")
#
#     starting_date = (selected_project_data.get("starting_date").date())
#     target_date = (selected_project_data.get("target_date").date())
#     current_expected_date = (selected_project_data.get("current_expected_date").date())
#
#     # st.write(selected_project_data)
#     st.title(project_name)
#
#     st.divider()
#     # Progress visualization
#     bar_column, ratio_column, task_ratio_column = st.columns([4, 1, 1])
#     with bar_column:
#         my_bar = st.progress(current_progress_ratio, text="Project Progress")
#     with ratio_column:
#         st.metric(label="Progress Ratio", value=current_progress_ratio)
#     with task_ratio_column:
#         st.metric(label="Completed Tasks", value=f"{num_completed_tasks}/{num_tasks}")
#
#     st.divider()
#
#     schedule_deviation = current_expected_date - target_date
#
#     if int(schedule_deviation.days) > 0:
#         current_timeline_color = "#FF0000"
#     else:
#         current_timeline_color = "#5DBB63"
#
#     timeline_column, deviation_column = st.columns([4, 2])
#     with timeline_column:
#         if int(schedule_deviation.days) > 0:
#             st.error(
#                 f"Start date: {starting_date} \n\n End date: {target_date} \n\n Expected End date:  {current_expected_date}")
#         else:
#             st.success(
#                 f"Start date: {starting_date} \n\n End date: {target_date} \n\n Expected End date:  {current_expected_date}")
#     with deviation_column:
#         st.metric(label="Current End date", value=str(current_expected_date), delta=int(schedule_deviation.days),
#                   delta_color="inverse")
#
#     st.divider()
#     # Create a selection widget for the calendar view
#     selected_view = st.selectbox("Select Calendar View", ["timeline", "multiMonthYear"])
#     if selected_view == "timeline":
#         calendar_options = {
#             "headerToolbar": {
#                 "left": "today,prev,next",
#                 "center": "title",
#                 "right": "timelineDay,timelineWeek,timelineMonth,timelineYear",
#             },
#             "initialView": "timelineMonth",
#             "resourceGroupField": "project",
#             "resources": [
#                 {"id": "expected_timeline",
#                  "project": project_name,
#                  "title": "Expected Timeline", },
#                 {"id": "current_timeline",
#                  "project": project_name,
#                  "title": "Current Timeline", },
#                 {"id": "events",
#                  "project": project_name,
#                  "title": "Events", },
#             ],
#         }
#     else:
#         calendar_options = {
#             "headerToolbar": {
#                 "left": "today,prev,next",
#                 "center": "title",
#                 "right": "multiMonthYear",
#             },
#             "initialView": "multiMonthYear",
#             "resourceGroupField": "project",
#             "resources": [
#                 {"id": "expected_timeline",
#                  "project": project_name,
#                  "title": "Expected Timeline", },
#                 {"id": "current_timeline",
#                  "project": project_name,
#                  "title": "Current Timeline", },
#                 {"id": "events",
#                  "project": project_name,
#                  "title": "Events", },
#             ],
#         }
#     calendar_events = [
#         {
#             "title": "Expected project timeline",
#             "start": str(starting_date),
#             "end": str(target_date),
#             "resourceId": "expected_timeline",
#         },
#         {
#             "title": "Current project timeline",
#             "start": str(starting_date),
#             "end": str(current_expected_date),
#             "resourceId": "current_timeline",
#             "color": current_timeline_color
#         },
#     ]
#     # Display the calendar using streamlit_calendar
#     st.title("Project Calendar")
#     calendar = calendar(events=calendar_events, options=calendar_options)
