# main.py (FINAL, CORRECTED - DUPLICATES REMOVED)

from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import date
import os
from werkzeug.utils import secure_filename
import uuid

# --- Flask App Initialization ---
app = Flask(__name__)
app.secret_key = 'your_super_secret_key_change_this_for_real'

# --- UPLOAD FOLDER CONFIGURATION ---
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Database Connection Configuration ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'admin_user',
    'password': 'AdminPassword123!',
    'database': 'mental_health_portal'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# --- Helper Function ---
def calculate_age(born):
    if not born: return None
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

# --- AUTHENTICATION & CORE ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

# --- AUTH: PATIENT ---
@app.route('/patient/login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Patient WHERE Email = %s AND Password = %s", (email, password))
        patient = cursor.fetchone()
        cursor.close()
        conn.close()
        if patient:
            session.clear()
            session['user_id'] = patient['PatientID']
            session['user_type'] = 'patient'
            session['first_name'] = patient['FirstName']
            flash('Login successful!', 'success')
            return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('patient_login.html')

@app.route('/patient/signup', methods=['GET', 'POST'])
def patient_signup():
    if request.method == 'POST':
        fname, lname, dob, email, password, phone = request.form['firstName'], request.form['lastName'], request.form['dob'], request.form['email'], request.form['password'], request.form['phoneNo']
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            query = "INSERT INTO Patient (FirstName, LastName, DOB, Email, Password, PhoneNo) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (fname, lname, dob, email, password, phone))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('patient_login'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "danger")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return render_template('patient_signup.html')

# --- AUTH: THERAPIST ---
@app.route('/therapist/login', methods=['GET', 'POST'])
def therapist_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Therapist WHERE Email = %s AND Password = %s AND VerificationStatus = 'Verified'", (email, password))
        therapist = cursor.fetchone()
        cursor.close()
        conn.close()
        if therapist:
            session.clear()
            session['user_id'] = therapist['TherapistID']
            session['user_type'] = 'therapist'
            session['first_name'] = therapist['FirstName']
            flash('Login successful!', 'success')
            return redirect(url_for('therapist_dashboard'))
        else:
            flash('Invalid credentials or account not verified.', 'danger')
    return render_template('therapist_login.html')

@app.route('/therapist/signup', methods=['GET', 'POST'])
def therapist_signup():
    if request.method == 'POST':
        if 'profilePicture' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['profilePicture']
        if file.filename == '' or not allowed_file(file.filename):
            flash('No selected file or invalid file type', 'danger')
            return redirect(request.url)
        try:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            conn = get_db_connection()
            cursor = conn.cursor()
            query = """INSERT INTO Therapist (FirstName, LastName, LicenseNumber, YearsOfExperience, HourlyRate, Email, Password, Biography, ProfilePicture) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (request.form['firstName'], request.form['lastName'], request.form['licenseNumber'], 
                                   request.form['yearsOfExperience'], request.form['hourlyRate'], request.form['email'], 
                                   request.form['password'], request.form['biography'], filename))
            conn.commit()
            flash('Registration successful! Your application is under review.', 'success')
            return redirect(url_for('therapist_login'))
        except mysql.connector.Error as err:
            flash(f"Error: {err}", "danger")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
    return render_template('therapist_signup.html')


# --- AUTH: ADMIN ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Admin WHERE Email = %s AND Password = %s", (email, password))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()
        if admin:
            session.clear()
            session['user_id'] = admin['AdminID']
            session['user_type'] = 'admin'
            session['first_name'] = admin['FirstName']
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
    return render_template('admin_login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# --- PUBLIC & PATIENT FEATURES ---

@app.route('/therapists')
def show_therapists():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT T.TherapistID, T.FirstName, T.LastName, T.Biography, T.HourlyRate, T.YearsOfExperience, T.Email, T.ProfilePicture,
           GROUP_CONCAT(S.SpecializationName SEPARATOR ', ') as Specializations
    FROM Therapist AS T
    LEFT JOIN Therapist_Specialization AS TS ON T.TherapistID = TS.TherapistID
    LEFT JOIN Specialization AS S ON TS.SpecializationID = S.SpecializationID
    WHERE T.VerificationStatus = 'Verified'
    GROUP BY T.TherapistID;
    """
    cursor.execute(query)
    therapist_data = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('therapists.html', therapists=therapist_data)

@app.route('/patient/find_match', methods=['GET', 'POST'])
def find_match():
    if not session.get('user_type') == 'patient':
        return redirect(url_for('patient_login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Specialization ORDER BY SpecializationName")
    all_specializations = cursor.fetchall()
    matched_therapists = None
    if request.method == 'POST':
        pref_spec_id = request.form.get('specialization_id')
        pref_gender = request.form.get('therapist_gender')
        pref_language = request.form.get('language')
        query = """
        SELECT T.*, GROUP_CONCAT(S.SpecializationID) as spec_ids, GROUP_CONCAT(S.SpecializationName) as spec_names
        FROM Therapist AS T
        LEFT JOIN Therapist_Specialization AS TS ON T.TherapistID = TS.TherapistID
        LEFT JOIN Specialization AS S ON TS.SpecializationID = S.SpecializationID
        WHERE T.VerificationStatus = 'Verified' GROUP BY T.TherapistID;
        """
        cursor.execute(query)
        all_therapists = cursor.fetchall()
        scored_therapists = []
        for therapist in all_therapists:
            score = 0
            therapist['match_reasons'] = []
            if therapist['spec_ids'] and pref_spec_id in therapist['spec_ids'].split(','):
                score += 10
                therapist['match_reasons'].append("Matches your chosen specialty")
            if pref_gender and therapist['Gender'] and pref_gender == therapist['Gender']:
                score += 5
                therapist['match_reasons'].append("Matches your gender preference")
            if pref_language and therapist['Languages'] and pref_language in therapist['Languages']:
                score += 8
                therapist['match_reasons'].append(f"Speaks {pref_language}")
            if score > 0:
                therapist['score'] = score
                scored_therapists.append(therapist)
        matched_therapists = sorted(scored_therapists, key=lambda x: x['score'], reverse=True)
    cursor.close()
    conn.close()
    return render_template('find_match.html', specializations=all_specializations, results=matched_therapists, form_submitted=(request.method == 'POST'))


@app.route('/book/therapist/<int:therapist_id>', methods=['POST'])
def book_session(therapist_id):
    if not session.get('user_type') == 'patient': return redirect(url_for('patient_login'))
    unique_room_name = str(uuid.uuid4())
    meeting_link = f"https://meet.jit.si/{unique_room_name}"
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO Appointment (PatientID, TherapistID, DateTime, Duration, SessionType, MeetingLink) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (session['user_id'], therapist_id, request.form['appointment_time'], 50, 'Video', meeting_link))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Appointment booked successfully! A unique video link has been generated.', 'success')
    return redirect(url_for('patient_dashboard'))

@app.route('/appointment/cancel/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    if not session.get('user_type') == 'patient': return redirect(url_for('patient_login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.callproc('CancelAppointment', [appointment_id])
    conn.commit()
    cursor.close()
    conn.close()
    flash('Appointment has been cancelled.', 'info')
    return redirect(url_for('patient_dashboard'))

@app.route('/patient/journal/add', methods=['POST'])
def add_journal_entry():
    if not session.get('user_type') == 'patient': return redirect(url_for('patient_login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Journal_Entry (PatientID, EntryText, Mood, EntryDate) VALUES (%s, %s, %s, %s)",
                   (session['user_id'], request.form['entryText'], request.form['mood'], date.today().strftime('%Y-%m-%d')))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Journal entry added!', 'success')
    return redirect(url_for('patient_dashboard'))

@app.route('/patient/invoices')
def patient_invoices():
    if not session.get('user_type') == 'patient': return redirect(url_for('patient_login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT I.InvoiceID, I.IssueDate, I.Amount, I.Status, A.DateTime, CONCAT(T.FirstName, ' ', T.LastName) as TherapistName
    FROM Invoice AS I JOIN Appointment AS A ON I.AppointmentID = A.AppointmentID JOIN Therapist AS T ON A.TherapistID = T.TherapistID
    WHERE A.PatientID = %s ORDER BY I.IssueDate DESC
    """
    cursor.execute(query, (session['user_id'],))
    invoices = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('patient_invoices.html', invoices=invoices)

@app.route('/invoice/pay/<int:invoice_id>', methods=['POST'])
def pay_invoice(invoice_id):
    if not session.get('user_type') == 'patient': return redirect(url_for('patient_login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Invoice SET Status = 'Paid' WHERE InvoiceID = %s", (invoice_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Thank you! Your payment was successful.', 'success')
    return redirect(url_for('patient_invoices'))

@app.route('/patient/resources')
def resource_library():
    if not session.get('user_type') == 'patient': return redirect(url_for('patient_login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT ArticleID, Title, LEFT(Content, 150) as Excerpt, Author, PublishDate FROM Article ORDER BY PublishDate DESC")
    articles = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('resource_library.html', articles=articles)

@app.route('/patient/article/<int:article_id>')
def view_article(article_id):
    if not session.get('user_type') == 'patient': return redirect(url_for('patient_login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Article WHERE ArticleID = %s", (article_id,))
    article = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('view_article.html', article=article)

@app.route('/patient/assessment/<int:assessment_id>', methods=['GET', 'POST'])
def take_assessment(assessment_id):
    if not session.get('user_type') == 'patient':
        return redirect(url_for('patient_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        total_score = 0
        answers = []
        # Dynamically get answers from the form
        for key, value in request.form.items():
            if key.startswith('q_'):
                total_score += int(value)
                answers.append(value)
        
        # Insert the main result
        insert_result_query = "INSERT INTO AssessmentResult (PatientID, AssessmentID, TotalScore) VALUES (%s, %s, %s)"
        cursor.execute(insert_result_query, (session['user_id'], assessment_id, total_score))
        conn.commit()
        
        # --- NEW: Post-Assessment Feedback Logic ---
        feedback_message = ""
        if assessment_id == 1: # Specific feedback for the GAD-7 Anxiety assessment
            if total_score <= 4:
                feedback_message = "Your results suggest minimal anxiety. This is great! Continue practicing self-care like mindfulness or going for a walk."
            elif total_score <= 9:
                feedback_message = "Your results suggest mild anxiety. It might be helpful to be mindful of your stress levels. Consider talking about this with your therapist."
            elif total_score <= 14:
                feedback_message = "Your results suggest moderate anxiety. It's a good idea to discuss these feelings with a professional. Techniques like journaling can also be very helpful."
            else:
                feedback_message = "Your results suggest severe anxiety. It is strongly recommended that you discuss these results with your therapist to create a plan for support."
        
        flash(f'Assessment submitted! Your score is {total_score}.', 'info')
        if feedback_message:
            flash(feedback_message, 'success')

        cursor.close()
        conn.close()
        return redirect(url_for('patient_dashboard'))

    # GET request: Fetch the assessment and all its questions
    cursor.execute("SELECT * FROM Assessment WHERE AssessmentID = %s", (assessment_id,))
    assessment = cursor.fetchone()
    cursor.execute("SELECT * FROM Question WHERE AssessmentID = %s", (assessment_id,))
    questions = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('take_assessment.html', assessment=assessment, questions=questions)

# --- DASHBOARDS & PROFILES ---

@app.route('/patient/dashboard')
def patient_dashboard():
    if not session.get('user_type') == 'patient': return redirect(url_for('patient_login'))
    patient_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT GetPatientNextAppointmentDate(%s) AS next_appt", (patient_id,))
    next_appointment = cursor.fetchone()['next_appt']
    cursor.callproc('GetPatientUpcomingAppointments', [patient_id])
    appointments = []
    for result in cursor.stored_results(): appointments = result.fetchall()
    cursor.execute("SELECT * FROM Journal_Entry WHERE PatientID = %s ORDER BY EntryDate DESC", (patient_id,))
    journals = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('patient_dashboard.html', appointments=appointments, journals=journals, next_appointment=next_appointment)

@app.route('/therapist/dashboard')
def therapist_dashboard():
    if not session.get('user_type') == 'therapist': return redirect(url_for('therapist_login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT A.AppointmentID, A.DateTime, A.Status, P.PatientID, P.FirstName, P.LastName, SN.NoteText, A.MeetingLink
    FROM Appointment AS A JOIN Patient AS P ON A.PatientID = P.PatientID
    LEFT JOIN Session_Notes AS SN ON A.AppointmentID = SN.AppointmentID
    WHERE A.TherapistID = %s ORDER BY A.DateTime DESC
    """
    cursor.execute(query, (session['user_id'],))
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('therapist_dashboard.html', appointments=appointments)

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('user_type') == 'admin': return redirect(url_for('admin_login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Therapist ORDER BY VerificationStatus, RegistrationDate DESC")
    therapists = cursor.fetchall()
    cursor.execute("SELECT * FROM Specialization ORDER BY SpecializationName")
    specializations = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin_dashboard.html', therapists=therapists, specializations=specializations)

@app.route('/admin/reports')
def admin_reports():
    if not session.get('user_type') == 'admin': return redirect(url_for('admin_login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    agg_query = "SELECT DATE_FORMAT(I.IssueDate, '%%Y-%%m') AS Month, SUM(I.Amount) AS MonthlyRevenue FROM Invoice AS I WHERE I.Status = 'Paid' GROUP BY Month ORDER BY Month DESC;"
    cursor.execute(agg_query)
    revenue_report = cursor.fetchall()
    nested_query = "SELECT PatientID, FirstName, LastName, Email, RegistrationDate FROM Patient WHERE PatientID NOT IN (SELECT DISTINCT PatientID FROM Appointment);"
    cursor.execute(nested_query)
    inactive_patients = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin_reports.html', revenue_report=revenue_report, inactive_patients=inactive_patients)

@app.route('/patient/profile', methods=['GET', 'POST'])
def patient_profile():
    if not session.get('user_type') == 'patient': return redirect(url_for('patient_login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    patient_id = session['user_id']
    if request.method == 'POST':
        fname, lname, phone = request.form['firstName'], request.form['lastName'], request.form['phoneNo']
        query = "UPDATE Patient SET FirstName = %s, LastName = %s, PhoneNo = %s WHERE PatientID = %s"
        cursor.execute(query, (fname, lname, phone, patient_id))
        conn.commit()
        flash('Profile updated successfully!', 'success')
        session['first_name'] = fname
        return redirect(url_for('patient_profile'))
    cursor.execute("SELECT * FROM Patient WHERE PatientID = %s", (patient_id,))
    patient = cursor.fetchone()
    patient['Age'] = calculate_age(patient['DOB'])
    cursor.close()
    conn.close()
    return render_template('patient_profile.html', patient=patient, journals=None)

@app.route('/therapist/profile', methods=['GET', 'POST'])
def therapist_profile():
    if not session.get('user_type') == 'therapist': return redirect(url_for('therapist_login'))
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    therapist_id = session['user_id']
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'update_details':
            new_rate, new_bio = request.form['hourlyRate'], request.form['biography']
            file = request.files.get('profilePicture')
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                query = "UPDATE Therapist SET HourlyRate = %s, Biography = %s, ProfilePicture = %s WHERE TherapistID = %s"
                cursor.execute(query, (new_rate, new_bio, filename, therapist_id))
            else:
                query = "UPDATE Therapist SET HourlyRate = %s, Biography = %s WHERE TherapistID = %s"
                cursor.execute(query, (new_rate, new_bio, therapist_id))
            conn.commit()
            flash('Profile details updated successfully!', 'success')
        elif form_type == 'update_specializations':
            selected_spec_ids = request.form.getlist('specialization_ids')
            cursor.execute("DELETE FROM Therapist_Specialization WHERE TherapistID = %s", (therapist_id,))
            if selected_spec_ids:
                insert_query = "INSERT INTO Therapist_Specialization (TherapistID, SpecializationID) VALUES (%s, %s)"
                data_to_insert = [(therapist_id, spec_id) for spec_id in selected_spec_ids]
                cursor.executemany(insert_query, data_to_insert)
            conn.commit()
            flash('Specializations updated successfully!', 'success')
        return redirect(url_for('therapist_profile'))
    cursor.execute("SELECT * FROM Therapist WHERE TherapistID = %s", (therapist_id,))
    therapist = cursor.fetchone()
    cursor.execute("SELECT GetTherapistTotalRevenue(%s) AS TotalRevenue", (therapist_id,))
    revenue = cursor.fetchone()['TotalRevenue']
    cursor.execute("SELECT * FROM Specialization ORDER BY SpecializationName")
    all_specializations = cursor.fetchall()
    cursor.execute("SELECT SpecializationID FROM Therapist_Specialization WHERE TherapistID = %s", (therapist_id,))
    therapist_spec_ids = [row['SpecializationID'] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return render_template('therapist_profile.html', therapist=therapist, total_revenue=revenue, all_specializations=all_specializations, therapist_spec_ids=therapist_spec_ids)

@app.route('/view/patient/<int:patient_id>')
def view_patient_by_therapist(patient_id):
    # This route now fetches assessment history as well
    if not session.get('user_type') in ['therapist', 'admin']:
        return redirect(url_for('index'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # ... (Authorization check code remains the same) ...
    has_access = False
    if session['user_type'] == 'admin':
        has_access = True
    elif session['user_type'] == 'therapist':
        cursor.execute("SELECT 1 FROM Appointment WHERE TherapistID = %s AND PatientID = %s LIMIT 1", (session['user_id'], patient_id))
        if cursor.fetchone():
            has_access = True
    
    if not has_access:
        flash('You are not authorized to view this profile.', 'danger')
        return redirect(url_for('therapist_dashboard'))

    # Fetch patient details
    cursor.execute("SELECT * FROM Patient WHERE PatientID = %s", (patient_id,))
    patient = cursor.fetchone()
    if patient:
        patient['Age'] = calculate_age(patient['DOB'])
    
    # Fetch journal entries
    cursor.execute("SELECT * FROM Journal_Entry WHERE PatientID = %s ORDER BY EntryDate DESC", (patient_id,))
    journals = cursor.fetchall()

    # NEW: Fetch assessment history
    assessment_history_query = """
    SELECT R.DateTaken, R.TotalScore, A.Name AS AssessmentName
    FROM AssessmentResult AS R
    JOIN Assessment AS A ON R.AssessmentID = A.AssessmentID
    WHERE R.PatientID = %s
    ORDER BY R.DateTaken DESC;
    """
    cursor.execute(assessment_history_query, (patient_id,))
    assessment_history = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return render_template('patient_profile.html', patient=patient, journals=journals, assessment_history=assessment_history)

# --- THERAPIST & ADMIN ACTIONS ---

@app.route('/therapist/notes/add/<int:appointment_id>', methods=['POST'])
def add_session_note(appointment_id):
    if not session.get('user_type') == 'therapist': return redirect(url_for('therapist_login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    # Using an UPSERT (Update or Insert) approach for simplicity.
    cursor.execute("DELETE FROM Session_Notes WHERE AppointmentID = %s", (appointment_id,)) # Simple approach: delete old note first
    cursor.execute("INSERT INTO Session_Notes (AppointmentID, NoteText) VALUES (%s, %s)", (appointment_id, request.form['noteText']))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Session note saved successfully!', 'success')
    return redirect(url_for('therapist_dashboard'))

@app.route('/admin/verify_therapist/<int:therapist_id>', methods=['POST'])
def verify_therapist(therapist_id):
    if not session.get('user_type') == 'admin': return redirect(url_for('admin_login'))
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE Therapist SET VerificationStatus = 'Verified' WHERE TherapistID = %s", (therapist_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Therapist has been verified and can now log in.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/specialization/add', methods=['POST'])
def add_specialization():
    if not session.get('user_type') == 'admin': return redirect(url_for('admin_login'))
    spec_name, spec_desc = request.form.get('specializationName'), request.form.get('specializationDescription')
    if spec_name:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Specialization (SpecializationName, Description) VALUES (%s, %s)", (spec_name, spec_desc))
            conn.commit()
            flash(f"Specialization '{spec_name}' added successfully!", 'success')
        except mysql.connector.Error as err:
            flash(f"Error adding specialization: {err}", 'danger')
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
    return redirect(url_for('admin_dashboard'))

# --- Main execution ---
if __name__ == '__main__':
    app.run(debug=True)