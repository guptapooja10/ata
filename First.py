import streamlit as st


def about_page():
    st.title("About")
    st.write("""Welcome to the comprehensive engineering solution application! The app is designed to streamline your 
    engineering processes, providing valuable insights into dimensions, costs, welding, heating processes, 
    project status and generating accurate price quotations. We aim to simplify complex tasks and enhance your 
    workflow, offering an intuitive and efficient tool for professionals in the engineering field. Explore the 
    various features and functionalities to optimize your work and achieve better results.""")


def features_page():
    st.title("Features")
    st.markdown("- **Feature 1:** Description of Feature 1")
    st.markdown("- **Feature 2:** Description of Feature 2")
    st.markdown("- **Feature 3:** Description of Feature 3")


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
    elif selected_page == "Contact":
        contact_page()


if __name__ == "__main__":
    main()
