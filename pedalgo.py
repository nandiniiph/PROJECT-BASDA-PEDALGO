import psycopg2
from tabulate import tabulate
import pyfiglet
from colorama import init, Fore
import os
import time
import datetime
from stdiomask import getpass

conn = psycopg2.connect(database= 'PEDAL.GO', user = 'postgres', password='@Nandini77', host='localhost', port=5432)
cur = conn.cursor()

        
def read(cur):
    try:
        loading_animation("Loading ya bosqueee")
        os.system('cls')
        print(Fore.YELLOW + "\n=========================================")
        print(Fore.CYAN + "                MENAMPILKAN DATA                   ")
        print(Fore.YELLOW + "=========================================")
        print(Fore.YELLOW + "Berikut beberapa tabel yang dapat ditampilkan: ")
        print(Fore.CYAN + "1. role")
        print(Fore.CYAN + "2. penyewaan")
        print(Fore.CYAN + "3. sepeda")
        print(Fore.CYAN + "4. detail_Penyewaan")
        print(Fore.CYAN + "5. transaksi")
        print(Fore.CYAN + "6. pengeluaran")
        select = input('Masukkan nama tabel yang ingin ditampilkan (harus sesuai dengan yang dicontoh): ')
        query = f'SELECT * FROM {select}'
        cur.execute(query)
        rowss = cur.fetchall()

        column_names = [description[0] for description in cur.description]
        print(tabulate(rowss, headers=column_names, tablefmt='fancy_grid'))
        input(Fore.MAGENTA + "\nTekan enter untuk melanjutkan...")
        admin_page(rows)  # Assuming rows should be passed as argument

    except (psycopg2.Error, NameError) as e:
        print(Fore.RED + f"Terjadi kesalahan: {e}")
        input(Fore.MAGENTA + "Tekan enter untuk kembali...")
        # Consider calling a main menu or error handling function here


def delete(cur):
    select = input('Masukkan nama tabel yang ingin dihapus: ')
    chose = input('Masukkan id yang ingin dihapus: ')
    query = f'DELETE FROM {select} WHERE id_{select} = {chose}'
    cur.execute(query)
    conn.commit()
    print('Data berhasil dihapus')
    time.sleep(2)
    loading_page()

def login():
    os.system('cls')
    print(Fore.YELLOW + "=========================================")
    print(Fore.CYAN + "                Login                    ")
    print(Fore.YELLOW + "=========================================")
    username = input(Fore.GREEN + 'Masukkan email: ' + Fore.RESET)
    password = getpass(Fore.GREEN + 'Masukkan password: ' + Fore.RESET)
    
    query = f"SELECT * FROM role WHERE email = '{username}' AND password = '{password}'"
    cur.execute(query)
    global rows
    rows = cur.fetchone()
    
    if rows is None:
        print(Fore.RED + 'Username atau password salah\n')
        input(Fore.MAGENTA + "Tekan enter untuk mencoba lagi...")
        return login()
    else:
        print(Fore.GREEN + 'Login berhasil\n')
        if rows[6] == 1:
            print(Fore.RED + 'Anda login sebagai user')
        else:
            print(Fore.RED + 'Anda login sebagai admin')
            admin_page(rows)
    input(Fore.MAGENTA + "Tekan enter untuk melanjutkan...")
    return rows

def register():
    os.system('cls')
    nama = input('Masukkan nama: ')
    email = input('Masukkan email: ')
    alamat = input('Masukkan alamat: ')
    noHp = input('Masukkan nomor HP: ')
    password = input('Masukkan password: ')
    query = f'INSERT INTO role (nama, email, alamat, no_handphone, id_jenis_role, password) VALUES (\'{nama}\', \'{email}\', \'{alamat}\', \'{noHp}\', \'1\', \'{password}\')'
    cur.execute(query)
    conn.commit()
    print('Registrasi berhasil')
    time.sleep(2)
    loading_page()
    
def sewa_sepeda():
    try:
        os.system('cls')
        print(Fore.YELLOW + "=========================================")
        print(Fore.CYAN + "                Sewa Sepeda              ")
        print(Fore.YELLOW + "=========================================\n")
        
        global tgl
        while True:
            try:
                tgl = input(Fore.WHITE + 'Masukkan tanggal sewa (YYYY-MM-DD): ' + Fore.RESET)
                if not tgl:
                    raise ValueError("Tanggal sewa tidak boleh kosong.")
                break
            except ValueError:
                print(Fore.RED + "Input tanggal tidak valid. Pastikan format tanggal (YYYY-MM-DD) benar.")

        while True:
            try:
                durasi = int(input(Fore.WHITE + 'Masukkan durasi sewa (jam): ' + Fore.RESET))
                if durasi < 0 or durasi > 3:
                    raise ValueError("Durasi sewa harus antara 0 dan 3 jam.")
                break
            except ValueError:
                print(Fore.RED + "Input durasi tidak valid. Masukkan angka antara 0 dan 3 jam.")

        while True:
            try:
                time_start = input(Fore.WHITE + 'Masukkan waktu mulai (HH:MM:SS): ' + Fore.RESET)
                if not time_start:
                    raise ValueError("Waktu mulai tidak boleh kosong.")
                break
            except ValueError:
                print(Fore.RED + "Input waktu mulai tidak valid. Pastikan format waktu (HH:MM:SS) benar.")

        while True:
            try:
                time_start_obj = datetime.datetime.strptime(time_start, '%H:%M:%S')
                time_end_obj = time_start_obj + datetime.timedelta(hours=durasi)
                time_end = time_end_obj.strftime('%H:%M:%S')
                if time_end_obj.hour > 15:
                    raise ValueError("Waktu penyewaan sudah ditutup. Maksimal waktu selesai adalah 15:00:00.")

                time_end = time_end_obj.strftime('%H:%M:%S')
                print(f"Waktu selesai: {time_end}")
                break
            except ValueError:
                print(Fore.RED + "Input tidak valid. Pastikan format tanggal, waktu, dan durasi benar. Waktu penyewaan maksimal 15:00:00.")
                input(Fore.MAGENTA + "Tekan enter untuk kembali...")
                sewa_sepeda()


            except psycopg2.Error as e:
                print(Fore.RED + f"Terjadi kesalahan pada database: {e}")
                conn.rollback()
                input(Fore.MAGENTA + "Tekan enter untuk kembali...")
        
        query = f"""
        SELECT * FROM sepeda 
        WHERE id_sepeda NOT IN (
            SELECT id_sepeda 
            FROM detail_penyewaan dp 
            JOIN penyewaan p ON p.id_penyewaan = dp.id_penyewaan 
            WHERE p.tanggal_penyewaan = %s 
            AND ((p.waktu_mulai <= %s AND p.waktu_selesai >= %s) 
            OR (p.waktu_mulai <= %s AND p.waktu_selesai >= %s))
        )
        """
        cur.execute(query, (tgl, time_start, time_start, time_end, time_end))
        rows = cur.fetchall()
        
        if not rows:
            print(Fore.RED + "Maaf, tidak ada sepeda yang tersedia untuk waktu yang dipilih.")
            input(Fore.MAGENTA + "Tekan enter untuk kembali...")
            after_login(logged_in_user)
            return
        
        
        column_names = [description[0] for description in cur.description]
        loading_animation("Sebentar ya banggg cari sepeda dulu....")
        print("=========================================")
        print("       Daftar Sepeda yang Tersedia       ")
        print("=========================================")
        print(tabulate(rows, headers=column_names, tablefmt='pretty'))
        
        id_sepeda = input(Fore.WHITE + 'Masukkan ID sepeda yang ingin disewa: ' + Fore.RESET)
        ket = input(Fore.WHITE + 'Masukkan keterangan (jika tidak ada beri - ajaaa): ' + Fore.RESET)
        
        penyewaan_query = "INSERT INTO penyewaan (tanggal_penyewaan, durasi_penyewaan, waktu_mulai, waktu_selesai) VALUES (%s, %s, %s, %s)"
        cur.execute(penyewaan_query, (tgl, durasi, time_start, time_end))
        
        cur.execute("SELECT id_penyewaan FROM penyewaan ORDER BY id_penyewaan DESC LIMIT 1")
        id_penyewaan = cur.fetchone()[0]
        
        detail_query = "INSERT INTO detail_penyewaan (keterangan, id_sepeda, id_role, id_penyewaan) VALUES (%s, %s, %s, %s)"
        cur.execute(detail_query, (ket, id_sepeda, logged_in_user[0], id_penyewaan))
        
        cur.execute("SELECT id_detail_penyewaan FROM detail_penyewaan ORDER BY id_detail_penyewaan DESC LIMIT 1")
        global datapenyewaan
        datapenyewaan = cur.fetchone()[0]
        
        conn.commit()
        
        print(Fore.GREEN + "\nPenyewaan berhasil! Selamat menikmati perjalanan Anda Dan Silahkan Melakukan Pembayaran")
        transaksi()
        return datapenyewaan
    except ValueError:
        print(Fore.RED + "Input tidak valid. Pastikan format tanggal, waktu, dan durasi benar.")
        input(Fore.MAGENTA + "Tekan enter untuk kembali...")
        sewa_sepeda()
    except psycopg2.Error as e:
        print(Fore.RED + f"Terjadi kesalahan pada database: {e}")
        conn.rollback()
        input(Fore.MAGENTA + "Tekan enter untuk kembali...")
        sewa_sepeda()

def transaksi():
    os.system('cls')
    print(Fore.YELLOW + "=========================================")
    print(Fore.CYAN + "            PILIH METODE PEMBAYARAN        ")
    print(Fore.YELLOW + "=========================================")
    print(Fore.CYAN + "1. Cash")
    print(Fore.CYAN + "2. Bank BRI")
    print(Fore.CYAN + "3. Bank Mandiri")
    print(Fore.CYAN + "4. Bank BCA")
    print(Fore.CYAN + "5. DANA")
    print(Fore.CYAN + "6. GOPAY")
    print(Fore.YELLOW + "=========================================")
    
    choice = input(Fore.MAGENTA + "Pilih metode pembayaran: ")
    jumlah_pembayaran = 5000  
    try :
        transaksi_query = "INSERT INTO transaksi (id_mtd_bayar, tanggal_transaksi, jumlah, id_detail_penyewaan, id_laporan_keuangan) VALUES (%s, %s, %s, %s, 1)"
        cur.execute(transaksi_query, (choice, tgl, jumlah_pembayaran, datapenyewaan))
        os.system('cls')
        print("----------BERIKUT DATA PENYEWAAN ANDA----------")
    
        cur.execute("SELECT id_transaksi FROM transaksi ORDER BY id_transaksi DESC LIMIT 1")
        id_transaksi = cur.fetchone()[0]
    
        conn.commit()

    # Menampilkan data penyewaan
        cur.execute("""SELECT r.nama, 
       p.tanggal_penyewaan, 
       p.waktu_mulai, 
       p.waktu_selesai, 
       s.id_sepeda, 
       CASE 
           WHEN t.id_mtd_bayar = 1 THEN 'cash'
           WHEN t.id_mtd_bayar = 2 THEN 'Bank BRI'
           WHEN t.id_mtd_bayar = 3 THEN 'Bank Mandiri'
           WHEN t.id_mtd_bayar = 4 THEN 'Bank BCA'
           WHEN t.id_mtd_bayar = 5 THEN 'Dana'
           WHEN t.id_mtd_bayar = 6 THEN 'Gopay'
       END AS metode_pembayaran
FROM transaksi t
JOIN detail_penyewaan dp ON t.id_detail_penyewaan = dp.id_detail_penyewaan
JOIN sepeda s ON s.id_sepeda = dp.id_sepeda
JOIN penyewaan p ON p.id_penyewaan = dp.id_penyewaan
JOIN role r ON r.id_role = dp.id_role
JOIN metode_pembayaran m ON m.id_mtd_bayar = t.id_mtd_bayar
    WHERE p.id_penyewaan = %s
    """, (datapenyewaan,))
    
        hasil = cur.fetchall()
        headers = [desc[0] for desc in cur.description]
        print(tabulate(hasil, headers=headers, tablefmt='pretty'))

        print(Fore.GREEN + "Pembayaran berhasil! Terima kasih telah menggunakan Pedalgo.")
    except psycopg2.Error as e:
        print(Fore.RED + f"Terjadi kesalahan pada database: {e}")
        conn.rollback()
    except Exception as e:
        print(Fore.RED + f"Terjadi kesalahan: {e}")
    finally:
        input(Fore.MAGENTA + "Tekan enter untuk kembali...")
        after_login(logged_in_user)
        return id_transaksi