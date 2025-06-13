import streamlit as st
new_task = st.text_input('Enter a new task', placeholder='e.g., Complete assignment')

if 'tasks' not in st.session_state:
    st.session_state.tasks = []
# Add button to store input
if st.button('Add Task'):
    if new_task.strip():
        st.session_state.tasks.append(new_task.strip())


st.subheader('Your Tasks:')
for i, task in enumerate(st.session_state.tasks):
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.write(f'{i+1}. {task}')
    with col2:
        if st.button('Delete', key=f'del_{i}'): 
            st.session_state.tasks.pop(i)
            st.rerun()  # Refresh the app to reflect changes

