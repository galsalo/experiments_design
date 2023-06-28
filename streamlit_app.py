import streamlit as st
import scipy.optimize
import numpy as np

##############################################################################
## The app is hosted and Live at: https://experiments-design.streamlit.app/ ##
##############################################################################
# Name: Gal Salomon
# I.D: 316613140


# Helper functions
def theta_func(theta):
    vals = []
    for i in range(doses_amount):
        current_val = np.power(doses_values[i], theta*st.session_state['patient_data'][i]['side_effects'])*np.power((1-np.power(doses_values[i],theta)), st.session_state['patient_data'][i]['patients']-st.session_state['patient_data'][i]['side_effects'])
        vals.append(current_val)

    return float(np.prod(vals))


def find_max_theta():
    return scipy.optimize.fminbound(lambda x: -theta_func(x), 0, 10, disp=False)


def get_closest_dose(doses, threshold):
    theta = find_max_theta()
    theta_vals = {dose: dose**theta for dose in doses}
    closest_value = min(theta_vals, key=lambda x: abs(theta_vals[x]-threshold))
    return doses.index(closest_value), theta



st.title('CRM Experiment')
st.write('This is a CRM experiment. Please enter the number of doses and their priors. Then, enter the threshold for the target distribution. The CRM will then recommend a dose for the next patient. After you enter the patient data, the CRM will update the dose recommendation. You can also see the theta estimate in the sidebar.')
st.write(':heavy_exclamation_mark: the estimators will be calculated only after the first patient with side effects and the first patient without side effects are entered.')
st.subheader('Enter the amount of doses')

if 'submitted_values' not in st.session_state:
    st.session_state['submitted_values'] = False

    # Number of doses and their values
doses_amount = st.number_input('Number of doses', value=1, min_value=1, format="%d")
doses_values = []

for i in range(doses_amount):
    dosage_prior = st.number_input(f'Enter the prior for dose {i+1}', value=0.0, format="%.3f")
    doses_values.append(dosage_prior)

# Threshold for the target distribution
threshold = st.number_input('Enter the threshold for the target distribution (m)', value=0.25, format="%.3f")

# Initialize session state for patient data
if 'patient_data' not in st.session_state and st.button('Submit Doses'):
    if 'side_effects_estimates' not in st.session_state:
        st.session_state['side_effects_estimates'] = [0 for i in range(doses_amount)]
    st.session_state['submitted_values'] = True
    st.session_state['patient_data'] = {i: {'patients': 0, 'side_effects': 0} for i in range(doses_amount)}
    if 'theta_calculated' not in st.session_state:
        st.session_state['theta_calculated'] = False

if st.session_state['submitted_values']:
    # Output the dose information
    st.write(f'You entered {doses_amount} doses.')
    st.write(f'Your priors are {["%.3f" % prior for prior in doses_values]}')
    st.write(f'Your threshold is {"%.3f" % threshold}')

    # Initialize session state for current dose
    if 'current_dose' not in st.session_state:
        st.session_state['current_dose'] = 0  # Start with the first dose

    # Notify the operator which dose to use
    st.subheader(f'Recommended dose: number {st.session_state["current_dose"] + 1}')

    # Ask if the patient experienced side effects
    st.markdown(f'<font size="4">Did the patient experience any side effects with dose number {st.session_state["current_dose"] + 1}?</font>', unsafe_allow_html=True)
    side_effects = st.radio('', options=[True, False])

    # Create a save result button
    if st.button('Submit Patient'):
        if 'curr_theta' not in st.session_state:
            st.session_state['curr_theta'] = 'Not calculated yet'
        if 'CRM' not in st.session_state:
            st.session_state['CRM'] = False
        if 'first_side_effect' not in st.session_state:
            st.session_state['first_side_effect'] = False
        if 'first_no_side_effect' not in st.session_state:
            st.session_state['first_no_side_effect'] = False

        # Update patient data in session state
        st.session_state['patient_data'][st.session_state["current_dose"]]['patients'] += 1

        # Side effect True
        if side_effects:
            st.session_state['first_side_effect'] = True
            st.session_state['patient_data'][st.session_state["current_dose"]]['side_effects'] += 1
            if st.session_state['first_side_effect'] and st.session_state['first_no_side_effect']:
                st.session_state['CRM'] = True
            if st.session_state['CRM']:
                st.session_state['current_dose'], st.session_state['curr_theta'] = get_closest_dose(doses_values, threshold)
                st.session_state['theta_calculated'] = True


        # Side effect False
        else:
            st.session_state['first_no_side_effect'] = True
            if st.session_state['first_side_effect'] and st.session_state['first_no_side_effect']:
                st.session_state['CRM'] = True
            if st.session_state['CRM']:
                st.session_state['current_dose'], st.session_state['curr_theta'] = get_closest_dose(doses_values, threshold)
                st.session_state['theta_calculated'] = True
            else:
                st.session_state['current_dose'] += 1
                if st.session_state['current_dose'] >= doses_amount:
                    st.session_state['current_dose'] = doses_amount - 1

        st.experimental_rerun()


if 'patient_data' in st.session_state:
    if st.session_state['theta_calculated']:
        st.sidebar.markdown(f'## Theta estimate: {st.session_state["curr_theta"]}')
        doses_estimates = np.power(doses_values, st.session_state['curr_theta'])
    else:
        doses_estimates = doses_values
    st.sidebar.markdown('## Doses data:')
    for i in range(doses_amount):
        st.sidebar.markdown(f'## Dose {i+1}')
        st.sidebar.markdown(f'Patients: {st.session_state["patient_data"][i]["patients"]}')
        st.sidebar.markdown(f'Side Effects: {st.session_state["patient_data"][i]["side_effects"]}')
        st.sidebar.markdown(f'Estimate: {doses_estimates[i]}')

