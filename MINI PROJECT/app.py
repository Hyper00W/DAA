from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import osmnx as ox
import networkx as nx
import geopy.distance

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

place_name = "Chandigarh University, Sahibzada Ajit Singh Nagar, India"
print("Downloading road network, this may take a moment...")
G = ox.graph_from_place(place_name, network_type="walk")
G = nx.Graph(G)

node_positions = {node: (G.nodes[node]["y"], G.nodes[node]["x"]) for node in G.nodes}

campus_locations = {
    "Gate 1": (30.771879, 76.579789),
    "Gate 2": (30.771148, 76.576295),
    "A1": (30.771617, 76.578250),
    "A2": (30.769855, 76.579357),
    "B1": (30.769617, 76.575606),
    "SH": (30.770747, 76.577946),
    "FC": (30.768793, 76.577916),
    "CC/B2": (30.769084, 76.576279),
    "C1": (30.76711207441493, 76.575975843947),
    "C3": (30.767174255704376, 76.57485203246935),
    "C2": (30.766080680167207, 76.57610101328784),
    "Tagore Hostel": (30.766222627361326, 76.57571570105372),
    "Gate 4": (30.766129233861406, 76.57488115897749),
    "B2": (30.769205930294973, 76.57586920399194),
    "Corner Cafe": (30.769171060935538, 76.57631585216063),
    "B4": (30.768628735135334, 76.57452754799152),
    "DSW": (30.76860219001556, 76.57547866320283),
    "Playground": (30.767913889833643, 76.57579312682144),
    "HDFC Bank": (30.7705250780109, 76.57717662325923),
    "Transport Department": (30.770508945696456, 76.57692516617526),

}

def get_nearest_node(lat, lon):
    return ox.distance.nearest_nodes(G, lon, lat)

@app.route("/get_path", methods=["POST"])
def get_path():
    data = request.json
    start, end = data["start"], data["end"]

    if start == end:
        return jsonify({"error": "Start and destination cannot be the same"}), 400

    try:
        start_lat, start_lon = campus_locations[start]
        end_lat, end_lon = campus_locations[end]

        start_node = get_nearest_node(start_lat, start_lon)
        end_node = get_nearest_node(end_lat, end_lon)

        path_nodes = nx.shortest_path(G, start_node, end_node, weight="length")
        path_coords = [node_positions[node] for node in path_nodes]
        distance = nx.shortest_path_length(G, start_node, end_node, weight="length")

        return jsonify({"path": path_nodes, "coords": path_coords, "distance": distance})
    except nx.NetworkXNoPath:
        return jsonify({"error": "No path found"}), 400

@socketio.on("update_location")
def handle_location_update(data):
    lat, lon = data["latitude"], data["longitude"]
    socketio.emit("new_location", {"latitude": lat, "longitude": lon})

@app.route("/")
def index():
    return render_template("index.html", locations=list(campus_locations.keys()))

@app.route('/find_path', methods=['POST'])
def find_path():
    print("Received request:", request.json)  # Debugging line
    return jsonify({"status": "debug"})



if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
