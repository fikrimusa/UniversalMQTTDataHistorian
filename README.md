# Universal MQTT Data Historian

A real-time IoT data storage platform that captures MQTT messages and stores them in SQLite database for historical analysis and data persistence.

## Why Universal MQTT Data Historian?
### Problem
- IoT devices generate continuous data streams
- MQTT brokers don't store message history
- Real-time data is lost without persistence
- Need for historical analysis and auditing

### Solution
- Capture all MQTT messages in real-time
- Store structured data in SQLite database
- Provide REST API for data access
- Enable historical data analysis and reporting

## System Architecture

![Architecture Diagram](/docs/SystemArchitecture.png)

## Features
- **Data Persistence**: Never lose IoT device messages
- **Historical Analysis**: Query past data for trends and patterns
- **Data Backup**: SQLite provides reliable local storage
- **API Access**: Programmatic access to stored data
- **Web Interface**: Real-time monitoring and visualization

## Project Structure
```bash
src/
├── main.py (FastAPI application)
├──database.py (SQLite database operations)
├── mqttClient.py (MQTT client management)
├── messageParser.py (Message parsing and analysis)
├── deviceSimulator.py (IoT device simulator)
├──websocketManager.py (WebSocket connection management)
static/
├── index.html (Web dashboard)
├── css/style.css (Dashboard styling)
├── js/dashboard.js (Frontend logic)
```

## API Endpoints
- `GET /` - API information
- `GET /status` - System health check
- `GET /messages` - Retrieve stored messages
- `GET /topics` - Discovered topics analysis
- `POST /publish/{topic}` - Publish MQTT messages
- `GET /dashboard` - Web dashboard
- `GET /api/stats` - System statistics
- `GET /api/queued-messages` - Real-time message queue
- `WS /ws` - WebSocket for live updates

## Run the application
Separate terminal windows are recommended for running the main application and the device simulator.
```
python3 src/main.py
python3 src/deviceSimulator.py
```
## Access the services
- API: `http://localhost:8000/`
- Dashboard: `http://localhost:8000/dashboard`
- SQLite Database: `mqtt_data.db`
- REST API Documentation: `http://localhost:8000/docs`

![IotMessageDashboard](/docs/IoTMessageDashboard.png)

![Database](/docs/database.png)

## License
This project is licensed under the MIT License.