BACKEND: FASTAPI
# server/main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import psycopg2
app = FastAPI()
# CORS setup for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Database connection
conn = psycopg2.connect(
    database="fitness_db",
    user="postgres",
    password="your_password",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()
# Pydantic models
class Workout(BaseModel):
    user_id: int
    type: str
    duration: int
    intensity: str
    calories: int
# Routes
@app.post("/workouts")
def log_workout(workout: Workout):
    query = """
        INSERT INTO workouts (user_id, type, duration, intensity, calories)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (workout.user_id, workout.type, workout.duration, workout.intensity, workout.calories))
    conn.commit()
    return {"message": "Workout logged successfully"}
@app.get("/workouts/{user_id}", response_model=List[Workout])
def get_workouts(user_id: int):
    cursor.execute("SELECT user_id, type, duration, intensity, calories FROM workouts WHERE user_id = %s", (user_id,))
    rows = cursor.fetchall()
    return [Workout(user_id=row[0], type=row[1], duration=row[2], intensity=row[3], calories=row[4]) for row in rows]

#FRONTEND: REACT 
// client/src/App.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
const API = "http://localhost:8000";
function App() {
  const [workout, setWorkout] = useState({ user_id: 1, type: "", duration: "", intensity: "", calories: "" });
  const [workouts, setWorkouts] = useState([]);

  const handleChange = (e) => {
    setWorkout({ ...workout, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await axios.post(`${API}/workouts`, workout);
    fetchWorkouts();
  };

  const fetchWorkouts = async () => {
    const res = await axios.get(`${API}/workouts/1`);
    setWorkouts(res.data);
  };

  useEffect(() => {
    fetchWorkouts();
  }, []);

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Fitness Tracker</h1>

      <form onSubmit={handleSubmit} className="space-y-2">
        <input className="w-full p-2 border" name="type" placeholder="Workout Type" onChange={handleChange} />
        <input className="w-full p-2 border" name="duration" placeholder="Duration (min)" onChange={handleChange} />
        <input className="w-full p-2 border" name="intensity" placeholder="Intensity" onChange={handleChange} />
        <input className="w-full p-2 border" name="calories" placeholder="Calories Burned" onChange={handleChange} />
        <button className="bg-blue-500 text-white p-2 rounded">Log Workout</button>
      </form>

      <div className="mt-6">
        <h2 className="text-xl font-semibold">Logged Workouts</h2>
        <ul className="mt-2 space-y-2">
          {workouts.map((w, i) => (
            <li key={i} className="border p-2 rounded">
              <p>{w.type} - {w.duration} min - {w.calories} cal</p>
              <p className="text-sm text-gray-500">Intensity: {w.intensity}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;
### FRONTEND SETUP 
// Tailwind setup (client/tailwind.config.js, index.css)
// Install Tailwind via https://tailwindcss.com/docs/guides/vite

// Vite config (vite.config.js)
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
});