import sqlite3, os
from cryptophic.main import encrypt_file, decrypt_file, get_dec_file_path
from pyutil import filereplace
import cpuinfo, wmi
from commons.ntptime import ntp_get_time
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from commons.common import Common
from PyQt5.QtWidgets import QMessageBox

license_file_name = r"license.dat"
database_file_name = r"data.db"

def access_license_list(license_str):
    expire_flag = ""
    expire_dt = None
    decrypt_file(os.path.join(license_file_name))
    dec_secure_path = get_dec_file_path()

    try:
        listFile = open(os.path.join(dec_secure_path, license_file_name), "r")
        if listFile:
            # Match inputed license and license list file
            matched = False
            for line in listFile:
                if license_str == line.split("&")[0]:
                    matched = True
                    expire_flag = line.split("&")[1]
            listFile.close()   

            # If Matched
            if matched == True:
                print("Matched")

                ### getting validate date
                try:
                    today_dt = ntp_get_time()
                    if today_dt is None:
                        encrypt_file(license_file_name)
                        return (-1, "")
                    expire_f = expire_flag.split("|")
                    expire_dt = today_dt
                    for e in expire_f:
                        e_ = e.replace("Year", "").replace("Month", "")
                        if "Day" in e_:
                            e__ = e_.replace("Day", "")
                            expire_dt += timedelta(days=int(e__))
                        else:
                            expire_dt += relativedelta(months=+int(e_))
                except Exception as e:
                    print("ntp error:", e)
                    encrypt_file(license_file_name)
                    return (-1, "")
                    
                ## Delete matched license from list file                   
                filereplace(os.path.join(dec_secure_path, license_file_name), license_str, "")
            else:
                print("Unmatched")
                encrypt_file(license_file_name)
                return (0, "")
        else:
            print("File non-exist")
            encrypt_file(license_file_name)
            return (0, "")
    except Exception as e:
        print("access_license_list: ", e)
        encrypt_file(license_file_name)
        return (0, "")

    encrypt_file(license_file_name)
    return (1, expire_dt.strftime('%d/%m/%Y %H:%M:%S'))
    

def read_information_db():
    decrypt_file(os.path.join(database_file_name))
    dec_secure_path = get_dec_file_path()
    try:
        connection = sqlite3.connect(os.path.join(dec_secure_path, database_file_name))
        cursor = connection.cursor()
    
        (count,) = connection.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{}'".format("appinfo")).fetchone()
        if count == 0:
            fpo, atpo = get_cpu_info()
            cursor.execute("""CREATE TABLE appinfo (isdst, expire, fpo, atpo)""")
            cursor.execute("INSERT INTO appinfo VALUES (?,?,?,?)", (False, "expire", fpo, atpo))
            connection.commit()
    
        cursor.execute("SELECT * FROM appinfo")
        result = cursor.fetchone()
        unlocked = result[0]
        expire_date = result[1]
        fpo_info = result[2]
        atpo_info = result[3]
    
    except OperationalError:
        encrypt_file(database_file_name)
        print("Database Error")
        return(False, "expire", "fpo", "atpo")
    
    finally:
        connection.close()
    encrypt_file(database_file_name)
    return (unlocked, expire_date, fpo_info, atpo_info)

def write_infomation_db(isdst, expire, fpo, atpo):
    decrypt_file(os.path.join(database_file_name))
    dec_secure_path = get_dec_file_path()

    try:
        connection = sqlite3.connect(os.path.join(dec_secure_path, database_file_name))
        cursor = connection.cursor()  
        cursor.execute("UPDATE appinfo SET isdst = ?, expire = ?, fpo = ?, atpo = ?", (isdst, expire, fpo, atpo))
        connection.commit()    

    except Exception as e: 
        encrypt_file(database_file_name)
        print("write_infomation_db: ", e)
        return(False, "expire", "fpo", "atpo")

    finally:
        connection.close() 

    encrypt_file(database_file_name)

def get_cpu_info():
    fpo_value = ""
    atpo_value = ""
    c = wmi.WMI()
    for s in c.Win32_Processor():
        fpo_value = s.ProcessorId
        atpo_value = s.Description
    
    return (fpo_value, atpo_value)