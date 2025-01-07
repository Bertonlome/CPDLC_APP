from flask import Flask, jsonify, render_template, request
from datetime import datetime
import time
import signal
import sys
from agent import *

app = Flask(__name__)

# INGESCAPE STUFF
def signal_handler(signal_received, frame):
    global is_interrupted
    print("\n", signal.strsignal(signal_received), sep="")
    is_interrupted = True
    print("\n exiting the app...")
    sys.exit(0)
    
def on_agent_event_callback(event, uuid, name, event_data, my_data):
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    # add code here if needed
    
def on_freeze_callback(is_frozen, my_data):
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    # add code here if needed

def reset_callback(io_type, name, value_type, value, my_data):
    igs.info(f"Output reset")
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    agent_object.Exp_Taxi_Clearance = False
    agent_object.Engine_Startup = False
    agent_object.Pushback = False
    agent_object.Taxi_Clearance = False
    agent_object.De_Icing = False
    agent_object.Load = False
    agent_object.Wilco = False
    agent_object.Execute = False
    agent_object.Cancel = False
    agent_object.Standby = False
    agent_object.Unable = False

def set_bool(name, value, my_data):
    igs.info(f"Output {name} written to {value}")
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    if name == "expected_taxi_clearance":
        agent_object.Exp_Taxi_Clearance = value
    elif name == "engine_startup":
        agent_object.Engine_Startup = value
    elif name == "pushback":
        agent_object.Pushback = value
    elif name == "taxi_clearance":
        agent_object.Taxi_Clearance = value
    elif name == "de-icing":
        agent_object.De_Icing = value
    elif name == "load":
        agent_object.Load = value
    elif name == "wilco":
        agent_object.Wilco = value
    elif name == "execute":
        agent_object.Execute = value
    elif name == "cancel":
        agent_object.Cancel = value
    elif name == "standby":
        agent_object.Standby = value
    elif name == "unable":
        agent_object.Unable = value
    else:
        igs.error("Invalid output name")


def string_input_callback(io_type, name, value_type, value, my_data):
    global response
    igs.info(f"Input {name} written to {value}")
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    agent_object.stringI = value
    response["status"] = "closed"
    response["message"]= value

# INGESCAPE STUFF

# Constant for error message
INVALID_DATA_ERROR = "Invalid data"

# Mock ATC responses, the taxi clearance message will remain unchanged
ATC_RESPONSES = {
    "expected_taxi_clearance": "TAXI VIA C, C1, B, B1. HOLDSHORT RWY 24R",
    "engine_startup": "ENGINE STARTUP APPROVED",
    "pushback": "PUSHBACK APPROVED",
    "taxi_clearance": "TAXI CLEARANCE GRANTED",
    "de_icing": "DE-ICING NOT REQUIRED"
}

response = {
    "timestamp": None,
    "action": None,
    "message": None,
    "status": None
}

# The taxi clearance message will not be altered
TAXI_CLEARANCE_MESSAGE = "TAXI VIA C, C1, B, B1. HOLDSHORT RWY 24R"

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Log route
@app.route('/log', methods=['GET'])
def log_action():
    time.sleep(2)  # Simulate delay
    response = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "message": "ATC has acknowledged your log request. Proceed with actions.",
    }
    app.logger.info("Log request acknowledged.")
    return jsonify(response)

# Handle ATC requests
@app.route('/request/<action>', methods=['GET'])
def request_action(action):
    global response
    if action in ATC_RESPONSES:
        if action == "expected_taxi_clearance":
            set_bool("expected_taxi_clearance", True, agent)
        if action == "engine_startup":
            set_bool("engine_startup", True, agent)
        if action == "pushback":
            set_bool("pushback", True, agent)
        if action == "taxi_clearance":
            set_bool("taxi_clearance", True, agent)
        if action == "de-icing":
            set_bool("de-icing", True, agent)
        response = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "action": action.replace("_", " ").title(),
            "message": ATC_RESPONSES[action],
            "status": "open"
        }
        while response["status"] == "open":
            time.sleep(1)
        app.logger.info(f"Action requested: {action} - Response: {response}")
        return jsonify(response)
    else:
        app.logger.warning(f"Invalid action requested: {action}")
        return jsonify({"error": "Invalid action"}), 400

# Load taxi clearance
@app.route('/load', methods=['POST'])
def load_taxi_clearance():
    data = request.get_json()
    if data and data.get("requestType") == "loadTaxiClearance":
        if response["status"] == None or response["status"] == "open":
            return jsonify({"error": "Action in progress"}), 400
        set_bool("load", True, agent)
        time.sleep(1)  # Simulate processing delay
        response["timestamp"] = datetime.now().strftime("%H:%M:%S")
        app.logger.info("Taxi clearance data loaded.")
        return jsonify(response)
    else:
        app.logger.error("Invalid request type for loading taxi clearance.")
        return jsonify({"error": INVALID_DATA_ERROR}), 400

# Update action status
@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    if "action" in data and "status" in data:
        action = data["action"]
        status = data["status"]
        time.sleep(1)  # Simulate status update
        app.logger.info(f"Status updated for {action}: {status}")
        return jsonify({"message": "Status updated successfully", "new_status": status})

    app.logger.error(f"Invalid data for status update: {data}")
    return jsonify({"error": INVALID_DATA_ERROR}), 400

# Handle Wilco, Standby, and Unable actions
@app.route('/action/<button>', methods=['POST'])
def handle_action(button):
    time.sleep(1)  # Simulate processing delay
    valid_buttons = ["wilco", "standby", "unable"]
    if button in valid_buttons:
        if button == "wilco":
            set_bool("wilco", True, agent)
        elif button == "standby":
            set_bool("standby", True, agent)
        elif button == "unable":
            set_bool("unable", True, agent)
        response = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "message": f"ATC has acknowledged your '{button.upper()}' action.",
        }
        app.logger.info(f"Button '{button.upper()}' action processed.")
        return jsonify(response)
    else:
        app.logger.warning(f"Invalid button action attempted: {button}")
        return jsonify({"error": "Invalid button action"}), 400

# Execute endpoint - does not affect the taxi clearance message
@app.route('/execute', methods=['POST'])
def execute_action():
    data = request.get_json()
    if data:
        set_bool("execute", True, agent)
        if response["status"] == None or response["status"] == "open":
            return jsonify({"error": "Action in progress"}), 400
        time.sleep(1)  # Simulate processing delay
        response["timestamp"] =datetime.now().strftime("%H:%M:%S")
        app.logger.info("Execute action processed.")
        return jsonify(response)
    else:
        app.logger.error("Invalid data for execute action.")
        return jsonify({"error": INVALID_DATA_ERROR}), 400

# Cancel endpoint - does not affect the taxi clearance message
@app.route('/cancel', methods=['POST'])
def cancel_action():
    data = request.get_json()
    if data:
        set_bool("cancel", True, agent)
        time.sleep(1)  # Simulate processing delay
        response = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "message": "CANCEL action received, but taxi clearance remains unchanged: " + TAXI_CLEARANCE_MESSAGE,
        }
        app.logger.info("Cancel action processed.")
        return jsonify(response)
    else:
        app.logger.error("Invalid data for cancel action.")
        return jsonify({"error": INVALID_DATA_ERROR}), 400

# Error handler for 404
@app.errorhandler(404)
def not_found(error):
    app.logger.warning("Attempted access to a non-existent endpoint.")
    return jsonify({"error": "Endpoint not found"}), 404

# Error handler for 500
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

# Utility route for health check
@app.route('/health', methods=['GET'])
def health_check():
    app.logger.info("Health check performed.")
    return jsonify({"status": "OK", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

if __name__ == '__main__':
        
    port = 5670
    agent_name = "Pilot CPDLC APP"
    device = "wlo1"

    # catch SIGINT handler before starting agent
    signal.signal(signal.SIGINT, signal_handler)
    interactive_loop = False


    igs.agent_set_name(agent_name)
    igs.definition_set_version("1.0")
    igs.log_set_console(True)
    igs.log_set_file(True, None)
    igs.log_set_stream(True)
    igs.set_command_line(sys.executable + " " + " ".join(sys.argv))

    agent = Echo()

    igs.observe_agent_events(on_agent_event_callback, agent)
    igs.observe_freeze(on_freeze_callback, agent)

    igs.input_create("reset", igs.IMPULSION_T, None)
    igs.input_create("string", igs.STRING_T, None)

    igs.output_create("Expected_Taxi_Clearance", igs.BOOL_T, False)
    igs.output_create("Engine_Startup", igs.BOOL_T, None)
    igs.output_create("Pushback", igs.BOOL_T, None)
    igs.output_create("Taxi_Clearance", igs.BOOL_T, None)
    igs.output_create("De_Icing", igs.BOOL_T, None)
    igs.output_create("Load", igs.BOOL_T, None)
    igs.output_create("Wilco", igs.BOOL_T, None)
    igs.output_create("Execute", igs.BOOL_T, None)
    igs.output_create("Cancel", igs.BOOL_T, None)
    igs.output_create("Standby", igs.BOOL_T, None)
    igs.output_create("Unable", igs.BOOL_T, None)


    igs.observe_input("reset", reset_callback, agent)
    igs.observe_input("string", string_input_callback, agent)

    igs.log_set_console(True)
    igs.log_set_console_level(igs.LOG_INFO)

    igs.start_with_device(device, port)
    # catch SIGINT handler after starting agent
    signal.signal(signal.SIGINT, signal_handler)


    app.run(debug=True)
