#!/bin/bash

APP_NAME="vite-todo-app"
echo "🚀 Creating $APP_NAME using Vite + React..."

# Create Vite app with React template
npm create vite@latest $APP_NAME -- --template react

cd $APP_NAME

# Install dependencies
npm install

# Overwrite App.jsx with todo logic$
cat > src/App.jsx << 'EOF'
import { useState } from 'react';
import './App.css';

function App() {
  const [todos, setTodos] = useState([]);
  const [input, setInput] = useState('');

  const handleAddTodo = () => {
    if (input.trim() === '') return;
    const newTodo = {
      id: Date.now(),
      text: input,
      completed: false,
    };
    setTodos([...todos, newTodo]);
    setInput('');
  };

  const handleDeleteTodo = (id) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  const handleToggleComplete = (id) => {
    setTodos(
      todos.map(todo =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      )
    );
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.heading}>📝 Vite + React Todo App</h1>

      <div style={styles.inputContainer}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Enter a todo"
          style={styles.input}
        />
        <button onClick={handleAddTodo} style={styles.button}>Add</button>
      </div>

      <ul style={styles.todoList}>
        {todos.map(todo => (
          <li key={todo.id} style={styles.todoItem}>
            <span
              style={{
                ...styles.todoText,
                textDecoration: todo.completed ? 'line-through' : 'none',
                color: todo.completed ? 'gray' : 'black',
              }}
            >
              {todo.text}
            </span>
            <div>
              <button onClick={() => handleToggleComplete(todo.id)} style={styles.smallButton}>
                {todo.completed ? 'Undo' : 'Done'}
              </button>
              <button onClick={() => handleDeleteTodo(todo.id)} style={styles.deleteButton}>
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;

const styles = {
  container: {
    maxWidth: '400px',
    margin: '50px auto',
    padding: '20px',
    borderRadius: '10px',
    backgroundColor: 'black',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  },
  heading: {
    textAlign: 'center',
    marginBottom: '20px',
    
  },
  inputContainer: {
    display: 'flex',
    gap: '10px',
    marginBottom: '20px',
  },
  input: {
    flex: 1,
    padding: '10px',
    fontSize: '16px',
  },
  button: {
    padding: '10px 15px',
    fontSize: '16px',
    backgroundColor: '#4CAF50',
    color: 'white',
    border: 'none',
    cursor: 'pointer',
  },
  todoList: {
    listStyle: 'none',
    padding: 0,
  },
  todoItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '10px',
    padding: '10px',
    backgroundColor: '#fff',
    borderRadius: '6px',
  },
  todoText: {
    fontSize: '16px',
  },
  smallButton: {
    marginRight: '10px',
    padding: '5px 10px',
  },
  deleteButton: {
    padding: '5px 10px',
    backgroundColor: '#ff4d4d',
    color: 'white',
    border: 'none',
  },
};
EOF

echo "✅ Setup complete!"
echo "👉 To start the app, run:"
echo "   cd $APP_NAME"
echo "   npm run dev"

xdg-open http://localhost:5173 &  # For Ubuntu


cd $APP_NAME
# Start the development server



npm run dev 



