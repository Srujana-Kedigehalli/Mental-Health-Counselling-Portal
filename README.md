# MHP Portal: An Online Mental Health Counselling Platform

## 📖 Project Overview

**MHP Portal** is a comprehensive, database-driven web application built as a project for the **Database Management System (UE23CS351A)** course. The objective was to design and build a full-stack, deployable application that works seamlessly with a robust relational database.

This platform serves as a secure and user-friendly bridge between individuals seeking mental health support and qualified, verified therapists. It moves beyond a simple booking system to provide a holistic mental health companion, incorporating features like an intelligent therapist matching engine, a resource library, patient assessments, and a secure three-tier role-based access system.

---

## ✨ Key Features

The application is architected around three distinct user roles: **Patient**, **Therapist**, and **Admin**.

#### For Patients:
*   **Secure Authentication:** Full signup and login functionality.
*   **Intelligent Therapist Matching:** A multi-factor "Find My Match" tool that scores and ranks therapists based on patient preferences (specialization, gender, language).
*   **Appointment Booking:** Seamlessly book sessions with therapists, which automatically generates a unique video call link.
*   **Personal Dashboard:** A central hub to view upcoming appointments, manage invoices, and access platform features.
*   **Private Journaling:** A secure space for patients to write and reflect on their thoughts and feelings.
*   **Resource Library & Assessments:** Access to articles written by professionals and the ability to take mental health assessments (like the GAD-7) with instant, personalized feedback.
*   **Profile Management:** View and update personal details.

#### For Therapists:
*   **Secure Registration & Verification:** A signup workflow where new therapists are reviewed and approved by an administrator before they can access the platform.
*   **Professional Dashboard:** A centralized view of their schedule of upcoming appointments.
*   **Patient Management:** Ability to view the profiles and journal entries of patients with whom they have an appointment, ensuring they are prepared for each session.
*   **Session Notes:** A feature to write and save confidential notes for each completed appointment.
*   **Profile Customization:** Full control over their public-facing profile, including profile picture, biography, hourly rate, and areas of specialization.
*   **Earnings Report:** An automated calculation of total revenue generated from paid sessions.

#### For Administrators:
*   **Secure Admin Login:** A separate, secure portal for platform management.
*   **Therapist Verification:** A dashboard to review and approve or reject new therapist applications, maintaining the quality of the platform.
*   **Content Management:** Ability to manage the master list of specializations available on the platform.
*   **Business Intelligence Reports:** Access to key reports, including monthly revenue summaries and lists of inactive patients to monitor platform health.

---

## 🛠️ Tech Stack & Database Design

#### Technologies Used
*   **Backend:** Python with the Flask web framework.
*   **Database:** MySQL.
*   **Frontend:** HTML5, CSS3 with the Bootstrap 5 framework for a responsive and professional UI.
*   **Languages:** Python, SQL.

#### Database Highlights
The project is built on a highly normalized relational schema (3NF) to ensure data integrity and minimize redundancy.

*   **Total Tables:** 15 (including entity, relationship, junction, and audit tables).
*   **Key Entities:** `Patient`, `Therapist`, `Admin`, `Appointment`, `Invoice`, `Article`, `Assessment`.
*   **Advanced SQL Features Implemented:**
    *   **2 Triggers:**
        1.  `After_Appointment_Insert`: Automatically creates an invoice when a session is booked.
        2.  `LogTherapistRateChange`: Creates an audit trail of changes to therapist pricing.
    *   **2 Stored Procedures:**
        1.  `GetPatientUpcomingAppointments`: Encapsulates logic for fetching a patient's schedule.
        2.  `CancelAppointment`: A transactional procedure to safely cancel an appointment and its associated invoice.
    *   **2 Functions:**
        1.  `GetTherapistTotalRevenue`: Calculates total earnings for a therapist.
        2.  `GetPatientNextAppointmentDate`: Finds the next scheduled appointment for a patient.
    *   **Complex Queries:**
        *   **JOIN Query:** Powers the dynamic therapist search feature.
        *   **Aggregate Query:** Used for the admin's monthly revenue report.
        *   **Nested Query (Subquery):** Used to identify inactive patients for admin reports.
*   **Security:** Implemented role-based access control using MySQL's `CREATE ROLE` and `GRANT` features to enforce the principle of least privilege.

---

## 🚀 Getting Started

Follow these instructions to get a local copy up and running.

#### Prerequisites
*   Python 3.x
*   A running MySQL server
*   MySQL Workbench (or any SQL client)

#### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2.  **Set up a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required Python packages:**
    ```bash
    pip install Flask mysql-connector-python
    ```

4.  **Set up the database:**
    *   Open MySQL Workbench and connect to your server.
    *   Create a new schema named `mental_health_portal`.
    *   Run the entire `database_setup.sql` file provided in this repository. This will create all the tables, triggers, procedures, functions, and insert the necessary sample data.

5.  **Configure the database connection:**
    *   Open the `main.py` file.
    *   In the `DB_CONFIG` dictionary, update the `user` and `password` to match your MySQL credentials.

6.  **Run the application:**
    ```bash
    python main.py
    ```
    The application will be running at `http://127.0.0.1:5000`.

---
