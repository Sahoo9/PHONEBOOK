import streamlit as st
from database import Database
import pandas as pd

# Initialize database
db = Database()

def init_session_state():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None

def login_page():
    st.title("📱 Phone Book Management System")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.header("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    user_id = db.verify_user(username, password)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.success("Login successful!")
                        st.experimental_rerun()
                    else:
                        st.error("Invalid username or password!")
                else:
                    st.error("Please fill in all fields!")

    with tab2:
        st.header("Register")
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit = st.form_submit_button("Register")
            
            if submit:
                if new_username and new_password and confirm_password:
                    if new_password == confirm_password:
                        if db.register_user(new_username, new_password):
                            st.success("Registration successful! Please login.")
                        else:
                            st.error("Username already exists!")
                    else:
                        st.error("Passwords do not match!")
                else:
                    st.error("Please fill in all fields!")

def main_page():
    st.title(f"📱 Welcome, {st.session_state.username}!")
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.session_state.username = None
        st.experimental_rerun()
    
    # Main menu
    menu = st.sidebar.selectbox(
        "Menu",
        ["View Contacts", "Add Contact", "Search Contacts", "Contact Statistics"]
    )
    
    if menu == "Add Contact":
        with st.expander("Add New Contact", expanded=True):
            with st.form("add_contact_form"):
                name = st.text_input("Name*")
                phone = st.text_input("Phone Number*")
                email = st.text_input("Email")
                address = st.text_area("Address")
                category = st.selectbox("Category", ["Family", "Friend", "Work", "Other"])
                notes = st.text_area("Notes")
                
                submit = st.form_submit_button("Add Contact")
                
                if submit:
                    if name and phone:
                        db.add_contact(st.session_state.user_id, name, phone, email, 
                                    address, category, notes)
                        st.success("Contact added successfully!")
                    else:
                        st.error("Name and Phone Number are required!")

    elif menu == "View Contacts":
        contacts = db.get_user_contacts(st.session_state.user_id)
        if not contacts.empty:
            for _, contact in contacts.iterrows():
                with st.expander(f"{contact['name']} - {contact['phone']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Email:**", contact['email'] or "N/A")
                        st.write("**Category:**", contact['category'])
                    with col2:
                        st.write("**Address:**", contact['address'] or "N/A")
                        st.write("**Notes:**", contact['notes'] or "N/A")
                    
                    if st.button("Edit", key=f"edit_{contact['id']}"):
                        with st.form(f"edit_form_{contact['id']}"):
                            name = st.text_input("Name*", contact['name'])
                            phone = st.text_input("Phone Number*", contact['phone'])
                            email = st.text_input("Email", contact['email'])
                            address = st.text_area("Address", contact['address'])
                            category = st.selectbox("Category", 
                                                ["Family", "Friend", "Work", "Other"],
                                                index=["Family", "Friend", "Work", "Other"].index(contact['category']))
                            notes = st.text_area("Notes", contact['notes'])
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                update = st.form_submit_button("Update")
                            with col2:
                                delete = st.form_submit_button("Delete")
                            
                            if update:
                                if name and phone:
                                    if db.update_contact(st.session_state.user_id, 
                                                    contact['id'], name, phone, email,
                                                    address, category, notes):
                                        st.success("Contact updated successfully!")
                                        st.experimental_rerun()
                                    else:
                                        st.error("Update failed!")
                                else:
                                    st.error("Name and Phone Number are required!")
                            
                            if delete:
                                if db.delete_contact(st.session_state.user_id, contact['id']):
                                    st.success("Contact deleted successfully!")
                                    st.experimental_rerun()
                                else:
                                    st.error("Delete failed!")
        else:
            st.info("No contacts found. Add some contacts!")

    elif menu == "Search Contacts":
        search_query = st.text_input("Search contacts by name, phone, or email")
        if search_query:
            results = db.search_user_contacts(st.session_state.user_id, search_query)
            if not results.empty:
                for _, contact in results.iterrows():
                    with st.expander(f"{contact['name']} - {contact['phone']}"):
                        st.write("**Email:**", contact['email'] or "N/A")
                        st.write("**Category:**", contact['category'])
                        st.write("**Address:**", contact['address'] or "N/A")
                        st.write("**Notes:**", contact['notes'] or "N/A")
            else:
                st.info("No matching contacts found.")

    elif menu == "Contact Statistics":
        contacts = db.get_user_contacts(st.session_state.user_id)
        if not contacts.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Contacts", len(contacts))
                category_counts = contacts['category'].value_counts()
                st.subheader("Contacts by Category")
                st.bar_chart(category_counts)
            
            with col2:
                st.subheader("Recent Contacts")
                recent = contacts.sort_values('created_at', ascending=False).head()
                for _, contact in recent.iterrows():
                    st.write(f"**{contact['name']}** ({contact['category']})")

        else:
            st.info("No contacts found. Add some contacts!")

def main():
    init_session_state()
    
    if st.session_state.user_id is None:
        login_page()
    else:
        main_page()

if __name__ == "__main__":
    main()