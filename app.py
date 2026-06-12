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
    "food_ordering": {
        "title": "Healthy Dinner Ordering",
        "icon": "🍽️",
        "desc": "Searches restaurants, filters healthy dinner meals, keeps the total under ₹300, and books after approval.",
        "default_query": "Order a healthy dinner for tonight under ₹300.",
        "agents": [
            {
                "name": "Restaurant Search Agent",
                "role": "Search nearby restaurants and their basic cuisines.",
                "tools": ["SearchNearbyRestaurants", "CalculateProximityKM"],
                "default_prompt": "Role: Restaurant Search Agent\nContext: Local food delivery listings.\nTask: Find nearby restaurants and list their distances.\nConstraints: Return matching dining names only. Do not calculate pricing."
            },
            {
                "name": "Dietary Filter Agent",
                "role": "Analyze menu items to filter for healthy options.",
                "tools": ["MatchDietProfile", "CalculateCalories"],
                "default_prompt": "Role: Dietary Health Specialist\nContext: Nutritional tables.\nTask: Inspect available dishes, filter out high-calorie junk foods, and highlight healthy options.\nConstraints: Recommend dishes with protein and low fats only."
            },
            {
                "name": "Price Guardrail Agent",
                "role": "Verify prices and keep total cost within user budget.",
                "tools": ["ComputeTotalCost", "ApplyDiscounts", "VerifyBudgetLimit"],
                "default_prompt": "Role: Cost Controller\nContext: Checkout calculations (tax + delivery fees).\nTask: Calculate total checkout cost and verify it is under the user-defined budget.\nConstraints: Flag a budget failure if cost exceeds the limit."
            },
            {
                "name": "Order Dispatch Agent",
                "role": "Process payment, simulate approval, and generate tracking details.",
                "tools": ["SimulateApproval", "TriggerOrderAPI", "GetTrackingVoucher"],
                "default_prompt": "Role: Checkout Dispatcher\nContext: Order finalization.\nTask: Ask for final authorization, place the order through the api, and generate tracking info.\nConstraints: Provide confirmation only after order receipt is generated."
            }
        ],
        "parameters": [
            {"id": "meal_choice", "label": "Dinner Meal Choice", "type": "select", "options": ["Healthy Quinoa Salad & Juice", "Avocado Toast & Green Tea", "Butter Paneer Masala & Naan (Cheat Meal)"], "default": "Healthy Quinoa Salad & Juice"},
            {"id": "delivery_tier", "label": "Delivery Priority", "type": "select", "options": ["Standard Delivery (+₹30)", "Priority Express (+₹80)"], "default": "Standard Delivery (+₹30)"},
            {"id": "budget_limit", "label": "Max Budget (₹)", "type": "slider", "options": [150, 500, 300], "default": 300}
        ]
    },
    "grocery_shopping": {
        "title": "Smart Grocery Shopping",
        "icon": "🛒",
        "desc": "Compiles a monthly grocery list, matches store availability, compares prices, and orders the cheapest overall option.",
        "default_query": "Purchase my monthly grocery list under ₹2500.",
        "agents": [
            {
                "name": "List Compiler Agent",
                "role": "Compile the monthly essentials grocery checklist.",
                "tools": ["ListEssentials", "CheckStapleCategories"],
                "default_prompt": "Role: Household Planner\nContext: Monthly grocery checklists.\nTask: Create a structured list of essentials (rice, flour, oil, salt, sugar) for monthly cooking.\nConstraints: Stick to standard household items only."
            },
            {
                "name": "Inventory Search Agent",
                "role": "Identify stores carrying all items on the checklist.",
                "tools": ["QueryStoreInventory", "VerifyInStock"],
                "default_prompt": "Role: Inventory Checker\nContext: Local store stock tables.\nTask: Search local stores to verify if all items in the checklist are fully in stock.\nConstraints: Return list of matching stores with inventory availability."
            },
            {
                "name": "Price Optimizer Agent",
                "role": "Compare basket prices across stores to find the cheapest.",
                "tools": ["ComputeBasketTotals", "ApplyStoreDiscounts"],
                "default_prompt": "Role: Price Auditor\nContext: Pricing matrices of different outlets.\nTask: Compare the total price of the items across stores and identify the cheapest option.\nConstraints: Recommend the single lowest-cost store. Alert if over budget."
            },
            {
                "name": "Order Scheduler Agent",
                "role": "Confirm basket booking and schedule delivery slot.",
                "tools": ["LockStoreOrder", "SelectDeliverySlot", "GenerateInvoice"],
                "default_prompt": "Role: Booking Dispatcher\nContext: Store checkout.\nTask: Complete the purchase order at the cheapest store, set delivery schedule, and issue invoice.\nConstraints: Highlight delivery date and time clearly."
            }
        ],
        "parameters": [
            {"id": "basket_type", "label": "Grocery Basket Type", "type": "select", "options": ["Basic Household Staples", "Premium Organic Pantry"], "default": "Basic Household Staples"},
            {"id": "store_preference", "label": "Preferred Store", "type": "select", "options": ["SuperMart (Cheapest)", "QuickGrocer (Fast)", "OrganicWhole (Premium)"], "default": "SuperMart (Cheapest)"},
            {"id": "max_budget", "label": "Max Budget (₹)", "type": "slider", "options": [1500, 4000, 2500], "default": 2500}
        ]
    },
    "laundry_pickup": {
        "title": "Express Laundry Pickup",
        "icon": "🧺",
        "desc": "Searches laundry services, checks pickup slots, selects the fastest delivery, and books pickup and delivery.",
        "default_query": "Schedule a laundry pickup and delivery before tomorrow.",
        "agents": [
            {
                "name": "Laundry Locator Agent",
                "role": "Find laundry services near the current address.",
                "tools": ["SearchLaundryServices", "CheckReviews"],
                "default_prompt": "Role: Laundry Locator\nContext: Local service map coordinates.\nTask: Find laundry and dry cleaning businesses near the user.\nConstraints: List company names and service distance only."
            },
            {
                "name": "Slot Checker Agent",
                "role": "Inspect available pickup slots for today.",
                "tools": ["GetAvailableSlots", "LockTemporarySlot"],
                "default_prompt": "Role: Schedule Inspector\nContext: Booking calendars.\nTask: Query booking calendars for laundry pickup slots available today.\nConstraints: Show immediate slots only."
            },
            {
                "name": "Turnaround Validator Agent",
                "role": "Select the fastest delivery mode to meet the deadline.",
                "tools": ["FilterByTurnaround", "CalculateExpressFare"],
                "default_prompt": "Role: Express Logistics Coordinator\nContext: Delivery turnarounds.\nTask: Check if laundry can be washed and delivered before tomorrow. Charge surcharge if express is needed.\nConstraints: Abort booking if deadline cannot be met."
            },
            {
                "name": "Booking Dispatcher Agent",
                "role": "Confirm booking and generate service receipt.",
                "tools": ["ConfirmBookingDB", "SendConfirmationAlert"],
                "default_prompt": "Role: Final Dispatcher\nContext: Finalizing bookings.\nTask: Complete booking on database, retrieve confirmation code, and send scheduling notification.\nConstraints: Output confirmation and price receipt."
            }
        ],
        "parameters": [
            {"id": "service_tier", "label": "Service Tier", "type": "select", "options": ["Express Surcharge (+₹150)", "Standard (48-hour turn)"], "default": "Express Surcharge (+₹150)"},
            {"id": "deadline_tomorrow", "label": "Must Deliver Before Tomorrow", "type": "checkbox", "default": True}
        ]
    },
    "study_planner": {
        "title": "Custom Study Planner",
        "icon": "📚",
        "desc": "Analyzes available hours, divides subjects, prioritizes difficult topics, generates a timetable, and schedules reminders.",
        "default_query": "Create an effective weekly study schedule.",
        "agents": [
            {
                "name": "Hour Analyzer Agent",
                "role": "Assess available hours in the weekly routine.",
                "tools": ["ReadAvailableHours", "AssessSubjectVolume"],
                "default_prompt": "Role: Hour Analyst\nContext: Student daily schedules.\nTask: Analyze available free hours across the week to allocate for studying.\nConstraints: Output total weekly study hours capacity."
            },
            {
                "name": "Topic Weight Classifier Agent",
                "role": "Divide subjects and flag difficult topics.",
                "tools": ["PrioritizeDifficultTopics", "CreateTopicMap"],
                "default_prompt": "Role: Subject Prioritizer\nContext: Syllabus and exam weightage database.\nTask: Rank subjects by difficulty and assign study weights to focus areas.\nConstraints: Give more time budget to hard subjects."
            },
            {
                "name": "Timetable Architect Agent",
                "role": "Draft a weekly timetable grid.",
                "tools": ["DraftTimetable", "OptimizeStudySpans"],
                "default_prompt": "Role: Timetable Architect\nContext: Weekly calendar layout.\nTask: Draft a day-wise calendar schedule distributing the topics across study spans.\nConstraints: Include rest breaks and avoid study fatigue."
            },
            {
                "name": "Reminder Scheduler Agent",
                "role": "Configure daily notification triggers.",
                "tools": ["RegisterDailyAlerts", "GenerateCalendarLink"],
                "default_prompt": "Role: Reminder Coordinator\nContext: Alert scheduling system.\nTask: Set up daily alarm schedules and notification reminders for study sessions.\nConstraints: Enable SMS reminders if selected."
            }
        ],
        "parameters": [
            {"id": "study_hours_daily", "label": "Daily Study Hours", "type": "slider", "options": [2, 10, 6], "default": 6},
            {"id": "primary_difficulty", "label": "Subject Difficulty", "type": "select", "options": ["High (Maths & Physics)", "Medium (Chemistry)", "Low (English & Arts)"], "default": "High (Maths & Physics)"},
            {"id": "sms_reminders", "label": "Enable SMS Reminders", "type": "checkbox", "default": True}
        ]
    },
    "vehicle_service": {
        "title": "Vehicle Service Booking",
        "icon": "🚗",
        "desc": "Searches service centers, compares prices and reviews, selects the best value, and books the service.",
        "default_query": "Service my bike at lowest cost with best rating.",
        "agents": [
            {
                "name": "Workshop Finder Agent",
                "role": "Search service centers in the delivery radius.",
                "tools": ["ListServiceCenters", "GetRatings"],
                "default_prompt": "Role: Workshop Scout\nContext: Business maps.\nTask: Find nearby service centers and collect rating data.\nConstraints: List workshops within a 10km radius only."
            },
            {
                "name": "Quote & Rating Analyzer Agent",
                "role": "Compare quotes and customer reviews.",
                "tools": ["FetchQuotes", "CalculateValueScore"],
                "default_prompt": "Role: Quote Auditor\nContext: Price quote catalogs.\nTask: Compare package pricing and reviews to find the best value workshops.\nConstraints: Filter out workshops with less than 4.0 stars."
            },
            {
                "name": "Value Selector Agent",
                "role": "Select the best center matching rating and budget bounds.",
                "tools": ["VerifyBudgetLimits", "ReserveServiceSlot"],
                "default_prompt": "Role: Value Matcher\nContext: Checking budget limits.\nTask: Check if service cost is within user limits. Choose highest rating within budget.\nConstraints: Flag error if no workshop meets budget."
            },
            {
                "name": "Service Booking Agent",
                "role": "Book the service slot and generate invoice receipt.",
                "tools": ["ConfirmServiceBooking", "GenerateReceiptPDF"],
                "default_prompt": "Role: Booking Specialist\nContext: Scheduling system.\nTask: Complete the workshop booking registration, set appointment date, and issue receipt.\nConstraints: Output booking slot and receipt details."
            }
        ],
        "parameters": [
            {"id": "service_pkg", "label": "Service Package", "type": "select", "options": ["General Tuning & Wash", "Full Engine Service & Detailing"], "default": "General Tuning & Wash"},
            {"id": "min_rating", "label": "Minimum Rating", "type": "select", "options": ["4.5+ Stars", "4.0+ Stars"], "default": "4.5+ Stars"},
            {"id": "budget_max", "label": "Max Budget (₹)", "type": "slider", "options": [800, 4000, 2000], "default": 2000}
        ]
    },
    "electricity_bill": {
        "title": "Electricity Bill Payment",
        "icon": "🧾",
        "desc": "Fetches pending utility bills, verifies amount and due dates, asks for approval, and processes payment.",
        "default_query": "Check my pending electricity bill and pay it before the due date.",
        "agents": [
            {
                "name": "Bill Retriever Agent",
                "role": "Retrieve active utility bill details.",
                "tools": ["QueryUtilityAccount", "RetrieveBillStatus"],
                "default_prompt": "Role: Bill Fetcher\nContext: Utility database registry.\nTask: Fetch the active bill amount and consumer details.\nConstraints: Return account consumer name and outstanding fee."
            },
            {
                "name": "Bill Auditor Agent",
                "role": "Validate bill amount details and due dates.",
                "tools": ["AuditAmount", "VerifyDueDate"],
                "default_prompt": "Role: Bill Auditor\nContext: Due date validation sheets.\nTask: Audit outstanding fee and verify deadline. Flag dispute if amount looks anomalous.\nConstraints: Terminate payment if bill is disputed."
            },
            {
                "name": "Gateway Authorization Agent",
                "role": "Verify wallet balance and simulate approval.",
                "tools": ["CheckWalletBalance", "ValidateGatewayStatus"],
                "default_prompt": "Role: Payment Gatekeeper\nContext: Wallet system verification.\nTask: Check user wallet balance and simulate fraud verification checks.\nConstraints: Deny checkout if wallet balance is insufficient."
            },
            {
                "name": "Payment Processor Agent",
                "role": "Process transaction and generate invoice receipt.",
                "tools": ["ExecutePayment", "GenerateReceiptCode"],
                "default_prompt": "Role: billing specialist\nContext: Bank transaction APIs.\nTask: Execute the bill payment, update payment status in PMS, and return transaction confirmation.\nConstraints: Output receipt code and success status."
            }
        ],
        "parameters": [
            {"id": "bill_status", "label": "Bill Status Mode", "type": "select", "options": ["Regular Bill", "Disputed Bill (Abnormal Charge)"], "default": "Regular Bill"},
            {"id": "wallet_balance", "label": "Wallet Balance (₹)", "type": "slider", "options": [500, 6000, 3000], "default": 3000},
            {"id": "due_days_left", "label": "Days until Due Date", "type": "slider", "options": [1, 15, 3], "default": 3}
        ]
    },
    "cab_booking": {
        "title": "Cab Booking Assistant",
        "icon": "🚕",
        "desc": "Finds nearby cabs, compares ETA and prices, selects the cheapest option, and completes booking after approval.",
        "default_query": "Book the cheapest cab to my college.",
        "agents": [
            {
                "name": "Cab Finder Agent",
                "role": "Locate nearby available cabs.",
                "tools": ["LocateNearbyCabs", "FetchETAs"],
                "default_prompt": "Role: Cab Locator\nContext: GPS rideshare API.\nTask: Scan nearby vehicles and list available vehicle types with ETAs.\nConstraints: List locations of drivers within 5km radius."
            },
            {
                "name": "Fare Comparison Agent",
                "role": "Compare fares and travel options.",
                "tools": ["FetchFares", "IdentifyCheapest"],
                "default_prompt": "Role: Fare Auditor\nContext: Rideshare pricing chart.\nTask: Compare the pricing of Auto, Mini, and Sedan categories for the target location.\nConstraints: Return fares ordered cheapest to most expensive."
            },
            {
                "name": "Cheapest Selector Agent",
                "role": "Select the best ride category under waiting and budget constraints.",
                "tools": ["FilterRideCategory", "ConfirmBookingAPI"],
                "default_prompt": "Role: Ride Matcher\nContext: Rideshare filters.\nTask: Choose the cheapest category matching maximum wait time constraints.\nConstraints: Abort if ETA exceeds the user's limit."
            },
            {
                "name": "Ride Dispatch Agent",
                "role": "Confirm booking and show driver tracking details.",
                "tools": ["DispatchVehicle", "GetDriverInfo"],
                "default_prompt": "Role: Dispatch Coordinator\nContext: Dispatch system database.\nTask: Finalize driver assignment, retrieve license plate and phone number, and output tracking info.\nConstraints: Render driver name and plates clearly."
            }
        ],
        "parameters": [
            {"id": "dest_distance", "label": "Destination", "type": "select", "options": ["College (5 km)", "Airport (35 km)"], "default": "College (5 km)"},
            {"id": "max_wait_minutes", "label": "Max Wait Time (mins)", "type": "slider", "options": [5, 25, 10], "default": 10},
            {"id": "cab_type_preference", "label": "Preferred Option", "type": "select", "options": ["Cheapest Available", "Sedan Comfort Only"], "default": "Cheapest Available"}
        ]
    },
    "doctor_booking": {
        "title": "Doctor Appointment Booking",
        "icon": "🏥",
        "desc": "Searches nearby doctors, compares appointment waiting times, selects the shortest wait slot, and books appointment.",
        "default_query": "Get doctor appointment with minimum waiting time.",
        "agents": [
            {
                "name": "Clinic Search Agent",
                "role": "Scan clinics specializing in relevant symptoms.",
                "tools": ["SearchClinics", "MatchSpecialty"],
                "default_prompt": "Role: Clinic Search Agent\nContext: Clinic listings database.\nTask: Find nearby clinics and specialist profiles matching candidate symptoms.\nConstraints: Limit search radius to 15km."
            },
            {
                "name": "Queue Analyzer Agent",
                "role": "Compare patient queues and waiting times.",
                "tools": ["FetchQueueWaitTime", "CompareSchedules"],
                "default_prompt": "Role: Queue Analyst\nContext: Clinic patient queue registries.\nTask: Analyze current active wait times and patient queue lengths for the clinics.\nConstraints: List clinics sorted by shortest wait times."
            },
            {
                "name": "Booking Scheduler Agent",
                "role": "Hold slot at clinic with shortest wait time.",
                "tools": ["HoldSlotDB", "CheckFees"],
                "default_prompt": "Role: Booking Coordinator\nContext: Scheduling system.\nTask: Lock the earliest available slot for the clinic with the shortest queue.\nConstraints: Verify consultation fees fit the budget."
            },
            {
                "name": "Alert Dispatcher Agent",
                "role": "Finalize booking and set up reminder alerts.",
                "tools": ["ConfirmBooking", "SendCalendarAlert"],
                "default_prompt": "Role: Notification Coordinator\nContext: Confirm booking tables.\nTask: Complete booking registration, generate barcode voucher, and set SMS reminders.\nConstraints: Confirm only after validation check passes."
            }
        ],
        "parameters": [
            {"id": "symptom_urgency", "label": "Symptom Urgency", "type": "select", "options": ["General Consultation (Non-urgent)", "Acute Pain (Urgent Emergency)"], "default": "General Consultation (Non-urgent)"},
            {"id": "max_distance", "label": "Max Distance Allowed", "type": "select", "options": ["Within 5 km", "Within 15 km"], "default": "Within 5 km"},
            {"id": "fee_budget", "label": "Max Consultation Fee (₹)", "type": "slider", "options": [300, 1500, 700], "default": 700}
        ]
    },
    "house_cleaning": {
        "title": "House Cleaning Booking",
        "icon": "🧹",
        "desc": "Lists house cleaning providers, compares cost and ratings, and schedules the best value service under budget.",
        "default_query": "Book house cleaning at lowest cost.",
        "agents": [
            {
                "name": "Cleaning Finder Agent",
                "role": "List cleaning agencies and customer reviews.",
                "tools": ["ListCleaningServices", "FetchRatings"],
                "default_prompt": "Role: Service Finder\nContext: Local listings map.\nTask: Search local cleaning agencies and download review ratings.\nConstraints: Return active listings and ratings only."
            },
            {
                "name": "Quote Estimator Agent",
                "role": "Calculate pricing estimates for cleaning scopes.",
                "tools": ["GetCleaningQuotes", "EvaluateValueScore"],
                "default_prompt": "Role: Quote Estimator\nContext: Cleaning service rate cards.\nTask: Fetch price quotes for the requested cleaning package and room count.\nConstraints: Exclude agencies with customer rating below 4.0 stars."
            },
            {
                "name": "Value Analyst Agent",
                "role": "Select best value provider under user budget.",
                "tools": ["LockCleaningSlot", "ValidatePrice"],
                "default_prompt": "Role: Budget Matcher\nContext: Customer price constraints.\nTask: Select the cheapest available quote under the budget limit.\nConstraints: Abort step if all quotes exceed budget limits."
            },
            {
                "name": "Service Scheduler Agent",
                "role": "Schedule booking slot and issue service receipt.",
                "tools": ["ConfirmCleanSchedule", "GenerateReceipt"],
                "default_prompt": "Role: Scheduler Coordinator\nContext: Cleaning booking database.\nTask: Confirm cleaning appointment, lock calendar date, and dispatch payment invoice receipt.\nConstraints: Output receipt details and timing slot."
            }
        ],
        "parameters": [
            {"id": "clean_scope", "label": "Cleaning Scope", "type": "select", "options": ["Standard 2-BHK Cleaning", "Deep Home Sanitization"], "default": "Standard 2-BHK Cleaning"},
            {"id": "customer_rating_min", "label": "Minimum Provider Rating", "type": "select", "options": ["4.2+ Stars", "4.7+ Stars"], "default": "4.2+ Stars"},
            {"id": "budget_limit", "label": "Max Budget (₹)", "type": "slider", "options": [1000, 5000, 2000], "default": 2000}
        ]
    },
    "sleep_routine": {
        "title": "Sleep Routine Planner",
        "icon": "💤",
        "desc": "Analyzes sleep history, calculates cycle bedtime, designs wind-down routines, and schedules alerts.",
        "default_query": "Design sleep routine to help me feel refreshed by 7:00 AM.",
        "agents": [
            {
                "name": "Pattern Analyzer Agent",
                "role": "Evaluate sleep patterns and track deficit.",
                "tools": ["ReadSleepHistory", "IdentifyDeficits"],
                "default_prompt": "Role: Sleep Pattern Analyst\nContext: User smart band historical logs.\nTask: Review average sleep durations and pinpoint sleep deficit hours.\nConstraints: Show analysis summaries only."
            },
            {
                "name": "Bedtime Calculator Agent",
                "role": "Compute optimal bedtime cycles for target wake time.",
                "tools": ["CalculateSleepCycles", "SetBedtimeAlert"],
                "default_prompt": "Role: Sleep Cycle Calculator\nContext: 90-minute sleep cycle standards.\nTask: Calculate optimal bedtime to complete targeted sleep cycles before target wake time.\nConstraints: Factor in 15 mins average latency to fall asleep."
            },
            {
                "name": "Routine Designer Agent",
                "role": "Draft healthy wind-down pre-sleep routines.",
                "tools": ["DraftRoutine", "FormatWindDownSteps"],
                "default_prompt": "Role: Sleep Routine Planner\nContext: Sleep hygiene guidelines.\nTask: Outline custom pre-sleep wind-down activities. Recommend adjustment for bad habits like gaming.\nConstraints: Avoid screen time in standard recommendations."
            },
            {
                "name": "Alert Scheduler Agent",
                "role": "Configure bedtime wind-down alerts and reminders.",
                "tools": ["ScheduleBedtimeAlerts", "ConnectFitnessTracker"],
                "default_prompt": "Role: Notification Setup Coordinator\nContext: Phone notification settings.\nTask: Program daily bedtime alerts, turn-off reminders, and morning wake-up alarms.\nConstraints: Output active routine parameters."
            }
        ],
        "parameters": [
            {"id": "target_wake_time", "label": "Target Wake-up Time", "type": "select", "options": ["06:00 AM", "07:00 AM", "08:00 AM"], "default": "07:00 AM"},
            {"id": "target_cycles", "label": "Desired Sleep Cycles", "type": "slider", "options": [4, 6, 5], "default": 5},
            {"id": "pre_sleep_habit", "label": "Pre-sleep Habit", "type": "select", "options": ["Reading & Dim Lights", "Gaming & Social Media (High Alert)"], "default": "Reading & Dim Lights"}
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
    Simulates execution for a single agent. Returns (log_lines, chat_msg, state_mutations, success_bool)
    """
    scenario = SCENARIOS[scenario_key]
    agent = scenario["agents"][step_num]
    agent_name = agent["name"]
    prompt = get_agent_instruction(scenario_key, agent_name)
    
    log_lines = []
    chat_msg = None
    state_mutations = {}
    success = True
    
    # Extract prompt instructions context
    p_lines = [l.strip() for l in prompt.split('\n') if ':' in l]
    prompt_hints = " ".join(p_lines)
    
    # --------------------------------------------------
    # Doctor Scenario Simulation Logic
    # --------------------------------------------------
    if scenario_key == "doctor":
        illness = params.get("illness", "Fever")
        time_pref = params.get("time", "Morning")
        budget = params.get("budget", 600)
        
        if step_num == 0:  # Doctor Search Agent
            log_lines.append(f"[AGENT: {agent_name}] Read System Instructions: {prompt_hints[:80]}...")
            log_lines.append(f"[AGENT: {agent_name}] Input parsed: illness='{illness}', query='{user_q}'")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool MatchSymptoms(illness='{illness}')...")
            
            if illness == "Fever":
                doctors = [{"name": "Dr. Sharma", "specialty": "General Physician", "dist": "1.2km", "fee": 500},
                           {"name": "Dr. Verma", "specialty": "General Medicine", "dist": "3.5km", "fee": 400}]
            elif illness == "Toothache":
                doctors = [{"name": "Dr. Alok (Dentist)", "specialty": "Orthodontics", "dist": "2.1km", "fee": 600}]
            else: # Fracture
                doctors = [{"name": "Dr. Kapoor (Ortho)", "specialty": "Orthopedics", "dist": "4.8km", "fee": 1000}]
            
            log_lines.append(f"[AGENT: {agent_name}] Calling tool CalculateProximity()... Found {len(doctors)} matching clinics nearby.")
            doc_names = ", ".join([d["name"] for d in doctors])
            log_lines.append(f"[AGENT: {agent_name}] Output response: {doc_names} are available nearby.")
            
            chat_msg = {
                "sender": agent_name, "avatar": "🩺",
                "content": f"Hi! Based on your symptom of {illness.lower()}, I searched nearby specialists. I found: " +
                           ", ".join([f"{d['name']} ({d['specialty']} - {d['dist']})" for d in doctors]) + ". Passing this to booking."
            }
            state_mutations = {"matched_doctors": doctors, "illness": illness, "time_pref": time_pref}
            
        elif step_num == 1:  # Appointment Booking Agent
            prev_doctors = st.session_state.shared_state.get("matched_doctors", [])
            log_lines.append(f"[AGENT: {agent_name}] Reading state matched_doctors: {prev_doctors}")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool GetAvailabilityList()...")
            
            selected_doc = prev_doctors[0] if prev_doctors else {"name": "Dr. Sharma", "fee": 500}
            slot = "10:00 AM" if "Morning" in time_pref else "3:00 PM"
            
            log_lines.append(f"[AGENT: {agent_name}] Lock slot at {slot} for {selected_doc['name']}.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool ReserveSlotDB()... Slot locked temporarily.")
            
            chat_msg = {
                "sender": agent_name, "avatar": "📅",
                "content": f"I verified schedules for the matching doctors. {selected_doc['name']} has an open slot tomorrow at {slot}. I've placed a temporary hold on it. Handing over to Payment Agent."
            }
            state_mutations = {"selected_doctor": selected_doc, "booking_slot": slot, "booking_status": "Temporarily Held"}
            
        elif step_num == 2:  # Payment Agent
            selected_doc = st.session_state.shared_state.get("selected_doctor", {"name": "Dr. Sharma", "fee": 500})
            fee = selected_doc.get("fee", 500)
            log_lines.append(f"[AGENT: {agent_name}] Reading doctor consultation fee: ₹{fee}")
            log_lines.append(f"[AGENT: {agent_name}] Budget limit set by user: ₹{budget}")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool CheckConsultationFee()...")
            
            if fee > budget:
                log_lines.append(f"[AGENT: {agent_name}] [CRITICAL ERROR] Fee ₹{fee} exceeds patient budget limit of ₹{budget}!")
                log_lines.append(f"[AGENT: {agent_name}] Check-in aborted. Booking rejected.")
                chat_msg = {
                    "sender": agent_name, "avatar": "💳",
                    "content": f"Warning! {selected_doc['name']}'s consultation fee is ₹{fee}, which exceeds your budget limit of ₹{budget}. Transaction declined. Reservation cancelled."
                }
                state_mutations = {"payment_verified": False, "booking_status": "Declined - Budget Exceeded", "error": "Insufficient Budget"}
                success = False
            else:
                log_lines.append(f"[AGENT: {agent_name}] Budget check passed. Calling ValidateGatewayStatus()... Gateway OK.")
                log_lines.append(f"[AGENT: {agent_name}] Transaction verified: ₹{fee} consultation fee processed.")
                chat_msg = {
                    "sender": agent_name, "avatar": "💳",
                    "content": f"Payment check successful! Verified consultation fee of ₹{fee}. Payment request generated and validated. Handing to Reminder Agent."
                }
                state_mutations = {"payment_verified": True, "fee_charged": fee, "booking_status": "Payment Verified"}
                
        elif step_num == 3:  # Reminder Agent
            doc = st.session_state.shared_state.get("selected_doctor", {"name": "Dr. Sharma"})
            slot = st.session_state.shared_state.get("booking_slot", "10:00 AM")
            log_lines.append(f"[AGENT: {agent_name}] Reading booking parameters for reminder template.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool CreateCalendarInvite()... Calendar ICS file built.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool ScheduleSMSGate()... Alert queued for tomorrow 1 hour before {slot}.")
            
            chat_msg = {
                "sender": agent_name, "avatar": "🔔",
                "content": f"I've registered calendar alerts and scheduled a SMS reminder for your appointment with {doc['name']} at {slot} tomorrow (1 hour lead time). All checks complete!"
            }
            state_mutations = {"reminder_scheduled": True, "reminder_lead_time": "1 hour", "booking_status": "Confirmed"}
            
    # --------------------------------------------------
    # Library Scenario Simulation Logic
    # --------------------------------------------------
    elif scenario_key == "library":
        book_title = params.get("book_title", "Artificial Intelligence")
        in_stock = params.get("in_stock", True)
        borrow_limit = params.get("borrow_limit", 1)
        
        if step_num == 0:  # Book Search Agent
            log_lines.append(f"[AGENT: {agent_name}] Searching book index database for: '{book_title}'")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool QueryCatalogDB()... Catalog match found.")
            
            chat_msg = {
                "sender": agent_name, "avatar": "🔍",
                "content": f"I searched the library archives. Yes, the book '{book_title}' exists in our database. Handing over to check stock levels."
            }
            state_mutations = {"book_title": book_title, "catalog_exists": True}
            
        elif step_num == 1:  # Availability Agent
            log_lines.append(f"[AGENT: {agent_name}] Checking inventory logs for '{book_title}'")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool CheckShelfStock()...")
            
            if not in_stock:
                log_lines.append(f"[AGENT: {agent_name}] [ALERT] Shelf inventory count is 0. Copy is checked out.")
                chat_msg = {
                    "sender": agent_name, "avatar": "📦",
                    "content": f"I checked the shelf. Unfortunately, all physical copies of '{book_title}' are currently borrowed by other students. I'll forward this to Reservation to queue you on the waitlist."
                }
                state_mutations = {"copies_available": 0, "waitlist_needed": True}
            else:
                log_lines.append(f"[AGENT: {agent_name}] Copy located on Shelf Row B, Shelf 4.")
                chat_msg = {
                    "sender": agent_name, "avatar": "📦",
                    "content": f"Good news! One physical copy of '{book_title}' is available on the shelf. Handing over to lock the reservation."
                }
                state_mutations = {"copies_available": 1, "waitlist_needed": False}
                
        elif step_num == 2:  # Reservation Agent
            waitlist = st.session_state.shared_state.get("waitlist_needed", False)
            log_lines.append(f"[AGENT: {agent_name}] Checking student active borrow limit: {borrow_limit} books")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool CheckUserBorrowLimit()...")
            
            if borrow_limit >= 3:
                log_lines.append(f"[AGENT: {agent_name}] [CRITICAL ERROR] Student has borrowed {borrow_limit} books (Limit: 3). Access blocked.")
                chat_msg = {
                    "sender": agent_name, "avatar": "🔐",
                    "content": f"Reservation failed. You currently have {borrow_limit} books checked out, reaching the library limit of 3 active loans. Please return a book to continue."
                }
                state_mutations = {"reservation_locked": False, "reservation_status": "Blocked - Limit Reached", "error": "Borrow Limit Exceeded"}
                success = False
            else:
                log_lines.append(f"[AGENT: {agent_name}] User limit check passed. Calling HoldCopyDB()...")
                if waitlist:
                    log_lines.append(f"[AGENT: {agent_name}] User added to Book Waitlist at position #1.")
                    chat_msg = {
                        "sender": agent_name, "avatar": "🔐",
                        "content": f"Since physical stock is out, I have placed your student ID #2948 in Waitlist Position 1 for '{book_title}'."
                    }
                    state_mutations = {"reservation_locked": True, "reservation_status": "Queued on Waitlist", "waitlist_pos": 1}
                else:
                    log_lines.append(f"[AGENT: {agent_name}] Physical copy locked under reservation ID 58291.")
                    chat_msg = {
                        "sender": agent_name, "avatar": "🔐",
                        "content": f"I have locked the available physical copy of '{book_title}' and reserved it under your student account. Forwarding to Notification Agent."
                    }
                    state_mutations = {"reservation_locked": True, "reservation_status": "Reserved", "hold_id": 58291}
                    
        elif step_num == 3:  # Notification Agent
            status = st.session_state.shared_state.get("reservation_status", "Reserved")
            hold_id = st.session_state.shared_state.get("hold_id", "Waitlist")
            log_lines.append(f"[AGENT: {agent_name}] Generating pickup code / barcode token.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool GenerateBarcode()... Token: lib_hold_{hold_id}")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool DispatchEmail()... Sent confirmation notification.")
            
            chat_msg = {
                "sender": agent_name, "avatar": "✉️",
                "content": f"Hold transaction complete! A pickup slip showing status '{status}' and barcode ID lib_hold_{hold_id} has been emailed to your student address. Pickup window is active."
            }
            state_mutations = {"notification_sent": True, "notification_type": "Email Slip", "barcode": f"LIB-HOLD-{hold_id}"}

    # --------------------------------------------------
    # Flight Scenario Simulation Logic
    # --------------------------------------------------
    elif scenario_key == "flight":
        ticket_valid = params.get("ticket_valid", "Confirmed")
        seat_pref = params.get("seat_pref", "Window")
        
        if step_num == 0:  # Flight Verification Agent
            log_lines.append(f"[AGENT: {agent_name}] Verifying booking database records.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool QueryPnrDB(pnr='AI-720')...")
            
            if ticket_valid == "Invalid PNR / Cancelled":
                log_lines.append(f"[AGENT: {agent_name}] [CRITICAL ERROR] Booking record for PNR: AI-720 shows status: CANCELLED/VOID.")
                chat_msg = {
                    "sender": agent_name, "avatar": "🛂",
                    "content": "Check-in failed. I could not locate a valid ticket under PNR AI-720. Your booking shows as cancelled or unconfirmed."
                }
                state_mutations = {"ticket_confirmed": False, "status": "Failed - Invalid PNR", "error": "Invalid PNR"}
                success = False
            else:
                log_lines.append(f"[AGENT: {agent_name}] Match located. PNR AI-720 is confirmed for Flight AI-502 tomorrow.")
                chat_msg = {
                    "sender": agent_name, "avatar": "🛂",
                    "content": "Ticket verified! I located confirmed booking PNR AI-720. Passenger is cleared for check-in. Forwarding to Seat Selection."
                }
                state_mutations = {"ticket_confirmed": True, "pnr": "AI-720", "flight_num": "AI-502", "route": "DEL → BOM"}
                
        elif step_num == 1:  # Seat Selection Agent
            pref = seat_pref
            log_lines.append(f"[AGENT: {agent_name}] Fetching layout mapping. Calling tool GetCabinMap()...")
            log_lines.append(f"[AGENT: {agent_name}] Target preference set to: '{pref}' seat")
            
            if pref == "Window":
                seat = "18A"
            elif pref == "Aisle":
                seat = "12C"
            else:
                seat = "15D (Emergency Exit)"
                
            log_lines.append(f"[AGENT: {agent_name}] Seat {seat} is open. Calling tool LockSeatAPI()... Locked.")
            chat_msg = {
                "sender": agent_name, "avatar": "💺",
                "content": f"I checked the layout for flight AI-502. Your preferred '{pref}' seat was available, and I have assigned you seat {seat}. Handing off to confirm check-in."
            }
            state_mutations = {"assigned_seat": seat, "seat_class": "Economy"}
            
        elif step_num == 2:  # Check-in Agent
            seat = st.session_state.shared_state.get("assigned_seat", "18A")
            log_lines.append(f"[AGENT: {agent_name}] Assembling check-in manifest data package.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool SubmitManifest()... Flight manifest updated successfully.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool CompleteRegistration()... Digital registration complete.")
            
            chat_msg = {
                "sender": agent_name, "avatar": "✅",
                "content": f"Check-in complete! Passenger checked into manifest with seat {seat}. Generating boarding pass next."
            }
            state_mutations = {"check_in_complete": True, "check_in_timestamp": "2026-06-11 12:46:00"}
            
        elif step_num == 3:  # Notification Agent
            seat = st.session_state.shared_state.get("assigned_seat", "18A")
            pnr = st.session_state.shared_state.get("pnr", "AI-720")
            flight = st.session_state.shared_state.get("flight_num", "AI-502")
            route = st.session_state.shared_state.get("route", "DEL → BOM")
            
            log_lines.append(f"[AGENT: {agent_name}] Creating digital boarding pass card.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool GenerateQRCode()... Pass generated.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool SendSMSAlert()... Pass delivered to mobile.")
            
            chat_msg = {
                "sender": agent_name, "avatar": "📱",
                "content": f"Boarding pass issued for {route}! I've generated your QR code and texted your mobile pass. Safe travels!"
            }
            state_mutations = {"boarding_pass_issued": True, "pass_qr_code": f"QR-PASS-{pnr}-{seat}"}

    # --------------------------------------------------
    # Hotel Scenario Simulation Logic
    # --------------------------------------------------
    elif scenario_key == "hotel":
        room_num = params.get("room_num", "Room 304")
        extend_days = params.get("extend_days", 2)
        room_available = params.get("room_available", True)
        card_declined = params.get("card_declined", False)
        
        if step_num == 0:  # Booking Verification Agent
            log_lines.append(f"[AGENT: {agent_name}] Fetching current booking folio for: '{room_num}'")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool GetStayDetails()... Match found.")
            
            chat_msg = {
                "sender": agent_name, "avatar": "🏨",
                "content": f"Verified! Guest in room {room_num} is active. Current checkout is tomorrow morning. Passing to Room Availability Agent."
            }
            state_mutations = {"room_num": room_num, "checkout_current": "Tomorrow morning", "guest_name": "Arpit Rawat"}
            
        elif step_num == 1:  # Room Availability Agent
            log_lines.append(f"[AGENT: {agent_name}] Checking PMS room occupancy calendar for {room_num}")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool CheckRoomInventory()...")
            
            if not room_available:
                log_lines.append(f"[AGENT: {agent_name}] [CRITICAL ALERT] {room_num} is booked by another guest starting tomorrow.")
                log_lines.append(f"[AGENT: {agent_name}] Calling tool FindAlternativeRoom()... Room 412 is open.")
                chat_msg = {
                    "sender": agent_name, "avatar": "🧹",
                    "content": f"Your current room ({room_num}) is already reserved by another party tomorrow. However, I checked alternate inventory, and we can move you to Room 412 (same category) for the extra {extend_days} days. Proceeding to payment."
                }
                state_mutations = {"room_available_same": False, "target_room": "Room 412", "daily_rate": 2000}
            else:
                log_lines.append(f"[AGENT: {agent_name}] Current room is open for extension. No conflicting reservations.")
                chat_msg = {
                    "sender": agent_name, "avatar": "🧹",
                    "content": f"Excellent! {room_num} is free for the next {extend_days} days. I'll extend your stay in the same room. Forwarding to Billing Agent."
                }
                state_mutations = {"room_available_same": True, "target_room": room_num, "daily_rate": 2000}
                
        elif step_num == 2:  # Payment Agent
            t_room = st.session_state.shared_state.get("target_room", room_num)
            rate = st.session_state.shared_state.get("daily_rate", 2000)
            total_bill = rate * extend_days
            log_lines.append(f"[AGENT: {agent_name}] Calculating extension billing: {extend_days} days @ ₹{rate}/night = ₹{total_bill}")
            log_lines.append(f"[AGENT: {agent_name}] Requesting credit authorization for ₹{total_bill}...")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool ChargeCreditCard()...")
            
            if card_declined:
                log_lines.append(f"[AGENT: {agent_name}] [CRITICAL ERROR] Credit Card processor returned status: DECLINED.")
                chat_msg = {
                    "sender": agent_name, "avatar": "💵",
                    "content": f"Credit Card decline! We tried to charge ₹{total_bill} to your card on file, but it was declined. Stay extension aborted. Please visit the reception counter."
                }
                state_mutations = {"payment_processed": False, "error": "Payment Declined", "checkout_status": "Overdue tomorrow"}
                success = False
            else:
                log_lines.append(f"[AGENT: {agent_name}] Payment status: AUTHORIZED. Folio balance updated.")
                chat_msg = {
                    "sender": agent_name, "avatar": "💵",
                    "content": f"Payment of ₹{total_bill} processed and billed to your room folio. Forwarding to Manager to complete database updates."
                }
                state_mutations = {"payment_processed": True, "total_charged": total_bill}
                
        elif step_num == 3:  # Confirmation Agent
            t_room = st.session_state.shared_state.get("target_room", room_num)
            days = extend_days
            log_lines.append(f"[AGENT: {agent_name}] Updating booking checkout bounds in PMS database.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool UpdateCheckOutDatePMS()... Database checkout updated.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool ExtendKeycardAccess()... Programming key card commands sent.")
            
            chat_msg = {
                "sender": agent_name, "avatar": "🔑",
                "content": f"Stay extension finalized! Room check-out date updated by {days} days. Your keycard access for {t_room} has been electronically extended. Enjoy your stay!"
            }
            state_mutations = {"keycard_extended": True, "final_room": t_room, "status": "Stay Extended Successful"}

    # --------------------------------------------------
    # Daily Commute Scenario Simulation Logic
    # --------------------------------------------------
    elif scenario_key == "commute":
        congestion = params.get("traffic_congestion", "Heavy Congestion (Accident)")
        cab_type = params.get("cab_type", "Prime Sedan")
        
        if step_num == 0:  # Traffic Monitoring Agent
            log_lines.append(f"[AGENT: {agent_name}] Fetching city congestion telemetry mapping.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool GetLiveTrafficAlerts()...")
            
            if congestion == "Heavy Congestion (Accident)":
                log_lines.append(f"[AGENT: {agent_name}] [ALERT] Major accident on Highway Route A. 35 mins delay.")
                chat_msg = {
                    "sender": agent_name, "avatar": "🚦",
                    "content": "Traffic alert! I scanned your typical Route A. There's heavy congestion and a block due to an accident, causing a 35-minute delay. Handing to Route Optimizer."
                }
                state_mutations = {"route_a_traffic": "Blocked", "route_a_time": 55}
            elif congestion == "Moderate Traffic":
                log_lines.append(f"[AGENT: {agent_name}] Standard slow traffic on Route A. 15 mins delay.")
                chat_msg = {
                    "sender": agent_name, "avatar": "🚦",
                    "content": "Route A is showing moderate commuter rush, adding about 15 minutes to your trip. Forwarding to Route Optimizer."
                }
                state_mutations = {"route_a_traffic": "Slow", "route_a_time": 35}
            else:
                log_lines.append(f"[AGENT: {agent_name}] Route A is clear. Normal transit times.")
                chat_msg = {
                    "sender": agent_name, "avatar": "🚦",
                    "content": "Excellent. Route A has light traffic today. Travel time is clear. Passing details on."
                }
                state_mutations = {"route_a_traffic": "Clear", "route_a_time": 20}
                
        elif step_num == 1:  # Route Optimization Agent
            route_a_state = st.session_state.shared_state.get("route_a_traffic", "Blocked")
            a_time = st.session_state.shared_state.get("route_a_time", 55)
            log_lines.append(f"[AGENT: {agent_name}] Reading traffic inputs. Route A: {a_time} mins.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool ComputeShortestPath()... Alternative Route B analyzed.")
            
            if a_time > 30:
                b_time = 25
                log_lines.append(f"[AGENT: {agent_name}] Alternative Route B selected: saves {a_time - b_time} minutes.")
                chat_msg = {
                    "sender": agent_name, "avatar": "🗺️",
                    "content": f"Bypassing Route A! Route B (bypass lane) will bypass the block, taking only {b_time} minutes. Selecting Route B. Passing to Cab Booking."
                }
                state_mutations = {"selected_route": "Route B (Bypass)", "commute_time_mins": b_time}
            else:
                log_lines.append(f"[AGENT: {agent_name}] Route A remains optimal at {a_time} minutes.")
                chat_msg = {
                    "sender": agent_name, "avatar": "🗺️",
                    "content": f"Route A remains the fastest path at {a_time} minutes. Staying on Route A. Passing to Cab Booking."
                }
                state_mutations = {"selected_route": "Route A (Standard)", "commute_time_mins": a_time}
                
        elif step_num == 2:  # Transport Booking Agent
            sel_route = st.session_state.shared_state.get("selected_route", "Route B")
            log_lines.append(f"[AGENT: {agent_name}] Integrating rideshare APIs. Choosing cab type: {cab_type}")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool RequestCabRide(route='{sel_route}')...")
            
            price = 450 if "Sedan" in cab_type else (300 if "Mini" in cab_type else 150)
            driver = "Rajesh Kumar (Rating: 4.9)"
            plate = "DL 1CA 4829"
            
            log_lines.append(f"[AGENT: {agent_name}] Cab locked. Driver: {driver}, Plate: {plate}, Cost: ₹{price}")
            chat_msg = {
                "sender": agent_name, "avatar": "🚖",
                "content": f"Cab request successful! I have booked a {cab_type} driven by {driver} (License: {plate}) on the optimized {sel_route}. Estimated fare: ₹{price}. Passing dispatcher updates to Notifications."
            }
            state_mutations = {"cab_booked": True, "driver_details": driver, "license_plate": plate, "cab_fare": price}
            
        elif step_num == 3:  # Notification Agent
            driver = st.session_state.shared_state.get("driver_details", "Rajesh Kumar")
            plate = st.session_state.shared_state.get("license_plate", "DL 1CA 4829")
            eta = 5
            route = st.session_state.shared_state.get("selected_route", "Route B")
            dur = st.session_state.shared_state.get("commute_time_mins", 25)
            
            log_lines.append(f"[AGENT: {agent_name}] Formatting passenger SMS alert package.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool SendSMSAlert()... SMS dispatched.")
            
            chat_msg = {
                "sender": agent_name, "avatar": "🔔",
                "content": f"All set! Driver {driver} is 5 mins away. Your ride route: {route} ({dur} mins travel time). Check your phone for details."
            }
            state_mutations = {"commute_notified": True, "commute_status": "On its way", "cab_eta_mins": eta}

    # --------------------------------------------------
    # Skill Scenario Simulation Logic
    # --------------------------------------------------
    elif scenario_key == "skill":
        goal = params.get("career_goal", "Data Scientist")
        known = params.get("known_skills", "None (Beginner)")
        
        if step_num == 0:  # Career Analysis Agent
            log_lines.append(f"[AGENT: {agent_name}] Querying industry capability maps for: '{goal}'")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool FetchCareerProfile()... Required standards list fetched.")
            
            if "Data Scientist" in goal:
                skills_needed = ["Python", "SQL Data Query", "Machine Learning Core", "Probability Statistics"]
            elif "Web Developer" in goal:
                skills_needed = ["HTML5 & CSS3", "JavaScript UI (React)", "NodeJS Backends", "API design"]
            else:
                skills_needed = ["AWS/GCP Architecture", "Docker Containers", "CI/CD Automations", "Kubernetes Scales"]
                
            log_lines.append(f"[AGENT: {agent_name}] Skills required: " + ", ".join(skills_needed))
            chat_msg = {
                "sender": agent_name, "avatar": "🎓",
                "content": f"A target role of '{goal}' requires core competencies in: " + ", ".join(skills_needed) + ". Passing this to Skill Gap Analyst."
            }
            state_mutations = {"career_goal": goal, "required_skills": skills_needed}
            
        elif step_num == 1:  # Skill Gap Agent
            req = st.session_state.shared_state.get("required_skills", [])
            log_lines.append(f"[AGENT: {agent_name}] Reading student profile records. Prior skills: '{known}'")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool AssessStudentProfile()...")
            
            # Map pre-existing skills
            known_list = []
            if "Python & SQL" in known:
                known_list = ["Python", "SQL Data Query"]
            elif "JavaScript" in known:
                known_list = ["HTML5 & CSS3", "JavaScript UI (React)"]
            elif "Linux" in known:
                known_list = ["AWS/GCP Architecture"]
                
            gap_skills = [s for s in req if s not in known_list]
            log_lines.append(f"[AGENT: {agent_name}] Competency Gap detected: " + ", ".join(gap_skills))
            
            chat_msg = {
                "sender": agent_name, "avatar": "📊",
                "content": f"Compared with your background in '{known}', the major gaps you need to master are: " + 
                           ", ".join(gap_skills) + ". Handing off to get curriculum recommendations."
            }
            state_mutations = {"known_skills_list": known_list, "gap_skills_list": gap_skills}
            
        elif step_num == 2:  # Course Recommendation Agent
            gap = st.session_state.shared_state.get("gap_skills_list", [])
            log_lines.append(f"[AGENT: {agent_name}] Searching matching course directories.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool SearchCourseCatalogs()... Match complete.")
            
            courses = []
            for g in gap:
                if "Python" in g:
                    courses.append({"skill": g, "course": "Python for Data Analysis (Coursera)", "cost": "Free Audit"})
                elif "SQL" in g:
                    courses.append({"skill": g, "course": "Advanced SQL Databases (Udemy)", "cost": "₹499"})
                elif "Learning" in g:
                    courses.append({"skill": g, "course": "Introduction to Machine Learning (Andrew Ng)", "cost": "Free Audit"})
                elif "React" in g:
                    courses.append({"skill": g, "course": "React - The Complete Guide (Academind)", "cost": "₹499"})
                elif "Node" in g:
                    courses.append({"skill": g, "course": "NodeJS Backend Foundations (Coursera)", "cost": "Free"})
                elif "Containers" in g:
                    courses.append({"skill": g, "course": "Docker & Kubernetes Mastery", "cost": "₹499"})
                else:
                    courses.append({"skill": g, "course": f"Foundations of {g} (Pluralsight)", "cost": "Trial Free"})
                    
            log_lines.append(f"[AGENT: {agent_name}] Recommending {len(courses)} curriculum items.")
            chat_msg = {
                "sender": agent_name, "avatar": "📖",
                "content": "I mapped out course curriculums for your skill gaps: " + 
                           "; ".join([f"{c['skill']} → {c['course']} ({c['cost']})" for c in courses]) + ". Passing to Coach to structure path."
            }
            state_mutations = {"recommended_courses": courses}
            
        elif step_num == 3:  # Progress Tracking Agent
            courses = st.session_state.shared_state.get("recommended_courses", [])
            log_lines.append(f"[AGENT: {agent_name}] Compiling academic milestones worksheet.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool GenerateSyllabusChecklist()... PDF syllabus created.")
            log_lines.append(f"[AGENT: {agent_name}] Setting up study schedule reminder triggers.")
            
            chat_msg = {
                "sender": agent_name, "avatar": "🏆",
                "content": f"Personalized syllabus roadmap compiled successfully! I've scheduled weekly email reports to keep track of your goals. You're ready to start!"
            }
            state_mutations = {"roadmap_ready": True, "weeks_to_complete": len(courses) * 4}

    # --------------------------------------------------
    # Vacation Scenario Simulation Logic
    # --------------------------------------------------
    elif scenario_key == "vacation":
        budget = params.get("budget_val", 30000)
        dur = params.get("duration", "5 Days")
        travelers = params.get("travelers", 2)
        
        if step_num == 0:  # Destination Recommendation Agent
            log_lines.append(f"[AGENT: {agent_name}] Filtering cities with holiday weather. Budget limit: ₹{budget} for {travelers} travelers.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool FilterDestinationsByPrice()...")
            
            if budget < 25000:
                dests = [{"city": "Jaipur", "avg_cost": 18000, "reason": "Affordable forts & palaces stay"},
                         {"city": "Udaipur", "avg_cost": 22000, "reason": "Lakes & heritage walks"}]
            else:
                dests = [{"city": "Goa", "avg_cost": 28000, "reason": "Beaches & sea activities"},
                         {"city": "Jaipur", "avg_cost": 18000, "reason": "Historical sight-seeing tour"}]
                         
            log_lines.append(f"[AGENT: {agent_name}] Found destinations: " + ", ".join([d["city"] for d in dests]))
            chat_msg = {
                "sender": agent_name, "avatar": "🏖️",
                "content": f"Hi! With a budget of ₹{budget} for {travelers} people, I recommend: " + 
                           ", ".join([f"{d['city']} ({d['reason']})" for d in dests]) + ". Forwarding to Budget Planner."
            }
            state_mutations = {"dest_list": dests, "total_budget": budget, "num_travelers": travelers, "dur": dur}
            
        elif step_num == 1:  # Budget Planning Agent
            dests = st.session_state.shared_state.get("dest_list", [])
            log_lines.append(f"[AGENT: {agent_name}] Doing detail costing for travel options. Calling tool SearchCheapFlights()...")
            
            # Select destination based on budget
            selected_dest = dests[-1] if dests else {"city": "Jaipur", "avg_cost": 18000}
            for d in dests:
                if d["city"] == "Goa" and budget >= 28000:
                    selected_dest = d
                    break
                    
            flight_cost = 6000 * travelers
            hotel_cost = 2500 * (5 if "5" in dur else (3 if "3" in dur else 7))
            total_est = flight_cost + hotel_cost
            
            log_lines.append(f"[AGENT: {agent_name}] Cost details for {selected_dest['city']}: Flights: ₹{flight_cost}, Hotel: ₹{hotel_cost}. Total: ₹{total_est}")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool EstimateHotelCosts()...")
            
            if total_est > budget:
                log_lines.append(f"[AGENT: {agent_name}] [CRITICAL ERROR] Estimated cost ₹{total_est} exceeds maximum budget of ₹{budget}!")
                chat_msg = {
                    "sender": agent_name, "avatar": "💸",
                    "content": f"Cost warning! Goa flights/hotel total ₹{total_est}, which exceeds your ₹{budget} budget for {travelers} people. Let me check if we can switch destination to Jaipur."
                }
                # Reroute to Jaipur automatically
                selected_dest = {"city": "Jaipur", "avg_cost": 18000}
                flight_cost = 4000 * travelers
                hotel_cost = 1500 * (5 if "5" in dur else (3 if "3" in dur else 7))
                total_est = flight_cost + hotel_cost
                log_lines.append(f"[AGENT: {agent_name}] Rerouting to Jaipur. New cost: ₹{total_est}. Budget matches.")
                
            chat_msg = {
                "sender": agent_name, "avatar": "💸",
                "content": f"I calculated costs for {selected_dest['city']}. Total estimated: ₹{total_est} (Flights: ₹{flight_cost}, Hotel: ₹{hotel_cost}). Fits budget! Forwarding to book packages."
            }
            state_mutations = {"selected_dest": selected_dest, "flight_cost": flight_cost, "hotel_cost": hotel_cost, "total_est": total_est}
            
        elif step_num == 2:  # Booking Agent
            dest = st.session_state.shared_state.get("selected_dest", {"city": "Jaipur"})
            log_lines.append(f"[AGENT: {agent_name}] Sending ticketing requests to Booking GDS APIs.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool LockFlightSeat()... Seats confirmed.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool PlaceTemporaryHoldHotel()... Hotel reservation verified.")
            
            chat_msg = {
                "sender": agent_name, "avatar": "🏨",
                "content": f"Booking complete! Flight tickets and hotel packages pre-booked successfully for your trip to {dest['city']}. Handing to Itinerary Architect."
            }
            state_mutations = {"booking_confirmed": True, "booking_reference": "VAC-5928-HTL"}
            
        elif step_num == 3:  # Itinerary Agent
            dest = st.session_state.shared_state.get("selected_dest", {"city": "Jaipur"})
            log_lines.append(f"[AGENT: {agent_name}] Compiling day-by-day vacation itinerary layout.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool GetLocalActivities()... Activities list added.")
            log_lines.append(f"[AGENT: {agent_name}] Calling tool CompileItineraryPdf()... Visual brochure rendered.")
            
            chat_msg = {
                "sender": agent_name, "avatar": "🗺️",
                "content": f"Itinerary complete! I've designed a day-wise sightseeing plan for {dest['city']}. Your complete travel brochure package has been generated successfully!"
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
        if status == "Confirmed":
            doc = state.get("selected_doctor", {"name": "Dr. Sharma", "fee": 500})
            slot = state.get("booking_slot", "10:00 AM")
            illness = state.get("illness", "Fever")
            fee = state.get("fee_charged", 500)
            
            html = f"""
            <div style="background:#fff; color:#0f172a; border-radius:12px; padding:20px; font-family:'Inter', sans-serif; box-shadow:0 10px 20px rgba(0,0,0,0.3); border-top:6px solid #10b981; max-width:400px; margin:auto;">
                <div style="text-align:center; border-bottom:2px dashed #cbd5e1; padding-bottom:12px; margin-bottom:14px;">
                    <div style="font-size:1.4rem; font-weight:800; text-transform:uppercase; letter-spacing:0.5px;">Clinic Appointment</div>
                    <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Digital Confirmation Voucher</div>
                </div>
                <div style="display:flex; flex-direction:column; gap:8px; font-size:0.85rem;">
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Patient:</span><span style="font-weight:600;">Arpit Rawat</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Symptom:</span><span style="font-weight:600;">{illness}</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Physician:</span><span style="font-weight:600;">{doc['name']}</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Time slot:</span><span style="font-weight:600; color:#6366f1;">Tomorrow at {slot}</span></div>
                    <div style="display:flex; justify-content:space-between; border-top:1px solid #cbd5e1; padding-top:8px; font-weight:700; font-size:1rem;"><span style="color:#0f172a;">Consultation Fee:</span><span>₹{fee}</span></div>
                </div>
                <div style="margin-top:16px; border-top:2px dashed #cbd5e1; padding-top:14px; text-align:center;">
                    <div style="font-family:monospace; font-size:1.8rem; letter-spacing:2px; background:#f1f5f9; padding:4px 0; border-radius:4px; display:inline-block; width:100%; color:#000;">||||||||||||||||||||||||||</div>
                    <div style="font-size:0.65rem; color:#64748b; margin-top:4px; font-family:monospace;">CL-HOLD-58291</div>
                </div>
            </div>
            """
        else: # Failure / Declined
            error_reason = state.get("error", "Insufficient Budget")
            html = f"""
            <div style="background:#fff; color:#0f172a; border-radius:12px; padding:20px; font-family:'Inter', sans-serif; box-shadow:0 10px 20px rgba(0,0,0,0.3); border-top:6px solid #ef4444; max-width:400px; margin:auto; text-align:center;">
                <div style="color:#ef4444; font-size:3rem; margin-bottom:10px;">❌</div>
                <div style="font-size:1.2rem; font-weight:800; text-transform:uppercase; color:#ef4444;">Booking Refused</div>
                <div style="font-size:0.85rem; color:#64748b; margin:10px 0 20px 0;">Reason: {error_reason} (Consultation cost exceeds user defined budget limit).</div>
                <div style="font-size:0.75rem; background:#fee2e2; color:#ef4444; padding:8px 12px; border-radius:6px; font-weight:600;">STATUS: TRANSACTION_ABORTED</div>
            </div>
            """
        return html

    elif scenario_key == "library":
        status = state.get("reservation_status", "Denied")
        if "Limit" in status or "Blocked" in status:
            error_reason = state.get("error", "Limit Exceeded")
            html = f"""
            <div style="background:#fff; color:#0f172a; border-radius:12px; padding:20px; font-family:'Inter', sans-serif; box-shadow:0 10px 20px rgba(0,0,0,0.3); border-top:6px solid #ef4444; max-width:400px; margin:auto; text-align:center;">
                <div style="color:#ef4444; font-size:3rem; margin-bottom:10px;">🔐</div>
                <div style="font-size:1.2rem; font-weight:800; text-transform:uppercase; color:#ef4444;">Loan Blocked</div>
                <div style="font-size:0.85rem; color:#64748b; margin:10px 0 20px 0;">Reason: {error_reason} (Student limit of 3 books already reached).</div>
                <div style="font-size:0.75rem; background:#fee2e2; color:#ef4444; padding:8px 12px; border-radius:6px; font-weight:600;">ACTION REQUIRED: RETURN AN ACTIVE LOAN</div>
            </div>
            """
        else:
            book = state.get("book_title", "Artificial Intelligence")
            bar = state.get("barcode", "LIB-HOLD-58291")
            html = f"""
            <div style="background:#fff; color:#0f172a; border-radius:12px; padding:20px; font-family:'Inter', sans-serif; box-shadow:0 10px 20px rgba(0,0,0,0.3); border-top:6px solid #0ea5e9; max-width:400px; margin:auto;">
                <div style="text-align:center; border-bottom:2px dashed #cbd5e1; padding-bottom:12px; margin-bottom:14px;">
                    <div style="font-size:1.4rem; font-weight:800; text-transform:uppercase; letter-spacing:0.5px; color:#0ea5e9;">Library Borrow slip</div>
                    <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Digital Reservation Pass</div>
                </div>
                <div style="display:flex; flex-direction:column; gap:8px; font-size:0.85rem;">
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Student ID:</span><span style="font-weight:600;">#2948</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Target Book:</span><span style="font-weight:600; text-align:right;">{book}</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Reservation Status:</span><span style="font-weight:700; color:#10b981;">{status}</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Hold Period:</span><span style="font-weight:600;">48 Hours</span></div>
                </div>
                <div style="margin-top:16px; border-top:2px dashed #cbd5e1; padding-top:14px; text-align:center;">
                    <div style="font-family:monospace; font-size:1.8rem; letter-spacing:2px; background:#f1f5f9; padding:4px 0; border-radius:4px; display:inline-block; width:100%; color:#000;">* {bar} *</div>
                    <div style="font-size:0.65rem; color:#64748b; margin-top:4px; font-family:monospace;">PICKUP WINDOW ENDS IN 48 HOURS</div>
                </div>
            </div>
            """
        return html

    elif scenario_key == "flight":
        if "Failed" in state.get("status", ""):
            html = f"""
            <div style="background:#fff; color:#0f172a; border-radius:12px; padding:20px; font-family:'Inter', sans-serif; box-shadow:0 10px 20px rgba(0,0,0,0.3); border-top:6px solid #ef4444; max-width:400px; margin:auto; text-align:center;">
                <div style="color:#ef4444; font-size:3rem; margin-bottom:10px;">⚠️</div>
                <div style="font-size:1.2rem; font-weight:800; text-transform:uppercase; color:#ef4444;">Check-in Denied</div>
                <div style="font-size:0.85rem; color:#64748b; margin:10px 0 20px 0;">No active flight booking located under PNR AI-720. Verification failed.</div>
                <div style="font-size:0.75rem; background:#fee2e2; color:#ef4444; padding:8px 12px; border-radius:6px; font-weight:600;">REASON: INVALID_PNR_RECORD</div>
            </div>
            """
        else:
            seat = state.get("assigned_seat", "18A")
            pnr = state.get("pnr", "AI-720")
            flight = state.get("flight_num", "AI-502")
            route = state.get("route", "DEL → BOM")
            html = f"""
            <div style="background: linear-gradient(135deg, #0f172a, #1e293b); color:#fff; border-radius:14px; border: 1px solid #334155; padding:20px; width:100%; max-width:400px; margin:auto; box-shadow:0 10px 30px rgba(0,0,0,0.4); display:flex; flex-direction:column; gap:12px;">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.1); padding-bottom:10px;">
                    <span style="font-family:'Outfit', sans-serif; font-weight:700; font-size:1rem; color:#0ea5e9; display:flex; align-items:center; gap:6px;">✈️ AIRLINE PASS</span>
                    <span style="font-size:0.65rem; text-transform:uppercase; background-color:rgba(14,165,233,0.15); color:#0ea5e9; padding:2px 8px; border-radius:10px; font-weight:600;">ECONOMY CLASS</span>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0;">
                    <div style="display:flex; flex-direction:column;">
                        <span style="font-family:'Outfit', sans-serif; font-size:1.6rem; font-weight:800; line-height:1;">DEL</span>
                        <span style="font-size:0.7rem; color:#94a3b8;">New Delhi</span>
                    </div>
                    <div style="color:#6366f1; font-weight:bold; font-size:1.2rem;">➔</div>
                    <div style="display:flex; flex-direction:column; text-align:right;">
                        <span style="font-family:'Outfit', sans-serif; font-size:1.6rem; font-weight:800; line-height:1;">BOM</span>
                        <span style="font-size:0.7rem; color:#94a3b8;">Mumbai</span>
                    </div>
                </div>
                <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:10px; background-color:rgba(0,0,0,0.2); border-radius:8px; padding:12px; border:1px solid rgba(255,255,255,0.05); text-align:center;">
                    <div><span style="font-size:0.6rem; color:#94a3b8; display:block;">FLIGHT</span><span style="font-size:0.85rem; font-weight:700; font-family:monospace;">{flight}</span></div>
                    <div><span style="font-size:0.6rem; color:#94a3b8; display:block;">SEAT</span><span style="font-size:0.85rem; font-weight:700; font-family:monospace; color:#10b981;">{seat}</span></div>
                    <div><span style="font-size:0.6rem; color:#94a3b8; display:block;">PNR</span><span style="font-size:0.85rem; font-weight:700; font-family:monospace;">{pnr}</span></div>
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px dashed rgba(255,255,255,0.1); padding-top:12px; margin-top:4px;">
                    <div>
                        <div style="font-size:0.75rem; font-weight:700; color:#10b981;">BOARDING ISSUED</div>
                        <div style="font-size:0.65rem; color:#94a3b8;">Please present barcode at gate.</div>
                    </div>
                    <div style="width:46px; height:46px; background:#fff; border-radius:4px; padding:3px;">
                        <svg viewBox="0 0 24 24" fill="black"><rect x="0" y="0" width="4" height="4"/><rect x="8" y="0" width="4" height="4"/><rect x="16" y="0" width="4" height="4"/><rect x="0" y="8" width="4" height="4"/><rect x="8" y="8" width="4" height="4"/><rect x="16" y="8" width="4" height="4"/><rect x="0" y="16" width="4" height="4"/><rect x="8" y="16" width="4" height="4"/><rect x="16" y="16" width="4" height="4"/></svg>
                    </div>
                </div>
            </div>
            """
        return html

    elif scenario_key == "hotel":
        if "Declined" in state.get("error", ""):
            html = f"""
            <div style="background:#fff; color:#0f172a; border-radius:12px; padding:20px; font-family:'Inter', sans-serif; box-shadow:0 10px 20px rgba(0,0,0,0.3); border-top:6px solid #ef4444; max-width:400px; margin:auto; text-align:center;">
                <div style="color:#ef4444; font-size:3rem; margin-bottom:10px;">💳</div>
                <div style="font-size:1.2rem; font-weight:800; text-transform:uppercase; color:#ef4444;">Extension Aborted</div>
                <div style="font-size:0.85rem; color:#64748b; margin:10px 0 20px 0;">Folio Payment Declined! Credit card transaction failed authorization.</div>
                <div style="font-size:0.75rem; background:#fee2e2; color:#ef4444; padding:8px 12px; border-radius:6px; font-weight:600;">VISIT RECEPTION COUNTER IMMEDIATELY</div>
            </div>
            """
        else:
            room = state.get("final_room", "Room 304")
            bill = state.get("total_charged", 4000)
            status = state.get("status", "Extended")
            html = f"""
            <div style="background:#fff; color:#0f172a; border-radius:12px; padding:20px; font-family:'Inter', sans-serif; box-shadow:0 10px 20px rgba(0,0,0,0.3); border-top:6px solid #6366f1; max-width:400px; margin:auto;">
                <div style="text-align:center; border-bottom:2px dashed #cbd5e1; padding-bottom:12px; margin-bottom:14px;">
                    <div style="font-size:1.3rem; font-weight:800; text-transform:uppercase; letter-spacing:0.5px;">Hotel Folio Invoice</div>
                    <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Digital Room Extension Slip</div>
                </div>
                <div style="display:flex; flex-direction:column; gap:8px; font-size:0.85rem;">
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Guest Name:</span><span style="font-weight:600;">Arpit Rawat</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Assigned Room:</span><span style="font-weight:600; color:#6366f1;">{room}</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Status:</span><span style="font-weight:700; color:#10b981;">{status}</span></div>
                    <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Folio Bill:</span><span style="font-weight:600;">₹{bill} (Charged to Card)</span></div>
                </div>
                <div style="margin-top:16px; border-top:2px dashed #cbd5e1; padding-top:14px; text-align:center;">
                    <div style="font-size:0.75rem; font-weight:bold; color:#10b981; background:#d1fae5; display:inline-block; padding:4px 12px; border-radius:6px;">RFID KEY CARD EXTENDED IN PMS</div>
                </div>
            </div>
            """
        return html

    elif scenario_key == "commute":
        driver = state.get("driver_details", "Rajesh Kumar")
        plate = state.get("license_plate", "DL 1CA 4829")
        fare = state.get("cab_fare", 450)
        route = state.get("selected_route", "Route B")
        dur = state.get("commute_time_mins", 25)
        html = f"""
        <div style="background:#1e293b; color:#fff; border-radius:12px; padding:20px; font-family:'Inter', sans-serif; box-shadow:0 10px 20px rgba(0,0,0,0.3); border-top:6px solid #eab308; max-width:400px; margin:auto; border:1px solid #334155;">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #334155; padding-bottom:10px; margin-bottom:12px;">
                <span style="font-weight:700; color:#eab308; font-size:0.95rem;">🚖 CAB DISPATCH VOUCHER</span>
                <span style="font-size:0.65rem; background:#3f3f46; color:#a1a1aa; padding:2px 6px; border-radius:4px;">CONFIRMED</span>
            </div>
            <div style="display:flex; flex-direction:column; gap:8px; font-size:0.85rem;">
                <div style="display:flex; justify-content:space-between;"><span style="color:#94a3b8;">Driver:</span><span style="font-weight:600;">{driver}</span></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#94a3b8;">Vehicle License:</span><span style="font-weight:600; font-family:monospace; color:#eab308;">{plate}</span></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#94a3b8;">Route:</span><span style="font-weight:600;">{route}</span></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#94a3b8;">Transit Duration:</span><span style="font-weight:600; color:#10b981;">{dur} Minutes</span></div>
                <div style="display:flex; justify-content:space-between; border-top:1px solid #334155; padding-top:8px; font-weight:700; font-size:0.95rem;"><span style="color:#fff;">Fare Charged:</span><span>₹{fare}</span></div>
            </div>
            <div style="margin-top:14px; text-align:center; font-size:0.75rem; color:#94a3b8; background:rgba(234,179,8,0.08); padding:8px; border-radius:6px; border:1px solid rgba(234,179,8,0.15);">
                ETA to Pickup Point: 5 Minutes
            </div>
        </div>
        """
        return html

    elif scenario_key == "skill":
        goal = state.get("career_goal", "Data Scientist")
        courses = state.get("recommended_courses", [])
        weeks = state.get("weeks_to_complete", 12)
        
        course_items = ""
        for c in courses:
            course_items += f"""
            <div style="margin-bottom:6px; padding:6px; border-radius:4px; background:#f8fafc; font-size:0.75rem;">
                <div style="font-weight:600; color:#0f172a;">{c['skill']}</div>
                <div style="color:#64748b; font-size:0.7rem;">{c['course']} ({c['cost']})</div>
            </div>
            """
            
        html = f"""
        <div style="background:#fff; color:#0f172a; border-radius:12px; padding:20px; font-family:'Inter', sans-serif; box-shadow:0 10px 20px rgba(0,0,0,0.3); border-top:6px solid #8b5cf6; max-width:400px; margin:auto;">
            <div style="text-align:center; border-bottom:2px dashed #cbd5e1; padding-bottom:12px; margin-bottom:12px;">
                <div style="font-size:1.3rem; font-weight:800; text-transform:uppercase; color:#8b5cf6;">Syllabus Roadmap</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Target: {goal}</div>
            </div>
            <div style="font-size:0.85rem; margin-bottom:10px;"><span style="color:#64748b;">Study Milestones:</span></div>
            {course_items}
            <div style="border-top:1px solid #cbd5e1; padding-top:8px; margin-top:10px; display:flex; justify-content:space-between; font-size:0.85rem; font-weight:700;">
                <span>Total Study Duration:</span>
                <span style="color:#8b5cf6;">~{weeks} Weeks</span>
            </div>
        </div>
        """
        return html

    elif scenario_key == "vacation":
        dest = state.get("selected_dest", {"city": "Jaipur"})
        flights = state.get("flight_cost", 8000)
        hotel = state.get("hotel_cost", 10000)
        total = state.get("total_est", 18000)
        dur = state.get("dur", "5 Days")
        ref = state.get("booking_reference", "VAC-5928-HTL")
        
        html = f"""
        <div style="background:#fff; color:#0f172a; border-radius:12px; padding:20px; font-family:'Inter', sans-serif; box-shadow:0 10px 20px rgba(0,0,0,0.3); border-top:6px solid #ec4899; max-width:400px; margin:auto;">
            <div style="text-align:center; border-bottom:2px dashed #cbd5e1; padding-bottom:12px; margin-bottom:14px;">
                <div style="font-size:1.3rem; font-weight:800; text-transform:uppercase; color:#ec4899;">Vacation Itinerary</div>
                <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">Target Destination: {dest['city']} ({dur})</div>
            </div>
            <div style="display:flex; flex-direction:column; gap:8px; font-size:0.85rem;">
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Booking Reference:</span><span style="font-weight:600; font-family:monospace;">{ref}</span></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Flights Package:</span><span style="font-weight:600;">₹{flights}</span></div>
                <div style="display:flex; justify-content:space-between;"><span style="color:#64748b;">Hotels Package:</span><span style="font-weight:600;">₹{hotel}</span></div>
                <div style="display:flex; justify-content:space-between; border-top:1px solid #cbd5e1; padding-top:8px; font-weight:700; font-size:1rem; color:#0f172a;"><span style="color:#0f172a;">Total Price:</span><span>₹{total}</span></div>
            </div>
            <div style="margin-top:16px; border-top:2px dashed #cbd5e1; padding-top:14px; text-align:center;">
                <span style="font-size:0.75rem; font-weight:bold; color:#ec4899; background:#fce7f3; display:inline-block; padding:4px 12px; border-radius:6px;">DAY-WISE ITINERARY GENERATED</span>
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
            components.html(html_receipt, height=310, scrolling=False)
        elif is_failed:
            st.markdown("#### 🎫 Output Generated Artifact")
            html_receipt = render_outcome_receipt(selected_key)
            components.html(html_receipt, height=220, scrolling=False)

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
