-- db_tour.sql
-- Database-design walkthrough for the IMAT2718 video presentation.
--
-- Run it from the project folder (the one containing db.sqlite3) with:
--     sqlite3 db.sqlite3 ".read db_tour.sql"
--
-- It lists the tables, shows the key fields with their primary and foreign
-- keys, and prints a little sample data — so you can narrate the database
-- design without typing anything live on camera.
--
-- Prerequisite: build and populate the database first, otherwise the tables
-- do not exist yet:
--     python manage.py migrate
--     python manage.py seed_demo

.headers on
.mode box
.nullvalue (null)

.print ''
.print '======== ALL TABLES IN THE DATABASE ========'
.tables

.print ''
.print '======== COURSE  ->  courses_course  (PK id, UNIQUE code) ========'
.schema courses_course

.print ''
.print '======== MODULE  ->  courses_module  (PK id, FK course_id REFERENCES courses_course) ========'
.schema courses_module

.print ''
.print '======== ENROLLMENT  ->  courses_enrollment  (junction: FK user_id + FK course_id, UNIQUE(user_id, course_id)) ========'
.schema courses_enrollment

.print ''
.print '======== USER  ->  accounts_user  (columns; pk=1 marks the primary key) ========'
PRAGMA table_info(accounts_user);

.print ''
.print '======== SAMPLE DATA: COURSES ========'
SELECT id, code, name FROM courses_course;

.print ''
.print '======== SAMPLE DATA: MODULES  (note the course_id foreign key) ========'
SELECT id, code, title, course_id FROM courses_module;

.print ''
.print '======== SAMPLE DATA: ENROLLMENTS  (note the user_id + course_id foreign keys) ========'
SELECT id, user_id, course_id, status FROM courses_enrollment;

.print ''
.print '======== SECURITY: passwords are stored HASHED, never in plain text ========'
SELECT username, is_teacher, substr(password, 1, 42) || '...' AS password_hash FROM accounts_user;

.print ''
.print '======== End of tour ========'
