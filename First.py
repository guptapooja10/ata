import streamlit as st


def about_page():
    st.title("About My App")
    st.write("""
        Welcome to My App! This app is designed to [describe the purpose of your app].
        """)


def features_page():
    st.title("Features")
    st.markdown("- **Feature 1:** Description of Feature 1")
    st.markdown("- **Feature 2:** Description of Feature 2")
    st.markdown("- **Feature 3:** Description of Feature 3")


def team_page():
    st.title("Team")
    st.markdown("Meet the creators behind My App:")
    st.markdown("- **John Doe:** Lead Developer ([LinkedIn](#))")
    st.markdown("- **Jane Smith:** UI/UX Designer ([LinkedIn](#))")
    st.markdown("- **Bob Johnson:** Data Scientist ([LinkedIn](#))")


def contact_page():
    st.title("Contact Us")
    st.markdown("Have questions or feedback? Reach out to us:")
    st.markdown("- **Email:** [your.email@example.com]")
    st.markdown("- **Twitter:** [@YourTwitterHandle]")


def main():
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.selectbox("Go to", ["About", "Features", "Team", "Contact"])

    if selected_page == "About":
        about_page()
    elif selected_page == "Features":
        features_page()
    elif selected_page == "Team":
        team_page()
    elif selected_page == "Contact":
        contact_page()


if __name__ == "__main__":
    main()
