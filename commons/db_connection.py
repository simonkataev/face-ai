import json
import os
import sqlite3
import traceback

from PyQt5.QtWidgets import QMessageBox

from commons.case_info import CaseInfo
from commons.common import Common
from commons.probing_result import ProbingResult
from cryptophic.main import get_dec_file_path, decrypt_file_to, encrypt_file_to


class DBConnection:
    def __init__(self):
        self.connection_string = None
        self.connection = None
        self.dec_db_file_path = ''
        self.create_connection_string()
        self.create_table()

    # create connection string from according register value and common value
    def create_connection_string(self):
        reg_value = Common.get_reg(Common.REG_KEY)
        connection_string_buff = ""
        if reg_value is not None:
            connection_string_buff = reg_value
        else:
            Common.show_message(QMessageBox.Warning, "You did not get data storage path. \n "
                                                     "The data storage path will be application root directory.",
                                "Data Storage not found", "Data Storage not found", "")
            connection_string_buff = Common.STORAGE_PATH
        # create database path from created database path
        Common.create_path(connection_string_buff)
        connection_string_buff += '/reports.db'
        self.connection_string = connection_string_buff
        # get the temporary path for enc/dec
        dec_root_path = get_dec_file_path()
        # create temporary database file
        dec_db_path = os.path.join(dec_root_path, Common.STORAGE_PATH)
        self.dec_db_file_path = os.path.join(dec_db_path, 'reports.db')
        Common.create_path(dec_db_path)

    def create_table(self):
        decrypt_file_to(os.path.join(self.connection_string), self.dec_db_file_path)
        try:
            query_string_cases = "create table if not exists cases (" \
                                 "id INTEGER PRIMARY KEY, " \
                                 "case_no TEXT," \
                                 "ps TEXT," \
                                 "examiner_name TEXT," \
                                 "examiner_no TEXT," \
                                 "remarks TEXT," \
                                 "subject_url TEXT," \
                                 "created_date DATE," \
                                 "probe_id TEXT," \
                                 "matched TEXT," \
                                 "report_generation_time TEXT," \
                                 "json_result TEXT);"
            query_string_targets = "create table if not exists targets (" \
                                   "id INTEGER PRIMARY KEY, " \
                                   "target_url TEXT," \
                                   "case_id INTEGER," \
                                   "similarity FLOAT);"
            self.connection = sqlite3.connect(self.dec_db_file_path)
            # self.connection = sqlite3.connect(self.connection_string)
            cursor = self.connection.cursor()
            cursor.execute(query_string_cases)
            cursor.execute(query_string_targets)
            self.connection.commit()
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())
        finally:
            if self.connection:
                self.connection.close()
                encrypt_file_to(self.dec_db_file_path, self.connection_string)

    def count_row_number(self, table_name):
        decrypt_file_to(os.path.join(self.connection_string), self.dec_db_file_path)
        try:
            query_string = "select count(id) from " + table_name + ";"
            self.connection = sqlite3.connect(self.dec_db_file_path)
            cursor = self.connection.cursor()
            cursor.execute(query_string)
            row = cursor.fetchone()
            self.connection.commit()
            if row:
                return row[0]
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())
        finally:
            if self.connection:
                self.connection.close()
                encrypt_file_to(self.dec_db_file_path, self.connection_string)
        return 0

    def get_values(self):
        decrypt_file_to(os.path.join(self.connection_string), self.dec_db_file_path)
        results = []
        try:
            query_string = "select " \
                           "id,probe_id,matched," \
                           "case_no,PS,examiner_no,examiner_name,remarks" \
                           ",subject_url,json_result,created_date" \
                           " from cases " \
                           " order by created_date desc"
            self.connection = sqlite3.connect(self.dec_db_file_path)
            cursor = self.connection.cursor()
            cursor.execute(query_string)
            rows = cursor.fetchall()
            self.connection.commit()
            for row in rows:
                probe_result = ProbingResult()
                case_info = CaseInfo()
                probe_result.probe_id = row[1]
                probe_result.matched = row[2]
                case_info.case_number = row[3]
                case_info.case_PS = row[4]
                case_info.examiner_no = row[5]
                case_info.examiner_name = row[6]
                case_info.remarks = row[7]
                case_info.subject_image_url = row[8]
                json_data = row[9]
                # json_data = json.dumps(json_data)
                json_data = json.loads(json_data)
                probe_result.json_result = json_data
                probe_result.created_date = row[10]
                probe_result.case_info = case_info
                results.append(probe_result)
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())
        finally:
            if self.connection:
                self.connection.close()
                encrypt_file_to(self.dec_db_file_path, self.connection_string)
        return results

    def search_results(self, search_val, total, current_page, number_per_page):
        decrypt_file_to(os.path.join(self.connection_string), self.dec_db_file_path)
        last_index = current_page * number_per_page
        query_string = ""
        if number_per_page >= total:
            query_string = "select id,probe_id,matched," \
                           "case_no,PS,examiner_no,examiner_name,remarks" \
                           ",subject_url,json_result,created_date" \
                           " from cases" \
                           " where created_date like '%" + search_val + "%' " \
                                                                        " or case_no like '%" + search_val + "%' " \
                                                                                                             " or ps like '%" + search_val + "%' " \
                                                                                                                                             " or probe_id like '%" + search_val + "%' " \
                                                                                                                                                                                   " or examiner_no like '%" + search_val + "%' " \
                                                                                                                                                                                                                            " or examiner_name like '%" + search_val + "%' " \
                                                                                                                                                                                                                                                                       " order by created_date desc limit " \
                           + str(number_per_page)
        else:

            if last_index == 0:
                query_string = "select id,probe_id,matched," \
                               "case_no,PS,examiner_no,examiner_name,remarks" \
                               ",subject_url,json_result,created_date" \
                               " from cases" \
                               " where created_date like '%" + search_val + "%' " \
                                                                            " or case_no like '%" + search_val + "%' " \
                                                                                                                 " or ps like '%" + search_val + "%' " \
                                                                                                                                                 " or probe_id like '%" + search_val + "%' " \
                                                                                                                                                                                       " or examiner_no like '%" + search_val + "%' " \
                                                                                                                                                                                                                                " or examiner_name like '%" + search_val + "%' " \
                                                                                                                                                                                                                                                                           " order by created_date desc limit " \
                               + str(number_per_page)
            else:
                query_string = "select id,probe_id,matched," \
                               "case_no,PS,examiner_no,examiner_name,remarks" \
                               ",subject_url,json_result,created_date" \
                               " from " \
                               " (select * from cases where created_date like '%" + search_val + "%' " \
                                                                                                 " or case_no like '%" + search_val + "%' " \
                                                                                                                                      " or ps like '%" + search_val + "%' " \
                                                                                                                                                                      " or probe_id like '%" + search_val + "%' " \
                                                                                                                                                                                                            " or examiner_no like '%" + search_val + "%' " \
                                                                                                                                                                                                                                                     " or examiner_name like '%" + search_val + "%' " \
                                                                                                                                                                                                                                                                                                " order by created_date desc) as a " \
                                                                                                                                                                                                                                                                                                " where a.id < " \
                                                                                                                                                                                                                                                                                                "(select min(id) from " \
                                                                                                                                                                                                                                                                                                " (select * from cases" \
                                                                                                                                                                                                                                                                                                " where created_date like '%" + search_val + "%' " \
                                                                                                                                                                                                                                                                                                                                             " or case_no like '%" + search_val + "%' " \
                                                                                                                                                                                                                                                                                                                                                                                  " or ps like '%" + search_val + "%' " \
                                                                                                                                                                                                                                                                                                                                                                                                                  " or probe_id like '%" + search_val + "%' " \
                                                                                                                                                                                                                                                                                                                                                                                                                                                        " or examiner_no like '%" + search_val + "%' " \
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 " or examiner_name like '%" + search_val + "%' " \
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            " order by created_date desc limit " \
                               + str(last_index) + "))" \
                                                   " limit " + str(number_per_page)
        results = []
        try:
            self.connection = sqlite3.connect(self.dec_db_file_path)
            cursor = self.connection.cursor()
            cursor.execute(query_string)
            rows = cursor.fetchall()
            self.connection.commit()
            for row in rows:
                probe_result = ProbingResult()
                case_info = CaseInfo()
                probe_result.probe_id = row[1]
                probe_result.matched = row[2]
                case_info.case_number = row[3]
                case_info.case_PS = row[4]
                case_info.examiner_no = row[5]
                case_info.examiner_name = row[6]
                case_info.remarks = row[7]
                case_info.subject_image_url = row[8]
                json_data = row[9]
                # json_data = json.dumps(json_data)
                json_data = json.loads(json_data)
                probe_result.json_result = json_data
                probe_result.created_date = row[10]
                probe_result.case_info = case_info
                results.append(probe_result)
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())
        finally:
            if self.connection:
                self.connection.close()
                encrypt_file_to(self.dec_db_file_path, self.connection_string)
        return results

    def count_search_results(self, search_val):
        decrypt_file_to(os.path.join(self.connection_string), self.dec_db_file_path)
        query_string = query_string = "select count(id) from cases" \
                                      " where created_date like '%" + search_val + "%' " \
                                                                                   " or case_no like '%" + search_val + "%' " \
                                                                                                                        " or ps like '%" + search_val + "%' " \
                                                                                                                                                        " or probe_id like '%" + search_val + "%' " \
                                                                                                                                                                                              " or examiner_no like '%" + search_val + "%' " \
                                                                                                                                                                                                                                       " or examiner_name like '%" + search_val + "%' " \
                                                                                                                                                                                                                                                                                  " order by created_date desc "
        try:
            self.connection = sqlite3.connect(self.dec_db_file_path)
            cursor = self.connection.cursor()
            cursor.execute(query_string)
            rows = cursor.fetchone()
            self.connection.commit()
            return rows[0]

        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())
        finally:
            if self.connection:
                self.connection.close()
                encrypt_file_to(self.dec_db_file_path, self.connection_string)
        return 0

    def get_last_inserted_id(self, table_name, id_field):
        decrypt_file_to(os.path.join(self.connection_string), self.dec_db_file_path)
        try:
            query_string = "select " + id_field + " from " + table_name + " order by " + id_field + " desc;"
            self.connection = sqlite3.connect(self.dec_db_file_path)
            cursor = self.connection.cursor()
            cursor.execute(query_string)
            rows = cursor.fetchone()
            self.connection.commit()
            if rows:
                for row in rows:
                    return row
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())
        finally:
            if self.connection:
                self.connection.close()
                encrypt_file_to(self.dec_db_file_path, self.connection_string)
        return 0

    # values : list of tuples
    def insert_values(self, table_name, fields, values):
        decrypt_file_to(os.path.join(self.connection_string), self.dec_db_file_path)
        try:
            self.connection = sqlite3.connect(self.dec_db_file_path)
            cursor = self.connection.cursor()
            query_string = "insert into " + table_name + "("
            # add field names to query
            for field in fields:
                query_string += field
                query_string += ","
            # remove last comma
            len_query = len(query_string)
            query_string = query_string[0:len_query - 1]
            query_string += ") values("
            # add value field to query
            for i in range(len(values[0])):
                query_string += "?,"
            query_string = query_string[0:len([query_string]) - 2]
            query_string += ")"
            cursor.executemany(query_string, values)
            self.connection.commit()
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())

        finally:
            if self.connection:
                self.connection.close()
                encrypt_file_to(self.dec_db_file_path, self.connection_string)
        return self.get_last_inserted_id(table_name, "id")

    def is_exist_value(self, table_name, field, value):
        decrypt_file_to(os.path.join(self.connection_string), self.dec_db_file_path)
        try:
            query_string = "select * from " + table_name + " where " + field + "=" + value
            self.connection = sqlite3.connect(self.dec_db_file_path)
            cursor = self.connection.cursor()
            cursor.execute(query_string)
            rows = cursor.fetchone()
            self.connection.commit()
            if rows:
                for row in rows:
                    return True
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())
        finally:
            if self.connection:
                self.connection.close()
                encrypt_file_to(self.dec_db_file_path, self.connection_string)
        return False

    def get_pagination_results(self, param, total, current_page, number_per_page):
        decrypt_file_to(os.path.join(self.connection_string), self.dec_db_file_path)
        results = []
        last_index = current_page * number_per_page
        query_string = ""
        if number_per_page >= total:
            query_string = "select id,probe_id,matched," \
                           "case_no,PS,examiner_no,examiner_name,remarks" \
                           ",subject_url,json_result,created_date" \
                           " from cases order by created_date DESC limit " + str(number_per_page)
        else:
            if last_index:
                query_string = "select id,probe_id,matched," \
                               "case_no,PS,examiner_no,examiner_name,remarks" \
                               ",subject_url,json_result,created_date" \
                               " from " \
                               " (select * from cases order by created_date DESC) as a " \
                               " where a.id < (select min(id) from (select * from cases order by created_date DESC limit " \
                               + str(last_index) + "))" \
                                                   " limit " + str(number_per_page)
            else:
                query_string = "select id,probe_id,matched," \
                               "case_no,PS,examiner_no,examiner_name,remarks" \
                               ",subject_url,json_result,created_date" \
                               " from cases order by created_date DESC limit " + str(number_per_page)
        try:
            self.connection = sqlite3.connect(self.dec_db_file_path)
            cursor = self.connection.cursor()
            cursor.execute(query_string)
            rows = cursor.fetchall()
            self.connection.commit()
            for row in rows:
                probe_result = ProbingResult()
                case_info = CaseInfo()
                probe_result.probe_id = row[1]
                probe_result.matched = row[2]
                case_info.case_number = row[3]
                case_info.case_PS = row[4]
                case_info.examiner_no = row[5]
                case_info.examiner_name = row[6]
                case_info.remarks = row[7]
                case_info.subject_image_url = row[8]
                json_data = row[9]
                # json_data = json.dumps(json_data)
                json_data = json.loads(json_data)
                probe_result.json_result = json_data
                probe_result.created_date = row[10]
                probe_result.case_info = case_info
                results.append(probe_result)
        except sqlite3.IntegrityError as e:
            print('INTEGRITY ERROR\n')
            print(traceback.print_exc())
        finally:
            if self.connection:
                self.connection.close()
                encrypt_file_to(self.dec_db_file_path, self.connection_string)
        return results

    def get_case_data(self, results):
        decrypt_file_to(os.path.join(self.connection_string), self.dec_db_file_path)
        case_no = ''
        ps = ''
        cases = []
        if results is not None:
            index = 0
            try:
                self.connection = sqlite3.connect(self.dec_db_file_path)
                for result in results:
                    img_path = result['image_path']
                    query_string = "select " \
                                   "case_no,ps,probe_id from cases " \
                                   " where subject_url='" + img_path + "'"
                                #    " where id=(select case_id from targets where target_url='" + img_path + "')"
                    cursor = self.connection.cursor()
                    cursor.execute(query_string)
                    rows = cursor.fetchall()
                    self.connection.commit()
                    case_no = ""
                    ps = ""
                    probe_id = ""
                    for row in rows:
                        case_no = row[0]
                        ps = row[1]
                        probe_id = row[2]
                    case = (case_no, ps, probe_id)
                    cases.append(case)
            except sqlite3.IntegrityError as e:
                print('INTEGRITY ERROR\n')
                print(traceback.print_exc())
            finally:
                if self.connection:
                    self.connection.close()
                    encrypt_file_to(self.dec_db_file_path, self.connection_string)
        return cases
