import streamlit as st
from translator import translate

st.set_page_config(page_title="Spanish Edu Translator", layout="centered")
st.title("Spanish Edu Translator")
st.caption("Correctness + grammar explanations + hint mode (educational focus)")

text = st.text_input("Enter an English sentence:", placeholder="e.g., I am tired. I like the dogs. I am studying.")
dialect = st.selectbox("Dialect:", ["Mexican Spanish", "Castilian Spanish"])
mode = st.radio("Mode:", ["Translate", "Hint"], horizontal=True)

col1, col2 = st.columns(2)
with col1:
    speaker_gender = st.selectbox("Speaker gender (for I/We adjectives):", ["Masculine", "Feminine"])
with col2:
    formality = st.selectbox("You (English) means:", ["tú (informal)", "usted (formal)"], index=0)

if st.button("Run"):
    if not text.strip():
        st.warning("Type a sentence first.")
    else:
        result = translate(
            text=text,
            dialect="mx" if dialect == "Mexican Spanish" else "es",
            mode="hint" if mode == "Hint" else "translate",
            speaker_gender="f" if speaker_gender.startswith("F") else "m",
            you_form="usted" if formality.startswith("usted") else "tu"
        )

        if result.get("error"):
            st.error(result["error"])

        if result.get("spanish"):
            st.subheader("Spanish")
            st.write(result["spanish"])

        if result.get("hint"):
            st.subheader("Hint")
            for h in result["hint"]:
                st.write(f"- {h}")

        st.subheader("Grammar Callouts")
        if result.get("callouts"):
            for c in result["callouts"]:
                st.info(f"**{c['title']}**\n\n{c['text']}")
        else:
            st.write("No callouts for this sentence yet.")
