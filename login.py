import streamlit as st

def login():
    st.title("Login")

    username = "admin"
    password = "yagoandrafa"

    
    input_user = st.text_input("Username")
    input_pass = st.text_input("Password", type="password")

    if st.button("Login"):
        if input_user == username and input_pass == password:
            st.session_state.logged_in = True
            st.success("Login bem-sucedido!")
            st.session_state.show_main = True
        else:
            st.error("Usuário ou senha inválidos.")

if __name__ == "__main__":
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.show_main = False

    if st.session_state.logged_in:
        import main_prop 
        main_prop.main()
    else:
        login()
 
