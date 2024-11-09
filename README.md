<h1> An App for patient report diagnosis for Doctors powered  by AI</h1>

<h2>Medico App</h2>
<p>Medico App is a Streamlit-based web application designed for doctors to manage and view patient data efficiently.</p>
It allows doctors to access patient details, review past medical reports, and interact with an AI-powered chatbot (using Llama AI) for faster diagnosis and support.
The app is powered by MongoDB for secure data storage and retrieval, enabling a seamless experience for healthcare providers.

<h2>Features</h2>
Doctor Dashboard: Lists all registered patients with basic details.

Patient Profile: Doctors can click on a patient to view a detailed profile that includes:

Patient Details: Basic info such as age, contact, symptoms, etc.

Reports: Past medical reports and current treatments. Doctors can upload and view reports.

AI Chatbot: Llama AI-powered chatbot that assists with diagnosis. Doctors can choose:

Patient Context: Uses patient’s medical history for tailored responses.

Web Search: Includes real-time web data in responses.

Medical Text Reference: Uses preloaded medical texts for reliable answers.

Secure Data Management: MongoDB integration for secure, scalable storage of all patient records, reports, and chatbot interactions.

<h2>Technology Stack</h2>

Frontend: Streamlit (Python)
Backend: Python, Llama AI
Database: MongoDB (using MongoDB Atlas for cloud deployment)
Other Libraries: pymongo for MongoDB integration, transformers for Llama AI, streamlit-chat for chatbot UI

<h1>Getting Started</h1>
Follow these steps to get the Medico App up and running locally:

<h2> Clone the repository:</h2> git clone https://github.com/your-username/medico-app.git
                                <p>cd medico-app</p>

<h2>Set Up Virtual Environment:</h2> python -m venv env source env/bin/activate  
                                     <p># For Windows: env\Scripts\activate</p>
<h2>Install Dependencies:</h2> pip install -r requirements.txt

<h2> Configure MongoDB:</h2> Set up a MongoDB Atlas cluster.

Update config.py with your MongoDB connection string.

<h2>Run the Application:</h2>

streamlit run app.py

<h1>Usage</h1>

<h2>Dashboard: View all registered patients.</h2>

<h2>Patient Profile: Access basic details and medical history.</h2>

<h2>View and upload new reports. Interact with the AI Chatbot</h2>
![image](https://github.com/user-attachments/assets/9c5a8c70-1888-4b58-a5ac-2db4b6ede881)
<h2>AI Chatbot: Ask questions related to patient diagnostics and receive answers based on selected contexts.</h2>
