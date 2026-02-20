import streamlit as st
from translator import translate

st.title("Educational Spanish Translator")

st.write("This translator explains grammar choices and supports dialects.")

text = st.text_input("Enter an English sentence:")

dialect = st.selectbox(
    "Choose Spanish dialect:",
    ["Mexican Spanish", "Castilian Spanish"]
)

mode = st.radio(
    "Mode:",
    ["Translate", "Hint"]
)

if st.button("Run"):
    if text:
        result = translate(
            text,
            dialect="mx" if dialect == "Mexican Spanish" else "es",
            mode="hint" if mode == "Hint" else "translate"
        )

        if result.get("output"):
            st.subheader("Spanish Output")
            st.write(result["output"])

        if result.get("hint"):
            st.subheader("Hint")
            st.write(result["hint"])

        st.subheader("Grammar Explanation")
        st.write(result["explanation"])
    else:
        st.warning("Please enter a sentence.")
