from services.database_service import init_db, create_problem


# ---------------------------------------------------------
# INITIALIZE DATABASE
# ---------------------------------------------------------

init_db()


# ---------------------------------------------------------
# SAMPLE CIVIC PROBLEMS
# ---------------------------------------------------------

problems = [

    {
        "title": "Detecting Road Damage Automatically",

        "problem": """
Many roads develop potholes, cracks and surface damage,
but identifying these problems manually takes time and
requires repeated inspections. A system is needed to
automatically identify and classify road damage from images
or collected road data so that authorities can prioritize
repairs.
""",

        "brief": {
            "title": "Detecting Road Damage Automatically",

            "problem": """
Road damage such as potholes and cracks is difficult to
monitor manually across large areas.
""",

            "affected_users": [
                "City authorities",
                "Road maintenance departments",
                "Drivers",
                "Residents"
            ],

            "current_approach": """
Road inspections are mostly performed manually or through
citizen complaints.
""",

            "available_data": [
                "Road images",
                "Location information",
                "Historical road damage records"
            ],

            "constraints": [
                "Limited inspection resources",
                "Large number of roads",
                "Different types of road damage"
            ],

            "desired_outcome": """
Automatically identify road damage and help authorities
prioritize maintenance.
""",

            "success_metrics": [
                "Accurate damage detection",
                "Reduced inspection time",
                "Useful repair priority information"
            ],

            "domain": [
                "Smart Cities",
                "Transportation",
                "Computer Vision",
                "Public Services"
            ],

            "required_skills": [
                "Python",
                "Machine Learning",
                "Computer Vision",
                "Data Analysis"
            ],

            "assumptions": [],
            "missing_information": []
        }
    },


    {
        "title": "Predicting Traffic Congestion in City Roads",

        "problem": """
Traffic congestion changes throughout the day and can
cause delays for commuters and emergency services.
Authorities need a way to analyze traffic patterns and
predict congestion before it becomes severe.
""",

        "brief": {
            "title": "Predicting Traffic Congestion in City Roads",

            "problem": """
City traffic congestion is difficult to predict because
traffic patterns change based on time, location and events.
""",

            "affected_users": [
                "Commuters",
                "Traffic authorities",
                "Emergency services",
                "Public transport operators"
            ],

            "current_approach": """
Traffic conditions are monitored using existing traffic
systems and manual observation.
""",

            "available_data": [
                "Traffic volume",
                "Time of day",
                "Road locations",
                "Historical traffic patterns"
            ],

            "constraints": [
                "Changing traffic patterns",
                "Incomplete data",
                "Large geographic areas"
            ],

            "desired_outcome": """
Predict traffic congestion and provide useful information
for traffic management.
""",

            "success_metrics": [
                "Prediction accuracy",
                "Reduced congestion",
                "Useful traffic alerts"
            ],

            "domain": [
                "Smart Cities",
                "Transportation",
                "Data Science"
            ],

            "required_skills": [
                "Python",
                "Machine Learning",
                "Data Analysis",
                "Predictive Analytics"
            ],

            "assumptions": [],
            "missing_information": []
        }
    },


    {
        "title": "Smart Waste Collection Monitoring",

        "problem": """
Waste collection vehicles often follow fixed schedules
even when some collection points are already full while
others have very little waste. This can lead to overflowing
bins and inefficient use of collection vehicles.
""",

        "brief": {
            "title": "Smart Waste Collection Monitoring",

            "problem": """
Waste collection schedules do not always reflect the
actual amount of waste at different collection points.
""",

            "affected_users": [
                "Municipal authorities",
                "Waste collection workers",
                "Residents"
            ],

            "current_approach": """
Waste collection generally follows fixed schedules and
routes.
""",

            "available_data": [
                "Waste-bin status",
                "Collection locations",
                "Collection schedules",
                "Historical collection data"
            ],

            "constraints": [
                "Limited collection vehicles",
                "Large number of collection points",
                "Changing waste levels"
            ],

            "desired_outcome": """
Improve waste collection efficiency by identifying
locations that need collection first.
""",

            "success_metrics": [
                "Reduced overflowing bins",
                "Improved collection efficiency",
                "Reduced unnecessary trips"
            ],

            "domain": [
                "Smart Cities",
                "Environment",
                "IoT",
                "Public Services"
            ],

            "required_skills": [
                "Python",
                "IoT",
                "Data Analysis",
                "Machine Learning"
            ],

            "assumptions": [],
            "missing_information": []
        }
    },


    {
        "title": "Citizen Complaint Classification System",

        "problem": """
Municipal departments receive large numbers of complaints
about roads, water supply, waste, streetlights and other
services. Manually reading and forwarding every complaint
can delay responses.
""",

        "brief": {
            "title": "Citizen Complaint Classification System",

            "problem": """
Citizen complaints need to be classified and routed to
the appropriate department efficiently.
""",

            "affected_users": [
                "Citizens",
                "Municipal employees",
                "Government departments"
            ],

            "current_approach": """
Complaints are manually reviewed and forwarded to
departments.
""",

            "available_data": [
                "Complaint descriptions",
                "Complaint categories",
                "Department information",
                "Historical complaint records"
            ],

            "constraints": [
                "Large complaint volume",
                "Different writing styles",
                "Incorrect or incomplete complaint information"
            ],

            "desired_outcome": """
Automatically classify complaints and route them to
the appropriate department.
""",

            "success_metrics": [
                "Classification accuracy",
                "Reduced processing time",
                "Faster complaint routing"
            ],

            "domain": [
                "Public Services",
                "Artificial Intelligence",
                "Natural Language Processing"
            ],

            "required_skills": [
                "Python",
                "AI",
                "Machine Learning",
                "Data Analysis"
            ],

            "assumptions": [],
            "missing_information": []
        }
    },


    {
        "title": "Mapping Unsafe Areas for Pedestrians",

        "problem": """
Pedestrians may face unsafe roads, poorly maintained
footpaths, missing crossings and areas with inadequate
street infrastructure. Authorities need better information
about locations where pedestrian safety can be improved.
""",

        "brief": {
            "title": "Mapping Unsafe Areas for Pedestrians",

            "problem": """
Information about pedestrian safety issues is often
fragmented and difficult to analyze geographically.
""",

            "affected_users": [
                "Pedestrians",
                "City planners",
                "Traffic authorities",
                "Local communities"
            ],

            "current_approach": """
Safety issues are reported through complaints,
inspections and separate datasets.
""",

            "available_data": [
                "Location data",
                "Road information",
                "Accident records",
                "Citizen reports"
            ],

            "constraints": [
                "Incomplete reports",
                "Large geographic areas",
                "Different types of safety problems"
            ],

            "desired_outcome": """
Create a data-driven map that helps identify areas
requiring pedestrian safety improvements.
""",

            "success_metrics": [
                "Useful geographic visualization",
                "Accurate identification of risk areas",
                "Better planning decisions"
            ],

            "domain": [
                "Smart Cities",
                "Transportation",
                "Public Safety",
                "Data Visualization"
            ],

            "required_skills": [
                "Data Analysis",
                "Python",
                "GIS",
                "Data Visualization"
            ],

            "assumptions": [],
            "missing_information": []
        }
    },


    {
        "title": "Predicting Water Supply Issues",

        "problem": """
Residents sometimes experience unexpected interruptions
in water supply. Authorities may have historical data
about supply schedules, complaints and infrastructure
issues but may not be able to identify patterns early.
""",

        "brief": {
            "title": "Predicting Water Supply Issues",

            "problem": """
Water supply problems can affect large numbers of
residents and are difficult to anticipate.
""",

            "affected_users": [
                "Residents",
                "Water department",
                "Municipal authorities"
            ],

            "current_approach": """
Issues are generally identified after complaints or
infrastructure failures.
""",

            "available_data": [
                "Water supply schedules",
                "Complaint records",
                "Maintenance records",
                "Infrastructure information"
            ],

            "constraints": [
                "Incomplete historical data",
                "Different infrastructure conditions",
                "Changing demand"
            ],

            "desired_outcome": """
Identify patterns that may indicate upcoming water
supply problems.
""",

            "success_metrics": [
                "Useful predictions",
                "Earlier identification of issues",
                "Reduced disruption"
            ],

            "domain": [
                "Public Services",
                "Data Science",
                "Smart Cities"
            ],

            "required_skills": [
                "Python",
                "Data Science",
                "Machine Learning",
                "Predictive Analytics"
            ],

            "assumptions": [],
            "missing_information": []
        }
    }

]


# ---------------------------------------------------------
# ADD PROBLEMS
# ---------------------------------------------------------

print("\nAdding SolveNet sample problems...\n")


for item in problems:

    try:

        problem_id = create_problem(
            title=item["title"],
            problem=item["problem"],
            problem_brief=item["brief"]
        )

        print(
            f"Added problem #{problem_id}: "
            f"{item['title']}"
        )

    except Exception as error:

        print(
            f"Could not add: {item['title']}"
        )

        print(
            f"Reason: {error}"
        )


print("\n--------------------------------------")
print("Sample problems added successfully.")
print("--------------------------------------\n")