import streamlit as st

st.set_page_config(page_title='📝 ToDo App', layout='centered')

st.title('✅ ToDo App in Streamlit')

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

def add_task():
    new_task = st.session_state.new_task.strip()
    if new_task:
        st.session_state.tasks.append({'title': new_task, 'done': False})
        st.session_state.new_task = ''

st.text_input('🆕 Add a task:', key='new_task', on_change=add_task, placeholder='Type and press Enter...')

st.subheader('📋 Your Tasks')

if not st.session_state.tasks:
    st.info('No tasks yet. Add one above!')
else:
    for i in range(len(st.session_state.tasks)):
        task = st.session_state.tasks[i]
        col1, col2, col3 = st.columns([0.1, 0.8, 0.1])

        with col1:
            if col1.checkbox('', value=task['done'], key=f'check_{i}'):
                st.session_state.tasks[i]['done'] = not task['done']

        with col2:
            st.markdown(
                # follow the correct syntax of f strings always use f'{'someting'}'
                task['title'] + (' ✅' if task['done'] else '')
            )

        with col3:
            if col3.button('🗑️', key=f'delete_{i}'):
                del st.session_state.tasks[i]
                st.rerun()
                break  # Important: exit the loop after deletion to avoid indexing errors

