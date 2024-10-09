import psycopg2
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

def get_database_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="DB_NAME",
        user="DB_USER",
        password="USER_PASSWORD")

def create_tables():
    db = get_database_connection()
    cur = db.cursor()
    try:
        # checks if norm.genders exists
        cur.execute('''select exists (
            select from	information_schema.tables
            where table_schema = 'norm'
            and table_name = 'genders');''')
        
        exsit = cur.fetchone()[0]
        
        if not exsit:
            cur.execute('''create table if not exists norm.Genders (
                Gender_ID int generated always as identity not null,
                Gender_Description varchar (100) not null,
                primary key (Gender_ID));''')

            cur.execute('''INSERT INTO norm.Genders (Gender_description) VALUES
                        ('زن'), ('مرد');''')
        
        # check if norm.Master_Types exists
        cur.execute('''select exists (
            select from	information_schema.tables
            where table_schema = 'norm'
            and table_name = 'master_types');''')
        
        exsit = cur.fetchone()[0]
        
        if not exsit:
            cur.execute('''create table if not exists norm.Master_Types (
            Master_Type_ID int generated always as identity not null,
            Master_Type_Description varchar (100) not null,
            primary key (Master_Type_ID));''')

            cur.execute('''INSERT INTO norm.Master_Types (Master_Type_Description) VALUES
                        ('روزانه'), ('شبانه');''')
        
        # checks if norm.Education_Statuses exists
        cur.execute('''select exists (
            select from	information_schema.tables
            where table_schema = 'norm'
            and table_name = 'education_statuses');''')
        
        exsit = cur.fetchone()[0]
        
        if not exsit:
            cur.execute('''create table if not exists norm.Education_Statuses (
            Education_Status_ID int generated always as identity not null,
            Education_Status_Description varchar (100) not null,
            primary key (Education_Status_ID));''')
            
            cur.execute('''INSERT INTO norm.Education_Statuses (Education_Status_Description) VALUES
                        ('فارغ التحصیل'), ('دانشجوی ترم آخر'), ('فارغ التحصیلی دکترای حرفه‌ای');''')
        
        cur.execute('''create table if not exists norm.Student_Info (
            National_ID varchar(100) not null,
            FirstName varchar(100) not null,
            LastName varchar(100) not null,
            Gender int not null,
            DateOfBirth Date not null,
            FatherName varchar(100),
            IDCard_Number varchar(100),
            IDCard_Serial varchar (100),
            Phone_Number varchar (100),
            Master_Field varchar(100) not null,
            Master_Type int NOT NULL,
            Master_University_Name varchar(100) not null,
            Master_Start_Date Date not null,
            Master_Graduation_Date Date not null,
            Master_Graduation_Status int NOT null,
            Master_Semester_Count int not null,
            Master_Score_Wout_Thesis int not null,
            Master_Score_With_Thesis int not null,
            Thesis_Score int not null,
            Master_Score_Normalized int not null,
            Applied_PHD_Field varchar(100) not null,
            English_Degree_Type varchar(100) not null,
            English_Degree_Score int not null,
            English_Degree_Education_Date Date not null,
            English_Degree_Validation_Date Date not null,
            PRIMARY KEY (National_ID),
            foreign key (Gender) references norm.Genders (Gender_ID),
            foreign key (Master_Type) references norm.Master_Types(Master_Type_ID),
            foreign key (Master_Graduation_Status) references norm.Education_Statuses(Education_Status_ID));''')
        
        # checks if norm.Essay_Types exists
        cur.execute('''select exists (
            select from	information_schema.tables
            where table_schema = 'norm'
            and table_name = 'essay_types');''')
        
        exsit = cur.fetchone()[0]
        
        if not exsit:
            cur.execute('''create table if not exists norm.Essay_Types (
            Essay_Type_ID int generated always as identity not null,
            Essay_Type_Description varchar (100) not null,
            primary key (Essay_Type_ID));''')

            cur.execute('''INSERT INTO norm.Essay_Types (Essay_Type_Description) VALUES
                        ('ISC'), ('ISI'), ('علمی - پژوهشی'), ('غیر علمی - پژوهشی');''')
        
        # checks if norm.Author_Types exists
        cur.execute('''select exists (
            select from	information_schema.tables
            where table_schema = 'norm'
            and table_name = 'author_types');''')
        
        exsit = cur.fetchone()[0]
        
        if not exsit:
            cur.execute('''create table if not exists norm.Author_Types (
            Author_Type_ID int generated always as identity not null,
            Author_Type_Description varchar (100) not null,
            primary key (Author_Type_ID));''')

            cur.execute('''INSERT INTO norm.Author_Types (Author_Type_Description) VALUES
                        ('دانشجو'), ('عضو هیأت علمی'), ('سایر');''')
        
        cur.execute('''create table if not exists norm.Essay_Detail (
            Essay_Detail_PK int generated always as identity not null,
            National_ID varchar(100) not null,
            Essay_title varchar(100) NOT NULL,
            ISSN varchar(100) not null,
            Essay_Type int,
            Extracted_From_Thesis boolean,
            Magazine_Full_Name varchar (255),
            Magazine_Short_Name varchar (255),
            Author_Name varchar (100) not null,
            Author_Type int not null,
            primary key (Essay_Detail_PK),
            unique (National_ID, ISSN),
            foreign key (National_ID) references norm.Student_Info (National_ID) ON DELETE CASCADE,
            foreign key (Essay_Type) references norm.Essay_Types (Essay_Type_ID),
            foreign key (Author_type) references norm.Author_Types (Author_Type_ID));''')
        
        db.commit()

    except Exception as e:
        print(f'Error creating tables: {e}')
        db.rollback()

    db.close

@app.route('/')
def index():

    db = get_database_connection()
    cur = db.cursor()
    cur.execute('''SELECT National_ID, FirstName, LastName, Applied_PHD_Field, master_score_with_thesis, master_score_normalized
                FROM norm.Student_Info
                order by norm.Student_Info.master_score_with_thesis desc;''')
    rows = cur.fetchall()
    records= []
    for row in rows:
        record = {
            'national_id': row[0],
            'first_name': row[1],
            'last_name': row[2],
            'requested_field': row[3],
            'score_with_thesis' : row[4],
            'normalized_score' : row[5]
        }
        records.append(record)

    cur.execute('''select avg(master_score_with_thesis), avg(master_score_normalized) from norm.student_info si;''')

    avg_score_with_thesis = ''
    avg_score_normalized = ''

    data = cur.fetchone()
    if (data[0] != None and data[1] != None):
        avg_score_with_thesis = round (data[0], 2)
        avg_score_normalized = round(data[1], 2)

    cur.close
    db.close

    return render_template('index.html', records=records, avg_score_with_thesis = avg_score_with_thesis, avg_score_normalized = avg_score_normalized)

@app.route('/new_form', methods=['GET', 'POST'])
def new_form():
    return render_template('form.html')

@app.route('/submit_form', methods=['GET', 'POST'])
def form():

    if request.method == 'POST':
        # Personal Information
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender = 2 if request.form.get('gender') == 'male' else 1
        birth_date = request.form.get('birth_date')
        national_id = request.form.get('national_id')
        father_name = request.form.get('father_name')
        id_number = request.form.get('id_number')
        serial_number = request.form.get('serial_number')
        phone_number = request.form.get('phone_number')

        # Educational Information
        master_field = request.form.get('master_field')
        master_university = request.form.get('master_university')
        master_type = 1 if request.form.get('master_type') == 'funded' else 2
        start_date = request.form.get('start_date')
        graduation_date = request.form.get('graduation_date')
        match (request.form.get('graduation_status')):
            case 'graduated':
                graduation_status = 1
            case 'last_semester_student':
                graduation_status = 2
            case 'pro_phd':
                graduation_status = 3
        semester_count = request.form.get('semester_count')
        score_wout_thesis = request.form.get('score_wout_thesis')
        score_with_thesis = request.form.get('score_with_thesis')
        thesis_score = request.form.get('thesis_score')
        score_normalized = request.form.get('score_normalized')
        applied_field = request.form.get('applied_field')

        # English Degree Information
        english_degree_type = request.form.get('english_degree_type')
        english_degree_score = request.form.get('english_degree_score')
        english_degree_education_date = request.form.get('english_degree_education_date')
        english_degree_validation_date = request.form.get('english_degree_validation_date')

        # Research Documents
        article_title = request.form.get('article_title')
        extracted_from_thesis = True if request.form.get('extracted_from_thesis') == 'yes' else False
        issn = request.form.get('issn')
        magazine_full_name = request.form.get('magazine_full_name')
        magazine_short_name = request.form.get('magazine_short_name')
        match (request.form.get('article_type')):
            case 'ISC':
                article_type = 1
            case 'ISI':
                article_type = 2
            case 'scientific':
                article_type = 3
            case 'non_scientific':
                article_type = 4
        author_name = request.form.get('author_name')
        match (request.form.get('author_title')):
            case 'student':
                author_title = 1
            case 'professor':
                author_title = 2
            case 'etc':
                author_title = 3

        db = get_database_connection()
        cur = db.cursor()
        cur.execute("INSERT INTO norm.student_info (national_id,firstname,lastname,gender,dateofbirth,fathername,idcard_number,idcard_serial,phone_number,master_field,master_type,master_university_name,master_start_date,master_graduation_date,master_graduation_status,master_semester_count,master_score_wout_thesis,master_score_with_thesis,thesis_score,master_score_normalized,applied_phd_field,english_degree_type,english_degree_score,english_degree_education_date,english_degree_validation_date) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (national_id, first_name, last_name, gender, birth_date, father_name, id_number, serial_number, phone_number, master_field, master_type, master_university, start_date, graduation_date, graduation_status, semester_count, score_wout_thesis, score_with_thesis, thesis_score, score_normalized, applied_field, english_degree_type, english_degree_score, english_degree_education_date, english_degree_validation_date,))

        cur.execute("INSERT INTO norm.essay_detail (national_id,essay_title,issn,essay_type,extracted_from_thesis,magazine_full_name,magazine_short_name,author_name,author_type) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)", (national_id, article_title, issn, article_type, extracted_from_thesis, magazine_full_name, magazine_short_name, author_name, author_title,))

        db.commit()
        cur.close()
        db.close()
        return redirect('/')
        

@app.route('/edit/<national_id>', methods=['GET','POST'])
def edit_student_info(national_id):
    if request.method == 'GET':

        db = get_database_connection()
        cur = db.cursor()
        cur.execute(f'''select * from norm.student_info si
                    inner join norm.essay_detail ed on si.national_id = ed.national_id
                    where si.national_id = '{national_id}';''')

        data = cur.fetchone()

        match data[14]:
            case 1:
                grad_stat = 'graduated'
            case 2:
                grad_stat = 'last_semester_student'
            case 3:
                grad_stat = 'pro_phd'

        match data[29]:
            case 1:
                art_type = 'ISC'
            case 2:
                art_type = 'ISI'
            case 3:
                art_type = 'scientific'
            case 4:
                art_type = 'non_scientific'
        
        match data[34]:
            case 1:
                author_tit = 'student'
            case 2:
                author_tit = 'professor'
            case 3:
                author_tit = 'etc'

        form_data = {
            'first_name': data[1],
            'last_name': data[2],
            'gender': 'male' if data[3] == 2 else 'female',
            'birth_date': data[4],
            'national_id': data[0],
            'father_name': data[5],
            'id_number': data[6],
            'serial_number': data[7],
            'phone_number': data[8],
            'master_field': data[9],
            'master_type': 'no_fund' if data[10] == 2 else 'funded',
            'master_university': data[11],
            'start_date': data[12],
            'graduation_date': data[13],
            'graduation_status': grad_stat,
            'semester_count': data[15],
            'score_wout_thesis': data[16],
            'score_with_thesis': data[17],
            'thesis_score': data[18],
            'score_normalized': data[19],
            'applied_field': data[20],
            'english_degree_type': data[21],
            'english_degree_score': data[22],
            'english_degree_education_date': data[23],
            'english_degree_validation_date': data[24],
            'article_title': data[27],
            'issn': data[28],
            'article_type': art_type,
            'extracted_from_thesis': 'yes' if data[30] == True else 'no',
            'magazine_full_name': data[31],
            'magazine_short_name': data[32],
            'author_name': data[33],
            'author_title': author_tit,
            }

        cur.close()
        db.close()
        
        return render_template('form_edit.html', **form_data)

@app.route('/submit_edition', methods=['GET', 'POST'])
def edit_form():

    if request.method == 'POST':
        # Personal Information
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender = 2 if request.form.get('gender') == 'male' else 1
        birth_date = request.form.get('birth_date')
        national_id = request.form.get('national_id')
        father_name = request.form.get('father_name')
        id_number = request.form.get('id_number')
        serial_number = request.form.get('serial_number')
        phone_number = request.form.get('phone_number')

        # Educational Information
        master_field = request.form.get('master_field')
        master_university = request.form.get('master_university')
        master_type = 1 if request.form.get('master_type') == 'funded' else 2
        start_date = request.form.get('start_date')
        graduation_date = request.form.get('graduation_date')
        match (request.form.get('graduation_status')):
            case 'graduated':
                graduation_status = 1
            case 'last_semester_student':
                graduation_status = 2
            case 'pro_phd':
                graduation_status = 3
        semester_count = request.form.get('semester_count')
        score_wout_thesis = request.form.get('score_wout_thesis')
        score_with_thesis = request.form.get('score_with_thesis')
        thesis_score = request.form.get('thesis_score')
        score_normalized = request.form.get('score_normalized')
        applied_field = request.form.get('applied_field')

        # English Degree Information
        english_degree_type = request.form.get('english_degree_type')
        english_degree_score = request.form.get('english_degree_score')
        english_degree_education_date = request.form.get('english_degree_education_date')
        english_degree_validation_date = request.form.get('english_degree_validation_date')

        # Research Documents
        article_title = request.form.get('article_title')
        extracted_from_thesis = True if request.form.get('extracted_from_thesis') == 'yes' else False
        issn = request.form.get('issn')
        magazine_full_name = request.form.get('magazine_full_name')
        magazine_short_name = request.form.get('magazine_short_name')
        match (request.form.get('article_type')):
            case 'ISC':
                article_type = 1
            case 'ISI':
                article_type = 2
            case 'scientific':
                article_type = 3
            case 'non_scientific':
                article_type = 4
        author_name = request.form.get('author_name')
        match (request.form.get('author_title')):
            case 'student':
                author_title = 1
            case 'professor':
                author_title = 2
            case 'etc':
                author_title = 3

        
        db = get_database_connection()
        cur = db.cursor()

        cur.execute("UPDATE norm.student_info SET firstname = %s,lastname = %s,gender = %s,dateofbirth = %s,fathername = %s,idcard_number = %s,idcard_serial = %s,phone_number = %s,master_field = %s,master_type = %s,master_university_name = %s,master_start_date = %s,master_graduation_date = %s,master_graduation_status = %s,master_semester_count = %s,master_score_wout_thesis = %s,master_score_with_thesis = %s,thesis_score = %s,master_score_normalized = %s,applied_phd_field = %s,english_degree_type = %s,english_degree_score = %s,english_degree_education_date = %s,english_degree_validation_date = %s WHERE national_id = %s", (first_name, last_name, gender, birth_date, father_name, id_number, serial_number, phone_number, master_field, master_type, master_university, start_date, graduation_date, graduation_status, semester_count, score_wout_thesis, score_with_thesis, thesis_score, score_normalized, applied_field, english_degree_type, english_degree_score, english_degree_education_date, english_degree_validation_date, national_id,))

        cur.execute("UPDATE norm.essay_detail SET essay_title = %s,issn = %s,essay_type = %s,extracted_from_thesis = %s,magazine_full_name = %s,magazine_short_name = %s,author_name = %s,author_type = %s WHERE national_id = %s", (article_title, issn, article_type, extracted_from_thesis, magazine_full_name, magazine_short_name, author_name, author_title,national_id,))

        db.commit()
        cur.close()
        db.close()
        return redirect('/')
        

@app.route('/delete/<national_id>', methods=['GET','POST'])
def delete_student(national_id):
    if request.method == 'GET':
        db = get_database_connection()
        cur = db.cursor()
        cur.execute(f'''DELETE FROM norm.student_info
	        WHERE national_id= '{national_id}';''',)
        db.commit()
        cur.close()
        db.close()
    return redirect('/')

@app.route('/search/<search_term>')
def search(search_term):

    print("here", type(search_term), search_term)
    records= []
    if search_term != None:
        db = get_database_connection()
        cur = db.cursor()
        cur.execute("SELECT National_ID, FirstName, LastName, Applied_PHD_Field, master_score_with_thesis, master_score_normalized FROM norm.Student_Info si WHERE si.firstname = %s or si.national_id = %s order by si.master_score_with_thesis desc", (search_term, search_term,))
        rows = cur.fetchall()
        for row in rows:
            record = {
                'national_id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'requested_field': row[3],
                'score_with_thesis' : row[4],
                'normalized_score' : row[5]
            }
            records.append(record)

    cur.execute('''select avg(master_score_with_thesis), avg(master_score_normalized) from norm.student_info si;''')

    avg_score_with_thesis = ''
    avg_score_normalized = ''

    data = cur.fetchone()
    if (data[0] != None and data[1] != None):
        avg_score_with_thesis = round (data[0], 2)
        avg_score_normalized = round(data[1], 2)

    cur.close
    db.close

    return render_template('index.html', records=records, avg_score_with_thesis = avg_score_with_thesis, avg_score_normalized = avg_score_normalized)

if __name__ == '__main__':
    create_tables()
    app.run()