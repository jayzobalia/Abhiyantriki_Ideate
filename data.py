import streamlit as st
with st.form("my_form"):
    st.write("Inside the form")
    #    slider_val = st.slider("Form slider")
    #    checkbox_val = st.checkbox("Form checkbox")
    arr = []
    address = st.text_input("Enter Address")
    obj1 = report_accident()
    arr = obj1.accept_location(address)

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("address: ", arr)

st.write("Outside the form")