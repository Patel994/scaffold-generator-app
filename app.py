import math
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# --- NEW: Re-engineered Calculation Engine ---
def _calculate_facade_scaffold(length, width, height, working_levels, include_ladder):
    
    # --- Base Unit Logic from your specs ---
    LIFT_HEIGHT = 6.5  # Standard vertical distance between rosettes in feet
    PLANK_WIDTH = 1.0  # Based on 5 planks for a 5ft width
    
    # --- Determine Bay Configuration ---
    # For simplicity in this example, we'll use the user's specified bay sizes.
    # A more advanced version could select from a list of available ledger sizes.
    bay_length = 7.0 # Using your example
    bay_width = 5.0  # Using your example
    
    num_bays = math.ceil(length / bay_length)
    num_vertical_runs = num_bays + 1
    num_lifts = math.ceil(height / LIFT_HEIGHT)

    materials = {}
    
    # --- 1. Base Components ---
    materials['Base Jacks / Collars (Starter)'] = num_vertical_runs * 2 # One of each

    # --- 2. Standards (Verticals) ---
    materials['Standards (Verticals)'] = num_vertical_runs * num_lifts

    # --- 3. Ledgers & Transoms (Calculated per lift) ---
    # Initialize with the base structural ledgers for all lifts
    materials[f'{bay_length} ft Ledgers'] = num_bays * (num_lifts + 1) * 2 # Front and back
    materials[f'{bay_width} ft Ledgers (Transoms)'] = num_vertical_runs * (num_lifts + 1) # End and internal
    
    # Add extra guardrails ONLY for the specified number of working levels
    materials[f'{bay_length} ft Ledgers'] += num_bays * working_levels * 2 # Mid & Top rails
    materials[f'{bay_width} ft Ledgers (Transoms)'] += 2 * working_levels * 2 # Mid & Top rails for the two ends

    # --- 4. Planks, Toe Boards & Bracing for WORKING levels ---
    materials['Steel Planks'] = math.ceil(width / PLANK_WIDTH) * num_bays * working_levels
    materials['Bay Braces'] = num_bays * 4 * working_levels # 2 per side per your spec
    
    # Toe boards for working levels
    materials[f'{bay_length} ft Toe Boards'] = num_bays * working_levels
    materials[f'{bay_width} ft Toe Boards'] = 2 * working_levels # Two ends
    
    # --- 5. Ladder Access Modification ---
    ladders = {}
    if include_ladder:
        # On each working level, modify one bay
        # Remove 1 long ledger (top rail) and 1 long toeboard
        materials[f'{bay_length} ft Ledgers'] -= 1 * working_levels
        materials[f'{bay_length} ft Toe Boards'] -= 1 * working_levels
        
        # Add 2 x 4ft ledgers and 1 x 4ft toeboard for the opening per working level
        materials['4 ft Ledgers (for ladder access)'] = 2 * working_levels
        materials['4 ft Toe Boards (for ladder access)'] = 1 * working_levels
        
        # --- 6. Calculate Ladder Sections ---
        deck_height_per_level = height / working_levels
        LADDER_SECTIONS = [5, 4, 3]
        height_to_climb = deck_height_per_level
        
        for section_size in LADDER_SECTIONS:
            num_sections = math.floor(height_to_climb / section_size)
            if num_sections > 0:
                ladders[f'{section_size} ft Ladder Section'] = ladders.get(f'{section_size} ft Ladder Section', 0) + num_sections
                height_to_climb -= num_sections * section_size
        if height_to_climb > 0: # Add smallest section for remainder
            ladders['3 ft Ladder Section'] = ladders.get('3 ft Ladder Section', 0) + 1
        
        # Multiply by number of working levels minus one (no ladder needed from top level)
        for key in ladders:
            ladders[key] *= working_levels

    # --- Final Assembly ---
    summary_details = {
        "Scaffold Type": "Facade Scaffold",
        "Bay Configuration": f"{num_bays} bay(s) @ {bay_length}ft x {bay_width}ft",
        "Overall Dimensions": f"~{num_bays * bay_length}ft L x {width}ft W x {height}ft H"
    }
    
    # Add ladders to the main material list if they exist
    if ladders:
        materials['--- LADDERS ---'] = '' # A separator for display
        materials.update(ladders)

    return {"materials": {k: (v if v != '' else '') for k, v in materials.items()}, "summary_details": summary_details}


# --- API Endpoint ---
@app.route('/api/generate', methods=['POST'])
def api_generate():
    data = request.get_json()
    scaffold_type = data.get('scaffold_type')
    summary, materials = {}, {}

    if scaffold_type == 'facade':
        calc_result = _calculate_facade_scaffold(
            float(data.get('length', 0)), float(data.get('width', 0)),
            float(data.get('height', 0)), int(data.get('working_levels', 0)),
            bool(data.get('include_ladder', False))
        )
        summary = calc_result['summary_details']
        materials = calc_result['materials']
    
    return jsonify({"summary": summary, "materials": materials})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)