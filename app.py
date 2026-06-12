import streamlit as st
import streamlit.components.v1 as components
import time
import json
import re
import textwrap
import os
import requests

# Load .env file manually if it exists to retrieve API keys locally
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

# Helper function to prevent indented HTML strings from being interpreted as code blocks by markdown parser
def render_html(html_str):
    dedented = textwrap.dedent(html_str).strip()
    # Flatten the HTML by removing newlines and leading whitespace on each line, preventing markdown code block conversion
    flattened = "".join(line.strip() for line in dedented.split("\n"))
    st.markdown(flattened, unsafe_allow_html=True)

# Set page configuration for wide layout and premium title
st.set_page_config(
    page_title="Agentic AI Multi-Agent Virtual Lab",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global premium CSS styling to overwrite standard Streamlit styling with dark cyber theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Font applications */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
    }
    
    /* Main background styling */
    .stApp {
        background-color: #070913;
        background-image: 
            radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.04) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(16, 185, 129, 0.02) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(168, 85, 247, 0.03) 0px, transparent 50%);
    }

    /* Glassmorphism containers */
    div[data-testid="stVerticalBlock"] > div.element-container {
        margin-bottom: 0.5rem;
    }
    
    .glass-card {
        background-color: rgba(20, 27, 48, 0.6);
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 18px;
        backdrop-filter: blur(12px);
        margin-bottom: 15px;
    }
    
    /* Custom headers and badges */
    .custom-title {
        font-size: 2.2rem;
        background: linear-gradient(135deg, #ffffff 40%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .custom-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 25px;
    }

    .agent-badge {
        font-size: 0.65rem;
        font-weight: 600;
        padding: 2px 6px;
        border-radius: 4px;
        background-color: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Terminal Console Display */
    .terminal-box {
        background-color: #05070f;
        border: 1px solid #1e293b;
        border-radius: 10px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        padding: 15px;
        color: #e2e8f0;
        height: 380px;
        overflow-y: auto;
        box-shadow: inset 0 2px 8px rgba(0,0,0,0.8);
    }
    
    .term-line {
        margin-bottom: 6px;
        line-height: 1.4;
    }
    
    .term-system { color: #818cf8; font-weight: 600; }
    .term-thinking { color: #f59e0b; }
    .term-tool { color: #38bdf8; }
    .term-reply { color: #34d399; }
    .term-error { color: #f87171; font-weight: 600; }
    
    /* Chat bubbles */
    .chat-container {
        border: 1px solid #1e293b;
        border-radius: 10px;
        background-color: rgba(7, 9, 19, 0.4);
        padding: 15px;
        height: 380px;
        overflow-y: auto;
    }
    
    .chat-bubble {
        display: flex;
        gap: 10px;
        margin-bottom: 12px;
        max-width: 85%;
    }
    
    .chat-avatar {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        color: white;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        flex-shrink: 0;
    }
    
    .chat-content-box {
        background-color: rgba(30, 41, 59, 0.4);
        border: 1px solid #1e293b;
        border-radius: 0 12px 12px 12px;
        padding: 8px 12px;
        font-size: 0.85rem;
        color: #e2e8f0;
    }
    
    /* Active Node Flow Styles */
    .flow-wrapper {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 20px 0;
        padding: 15px;
        background-color: rgba(20, 27, 48, 0.4);
        border: 1px solid #1e293b;
        border-radius: 12px;
    }
    
    .flow-node {
        flex: 1;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #1e293b;
        background-color: rgba(13, 18, 34, 0.8);
        font-size: 0.8rem;
        font-weight: 600;
        transition: all 0.3s;
        max-width: 170px;
    }
    
    .flow-node.idle {
        opacity: 0.5;
        border-color: #1e293b;
    }
    .flow-node.thinking {
        border-color: #f59e0b;
        box-shadow: 0 0 12px rgba(245, 158, 11, 0.3);
        background-color: rgba(245, 158, 11, 0.05);
    }
    .flow-node.completed {
        border-color: #10b981;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
    }
    .flow-node.failed {
        border-color: #ef4444;
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.3);
    }
    
    .flow-arrow {
        color: #1e293b;
        font-size: 1.2rem;
        padding: 0 5px;
    }
    
    .flow-arrow.active {
        color: #6366f1;
        animation: arrowPulse 1.5s infinite;
    }
    
    @keyframes arrowPulse {
        0% { opacity: 0.3; }
        50% { opacity: 1; }
        100% { opacity: 0.3; }
    }
    
    /* Prompt Evaluator Scorecard UI styling */
    .eval-score-card {
        text-align: center;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #1e293b;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.05));
        margin-bottom: 20px;
    }
    .eval-score-val {
        font-family: 'Outfit', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 5px;
    }
    .eval-component-card {
        background-color: rgba(13, 18, 34, 0.5);
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# 1. SCENARIOS DEFINITIONS
# --------------------------------------------------------------------------

SCENARIOS = {
    "library": {
        "title": "Library Book Borrowing Assistant",
        "icon": "📚",
        "desc": "Is scenario mein user ko Artificial Intelligence ki book kal assignment ke liye chahiye. Multi-Agent system milkar book search, availability check, reservation aur notification ka kaam karta hai.",
        "default_query": "I need the book 'Artificial Intelligence' for my assignment.",
        "agents": [
            {
                "name": "Book Search Agent",
                "role": "Agent library catalog aur digital database search karta hai.",
                "tools": ["QueryCatalogDB", "CheckISBN"],
                "default_prompt": "Role: Book Search Agent\nContext: Library catalog aur digital database.\nTask: Kaunsi library mein yeh book available hai?\nConstraints: Return matching details."
            },
            {
                "name": "Availability Agent",
                "role": "Current issue records aur reservations check kiye jaate hain.",
                "tools": ["CheckShelfStock", "GetReservationsCount"],
                "default_prompt": "Role: Availability Agent\nContext: Current issue records and reservations.\nTask: Kya book abhi available hai?\nConstraints: Verify physical copies."
            },
            {
                "name": "Reservation Agent",
                "role": "Student eligibility aur borrowing limit verify ki jaati hai.",
                "tools": ["HoldCopyDB", "CheckUserBorrowLimit"],
                "default_prompt": "Role: Reservation Agent\nContext: Student eligibility database.\nTask: Kya student ke liye book reserve ki ja sakti hai?\nConstraints: Ensure limit not exceeded."
            },
            {
                "name": "Notification Agent",
                "role": "Reservation ID generate karke email/SMS bheja jaata hai.",
                "tools": ["DispatchEmail", "GenerateBarcode"],
                "default_prompt": "Role: Notification Agent\nContext: Confirmation notification systems.\nTask: Student ko confirmation kaise milega?\nConstraints: Dispatch email/SMS."
            }
        ],
        "parameters": [
            {"id": "book_title", "label": "Book Title", "type": "select", "options": ["Artificial Intelligence", "Advanced Python Coding", "Organic Chemistry"], "default": "Artificial Intelligence"},
            {"id": "in_stock", "label": "Copy Available on Shelf", "type": "checkbox", "default": True},
            {"id": "borrow_limit", "label": "Student Active Borrows", "type": "slider", "options": [0, 5, 1], "default": 1}
        ]
    },
    "flight": {
        "title": "Flight Check-In Assistant",
        "icon": "✈️",
        "desc": "Is scenario mein user ki flight kal hai aur use online check-in karke window seat chahiye.",
        "default_query": "My flight is tomorrow. Please complete check-in with a window seat.",
        "agents": [
            {
                "name": "Flight Verification Agent",
                "role": "PNR, flight date aur check-in window verify ki jaati hai.",
                "tools": ["QueryPnrDB", "VerifyIdentityStatus"],
                "default_prompt": "Role: Flight Verification Agent\nContext: Flight ticketing system.\nTask: Kya ticket check-in ke liye valid hai?\nConstraints: Check date and check-in window."
            },
            {
                "name": "Seat Selection Agent",
                "role": "Seat map analyze karke best window seat choose ki jaati hai.",
                "tools": ["GetCabinMap", "LockSeatAPI"],
                "default_prompt": "Role: Seat Selection Agent\nContext: Seat layout maps.\nTask: Kaunsi window seat available hai?\nConstraints: Pick best window seat."
            },
            {
                "name": "Check-In Agent",
                "role": "Passenger details aur baggage allowance verify kiya jaata hai.",
                "tools": ["SubmitManifest", "CompleteRegistration"],
                "default_prompt": "Role: Check-In Agent\nContext: Manifest update registry.\nTask: Kya online check-in complete ho sakta hai?\nConstraints: Verify baggage constraints."
            },
            {
                "name": "Notification Agent",
                "role": "Boarding pass PDF generate karke email aur app mein send kiya jaata hai.",
                "tools": ["GenerateQRCode", "SendSMSAlert"],
                "default_prompt": "Role: Notification Agent\nContext: Delivery verification.\nTask: Boarding pass kaise deliver hoga?\nConstraints: Email/SMS boarding pass PDF."
            }
        ],
        "parameters": [
            {"id": "ticket_valid", "label": "Ticket Booking Status", "type": "select", "options": ["Confirmed", "Invalid PNR / Cancelled"], "default": "Confirmed"},
            {"id": "seat_pref", "label": "Seat Preference", "type": "select", "options": ["Window", "Aisle", "Exit Row"], "default": "Window"}
        ]
    },
    "doctor": {
        "title": "Doctor Appointment Booking",
        "icon": "🏥",
        "desc": "Is scenario mein user ko kal evening mein doctor appointment minimum waiting time ke saath book karni hai.",
        "default_query": "I have a fever and need to see a doctor tomorrow evening with minimum waiting time.",
        "agents": [
            {
                "name": "Doctor Search Agent",
                "role": "Location aur specialty ke basis par doctors search kiye jaate hain.",
                "tools": ["SearchClinicsAPI", "MatchSymptoms", "CalculateProximity"],
                "default_prompt": "Role: Doctor Search Agent\nContext: Registered doctor directories.\nTask: Kal evening mein kaunse doctors available hain?\nConstraints: Limit search by distance and specialty."
            },
            {
                "name": "Slot Selection Agent",
                "role": "Appointment queues compare ki jaati hain.",
                "tools": ["GetAvailabilityList", "ReserveSlotDB"],
                "default_prompt": "Role: Slot Selection Agent\nContext: Clinic schedule lists.\nTask: Kis slot mein sabse kam waiting time hai?\nConstraints: Compare active queues."
            },
            {
                "name": "Approval Agent",
                "role": "Doctor details aur consultation fee dikhayi jaati hai.",
                "tools": ["CheckConsultationFee", "ValidateGatewayStatus"],
                "default_prompt": "Role: Approval Agent\nContext: Booking validation and fee presentation.\nTask: Kya user appointment approve karta hai?\nConstraints: Ensure fee is approved by budget."
            },
            {
                "name": "Booking Agent",
                "role": "Slot reserve karke booking ID generate ki jaati hai.",
                "tools": ["ScheduleSMSGate", "CreateCalendarInvite"],
                "default_prompt": "Role: Booking Agent\nContext: Final booking system database.\nTask: Kya appointment book ki ja sakti hai?\nConstraints: Generate receipt and reminders."
            }
        ],
        "parameters": [
            {"id": "illness", "label": "Patient Symptoms", "type": "select", "options": ["Fever", "Toothache", "Fracture (Emergency)"], "default": "Fever"},
            {"id": "time", "label": "Preferred Time", "type": "select", "options": ["Morning (09:00 - 12:00)", "Afternoon (13:00 - 17:00)"], "default": "Morning (09:00 - 12:00)"},
            {"id": "budget", "label": "Max Consultation Budget (₹)", "type": "slider", "options": [200, 1500, 600], "default": 600}
        ]
    },
    "hotel": {
        "title": "Hotel Room Extension Assistant",
        "icon": "🏨",
        "desc": "Yahaan user apna hotel stay 2 din aur extend karna chahta hai.",
        "default_query": "I want to stay two more days in my room.",
        "agents": [
            {
                "name": "Booking Verification Agent",
                "role": "Booking database verify kiya jaata hai.",
                "tools": ["GetStayDetails", "VerifyIdentity"],
                "default_prompt": "Role: Booking Verification Agent\nContext: Hotel PMS systems.\nTask: Kya booking valid hai?\nConstraints: Confirm registration status."
            },
            {
                "name": "Room Availability Agent",
                "role": "Hotel inventory check ki jaati hai.",
                "tools": ["CheckRoomInventory", "FindAlternativeRoom"],
                "default_prompt": "Role: Room Availability Agent\nContext: Room schedules.\nTask: Kya same room agle 2 din available hai?\nConstraints: Verify back-to-back reservations."
            },
            {
                "name": "Payment Agent",
                "role": "Room charges, tax aur service charges calculate kiye jaate hain.",
                "tools": ["CalculateExtensionCost", "ChargeCreditCard"],
                "default_prompt": "Role: Payment Agent\nContext: Folio calculation tools.\nTask: Additional charge kitna hoga?\nConstraints: Calculate total additional charge."
            },
            {
                "name": "Confirmation Agent",
                "role": "Payment verify karke booking update ki jaati hai.",
                "tools": ["ExtendKeycardAccess", "UpdateCheckOutDatePMS"],
                "default_prompt": "Role: Confirmation Agent\nContext: Keycard RFID and checkout dates database.\nTask: Kya booking extend ho sakti hai?\nConstraints: Output extended checkout details."
            }
        ],
        "parameters": [
            {"id": "room_num", "label": "Current Room Number", "type": "text", "default": "Room 304"},
            {"id": "extend_days", "label": "Extension Days", "type": "slider", "options": [1, 7, 2], "default": 2},
            {"id": "room_available", "label": "Current Room Available for Extension", "type": "checkbox", "default": True},
            {"id": "card_declined", "label": "Simulate Credit Card Decline", "type": "checkbox", "default": False}
        ]
    },
    "commute": {
        "title": "Daily Commute Management",
        "icon": "🚗",
        "desc": "User office 9 baje se pehle minimum travel time mein pahunchna chahta hai.",
        "default_query": "How can I reach office on time before 9 AM today?",
        "agents": [
            {
                "name": "Traffic Monitoring Agent",
                "role": "Live traffic data analyze kiya jaata hai.",
                "tools": ["GetLiveTrafficAlerts", "QueryIncidentDB"],
                "default_prompt": "Role: Traffic Monitoring Agent\nContext: Live GPS coordinates.\nTask: Current traffic condition kya hai?\nConstraints: Report blocks or accidents."
            },
            {
                "name": "Route Optimization Agent",
                "role": "Sabhi routes ki ETA compare ki jaati hai.",
                "tools": ["ComputeShortestPath", "EstimateTravelTime"],
                "default_prompt": "Role: Route Optimization Agent\nContext: Route networks.\nTask: Kya koi faster route available hai?\nConstraints: Compare all routes."
            },
            {
                "name": "Transport Booking Agent",
                "role": "User preference aur cab availability check ki jaati hai.",
                "tools": ["RequestCabRide", "ConfirmRideCost"],
                "default_prompt": "Role: Transport Booking Agent\nContext: Rideshare API integrations.\nTask: Kya transport book karna hai?\nConstraints: Lock fare prices."
            },
            {
                "name": "Notification Agent",
                "role": "Live ETA aur alerts send kiye jaate hain.",
                "tools": ["SendSMSAlert", "GetLiveCabLocation"],
                "default_prompt": "Role: Notification Agent\nContext: Alert system.\nTask: User ko updates kaise milenge?\nConstraints: Send vehicle plate and ETA."
            }
        ],
        "parameters": [
            {"id": "traffic_congestion", "label": "Route A Traffic Level", "type": "select", "options": ["Heavy Congestion (Accident)", "Moderate Traffic", "Light Traffic"], "default": "Heavy Congestion (Accident)"},
            {"id": "cab_type", "label": "Cab Category Choice", "type": "select", "options": ["Prime Sedan", "Mini Eco", "Auto Rickshaw"], "default": "Prime Sedan"}
        ]
    },
    "skill": {
        "title": "Skill Development Assistant",
        "icon": "🎯",
        "desc": "User agle 12 months mein Data Scientist banna chahta hai.",
        "default_query": "I want to become a Data Scientist in the next 12 months.",
        "agents": [
            {
                "name": "Career Analysis Agent",
                "role": "Goal ko analyze karke required role identify kiya jaata.",
                "tools": ["FetchCareerProfile", "QuerySkillDatabase"],
                "default_prompt": "Role: Career Analysis Agent\nContext: Career goal mapping.\nTask: User ka career goal kya hai?\nConstraints: Identify expected certifications."
            },
            {
                "name": "Skill Gap Agent",
                "role": "Current skills aur required skills compare ki jaati hain.",
                "tools": ["AssessStudentProfile", "ListMissingSkills"],
                "default_prompt": "Role: Skill Gap Agent\nContext: Comparing student background against profile.\nTask: Kaun si skills missing hain?\nConstraints: Group into skill levels."
            },
            {
                "name": "Course Recommendation Agent",
                "role": "Best rated courses search aur rank kiye jaate hain.",
                "tools": ["SearchCourseCatalogs", "MatchCertifications"],
                "default_prompt": "Role: Course Recommendation Agent\nContext: Course catalogs.\nTask: Kaunse courses help karenge?\nConstraints: Recommend high-rated learning paths."
            },
            {
                "name": "Progress Tracking Agent",
                "role": "Learning plan aur milestones create kiye jaate hain.",
                "tools": ["GenerateSyllabusChecklist", "ScheduleWeeklyReminders"],
                "default_prompt": "Role: Progress Tracking Agent\nContext: Weekly planning metrics.\nTask: Progress kaise monitor hogi?\nConstraints: Generate syllabus checkpoints."
            }
        ],
        "parameters": [
            {"id": "career_goal", "label": "Target Career Goal", "type": "select", "options": ["Data Scientist", "Full-Stack Web Developer", "Cloud Solutions Architect"], "default": "Data Scientist"},
            {"id": "known_skills", "label": "Skills You Already Know", "type": "select", "options": ["None (Beginner)", "Basic Python & SQL", "JavaScript & HTML5", "Linux & Shell Scripting"], "default": "Basic Python & SQL"}
        ]
    },
    "vacation": {
        "title": "Vacation Planning Assistant",
        "icon": "🌴",
        "desc": "User ko ₹30,000 ke andar 5 din ki vacation plan karni hai.",
        "default_query": "Plan a 5-day vacation under ₹30,000.",
        "agents": [
            {
                "name": "Destination Recommendation Agent",
                "role": "Popular destinations aur total cost compare ki jaati hai.",
                "tools": ["FilterDestinationsByPrice", "QueryWeatherAPI"],
                "default_prompt": "Role: Destination Recommendation Agent\nContext: Flight and hotel cost listings.\nTask: Budget mein kaunsi destinations possible hain?\nConstraints: Suggest options within total budget."
            },
            {
                "name": "Budget Planning Agent",
                "role": "Travel, stay aur food cost analyze ki jaati hai.",
                "tools": ["EstimateHotelCosts", "SearchCheapFlights"],
                "default_prompt": "Role: Budget Planning Agent\nContext: Pricing indices.\nTask: Sabse best value destination kaunsi hai?\nConstraints: Factor in hotel, flights, food."
            },
            {
                "name": "Booking Agent",
                "role": "Availability check karke booking ki jaati hai.",
                "tools": ["PlaceTemporaryHoldHotel", "LockFlightSeat"],
                "default_prompt": "Role: Booking Agent\nContext: Booking systems.\nTask: Kya travel aur hotel book kiya ja sakta hai?\nConstraints: Secure reservations."
            },
            {
                "name": "Itinerary Agent",
                "role": "Attractions aur travel time optimize kiya jaata hai.",
                "tools": ["GetLocalActivities", "CompileItineraryPdf"],
                "default_prompt": "Role: Itinerary Agent\nContext: Day-wise scheduling.\nTask: Day-wise plan kya hoga?\nConstraints: Optimize activities and sightseeing."
            }
        ],
        "parameters": [
            {"id": "budget_val", "label": "Vacation Budget Limit (₹)", "type": "slider", "options": [15000, 80000, 30000], "default": 30000},
            {"id": "duration", "label": "Vacation Duration", "type": "select", "options": ["3 Days", "5 Days", "7 Days"], "default": "5 Days"},
            {"id": "travelers", "label": "Number of Travelers", "type": "slider", "options": [1, 5, 2], "default": 2}
        ]
    }
}

# Initialize session states
if "selected_scenario" not in st.session_state:
    st.session_state.selected_scenario = "doctor"
if "current_step" not in st.session_state:
    st.session_state.current_step = 0
if "logs" not in st.session_state:
    st.session_state.logs = ["[SYSTEM] Ready. Select a scenario and run to start simulation."]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "custom_prompts" not in st.session_state:
    st.session_state.custom_prompts = {}
if "run_counter" not in st.session_state:
    st.session_state.run_counter = 0
if "query_override" not in st.session_state:
    st.session_state.query_override = ""
if "param_values" not in st.session_state:
    st.session_state.param_values = {}
if "shared_state" not in st.session_state:
    st.session_state.shared_state = {}
if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = os.getenv("GROQ_API_KEY", "")

# Load default prompts into session state if not exist
for s_key, s_val in SCENARIOS.items():
    if s_key not in st.session_state.custom_prompts:
        st.session_state.custom_prompts[s_key] = {}
        for agent in s_val["agents"]:
            st.session_state.custom_prompts[s_key][agent["name"]] = agent["default_prompt"]


# --------------------------------------------------------------------------
# 2. SIMULATION DYNAMIC REASONING ENGINE (PYTHON)
# --------------------------------------------------------------------------

def get_agent_instruction(scenario_key, agent_name):
    # Retrieve modified prompt if edits were made, else default
    return st.session_state.custom_prompts[scenario_key].get(agent_name, "")

def run_agent_simulation_step(scenario_key, step_num, params, user_q):
    """
    Simulates execution for a single agent. Returns (log_lines, chat_msg, success_bool)
    """
    scenario = SCENARIOS[scenario_key]
    agent = scenario["agents"][step_num]
    agent_name = agent["name"]
    prompt = get_agent_instruction(scenario_key, agent_name)
    
    log_lines = []
    chat_msg = None
    state_mutations = {}
    success = True
    
    # --------------------------------------------------
    # Doctor Scenario Simulation Logic
    # --------------------------------------------------
    if scenario_key == "doctor":
        illness = params.get("illness", "Fever")
        time_pref = params.get("time", "Morning")
        budget = params.get("budget", 600)
        
        if step_num == 0:  # Doctor Search Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Kal evening mein kaunse doctors available hain?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Location aur specialty ke basis par doctors search kiye jaate hain.")
            chat_msg = {
                "sender": agent_name, "avatar": "🩺",
                "content": "4 doctors available mile."
            }
            state_mutations = {"matched_doctors_count": 4, "illness": illness, "time_pref": time_pref}
            
        elif step_num == 1:  # Slot Selection Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Kis slot mein sabse kam waiting time hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Appointment queues compare ki jaati hain.")
            chat_msg = {
                "sender": agent_name, "avatar": "📅",
                "content": "6 PM slot available hai with only 10 minutes wait."
            }
            state_mutations = {"booking_slot": "6:00 PM", "waiting_time": "10 mins", "booking_status": "Slot Checked"}
            
        elif step_num == 2:  # Approval Agent
            fee = 500
            log_lines.append(f"[AGENT: {agent_name}] Question: Kya user appointment approve karta hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Doctor details aur consultation fee dikhayi jaati hai.")
            if fee > budget:
                log_lines.append(f"[AGENT: {agent_name}] [CRITICAL ERROR] Fee ₹{fee} exceeds budget ₹{budget}!")
                chat_msg = {
                    "sender": agent_name, "avatar": "💳",
                    "content": f"Warning! Consultation fee is ₹{fee}, which exceeds your budget limit of ₹{budget}. User rejected."
                }
                state_mutations = {"payment_verified": False, "booking_status": "Failed", "error": "Budget Exceeded"}
                success = False
            else:
                chat_msg = {
                    "sender": agent_name, "avatar": "💳",
                    "content": "User approved."
                }
                state_mutations = {"payment_verified": True, "fee_charged": fee, "booking_status": "Approved"}
                
        elif step_num == 3:  # Booking Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Kya appointment book ki ja sakti hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Slot reserve karke booking ID generate ki jaati hai.")
            chat_msg = {
                "sender": agent_name, "avatar": "🔔",
                "content": "Appointment confirmed."
            }
            state_mutations = {"booking_confirmed": True, "booking_status": "Confirmed", "booking_id": "APT-58291"}

    # --------------------------------------------------
    # Library Scenario Simulation Logic
    # --------------------------------------------------
    elif scenario_key == "library":
        book_title = params.get("book_title", "Artificial Intelligence")
        in_stock = params.get("in_stock", True)
        borrow_limit = params.get("borrow_limit", 1)
        
        if step_num == 0:  # Book Search Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Kaunsi library mein yeh book available hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Agent library catalog aur digital database search karta hai.")
            chat_msg = {
                "sender": agent_name, "avatar": "🔍",
                "content": "AI Fundamentals book Central Library mein mil gayi."
            }
            state_mutations = {"book_title": book_title, "catalog_exists": True}
            
        elif step_num == 1:  # Availability Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Kya book abhi available hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Current issue records aur reservations check kiye jaate hain.")
            if not in_stock:
                chat_msg = {
                    "sender": agent_name, "avatar": "📦",
                    "content": "No copies available on the shelf. Adding to waitlist."
                }
                state_mutations = {"copies_available": 0, "waitlist_needed": True}
            else:
                chat_msg = {
                    "sender": agent_name, "avatar": "📦",
                    "content": "2 copies available hain."
                }
                state_mutations = {"copies_available": 2, "waitlist_needed": False}
                
        elif step_num == 2:  # Reservation Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Kya student ke liye book reserve ki ja sakti hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Student eligibility aur borrowing limit verify ki jaati hai.")
            if borrow_limit >= 3:
                log_lines.append(f"[AGENT: {agent_name}] [CRITICAL ERROR] Student has borrowed {borrow_limit} books (Limit: 3).")
                chat_msg = {
                    "sender": agent_name, "avatar": "🔐",
                    "content": "Reservation failed. Student borrowing limit exceeded."
                }
                state_mutations = {"reservation_locked": False, "reservation_status": "Blocked - Limit Reached", "error": "Limit Exceeded"}
                success = False
            else:
                chat_msg = {
                    "sender": agent_name, "avatar": "🔐",
                    "content": "Reservation successful."
                }
                state_mutations = {"reservation_locked": True, "reservation_status": "Reserved", "hold_id": 58291}
                
        elif step_num == 3:  # Notification Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Student ko confirmation kaise milega?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Reservation ID generate karke email/SMS bheja jaata hai.")
            chat_msg = {
                "sender": agent_name, "avatar": "✉️",
                "content": "Pickup details student ko send kar di gayi."
            }
            state_mutations = {"notification_sent": True, "notification_type": "SMS/Email", "barcode": "LIB-HOLD-58291", "reservation_status": "Reserved"}

    # --------------------------------------------------
    # Flight Scenario Simulation Logic
    # --------------------------------------------------
    elif scenario_key == "flight":
        ticket_valid = params.get("ticket_valid", "Confirmed")
        seat_pref = params.get("seat_pref", "Window")
        
        if step_num == 0:  # Flight Verification Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Kya ticket check-in ke liye valid hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: PNR, flight date aur check-in window verify ki jaati hai.")
            if ticket_valid != "Confirmed":
                log_lines.append(f"[AGENT: {agent_name}] [CRITICAL ERROR] Ticket status is invalid.")
                chat_msg = {
                    "sender": agent_name, "avatar": "✈️",
                    "content": "Check-in rejected. Booking status is invalid."
                }
                state_mutations = {"ticket_verified": False, "checkin_status": "Failed", "error": "Invalid Ticket"}
                success = False
            else:
                chat_msg = {
                    "sender": agent_name, "avatar": "✈️",
                    "content": "Booking confirmed."
                }
                state_mutations = {"ticket_verified": True, "checkin_status": "Verified"}
                
        elif step_num == 1:  # Seat Selection Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Kaunsi window seat available hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Seat map analyze karke best window seat choose ki jaati hai.")
            chat_msg = {
                "sender": agent_name, "avatar": "💺",
                "content": "Window Seat 18A select ho gayi."
            }
            state_mutations = {"assigned_seat": "18A", "seat_type": "Window"}
            
        elif step_num == 2:  # Check-In Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Kya online check-in complete ho sakta hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Passenger details aur baggage allowance verify kiya jaata hai.")
            chat_msg = {
                "sender": agent_name, "avatar": "✅",
                "content": "Check-in successful."
            }
            state_mutations = {"checkin_completed": True, "checkin_status": "Successful"}
            
        elif step_num == 3:  # Notification Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Boarding pass kaise deliver hoga?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Boarding pass PDF generate karke email aur app mein send kiya jaata hai.")
            chat_msg = {
                "sender": agent_name, "avatar": "📱",
                "content": "Boarding pass successfully send ho gaya."
            }
            state_mutations = {"boarding_pass_sent": True, "delivery_channel": "Email & App"}

    # --------------------------------------------------
    # Hotel Scenario Simulation Logic
    # --------------------------------------------------
    elif scenario_key == "hotel":
        room_num = params.get("room_num", "Room 304")
        room_available = params.get("room_available", True)
        card_declined = params.get("card_declined", False)
        extend_days = params.get("extend_days", 2)
        
        if step_num == 0:  # Booking Verification Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Kya booking valid hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Booking database verify kiya jaata hai.")
            chat_msg = {
                "sender": agent_name, "avatar": "🏨",
                "content": "Active booking found."
            }
            state_mutations = {"booking_valid": True, "guest_name": "Arpit Rawat"}
            
        elif step_num == 1:  # Room Availability Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Kya same room agle 2 din available hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Hotel inventory check ki jaati hai.")
            if not room_available:
                chat_msg = {
                    "sender": agent_name, "avatar": "🧹",
                    "content": f"Room {room_num} is occupied. Alternate room 412 is available."
                }
                state_mutations = {"room_available_same": False, "target_room": "Room 412", "daily_rate": 2000}
            else:
                chat_msg = {
                    "sender": agent_name, "avatar": "🧹",
                    "content": "Same room available hai."
                }
                state_mutations = {"room_available_same": True, "target_room": room_num, "daily_rate": 2000}
                
        elif step_num == 2:  # Payment Agent
            rate = 2000
            total_bill = rate * extend_days
            log_lines.append(f"[AGENT: {agent_name}] Question: Additional charge kitna hoga?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Room charges, tax aur service charges calculate kiye jaate hain.")
            if card_declined:
                log_lines.append(f"[AGENT: {agent_name}] [CRITICAL ERROR] Credit Card processor returned status: DECLINED.")
                chat_msg = {
                    "sender": agent_name, "avatar": "💵",
                    "content": f"Credit Card decline! Total additional charge ₹{total_bill}. Stay extension aborted."
                }
                state_mutations = {"payment_processed": False, "error": "Payment Declined", "checkout_status": "Overdue tomorrow"}
                success = False
            else:
                chat_msg = {
                    "sender": agent_name, "avatar": "💵",
                    "content": f"Total additional charge ₹{total_bill}."
                }
                state_mutations = {"payment_processed": True, "total_charged": total_bill}
                
        elif step_num == 3:  # Confirmation Agent
            t_room = st.session_state.shared_state.get("target_room", room_num)
            log_lines.append(f"[AGENT: {agent_name}] Question: Kya booking extend ho sakta hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Payment verify karke booking update ki jaati hai.")
            chat_msg = {
                "sender": agent_name, "avatar": "🔑",
                "content": "Stay successfully extended."
            }
            state_mutations = {"keycard_extended": True, "final_room": t_room, "status": "Stay Extended Successful"}

    # --------------------------------------------------
    # Daily Commute Scenario Simulation Logic
    # --------------------------------------------------
    elif scenario_key == "commute":
        congestion = params.get("traffic_congestion", "Heavy Congestion (Accident)")
        cab_type = params.get("cab_type", "Prime Sedan")
        
        if step_num == 0:  # Traffic Monitoring Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Current traffic condition kya hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Live traffic data analyze kiya jaata hai.")
            if congestion == "Heavy Congestion (Accident)":
                chat_msg = {
                    "sender": agent_name, "avatar": "🚦",
                    "content": "Route A par heavy traffic hai."
                }
                state_mutations = {"route_a_traffic": "Blocked", "route_a_time": 55}
            elif congestion == "Moderate Traffic":
                chat_msg = {
                    "sender": agent_name, "avatar": "🚦",
                    "content": "Route A has moderate traffic."
                }
                state_mutations = {"route_a_traffic": "Slow", "route_a_time": 35}
            else:
                chat_msg = {
                    "sender": agent_name, "avatar": "🚦",
                    "content": "Route A is clear."
                }
                state_mutations = {"route_a_traffic": "Clear", "route_a_time": 20}
                
        elif step_num == 1:  # Route Optimization Agent
            a_time = st.session_state.shared_state.get("route_a_time", 55)
            log_lines.append(f"[AGENT: {agent_name}] Question: Kya koi faster route available hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Sabhi routes ki ETA compare ki jaati hai.")
            if a_time > 30:
                chat_msg = {
                    "sender": agent_name, "avatar": "🗺️",
                    "content": "Route B fastest hai."
                }
                state_mutations = {"selected_route": "Route B", "commute_time_mins": 25}
            else:
                chat_msg = {
                    "sender": agent_name, "avatar": "🗺️",
                    "content": "Route A fastest hai."
                }
                state_mutations = {"selected_route": "Route A", "commute_time_mins": a_time}
                
        elif step_num == 2:  # Transport Booking Agent
            sel_route = st.session_state.shared_state.get("selected_route", "Route B")
            log_lines.append(f"[AGENT: {agent_name}] Question: Kya transport book karna hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: User preference aur cab availability check ki jaati hai.")
            price = 450 if "Sedan" in cab_type else (300 if "Mini" in cab_type else 150)
            chat_msg = {
                "sender": agent_name, "avatar": "🚖",
                "content": f"Cab booked via {sel_route}."
            }
            state_mutations = {"cab_booked": True, "driver_details": "Rajesh Kumar (Rating: 4.9)", "license_plate": "DL 1CA 4829", "cab_fare": price}
            
        elif step_num == 3:  # Notification Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: User ko updates kaise milenge?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Live ETA aur alerts send kiye jaate hain.")
            chat_msg = {
                "sender": agent_name, "avatar": "🔔",
                "content": "Updates successfully sent."
            }
            state_mutations = {"commute_notified": True, "commute_status": "On its way"}

    # --------------------------------------------------
    # Skill Scenario Simulation Logic
    # --------------------------------------------------
    elif scenario_key == "skill":
        goal = params.get("career_goal", "Data Scientist")
        known = params.get("known_skills", "Basic Python & SQL")
        
        if step_num == 0:  # Career Analysis Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: User ka career goal kya hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Goal ko analyze karke required role identify kiya yaata.")
            chat_msg = {
                "sender": agent_name, "avatar": "🎓",
                "content": f"Goal identified – {goal}."
            }
            state_mutations = {"career_goal": goal}
            
        elif step_num == 1:  # Skill Gap Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Kaun si skills missing hain?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Current skills aur required skills compare ki jaati hain.")
            chat_msg = {
                "sender": agent_name, "avatar": "📊",
                "content": "Python, SQL, Machine Learning aur Data Visualization missing hain."
            }
            state_mutations = {"missing_skills": ["Python", "SQL", "Machine Learning", "Data Visualization"]}
            
        elif step_num == 2:  # Course Recommendation Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Kaunse courses help karenge?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Best rated courses search aur rank kiye jaate hain.")
            chat_msg = {
                "sender": agent_name, "avatar": "📖",
                "content": "Personalized learning path recommended."
            }
            state_mutations = {"recommended_courses": [
                {"skill": "Python", "course": "Python for Data Analysis", "cost": "Free Audit"},
                {"skill": "SQL", "course": "Advanced SQL Databases", "cost": "₹499"},
                {"skill": "Machine Learning", "course": "Introduction to Machine Learning", "cost": "Free Audit"}
            ]}
            
        elif step_num == 3:  # Progress Tracking Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Progress kaise monitor hogi?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Learning plan aur milestones create kiye jaate hain.")
            chat_msg = {
                "sender": agent_name, "avatar": "🏆",
                "content": "12-month learning plan ready."
            }
            state_mutations = {"roadmap_ready": True, "weeks_to_complete": 12}

    # --------------------------------------------------
    # Vacation Scenario Simulation Logic
    # --------------------------------------------------
    elif scenario_key == "vacation":
        budget = params.get("budget_val", 30000)
        dur = params.get("duration", "5 Days")
        travelers = params.get("travelers", 2)
        
        if step_num == 0:  # Destination Recommendation Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Budget mein kaunsi destinations possible hain?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Popular destinations aur total cost compare ki jaati hai.")
            chat_msg = {
                "sender": agent_name, "avatar": "🏖️",
                "content": "Jaipur, Goa aur Udaipur options mile."
            }
            state_mutations = {"dest_list": ["Jaipur", "Goa", "Udaipur"]}
            
        elif step_num == 1:  # Budget Planning Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Sabse best value destination kaunsi hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Travel, stay aur food cost analyze ki jaati hai.")
            chat_msg = {
                "sender": agent_name, "avatar": "💸",
                "content": "Jaipur selected."
            }
            state_mutations = {"selected_dest": {"city": "Jaipur", "avg_cost": 18000}, "total_est": 18000}
            
        elif step_num == 2:  # Booking Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Kya travel aur hotel book kiya ja sakta hai?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Availability check karke booking ki jaati hai.")
            chat_msg = {
                "sender": agent_name, "avatar": "🏨",
                "content": "Travel aur hotel successfully booked."
            }
            state_mutations = {"booking_confirmed": True, "booking_reference": "VAC-5928-HTL"}
            
        elif step_num == 3:  # Itinerary Agent
            log_lines.append(f"[AGENT: {agent_name}] Question: Day-wise plan kya hoga?")
            log_lines.append(f"[AGENT: {agent_name}] Logic: Attractions aur travel time optimize kiya jaata hai.")
            chat_msg = {
                "sender": agent_name, "avatar": "🗺️",
                "content": "Complete 5-day itinerary generated."
            }
            state_mutations = {"itinerary_ready": True, "itinerary_id": "ITIN-JAIPUR-05"}
            
    # Commit changes
    for key, val in state_mutations.items():
        st.session_state.shared_state[key] = val
        
    return log_lines, chat_msg, success


# --------------------------------------------------------------------------
# 3. PREMIUM HTML ARTIFACT GENERATOR FOR OUTPUTS
# --------------------------------------------------------------------------

def render_outcome_receipt(scenario_key):
    """
    Returns visual HTML mockup card for the final artifact of the pipeline
    """
    state = st.session_state.shared_state
    
    if scenario_key == "doctor":
        status = state.get("booking_status", "Declined")
        if status == "Confirmed" or status == "Approved":
            doc_name = "Dr. Sharma"
            slot = state.get("booking_slot", "6:00 PM")
            illness = state.get("illness", "Fever")
            fee = state.get("fee_charged", 500)
            
            html = f"""
            <div style="background:#ffffff; color:#1e293b; border-radius:16px; padding:22px; font-family:'Outfit', 'Inter', sans-serif; box-shadow:0 10px 25px rgba(0,0,0,0.08); border-top:6px solid #6366f1; max-width:360px; margin:auto; border-left:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0; box-sizing:border-box;">
                <div style="text-align:center; border-bottom:2px dashed #cbd5e1; padding-bottom:12px; margin-bottom:14px;">
                    <div style="font-size:1.3rem; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; color:#4f46e5;">🩺 Clinic Appointment</div>
                    <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Digital Confirmation Voucher</div>
                </div>
                <div style="display:flex; flex-direction:column; gap:8px; font-size:0.85rem; border-bottom:2px dashed #cbd5e1; padding-bottom:14px; margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Patient:</span><span style="font-weight:600; color:#0f172a;">Arpit Rawat</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Symptom:</span><span style="font-weight:600; color:#0f172a;">{illness}</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Physician:</span><span style="font-weight:600; color:#0f172a;">{doc_name}</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Time slot:</span><span style="font-weight:600; color:#6366f1;">Tomorrow at {slot}</span></div>
                    <div style="display:flex; justify-content:space-between; border-top:1px solid #f1f5f9; padding-top:6px; font-weight:700;"><span style="color:#64748b;">Consultation Fee:</span><span style="color:#0f172a;">₹{fee}</span></div>
                </div>
                <div style="margin-bottom:14px;">
                    <div style="font-weight:700; font-size:0.85rem; color:#475569; margin-bottom:8px;">📋 Final Output Checklist:</div>
                    <div style="display:flex; flex-direction:column; gap:6px;">
                        <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Appointment Confirmed</div>
                        <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Reminder Set</div>
                        <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Receipt Generated</div>
                    </div>
                </div>
                <div style="background:#e0e7ff; border-left:4px solid #6366f1; padding:10px 12px; border-radius:6px;">
                    <div style="font-weight:700; font-size:0.75rem; color:#4338ca; margin-bottom:2px; display:flex; align-items:center; gap:4px;">💡 Key Takeaway:</div>
                    <div style="font-size:0.75rem; color:#312e81; line-height:1.35; font-style:italic;">"System best doctor aur minimum waiting time wala slot automatically select karta hai."</div>
                </div>
            </div>
            """
        else: # Failure / Declined
            error_reason = state.get("error", "Insufficient Budget")
            html = f"""
            <div style="background:#fff; color:#0f172a; border-radius:16px; padding:22px; font-family:'Outfit', 'Inter', sans-serif; box-shadow:0 10px 25px rgba(0,0,0,0.08); border-top:6px solid #ef4444; max-width:360px; margin:auto; text-align:center; box-sizing:border-box; border-left:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0;">
                <div style="color:#ef4444; font-size:3rem; margin-bottom:10px;">❌</div>
                <div style="font-size:1.2rem; font-weight:800; text-transform:uppercase; color:#ef4444; letter-spacing:0.5px;">Booking Refused</div>
                <div style="font-size:0.85rem; color:#64748b; margin:10px 0 20px 0;">Reason: {error_reason} (Consultation cost exceeds user defined budget limit).</div>
                <div style="font-size:0.75rem; background:#fee2e2; color:#ef4444; padding:8px 12px; border-radius:6px; font-weight:600; letter-spacing:0.5px;">STATUS: TRANSACTION_ABORTED</div>
            </div>
            """
        return html
    
    elif scenario_key == "library":
        status = state.get("reservation_status", "Denied")
        if status == "Failed" or "Limit" in status or "Blocked" in status:
            error_reason = state.get("error", "Limit Exceeded")
            html = f"""
            <div style="background:#fff; color:#0f172a; border-radius:16px; padding:22px; font-family:'Outfit', 'Inter', sans-serif; box-shadow:0 10px 25px rgba(0,0,0,0.08); border-top:6px solid #ef4444; max-width:360px; margin:auto; text-align:center; box-sizing:border-box; border-left:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0;">
                <div style="color:#ef4444; font-size:3rem; margin-bottom:10px;">🔐</div>
                <div style="font-size:1.2rem; font-weight:800; text-transform:uppercase; color:#ef4444; letter-spacing:0.5px;">Loan Blocked</div>
                <div style="font-size:0.85rem; color:#64748b; margin:10px 0 20px 0;">Reason: {error_reason} (Student limit of 3 books already reached).</div>
                <div style="font-size:0.75rem; background:#fee2e2; color:#ef4444; padding:8px 12px; border-radius:6px; font-weight:600; letter-spacing:0.5px;">ACTION REQUIRED: RETURN AN ACTIVE LOAN</div>
            </div>
            """
        else:
            book = state.get("book_title", "Artificial Intelligence")
            bar = state.get("barcode", "LIB-HOLD-58291")
            
            html = f"""
            <div style="background:#ffffff; color:#1e293b; border-radius:16px; padding:22px; font-family:'Outfit', 'Inter', sans-serif; box-shadow:0 10px 25px rgba(0,0,0,0.08); border-top:6px solid #10b981; max-width:360px; margin:auto; border-left:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0; box-sizing:border-box;">
                <div style="text-align:center; border-bottom:2px dashed #cbd5e1; padding-bottom:12px; margin-bottom:14px;">
                    <div style="font-size:1.3rem; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; color:#059669;">📚 Library Borrow Pass</div>
                    <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Digital Reservation Slip</div>
                </div>
                <div style="display:flex; flex-direction:column; gap:8px; font-size:0.85rem; border-bottom:2px dashed #cbd5e1; padding-bottom:14px; margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Student ID:</span><span style="font-weight:600; color:#0f172a;">#2948</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Target Book:</span><span style="font-weight:600; color:#0f172a; text-align:right;">{book}</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Reservation Status:</span><span style="font-weight:700; color:#10b981;">{status}</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Hold Period:</span><span style="font-weight:600; color:#0f172a;">48 Hours</span></div>
                </div>
                <div style="margin-bottom:14px;">
                    <div style="font-weight:700; font-size:0.85rem; color:#475569; margin-bottom:8px;">📋 Final Output Checklist:</div>
                    <div style="display:flex; flex-direction:column; gap:6px;">
                        <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Book Reserved</div>
                        <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Reservation ID Generated</div>
                        <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Pickup Notification Sent</div>
                    </div>
                </div>
                <div style="background:#ecfdf5; border-left:4px solid #10b981; padding:10px 12px; border-radius:6px;">
                    <div style="font-weight:700; font-size:0.75rem; color:#047857; margin-bottom:2px; display:flex; align-items:center; gap:4px;">💡 Key Takeaway:</div>
                    <div style="font-size:0.75rem; color:#065f46; line-height:1.35; font-style:italic;">"Yahaan agents sequentially kaam karte hain aur user ko bina manually search kiye book reserve karke dete hain."</div>
                </div>
            </div>
            """
        return html
        
    elif scenario_key == "flight":
        status = state.get("checkin_status", "Failed")
        if status == "Failed" or "Failed" in state.get("error", ""):
            html = f"""
            <div style="background:#fff; color:#0f172a; border-radius:16px; padding:22px; font-family:'Outfit', 'Inter', sans-serif; box-shadow:0 10px 25px rgba(0,0,0,0.08); border-top:6px solid #ef4444; max-width:360px; margin:auto; text-align:center; box-sizing:border-box; border-left:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0;">
                <div style="color:#ef4444; font-size:3rem; margin-bottom:10px;">⚠️</div>
                <div style="font-size:1.2rem; font-weight:800; text-transform:uppercase; color:#ef4444; letter-spacing:0.5px;">Check-in Denied</div>
                <div style="font-size:0.85rem; color:#64748b; margin:10px 0 20px 0;">No active flight booking located under PNR AI-720. Verification failed.</div>
                <div style="font-size:0.75rem; background:#fee2e2; color:#ef4444; padding:8px 12px; border-radius:6px; font-weight:600; letter-spacing:0.5px;">REASON: INVALID_PNR_RECORD</div>
            </div>
            """
        else:
            seat = state.get("assigned_seat", "18A")
            
            html = f"""
            <div style="background:#ffffff; color:#1e293b; border-radius:16px; padding:22px; font-family:'Outfit', 'Inter', sans-serif; box-shadow:0 10px 25px rgba(0,0,0,0.08); border-top:6px solid #0284c7; max-width:360px; margin:auto; border-left:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0; box-sizing:border-box;">
                <div style="text-align:center; border-bottom:2px dashed #cbd5e1; padding-bottom:12px; margin-bottom:14px;">
                    <div style="font-size:1.3rem; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; color:#0284c7;">✈️ Airline Pass</div>
                    <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Digital Boarding Voucher</div>
                </div>
                <div style="display:flex; flex-direction:column; gap:8px; font-size:0.85rem; border-bottom:2px dashed #cbd5e1; padding-bottom:14px; margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Flight:</span><span style="font-weight:600; color:#0f172a;">AI-502</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Seat Assignment:</span><span style="font-weight:700; color:#0284c7;">{seat} (Window)</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">PNR:</span><span style="font-weight:600; color:#0f172a; font-family:monospace;">AI-720</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Route:</span><span style="font-weight:600; color:#0f172a;">DEL ➔ BOM</span></div>
                </div>
                <div style="margin-bottom:14px;">
                    <div style="font-weight:700; font-size:0.85rem; color:#475569; margin-bottom:8px;">📋 Final Output Checklist:</div>
                    <div style="display:flex; flex-direction:column; gap:6px;">
                        <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Check-in Completed</div>
                        <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Seat Assigned</div>
                        <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Boarding Pass Sent</div>
                    </div>
                </div>
                <div style="background:#e0f2fe; border-left:4px solid #0284c7; padding:10px 12px; border-radius:6px;">
                    <div style="font-weight:700; font-size:0.75rem; color:#0369a1; margin-bottom:2px; display:flex; align-items:center; gap:4px;">💡 Key Takeaway:</div>
                    <div style="font-size:0.75rem; color:#075985; line-height:1.35; font-style:italic;">"Multi-Agent system poora check-in process automate karta hai aur user ka time bachata hai."</div>
                </div>
            </div>
            """
        return html
        
    elif scenario_key == "hotel":
        if state.get("payment_processed") == False or "Declined" in state.get("error", ""):
            html = f"""
            <div style="background:#fff; color:#0f172a; border-radius:16px; padding:22px; font-family:'Outfit', 'Inter', sans-serif; box-shadow:0 10px 25 rgba(0,0,0,0.08); border-top:6px solid #ef4444; max-width:360px; margin:auto; text-align:center; box-sizing:border-box; border-left:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0;">
                <div style="color:#ef4444; font-size:3rem; margin-bottom:10px;">💳</div>
                <div style="font-size:1.2rem; font-weight:800; text-transform:uppercase; color:#ef4444; letter-spacing:0.5px;">Extension Aborted</div>
                <div style="font-size:0.85rem; color:#64748b; margin:10px 0 20px 0;">Folio Payment Declined! Credit card transaction failed authorization.</div>
                <div style="font-size:0.75rem; background:#fee2e2; color:#ef4444; padding:8px 12px; border-radius:6px; font-weight:600; letter-spacing:0.5px;">VISIT RECEPTION COUNTER IMMEDIATELY</div>
            </div>
            """
        else:
            room = state.get("final_room", "Room 304")
            bill = state.get("total_charged", 4000)
            
            html = f"""
            <div style="background:#ffffff; color:#1e293b; border-radius:16px; padding:22px; font-family:'Outfit', 'Inter', sans-serif; box-shadow:0 10px 25px rgba(0,0,0,0.08); border-top:6px solid #ea580c; max-width:360px; margin:auto; border-left:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0; box-sizing:border-box;">
                <div style="text-align:center; border-bottom:2px dashed #cbd5e1; padding-bottom:12px; margin-bottom:14px;">
                    <div style="font-size:1.3rem; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; color:#ea580c;">🏨 Hotel Room Extension</div>
                    <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Digital Room Extension Voucher</div>
                </div>
                <div style="display:flex; flex-direction:column; gap:8px; font-size:0.85rem; border-bottom:2px dashed #cbd5e1; padding-bottom:14px; margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Guest Name:</span><span style="font-weight:600; color:#0f172a;">Arpit Rawat</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Assigned Room:</span><span style="font-weight:700; color:#ea580c;">{room}</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Status:</span><span style="font-weight:600; color:#059669;">Stay Extended</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Folio Bill:</span><span style="font-weight:600; color:#0f172a;">₹{bill} (Charged to Card)</span></div>
                </div>
                <div style="margin-bottom:14px;">
                    <div style="font-weight:700; font-size:0.85rem; color:#475569; margin-bottom:8px;">📋 Final Output Checklist:</div>
                    <div style="display:flex; flex-direction:column; gap:6px;">
                        <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Stay Extended</div>
                        <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> New Checkout Date</div>
                        <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Receipt Generated</div>
                    </div>
                </div>
                <div style="background:#fff7ed; border-left:4px solid #ea580c; padding:10px 12px; border-radius:6px;">
                    <div style="font-weight:700; font-size:0.75rem; color:#c2410c; margin-bottom:2px; display:flex; align-items:center; gap:4px;">💡 Key Takeaway:</div>
                    <div style="font-size:0.75rem; color:#9a3412; line-height:1.35; font-style:italic;">"Multiple agents booking verification se lekar payment aur confirmation tak ka kaam automate karte hain."</div>
                </div>
            </div>
            """
        return html
        
    elif scenario_key == "commute":
        driver = state.get("driver_details", "Rajesh Kumar")
        plate = state.get("license_plate", "DL 1CA 4829")
        fare = state.get("cab_fare", 450)
        route = state.get("selected_route", "Route B")
        
        html = f"""
        <div style="background:#ffffff; color:#1e293b; border-radius:16px; padding:22px; font-family:'Outfit', 'Inter', sans-serif; box-shadow:0 10px 25px rgba(0,0,0,0.08); border-top:6px solid #475569; max-width:360px; margin:auto; border-left:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0; box-sizing:border-box;">
            <div style="text-align:center; border-bottom:2px dashed #cbd5e1; padding-bottom:12px; margin-bottom:14px;">
                <div style="font-size:1.3rem; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; color:#475569;">🚖 Commute Voucher</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Digital Dispatch Slip</div>
            </div>
            <div style="display:flex; flex-direction:column; gap:8px; font-size:0.85rem; border-bottom:2px dashed #cbd5e1; padding-bottom:14px; margin-bottom:14px;">
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Driver:</span><span style="font-weight:600; color:#0f172a;">{driver}</span></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Vehicle License:</span><span style="font-weight:700; color:#475569; font-family:monospace;">{plate}</span></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Route Selected:</span><span style="font-weight:600; color:#0f172a;">{route} (Fastest)</span></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">ETA to Pickup:</span><span style="font-weight:600; color:#059669;">5 Minutes</span></div>
                <div style="display:flex; justify-content:space-between; border-top:1px solid #f1f5f9; padding-top:6px; font-weight:700;"><span style="color:#64748b;">Est. Fare:</span><span style="color:#0f172a;">₹{fare}</span></div>
            </div>
            <div style="margin-bottom:14px;">
                <div style="font-weight:700; font-size:0.85rem; color:#475569; margin-bottom:8px;">📋 Final Output Checklist:</div>
                <div style="display:flex; flex-direction:column; gap:6px;">
                    <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Best Route Selected</div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Cab Booked</div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> ETA Shared</div>
                </div>
            </div>
            <div style="background:#f1f5f9; border-left:4px solid #475569; padding:10px 12px; border-radius:6px;">
                <div style="font-weight:700; font-size:0.75rem; color:#334155; margin-bottom:2px; display:flex; align-items:center; gap:4px;">💡 Key Takeaway:</div>
                <div style="font-size:0.75rem; color:#475569; line-height:1.35; font-style:italic;">"Real-time data ka use karke system travel time ko optimize karta hai."</div>
            </div>
        </div>
        """
        return html
        
    elif scenario_key == "skill":
        goal = state.get("career_goal", "Data Scientist")
        
        html = f"""
        <div style="background:#ffffff; color:#1e293b; border-radius:16px; padding:22px; font-family:'Outfit', 'Inter', sans-serif; box-shadow:0 10px 25px rgba(0,0,0,0.08); border-top:6px solid #0f766e; max-width:360px; margin:auto; border-left:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0; box-sizing:border-box;">
            <div style="text-align:center; border-bottom:2px dashed #cbd5e1; padding-bottom:12px; margin-bottom:14px;">
                <div style="font-size:1.3rem; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; color:#0f766e;">🎯 Career Roadmap</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Digital Syllabus Package</div>
            </div>
            <div style="display:flex; flex-direction:column; gap:8px; font-size:0.85rem; border-bottom:2px dashed #cbd5e1; padding-bottom:14px; margin-bottom:14px;">
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Target Goal:</span><span style="font-weight:700; color:#0f766e;">{goal}</span></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Core Focus:</span><span style="font-weight:600; color:#0f172a;">Python, SQL & ML</span></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Duration:</span><span style="font-weight:600; color:#0f172a;">12 Months Roadmap</span></div>
            </div>
            <div style="margin-bottom:14px;">
                <div style="font-weight:700; font-size:0.85rem; color:#475569; margin-bottom:8px;">📋 Final Output Checklist:</div>
                <div style="display:flex; flex-direction:column; gap:6px;">
                    <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Skill Gap Report</div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Learning Roadmap</div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Progress Tracker</div>
                </div>
            </div>
            <div style="background:#f0fdfa; border-left:4px solid #0f766e; padding:10px 12px; border-radius:6px;">
                <div style="font-weight:700; font-size:0.75rem; color:#115e59; margin-bottom:2px; display:flex; align-items:center; gap:4px;">💡 Key Takeaway:</div>
                <div style="font-size:0.75rem; color:#134e4a; line-height:1.35; font-style:italic;">"Agents user ke career goal ko achieve karne ke liye personalized roadmap create karte hain."</div>
            </div>
        </div>
        """
        return html
        
    elif scenario_key == "vacation":
        total = state.get("total_est", 18000)
        ref = state.get("booking_reference", "VAC-5928-HTL")
        
        html = f"""
        <div style="background:#ffffff; color:#1e293b; border-radius:16px; padding:22px; font-family:'Outfit', 'Inter', sans-serif; box-shadow:0 10px 25px rgba(0,0,0,0.08); border-top:6px solid #db2777; max-width:360px; margin:auto; border-left:1px solid #e2e8f0; border-right:1px solid #e2e8f0; border-bottom:1px solid #e2e8f0; box-sizing:border-box;">
            <div style="text-align:center; border-bottom:2px dashed #cbd5e1; padding-bottom:12px; margin-bottom:14px;">
                <div style="font-size:1.3rem; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; color:#db2777;">🌴 Vacation Planner</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Digital Holiday Package</div>
            </div>
            <div style="display:flex; flex-direction:column; gap:8px; font-size:0.85rem; border-bottom:2px dashed #cbd5e1; padding-bottom:14px; margin-bottom:14px;">
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Destination:</span><span style="font-weight:700; color:#db2777;">Jaipur (5 Days)</span></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Booking Reference:</span><span style="font-weight:600; color:#0f172a; font-family:monospace;">{ref}</span></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Flights & Hotel:</span><span style="font-weight:600; color:#059669;">Pre-booked Confirmed</span></div>
                <div style="display:flex; justify-content:space-between; border-top:1px solid #f1f5f9; padding-top:6px; font-weight:700;"><span style="color:#64748b;">Total Price:</span><span style="color:#0f172a;">₹{total}</span></div>
            </div>
            <div style="margin-bottom:14px;">
                <div style="font-weight:700; font-size:0.85rem; color:#475569; margin-bottom:8px;">📋 Final Output Checklist:</div>
                <div style="display:flex; flex-direction:column; gap:6px;">
                    <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Destination Selected</div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Budget Planned</div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Bookings Confirmed</div>
                    <div style="display:flex; align-items:center; gap:8px; font-size:0.8rem; color:#059669; font-weight:600;"><span style="font-size:0.95rem;">✔</span> Itinerary Ready</div>
                </div>
            </div>
            <div style="background:#fdf2f8; border-left:4px solid #db2777; padding:10px 12px; border-radius:6px;">
                <div style="font-weight:700; font-size:0.75rem; color:#9d174d; margin-bottom:2px; display:flex; align-items:center; gap:4px;">💡 Key Takeaway:</div>
                <div style="font-size:0.75rem; color:#831843; line-height:1.35; font-style:italic;">"Different agents milkar complete vacation planning automatically kar dete hain."</div>
            </div>
        </div>
        """
        return html
        
    return ""


# --------------------------------------------------------------------------
# 4. STRUCTURED PROMPT EVALUATOR ENGINE (RTFC FRAMEWORK)
# --------------------------------------------------------------------------

def evaluate_rtfc_prompt_local(prompt_text):
    """
    Local heuristic-based evaluator for prompt quality.
    """
    # Regex to find sections
    role_match = re.search(r'Role:(.*?)(?:Context:|Task:|Constraints:|$)', prompt_text, re.DOTALL | re.IGNORECASE)
    context_match = re.search(r'Context:(.*?)(?:Role:|Task:|Constraints:|$)', prompt_text, re.DOTALL | re.IGNORECASE)
    task_match = re.search(r'Task:(.*?)(?:Role:|Context:|Constraints:|$)', prompt_text, re.DOTALL | re.IGNORECASE)
    constraints_match = re.search(r'Constraints:(.*?)(?:Role:|Context:|Task:|$)', prompt_text, re.DOTALL | re.IGNORECASE)
    
    role_content = role_match.group(1).strip() if role_match else ""
    context_content = context_match.group(1).strip() if context_match else ""
    task_content = task_match.group(1).strip() if task_match else ""
    constraints_content = constraints_match.group(1).strip() if constraints_match else ""
    
    scores = {}
    feedback = {}
    
    # 1. Role (Max 25)
    role_score = 0
    role_fb = []
    if not role_content:
        role_fb.append("Missing 'Role' section completely. Define the agent identity (e.g. 'Act as an expert doctor booking agent').")
    else:
        role_score += 5  # Has role section
        # Identity phrasing
        role_lower = role_content.lower()
        if any(w in role_lower for w in ["act as", "you are", "role:", "persona"]):
            role_score += 5
        else:
            role_fb.append("Use explicit identity phrasing like 'Act as...' or 'You are...' to anchor the agent's persona.")
            
        # Expertise / domain specification
        if any(w in role_lower for w in ["expert", "senior", "specialist", "consultant", "engineer", "analyst", "planner", "auditor", "coordinator", "manager"]):
            role_score += 5
        else:
            role_fb.append("Specify an expertise level or explicit professional title (e.g., 'Senior Planner', 'Cost Controller specialist').")
            
        # Domain setting/field
        if len(role_lower.split()) > 3:
            role_score += 5
        else:
            role_fb.append("Expand the role description to specify the context of action (e.g. 'specializing in medical accounts').")
            
        # Length check
        if len(role_content) >= 15:
            role_score += 5
        else:
            role_fb.append("Role explanation is too brief. Add more credentials/details.")
            
        if not role_fb:
            role_fb.append("Excellent persona. Explicit persona and credentials help align output style and quality.")
    scores["Role"] = role_score
    feedback["Role"] = " ".join(role_fb)
    
    # 2. Context (Max 25)
    context_score = 0
    context_fb = []
    if not context_content:
        context_fb.append("Missing 'Context' section completely. Provide background environment information.")
    else:
        context_score += 5  # Has context section
        context_lower = context_content.lower()
        
        # Check for databases, APIs, logs, inputs
        if any(w in context_lower for w in ["database", "api", "logs", "table", "input", "schema", "variables", "history", "files", "spreadsheet", "record", "system"]):
            context_score += 10
        else:
            context_fb.append("Specify data environments, databases, or API sources the agent interacts with (e.g., 'GPS rideshare API', 'syllabus catalog').")
            
        # Check for parameters / scopes / bounds
        if any(w in context_lower for w in ["local", "nearby", "budget", "limit", "radius", "weekly", "daily", "monthly", "user"]):
            context_score += 5
        else:
            context_fb.append("Define operational bounds or user-defined variable environments within the context.")
            
        # Length check
        if len(context_content) >= 25:
            context_score += 5
        else:
            context_fb.append("Context description is short. More background data helps avoid default model assumptions.")
            
        if not context_fb:
            context_fb.append("Clear context details. Accurate environmental background limits model assumptions.")
    scores["Context"] = context_score
    feedback["Context"] = " ".join(context_fb)
    
    # 3. Task (Max 25)
    task_score = 0
    task_fb = []
    if not task_content:
        task_fb.append("Missing 'Task' section completely. The core action to execute is missing.")
    else:
        task_score += 5  # Has task section
        task_lower = task_content.lower()
        
        # Check for strong action verbs
        verbs = ["analyze", "compare", "calculate", "compute", "find", "select", "verify", "generate", "schedule", "retrieve", "compile", "identify", "search", "inspect", "filter", "evaluate", "assess", "prioritize", "draft", "complete", "extract", "check"]
        if any(v in task_lower for v in verbs):
            task_score += 10
        else:
            task_fb.append("Use strong action-oriented verbs (e.g., 'Verify', 'Extract', 'Calculate') as the core task instruction.")
            
        # Check for IO format / target clarity
        if any(w in task_lower for w in ["list", "json", "format", "output", "return", "report", "results", "response", "render", "invoice", "receipt", "alert", "notification"]):
            task_score += 5
        else:
            task_fb.append("Specify clear input/output formats or targets (e.g. 'return list', 'generate JSON').")
            
        # Length check
        if len(task_content) >= 35:
            task_score += 5
        else:
            task_fb.append("Task details are sparse. Make the task instructions highly detailed and specific.")
            
        if not task_fb:
            task_fb.append("Strong task instruction. Active verbs and formatting parameters lead to predictable outputs.")
    scores["Task"] = task_score
    feedback["Task"] = " ".join(task_fb)
    
    # 4. Constraints (Max 25)
    constraints_score = 0
    constraints_fb = []
    if not constraints_content:
        constraints_fb.append("Missing 'Constraints' section. Guardrails are critical to prevent formatting and logical drift.")
    else:
        constraints_score += 5  # Has constraints section
        constraints_lower = constraints_content.lower()
        
        # Check for negative constraints
        if any(w in constraints_lower for w in ["do not", "never", "avoid", "no conversation", "raw only", "must not", "without", "exclude", "not output", "no explanation", "no preamble", "don't"]):
            constraints_score += 10
        else:
            constraints_fb.append("Include explicit negative constraints (e.g. 'Do not include conversational preamble', 'Do not summarize') to restrict unwanted output.")
            
        # Check for strict boundaries/limitations
        if any(w in constraints_lower for w in ["only", "strictly", "under", "limit", "max", "min", "within", "range", "exactly", "format", "rules", "must"]):
            constraints_score += 5
        else:
            constraints_fb.append("Add strict limit boundaries or format boundaries (e.g. 'within 10km', 'maximum of 3 items').")
            
        # Length check
        if len(constraints_content) >= 20:
            constraints_score += 5
        else:
            constraints_fb.append("Constraints are too brief. Add more structural guardrails.")
            
        if not constraints_fb:
            constraints_fb.append("Excellent constraints. Explicit limits prevent pipeline integrity breakages across agent transitions.")
    scores["Constraints"] = constraints_score
    feedback["Constraints"] = " ".join(constraints_fb)
    
    total_score = sum(scores.values())
    
    return {
        "total": total_score,
        "sections": {
            "Role": {"score": scores["Role"], "text": role_content, "feedback": feedback["Role"]},
            "Context": {"score": scores["Context"], "text": context_content, "feedback": feedback["Context"]},
            "Task": {"score": scores["Task"], "text": task_content, "feedback": feedback["Task"]},
            "Constraints": {"score": scores["Constraints"], "text": constraints_content, "feedback": feedback["Constraints"]}
        },
        "is_local": True
    }


def evaluate_rtfc_prompt_groq(prompt_text, api_key):
    """
    Evaluates a prompt using the Groq API (Llama-3.3-70b-versatile).
    Returns scorecard data and recommendations in JSON format.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are an expert prompt engineer and grader. Evaluate the given prompt based on the RTFC framework:\n"
        "- Role (Identity, Expertise, Persona)\n"
        "- Context (Data setting, system boundary, background)\n"
        "- Task (Core action, strong verbs, target inputs/outputs)\n"
        "- Constraints (Negative constraints, format boundaries, limits)\n\n"
        "Assign a score out of 25 for each of these 4 sections (Role, Context, Task, Constraints) based on quality, precision, clarity, and suitability for a multi-agent system.\n"
        "Provide constructive, actionable feedback (1-3 sentences) for each section. If the section is completely missing, the score should be 0 and the feedback should indicate it is missing.\n\n"
        "You MUST return a JSON object with this exact structure:\n"
        "{\n"
        "  \"total\": <sum of scores, integer between 0 and 100>,\n"
        "  \"sections\": {\n"
        "    \"Role\": { \"score\": <integer 0-25>, \"feedback\": \"<constructive feedback string>\" },\n"
        "    \"Context\": { \"score\": <integer 0-25>, \"feedback\": \"<constructive feedback string>\" },\n"
        "    \"Task\": { \"score\": <integer 0-25>, \"feedback\": \"<constructive feedback string>\" },\n"
        "    \"Constraints\": { \"score\": <integer 0-25>, \"feedback\": \"<constructive feedback string>\" }\n"
        "  }\n"
        "}"
    )
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please evaluate this prompt:\n\n{prompt_text}"}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    res_json = response.json()
    content = res_json["choices"][0]["message"]["content"]
    result = json.loads(content)
    
    # Parse and ensure it contains the expected structure
    total = int(result.get("total", 0))
    sections = result.get("sections", {})
    
    role_match = re.search(r'Role:(.*?)(?:Context:|Task:|Constraints:|$)', prompt_text, re.DOTALL | re.IGNORECASE)
    context_match = re.search(r'Context:(.*?)(?:Role:|Task:|Constraints:|$)', prompt_text, re.DOTALL | re.IGNORECASE)
    task_match = re.search(r'Task:(.*?)(?:Role:|Context:|Constraints:|$)', prompt_text, re.DOTALL | re.IGNORECASE)
    constraints_match = re.search(r'Constraints:(.*?)(?:Role:|Context:|Task:|$)', prompt_text, re.DOTALL | re.IGNORECASE)
    
    parsed_result = {
        "total": total,
        "sections": {
            "Role": {
                "score": int(sections.get("Role", {}).get("score", 0)),
                "text": role_match.group(1).strip() if role_match else "",
                "feedback": sections.get("Role", {}).get("feedback", "No feedback provided.")
            },
            "Context": {
                "score": int(sections.get("Context", {}).get("score", 0)),
                "text": context_match.group(1).strip() if context_match else "",
                "feedback": sections.get("Context", {}).get("feedback", "No feedback provided.")
            },
            "Task": {
                "score": int(sections.get("Task", {}).get("score", 0)),
                "text": task_match.group(1).strip() if task_match else "",
                "feedback": sections.get("Task", {}).get("feedback", "No feedback provided.")
            },
            "Constraints": {
                "score": int(sections.get("Constraints", {}).get("score", 0)),
                "text": constraints_match.group(1).strip() if constraints_match else "",
                "feedback": sections.get("Constraints", {}).get("feedback", "No feedback provided.")
            }
        },
        "is_local": False
    }
    return parsed_result


def evaluate_rtfc_prompt(prompt_text):
    """
    Evaluates a prompt structured with Role, Context, Task, and Constraints.
    Returns scorecard data and recommendations.
    """
    st.session_state["groq_error"] = None
    groq_api_key = st.session_state.get("groq_api_key", "").strip() or os.getenv("GROQ_API_KEY", "").strip()
    if groq_api_key:
        try:
            return evaluate_rtfc_prompt_groq(prompt_text, groq_api_key)
        except Exception as e:
            st.session_state["groq_error"] = str(e)
    return evaluate_rtfc_prompt_local(prompt_text)


# --------------------------------------------------------------------------
# 5. STREAMLIT INTERFACE BUILDER
# --------------------------------------------------------------------------

# Layout: Main App Title and Subheader
st.markdown("<h1 class='custom-title'>🤖 Multi-Agent Virtual Lab</h1>", unsafe_allow_html=True)
st.markdown("<p class='custom-subtitle'>Interactive playground for designing, visualizing, and evaluating multi-agent orchestration flows.</p>", unsafe_allow_html=True)

# Sidebar: Scenario selector and controls
with st.sidebar:
    st.markdown("### 🎛️ Controller Hub")
    
    # Scenario select dropdown
    scenario_list = list(SCENARIOS.keys())
    scenario_titles = [f"{SCENARIOS[k]['icon']} {SCENARIOS[k]['title']}" for k in scenario_list]
    
    if st.session_state.selected_scenario not in scenario_list:
        st.session_state.selected_scenario = scenario_list[0]
        
    selected_title = st.selectbox(
        "Active Scenario",
        options=scenario_titles,
        index=scenario_list.index(st.session_state.selected_scenario)
    )
    
    # Map back selection to scenario key
    selected_key = scenario_list[scenario_titles.index(selected_title)]
    
    # If selection changes, reset simulation state
    if selected_key != st.session_state.selected_scenario:
        st.session_state.selected_scenario = selected_key
        st.session_state.current_step = 0
        st.session_state.logs = [f"[SYSTEM] Switched to scenario: {SCENARIOS[selected_key]['title']}. Ready."]
        st.session_state.chat_history = []
        st.session_state.query_override = ""
        st.session_state.shared_state = {}
        st.rerun()
        
    st.markdown("---")
    st.markdown("### ⏱️ Pipeline Controls")
    
    # Run full simulation button
    if st.button("🚀 Run Full Pipeline", use_container_width=True):
        st.session_state.current_step = 0
        st.session_state.logs = [f"[SYSTEM] Starting automated multi-agent pipeline for '{SCENARIOS[selected_key]['title']}'..."]
        st.session_state.chat_history = []
        st.session_state.shared_state = {}
        st.session_state.run_counter += 1
        
        # Sequentially run agents
        for i in range(4):
            st.session_state.current_step = i
            # Simulate latency
            time.sleep(0.4)
            # Evaluate step logic
            logs, chat, success = run_agent_simulation_step(
                selected_key, i, 
                st.session_state.param_values.get(selected_key, {}),
                st.session_state.query_override or SCENARIOS[selected_key]["default_query"]
            )
            st.session_state.logs.extend(logs)
            if chat:
                st.session_state.chat_history.append(chat)
                
            if not success:
                st.session_state.logs.append("[SYSTEM] [FAILED] Pipeline execution aborted due to agent failure.")
                st.session_state.current_step = i # freeze on failed step
                break
        else:
            # Complete successfully
            st.session_state.current_step = 4
            st.session_state.logs.append("[SYSTEM] [SUCCESS] All 4 agents executed successfully. Final artifact compiled.")
            
        st.rerun()

    # Step-by-step executor button
    col_step, col_reset = st.columns(2)
    with col_step:
        if st.button("⏭️ Next Step", use_container_width=True):
            if st.session_state.current_step >= 4:
                st.session_state.current_step = 0
                st.session_state.logs = ["[SYSTEM] Loop restarted. Ready."]
                st.session_state.chat_history = []
                st.session_state.shared_state = {}
                st.rerun()
                
            step = st.session_state.current_step
            if step == 0:
                st.session_state.logs = [f"[SYSTEM] Initializing step-by-step workflow..."]
                st.session_state.chat_history = []
                st.session_state.shared_state = {}
                st.session_state.run_counter += 1
                
            logs, chat, success = run_agent_simulation_step(
                selected_key, step, 
                st.session_state.param_values.get(selected_key, {}),
                st.session_state.query_override or SCENARIOS[selected_key]["default_query"]
            )
            st.session_state.logs.extend(logs)
            if chat:
                st.session_state.chat_history.append(chat)
                
            if not success:
                st.session_state.logs.append("[SYSTEM] [FAILED] Aborted at step due to constraint violation.")
                # We stay at this step
            else:
                st.session_state.current_step += 1
                if st.session_state.current_step == 4:
                    st.session_state.logs.append("[SYSTEM] [SUCCESS] All 4 steps complete.")
            st.rerun()
            
    with col_reset:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.current_step = 0
            st.session_state.logs = ["[SYSTEM] Simulation reset. Ready."]
            st.session_state.chat_history = []
            st.session_state.shared_state = {}
            st.rerun()
            
    st.markdown("---")
    st.markdown("### 📊 Metrics Summary")
    st.metric("Total Runs", st.session_state.run_counter)
    st.metric("State Mutators", len(st.session_state.shared_state) if "shared_state" in st.session_state else 0)

# Main Dashboard Workspace splits
col_main_left, col_main_right = st.columns([1.1, 0.9])

with col_main_left:
    # --------------------------------------------------
    # MAIN WORKSPACE LEFT: CONFIG & CANVAS
    # --------------------------------------------------
    st.markdown(f"### Selected: {SCENARIOS[selected_key]['icon']} {SCENARIOS[selected_key]['title']}")
    st.markdown(f"<span style='color:#94a3b8; font-size:0.9rem;'>{SCENARIOS[selected_key]['desc']}</span>", unsafe_allow_html=True)
    
    # 1. Custom User Prompt Override
    q_default = SCENARIOS[selected_key]["default_query"]
    q_val = st.text_input(
        "User Request Prompt",
        value=st.session_state.query_override or q_default,
        help="Edit the initial trigger prompt to feed into the pipeline."
    )
    if q_val != (st.session_state.query_override or q_default):
        st.session_state.query_override = q_val
        
    # 2. Dynamic Scenario Parameters Panel
    st.markdown("#### ⚙️ Parameters & State Variables")
    params_data = SCENARIOS[selected_key]["parameters"]
    
    if selected_key not in st.session_state.param_values:
        st.session_state.param_values[selected_key] = {}
        for p in params_data:
            st.session_state.param_values[selected_key][p["id"]] = p["default"]
            
    # Draw parameters dynamically in a neat card layout
    with st.container(border=True):
        cols_param = st.columns(len(params_data))
        for index, p in enumerate(params_data):
            p_id = p["id"]
            with cols_param[index]:
                if p["type"] == "select":
                    sel_val = st.selectbox(
                        p["label"],
                        options=p["options"],
                        index=p["options"].index(st.session_state.param_values[selected_key].get(p_id, p["default"]))
                    )
                    st.session_state.param_values[selected_key][p_id] = sel_val
                elif p["type"] == "slider":
                    opts = p["options"]
                    sl_val = st.slider(
                        p["label"],
                        min_value=opts[0],
                        max_value=opts[1],
                        value=st.session_state.param_values[selected_key].get(p_id, p["default"])
                    )
                    st.session_state.param_values[selected_key][p_id] = sl_val
                elif p["type"] == "checkbox":
                    cb_val = st.checkbox(
                        p["label"],
                        value=st.session_state.param_values[selected_key].get(p_id, p["default"])
                    )
                    st.session_state.param_values[selected_key][p_id] = cb_val
                elif p["type"] == "text":
                    tx_val = st.text_input(
                        p["label"],
                        value=st.session_state.param_values[selected_key].get(p_id, p["default"])
                    )
                    st.session_state.param_values[selected_key][p_id] = tx_val

    # 3. Visual Execution Map
    st.markdown("#### 🧬 Workflow Execution Flow")
    
    # Setup node colors and class strings
    step = st.session_state.current_step
    node_classes = ["idle"] * 4
    
    # Shared state check for failures
    is_failed = "error" in st.session_state.shared_state if "shared_state" in st.session_state else False
    
    for idx in range(4):
        if idx < step:
            node_classes[idx] = "completed"
        elif idx == step:
            node_classes[idx] = "failed" if is_failed else "thinking"
        else:
            node_classes[idx] = "idle"
            
    # Build visual diagram HTML with inline styling
    agents = SCENARIOS[selected_key]["agents"]
    
    flow_html = f"""
    <div style="display: flex; align-items: center; justify-content: space-around; background: rgba(13,18,34,0.6); padding:16px 12px; border-radius:12px; border:1px solid #1e293b; overflow-x:auto;">
        <!-- NODE 1 -->
        <div style="flex:1; text-align:center; padding:10px; border-radius:8px; border: 1px solid {'#10b981' if node_classes[0] == 'completed' else ('#f59e0b' if node_classes[0] == 'thinking' else ('#ef4444' if node_classes[0] == 'failed' else '#1e293b'))}; background-color: rgba(7,9,19,0.8); min-width:110px; box-shadow: { '0 0 10px rgba(16,185,129,0.2)' if node_classes[0] == 'completed' else ('0 0 12px rgba(245,158,11,0.3)' if node_classes[0] == 'thinking' else '') };">
            <div style="font-size:0.6rem; color:#94a3b8; font-weight:bold; letter-spacing:0.5px;">AGENT 1</div>
            <div style="font-size:0.75rem; font-weight:700; color:#fff; margin-top:2px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{agents[0]['name'].split(' ')[0]}</div>
            <div style="font-size:0.55rem; color:{'#10b981' if node_classes[0] == 'completed' else ('#f59e0b' if node_classes[0] == 'thinking' else ('#ef4444' if node_classes[0] == 'failed' else '#64748b'))}; font-weight:bold; margin-top:4px;">{node_classes[0].upper()}</div>
        </div>
        
        <!-- ARROW 1-2 -->
        <div style="font-size:1.1rem; color:{'#6366f1' if step > 0 else '#1e293b'}; padding:0 4px;">➔</div>
        
        <!-- NODE 2 -->
        <div style="flex:1; text-align:center; padding:10px; border-radius:8px; border: 1px solid {'#10b981' if node_classes[1] == 'completed' else ('#f59e0b' if node_classes[1] == 'thinking' else ('#ef4444' if node_classes[1] == 'failed' else '#1e293b'))}; background-color: rgba(7,9,19,0.8); min-width:110px; box-shadow: { '0 0 10px rgba(16,185,129,0.2)' if node_classes[1] == 'completed' else ('0 0 12px rgba(245,158,11,0.3)' if node_classes[1] == 'thinking' else '') };">
            <div style="font-size:0.6rem; color:#94a3b8; font-weight:bold; letter-spacing:0.5px;">AGENT 2</div>
            <div style="font-size:0.75rem; font-weight:700; color:#fff; margin-top:2px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{agents[1]['name'].split(' ')[0]}</div>
            <div style="font-size:0.55rem; color:{'#10b981' if node_classes[1] == 'completed' else ('#f59e0b' if node_classes[1] == 'thinking' else ('#ef4444' if node_classes[1] == 'failed' else '#64748b'))}; font-weight:bold; margin-top:4px;">{node_classes[1].upper()}</div>
        </div>
        
        <!-- ARROW 2-3 -->
        <div style="font-size:1.1rem; color:{'#6366f1' if step > 1 else '#1e293b'}; padding:0 4px;">➔</div>
        
        <!-- NODE 3 -->
        <div style="flex:1; text-align:center; padding:10px; border-radius:8px; border: 1px solid {'#10b981' if node_classes[2] == 'completed' else ('#f59e0b' if node_classes[2] == 'thinking' else ('#ef4444' if node_classes[2] == 'failed' else '#1e293b'))}; background-color: rgba(7,9,19,0.8); min-width:110px; box-shadow: { '0 0 10px rgba(16,185,129,0.2)' if node_classes[2] == 'completed' else ('0 0 12px rgba(245,158,11,0.3)' if node_classes[2] == 'thinking' else '') };">
            <div style="font-size:0.6rem; color:#94a3b8; font-weight:bold; letter-spacing:0.5px;">AGENT 3</div>
            <div style="font-size:0.75rem; font-weight:700; color:#fff; margin-top:2px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{agents[2]['name'].split(' ')[0]}</div>
            <div style="font-size:0.55rem; color:{'#10b981' if node_classes[2] == 'completed' else ('#f59e0b' if node_classes[2] == 'thinking' else ('#ef4444' if node_classes[2] == 'failed' else '#64748b'))}; font-weight:bold; margin-top:4px;">{node_classes[2].upper()}</div>
        </div>
        
        <!-- ARROW 3-4 -->
        <div style="font-size:1.1rem; color:{'#6366f1' if step > 2 else '#1e293b'}; padding:0 4px;">➔</div>
        
        <!-- NODE 4 -->
        <div style="flex:1; text-align:center; padding:10px; border-radius:8px; border: 1px solid {'#10b981' if node_classes[3] == 'completed' else ('#f59e0b' if node_classes[3] == 'thinking' else ('#ef4444' if node_classes[3] == 'failed' else '#1e293b'))}; background-color: rgba(7,9,19,0.8); min-width:110px; box-shadow: { '0 0 10px rgba(16,185,129,0.2)' if node_classes[3] == 'completed' else ('0 0 12px rgba(245,158,11,0.3)' if node_classes[3] == 'thinking' else '') };">
            <div style="font-size:0.6rem; color:#94a3b8; font-weight:bold; letter-spacing:0.5px;">AGENT 4</div>
            <div style="font-size:0.75rem; font-weight:700; color:#fff; margin-top:2px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{agents[3]['name'].split(' ')[0]}</div>
            <div style="font-size:0.55rem; color:{'#10b981' if node_classes[3] == 'completed' else ('#f59e0b' if node_classes[3] == 'thinking' else ('#ef4444' if node_classes[3] == 'failed' else '#64748b'))}; font-weight:bold; margin-top:4px;">{node_classes[3].upper()}</div>
        </div>
    </div>
    """
    flow_iframe_html = f"""
    <body style="margin: 0; background: transparent; font-family: 'Inter', -apple-system, sans-serif; overflow: hidden;">
        {flow_html}
    </body>
    """
    components.html(flow_iframe_html, height=105, scrolling=False)
    
    # 4. Inspector / details of matching agent
    active_idx = min(step, 3)
    active_agent = agents[active_idx]
    
    st.markdown(f"**Selected Node Details: `{active_agent['name']}`**")
    st.markdown(f"* **Agent Expertise:** {active_agent['role']}")
    
    # Show tools
    tool_tags = "".join([f"<span class='tool-tag' style='margin-right:6px;'>🛠️ {t}</span>" for t in active_agent["tools"]])
    st.markdown(f"<div>{tool_tags}</div>", unsafe_allow_html=True)

with col_main_right:
    # --------------------------------------------------
    # MAIN WORKSPACE RIGHT: LOGS, CONSOLE, PROMPTS, EVALUATOR
    # --------------------------------------------------
    tab_console, tab_prompt_eval, tab_state, tab_prompt_edit, tab_guide = st.tabs([
        "💻 Logs & Conversations", 
        "📝 Prompt Evaluator",
        "📂 State Context", 
        "✏️ System Prompts", 
        "🧭 Architecture Guide"
    ])
    
    # Tab 1: Terminal Console Logs & Conversations split
    with tab_console:
        col_logs, col_chat = st.columns(2)
        
        with col_logs:
            st.markdown("**Dev Runtime Terminal**")
            log_html_lines = []
            for line in st.session_state.logs:
                if "[SYSTEM]" in line:
                    log_html_lines.append(f"<div class='term-line term-system'>{line}</div>")
                elif "Thinking..." in line or "Read System" in line:
                    log_html_lines.append(f"<div class='term-line term-thinking'>{line}</div>")
                elif "Calling tool" in line:
                    log_html_lines.append(f"<div class='term-line term-tool'>{line}</div>")
                elif "[CRITICAL ERROR]" in line or "[FAILED]" in line:
                    log_html_lines.append(f"<div class='term-line term-error'>{line}</div>")
                else: # replies
                    log_html_lines.append(f"<div class='term-line term-reply'>{line}</div>")
                    
            render_html(f"""
            <div class="terminal-box">
                {"".join(log_html_lines)}
            </div>
            """)
            
        with col_chat:
            st.markdown("**Shared Agent Message Board**")
            chat_bubbles = []
            
            if not st.session_state.chat_history:
                render_html("""
                <div class="chat-container" style="display:flex; flex-direction:column; align-items:center; justify-content:center; color:#64748b; text-align:center;">
                    <span style="font-size:2rem; margin-bottom:10px;">💬</span>
                    <span>No messages exchanged yet.<br>Start simulation to see agents discuss.</span>
                </div>
                """)
            else:
                for msg in st.session_state.chat_history:
                    chat_bubbles.append(f"""
                    <div class="chat-bubble">
                        <div class="chat-avatar" style="background:#6366f1;">{msg['avatar']}</div>
                        <div class="chat-msg-body">
                            <div style="font-size:0.7rem; font-weight:700; color:#cbd5e1;">{msg['sender']}</div>
                            <div class="chat-content-box">{msg['content']}</div>
                        </div>
                    </div>
                    """)
                render_html(f"""
                <div class="chat-container">
                    {"".join(chat_bubbles)}
                </div>
                """)
                
        # If pipeline completed, render the visual artifact card!
        if step >= 4:
            st.markdown("#### 🎫 Output Generated Artifact")
            html_receipt = render_outcome_receipt(selected_key)
            components.html(html_receipt, height=450, scrolling=False)
        elif is_failed:
            st.markdown("#### 🎫 Output Generated Artifact")
            html_receipt = render_outcome_receipt(selected_key)
            components.html(html_receipt, height=300, scrolling=False)

    # Tab 2: Structured Prompt Evaluator
    with tab_prompt_eval:
        st.markdown("### 📝 Structured Prompt Evaluator")
        st.write("Write your structured prompt in the input below using the **RTFC** (Role, Task, Feature/Context, Constraints) format to evaluate its effectiveness.")
        
        # User structured prompt input
        default_eval_prompt = (
            "Role:\nAct as an Industrial Safety Consultant.\n\n"
            "Context:\nManaging a chemicals production plant floor safety check.\n\n"
            "Task:\nAnalyze the floor incident checklist and highlight OSHA compliance violations.\n\n"
            "Constraints:\nOutput bullet points of warnings only. Do not summarize or output conversation."
        )
        
        user_prompt_input = st.text_area(
            "Write your structured prompt below",
            value=default_eval_prompt,
            height=200,
            key="evaluator_prompt_box"
        )
        
        if st.button("➡️ Evaluate Prompt", use_container_width=True):
            # Run evaluation
            report = evaluate_rtfc_prompt(user_prompt_input)
            
            # Show overall score
            st.markdown("#### 📊 Prompt Scorecard")
            if report.get("is_local", True):
                error_msg = st.session_state.get("groq_error")
                if error_msg:
                    st.warning(f"⚠️ Live Groq LLM evaluation failed: {error_msg}. Running local quality heuristic fallback evaluation.")
                else:
                    st.warning("⚠️ Live Groq LLM evaluation failed or timed out. Running local quality heuristic fallback evaluation.")
            else:
                st.success("🟢 Running live Groq LLM evaluation.")
            col_score, col_status = st.columns([1, 2])
            
            with col_score:
                render_html(f"""
                <div class='eval-score-card'>
                    <div style='font-size:0.8rem; color:#94a3b8; font-weight:600;'>OVERALL SCORE</div>
                    <div class='eval-score-val' style='color:{"#10b981" if report["total"] >= 80 else ("#f59e0b" if report["total"] >= 50 else "#ef4444")}'>{report["total"]}</div>
                    <div style='font-size:0.7rem; color:#94a3b8; font-weight:600;'>OUT OF 100</div>
                </div>
                """)
                
            with col_status:
                st.markdown("**Structured Breakdown Assessment**")
                for comp, details in report["sections"].items():
                    score_pct = (details["score"] / 25) * 100
                    render_html(f"""
                    <div class='eval-component-card'>
                        <div style='display:flex; justify-content:space-between; font-size:0.8rem;'>
                            <span style='font-weight:700; color:#fff;'>{comp}</span>
                            <span style='font-weight:700; color:#6366f1;'>{details["score"]}/25</span>
                        </div>
                        <div style='font-size:0.75rem; color:#94a3b8; margin-top:4px;'>{details["feedback"]}</div>
                    </div>
                    """)
                    
            # Explanations for RTFC structure
            st.markdown("---")
            st.markdown("#### 💡 Prompt Engineering Guide (RTFC Framework)")
            st.info("""
            * **Role (Who):** Gives the model a perspective, background knowledge, and specific tone to emulate.
            * **Context (Where):** Provides background info, data schemas, API specifications, and limits the system space.
            * **Task (What):** Clear instructions of what action to perform (use strong verbs: *classify, calculate, write*).
            * **Constraints (How):** Guardrails defining output formats, limits, styles, and strictly what the agent must *not* do.
            """)

    # Tab 3: State Context Inspector
    with tab_state:
        st.markdown("**Shared Memory State Context**")
        st.write("This represents the mutable payload passed sequentially from agent to agent.")
        
        # Build JSON display
        state_dict = st.session_state.shared_state
        st.json(state_dict)

    # Tab 4: System Prompts Editor
    with tab_prompt_edit:
        st.markdown("**System Prompt Template Editor**")
        st.write("Modify prompt structures to change agent instructions. Click Run/Step to execute under modified prompts.")
        
        agent_names = [a["name"] for a in SCENARIOS[selected_key]["agents"]]
        selected_edit_agent = st.selectbox(
            "Select Agent to Edit Prompt",
            options=agent_names
        )
        
        # Text area linked to session state prompt overrides
        current_prompt_text = st.session_state.custom_prompts[selected_key][selected_edit_agent]
        new_prompt_text = st.text_area(
            "System Prompt Text",
            value=current_prompt_text,
            height=200
        )
        
        if new_prompt_text != current_prompt_text:
            st.session_state.custom_prompts[selected_key][selected_edit_agent] = new_prompt_text
            
        if st.button("Restore Default Prompts", key="reset_prompt_btn"):
            for agent in SCENARIOS[selected_key]["agents"]:
                st.session_state.custom_prompts[selected_key][agent["name"]] = agent["default_prompt"]
            st.rerun()

    # Tab 5: Architecture Guide
    with tab_guide:
        st.markdown("### Sequential Chain Handoff Architecture")
        st.write("""
        This virtual lab demonstrates a **Sequential Chain Pattern** of multi-agent execution, which is highly effective for linear, multi-stage business pipelines.
        """)
        
        st.markdown("""
        #### 1. State Handoff Pattern
        In a sequential pipeline, agents do not talk arbitrarily. Instead, they operate on a shared memory object (the **State**). Agent 1 executes, mutates the state, and passes it to Agent 2. This linear progression is efficient and easy to debug.
        
        #### 2. Specialized Roles & Micro-Tools
        Instead of prompting a single large model to handle searching, booking, billing, and scheduling reminders, we split the workflow into 4 distinct roles, each equipped with custom, scoped tools (APIs/Databases). This reduces the cognitive load on the LLM and keeps hallucination rates near zero.
        
        #### 3. Linear Guardrails
        Programmatic validators act as gatekeepers between agent handoffs. For instance, if the *Payment Agent* returns `success: False` due to budget bounds, the sequence immediately breaks, preventing down-stream resources from executing.
        """)
