# FitBuddy

FitBuddy is an AI-powered fitness plan generator built with:

- FastAPI
- Python
- Jinja2
- SQLite
- SQLAlchemy
- Google Gemini
- HTML
- CSS
- Pydantic

## Features

### 1. Personalized workout plan

Users provide:

- User ID
- Name
- Age
- Weight
- Fitness goal
- Workout intensity

FitBuddy generates a personalized 7-day workout plan.

### 2. Nutrition / recovery tip

FitBuddy generates a short nutrition or recovery recommendation.

### 3. AI feedback

Users can provide feedback such as:

"Add more cardio."

or:

"Make Friday a lighter recovery day."

FitBuddy generates a complete revised plan.

### 4. Database

SQLite stores:

- User information
- Original workout plan
- Updated workout plan
- Nutrition tip
- Creation time
- Update time

### 5. Admin dashboard

The admin can view registered users and their plans.

## Installation

Create a virtual environment:

Windows:

```powershell
py -m venv .venv