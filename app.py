from flask import Flask, jsonify, render_template
import signal
from pathlib import Path
from echo import *

port = 5670
agent_name = "echo"
device = "wlo1"

ingescape_path = Path("~/Documents/IngeScape").expanduser()

app = Flask(__name__)

def return_io_value_type_as_str(value_type):
    if value_type == igs.INTEGER_T:
        return "Integer"
    elif value_type == igs.DOUBLE_T:
        return "Double"
    elif value_type == igs.BOOL_T:
        return "Bool"
    elif value_type == igs.STRING_T:
        return "String"
    elif value_type == igs.IMPULSION_T:
        return "Impulsion"
    elif value_type == igs.DATA_T:
        return "Data"
    else:
        return "Unknown"
    
def return_event_type_as_str(event_type):
    if event_type == igs.PEER_ENTERED:
        return "PEER_ENTERED"
    elif event_type == igs.PEER_EXITED:
        return "PEER_EXITED"
    elif event_type == igs.AGENT_ENTERED:
        return "AGENT_ENTERED"
    elif event_type == igs.AGENT_UPDATED_DEFINITION:
        return "AGENT_UPDATED_DEFINITION"
    elif event_type == igs.AGENT_KNOWS_US:
        return "AGENT_KNOWS_US"
    elif event_type == igs.AGENT_EXITED:
        return "AGENT_EXITED"
    elif event_type == igs.AGENT_UPDATED_MAPPING:
        return "AGENT_UPDATED_MAPPING"
    elif event_type == igs.AGENT_WON_ELECTION:
        return "AGENT_WON_ELECTION"
    elif event_type == igs.AGENT_LOST_ELECTION:
        return "AGENT_LOST_ELECTION"
    else:
        return "UNKNOWN"
    

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

# inputs
def impulsion_input_callback(io_type, name, value_type, value, my_data):
    igs.info(f"Input {name} written")
    igs.output_set_impulsion("impulsion")

def bool_input_callback(io_type, name, value_type, value, my_data):
    igs.info(f"Input {name} written to {value}")
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    agent_object.boolI = value
    agent_object.boolO = value

def integer_input_callback(io_type, name, value_type, value, my_data):
    igs.info(f"Input {name} written to {value}")
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    agent_object.integerI = value
    agent_object.integerO = value

def double_input_callback(io_type, name, value_type, value, my_data):
    igs.info(f"Input {name} written to {value}")
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    agent_object.doubleI = value
    agent_object.doubleO = value

def string_input_callback(io_type, name, value_type, value, my_data):
    igs.info(f"Input {name} written to {value}")
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    agent_object.stringI = value
    agent_object.stringO = value

def data_input_callback(io_type, name, value_type, value, my_data):
    igs.info(f"Input {name} written to {value}")
    agent_object = my_data
    assert isinstance(agent_object, Echo)
    agent_object.dataI = value
    agent_object.dataO = value




@app.route('/')
def index():
    return render_template('index.html')

@app.route('/request/<action>')
def handle_request(action):
    if action == 'engine-start':
        message = 'Engine Start Approved by ATC'
        string_input_callback(igs.STRING_T,"string",None,"Request ENGINE START",agent)
    elif action == 'pushback':
        message = 'Pushback Approved by ATC'
        string_input_callback(igs.STRING_T,"string",None,"Request PUSHBACK",agent)
    elif action == 'taxi-clearance':
        message = 'Taxi Clearance Approved: Proceed to Runway 24L'
        string_input_callback(igs.STRING_T,"string",None,"Request TAXI-CLEARANCE",agent)
    elif action == 'lineup':
        message = 'Lineup Approved by ATC'
        string_input_callback(igs.STRING_T,"string",None,"Request LINEUP",agent)
    elif action == 'takeoff-clearance':
        message = 'Takeoff Clearance Approved by ATC'
        string_input_callback(igs.STRING_T,"string",None,"Request TAKEOFF-CLEARANCE",agent)
    else:
        message = 'Request Not Recognized'
    
    # Show response buttons for specific requests (e.g., Taxi Clearance)
    show_response_buttons = action == 'taxi-clearance'
    
    return jsonify({'message': message, 'showResponseButtons': show_response_buttons})

@app.route('/response/<action>')
def handle_response(action):
    # Example logic for handling responses
    if action in ['wilco', 'standby', 'unable']:
        # Mark as success
        return jsonify({'status': 'success', 'request': 'taxi-clearance'})
    return jsonify({'status': 'error'})

if __name__ == '__main__':


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

    igs.input_create("impulsion", igs.IMPULSION_T, None)
    igs.input_create("bool", igs.BOOL_T, None)
    igs.input_create("integer", igs.INTEGER_T, None)
    igs.input_create("double", igs.DOUBLE_T, None)
    igs.input_create("string", igs.STRING_T, None)
    igs.input_create("data", igs.DATA_T, None)

    igs.output_create("impulsion", igs.IMPULSION_T, None)
    igs.output_create("bool", igs.BOOL_T, None)
    igs.output_create("integer", igs.INTEGER_T, None)
    igs.output_create("double", igs.DOUBLE_T, None)
    igs.output_create("string", igs.STRING_T, None)
    igs.output_create("data", igs.DATA_T, None)

    igs.observe_input("impulsion", impulsion_input_callback, agent)
    igs.observe_input("bool", bool_input_callback, agent)
    igs.observe_input("integer", integer_input_callback, agent)
    igs.observe_input("double", double_input_callback, agent)
    igs.observe_input("string", string_input_callback, agent)
    igs.observe_input("data", data_input_callback, agent)

    igs.log_set_console(True)
    igs.log_set_console_level(igs.LOG_INFO)

    igs.start_with_device(device, port)
    # catch SIGINT handler after starting agent
    signal.signal(signal.SIGINT, signal_handler)


    app.run(debug=True, use_reloader=False)
