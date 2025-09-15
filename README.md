# Flask CRUD API

A simple Flask application with complete CRUD (Create, Read, Update, Delete) operations for task management.

## Features

- ✅ Create new tasks
- ✅ Read all tasks or specific task by ID
- ✅ Update existing tasks
- ✅ Delete tasks
- ✅ Filter tasks by completion status
- ✅ Search tasks by title or description
- ✅ Health check endpoint
- ✅ Proper error handling and validation
- ✅ JSON responses

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Flask application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Health Check
- **GET** `/api/health`
- Returns API status and task count

### 2. Get All Tasks
- **GET** `/api/tasks`
- Query parameters:
  - `completed=true/false` - Filter by completion status
  - `search=term` - Search in title and description

### 3. Get Specific Task
- **GET** `/api/tasks/<task_id>`
- Returns a specific task by ID

### 4. Create Task
- **POST** `/api/tasks`
- Required fields: `title`, `description`
- Optional fields: `completed` (defaults to false)

### 5. Update Task
- **PUT** `/api/tasks/<task_id>`
- Fields to update: `title`, `description`, `completed`

### 6. Delete Task
- **DELETE** `/api/tasks/<task_id>`
- Removes the task from the system

## Example Usage

### Create a Task
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn Flask",
    "description": "Build a CRUD API with Flask",
    "completed": false
  }'
```

### Get All Tasks
```bash
curl http://localhost:5000/api/tasks
```

### Get Completed Tasks Only
```bash
curl "http://localhost:5000/api/tasks?completed=true"
```

### Search Tasks
```bash
curl "http://localhost:5000/api/tasks?search=flask"
```

### Update a Task
```bash
curl -X PUT http://localhost:5000/api/tasks/<task_id> \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn Flask - Updated",
    "completed": true
  }'
```

### Delete a Task
```bash
curl -X DELETE http://localhost:5000/api/tasks/<task_id>
```

## Testing

Run the included test script to verify all endpoints:

```bash
python test_api.py
```

Make sure the Flask app is running before executing the test script.

## API Documentation

Visit `http://localhost:5000/` to see the interactive API documentation with all available endpoints and example payloads.

## Data Structure

Each task has the following structure:
```json
{
  "id": "unique-uuid",
  "title": "Task title",
  "description": "Task description",
  "completed": false,
  "created_at": "2024-01-01T12:00:00.000000",
  "updated_at": "2024-01-01T12:00:00.000000"
}
```

## Notes

- This implementation uses in-memory storage for simplicity
- In production, replace with a proper database (PostgreSQL, MySQL, etc.)
- All timestamps are in ISO format
- Task IDs are generated using UUID4 for uniqueness
