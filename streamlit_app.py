import streamlit as st

st.title('Experiment Design')
st.subheader('Enter the amount of doses')

doses = st.number_input('Number of doses', value=1, min_value=1, format="%d")
priors = []
for i in range(doses):
    prior = st.number_input(f'Enter the prior distribution for dose {i+1}', value=0.0, format="%.3f")
    priors.append(prior)


m = st.number_input('Enter the threshold for the target distribution', value=0.0, format="%.3f")
st.write(f'You entered {doses} doses.')
st.write(f'Your priors are {["%.3f" % prior for prior in priors]}')
st.write(f'Your threshold is {"%.3f" % m}')

ordered_priors = sorted(priors)

if st.button('Submit Parameters'):
    for i in doses:
        if f'dose_{i}' not in st.session_state:
            st.session_state['doses'][f'dose_{i}'] = {'patients': 0, 'side_effects': 0, 'dosage': i}

    if 'current_dose' not in st.session_state:
        st.session_state['current_dose'] = min(ordered_priors)

    st.write(f'You should use dose with prior {st.session_state["current_dose"]}')
    side_effects = st.radio(f'Did the patient experience any side effects with dose {st.session_state["current_dose"]}?', options=[True, False])


if st.button('Next Patient'):

    st.session_state['doses'][f'dose_{st.session_state["current_dose"]}']['patients'] += 1
    if side_effects:
        st.session_state['patient_data'][st.session_state["current_dose"]]['side_effects'] += 1

    # If there were side effects, reduce the dose for the next patient (if not already at the lowest dose)
    # If there were no side effects, increase the dose for the next patient (if not already at the highest dose)
    if side_effects and st.session_state["current_dose"] > 0:
        st.session_state["current_dose"] -= 1
    elif not side_effects and st.session_state["current_dose"] < doses - 1:
        st.session_state["current_dose"] += 1

for i in range(doses):
    st.sidebar.markdown(f'### Dose Group {i+1}')
    st.sidebar.text(f'Patients: {st.session_state["patient_data"][i]["patients"]}')
    st.sidebar.text(f'Side Effects: {st.session_state["patient_data"][i]["side_effects"]}')
