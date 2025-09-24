import mysql.connector
from mysql.connector import Error
from decimal import Decimal
import bcrypt
from dbconfig_bank import config


def get_db_connection():
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"❌ Error saat menghubungkan ke MySQL: {e}")
        return None
    
def registrasi_user(username, password):
    "Mendaftarkan user baru dengan password yang di-hash."
    try:
        # Mengubah password string menjadi byte
        password_bytes = password.encode('utf-8')
        # Membuat salt dan hash password
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password_bytes, salt)
        
        query = "INSERT INTO user (username, password_hash) VALUES (%s, %s)"
        # Menyimpan hash sebagai string di database
        args = (username, password_hash.decode('utf-8'))
        
        conn = get_db_connection()
        if not conn: return False
        
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
        print(f"✅ User '{username}' berhasil diregistrasi.")
        return True
    except Error as e:
        # Menangani jika username sudah ada
        if e.errno == 1062: # Duplicate entry
            print(f"❌ Gagal: Username '{username}' sudah digunakan.")
        else:
            print(f"❌ Gagal melakukan registrasi: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def login_user(username, password):
    """Memverifikasi login user dengan password yang di-hash."""
    try:
        query = "SELECT password_hash FROM user WHERE username = %s"
        args = (username,)
        
        conn = get_db_connection()
        if not conn: return False

        cursor = conn.cursor()
        cursor.execute(query, args)
        result = cursor.fetchone()

        if result:
            password_hash_from_db = result[0].encode('utf-8')
            password_bytes = password.encode('utf-8')
            
            if bcrypt.checkpw(password_bytes, password_hash_from_db):
                print(f"✅ Login berhasil! Selamat datang, {username}.")
                return True
        
        print("❌ Login gagal: Username atau password salah.")
        return False
    except Error as e:
        print(f"❌ Terjadi error saat login: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def tambah_nasabah(nama, alamat, email, telepon):
    """(CREATE) Menambahkan nasabah baru ke tabel nasabah."""
    query = "INSERT INTO nasabah (nama_lengkap, alamat, email, nomor_telepon) VALUES (%s, %s, %s, %s)"
    args = (nama, alamat, email, telepon)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, args)
            conn.commit()
            print("✅ Nasabah baru berhasil ditambahkan!")
        except Error as e:
            print(f"❌ Gagal menambahkan nasabah: {e}")
        finally:
            cursor.close()
            conn.close()

def lihat_semua_nasabah():
    """(READ) Membaca dan menampilkan semua data dari tabel nasabah."""
    query = "SELECT id, nama_lengkap, email, nomor_telepon FROM nasabah"
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            if not results:
                print("Tidak ada data nasabah.")
                return
            print("\n--- Daftar Nasabah ---")
            for row in results:
                print(f"ID: {row[0]}, Nama: {row[1]}, Email: {row[2]}, Telepon: {row[3]}")
            print("----------------------\n")
        except Error as e:
            print(f"❌ Gagal membaca data: {e}")
        finally:
            cursor.close()
            conn.close()

def update_email_nasabah(nasabah_id, email_baru):
    "update email nasabah berdasarkan ID"
    query = "UPDATE nasabah SET email = %s WHERE id = %s"
    args = (email_baru, nasabah_id)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, args)
            conn.commit()
            if cursor.rowcount > 0:
                print(f"✅ Email untuk nasabah ID {nasabah_id} berhasil diupdate.")
            else:
                print(f"⚠️ Nasabah dengan ID {nasabah_id} tidak ditemukan.")
        except Error as e:
            print(f"❌ Gagal mengupdate nasabah: {e}")
        finally:
            cursor.close()
            conn.close()

def hapus_nasabah(nasabah_id):
    """(DELETE) Menghapus nasabah berdasarkan ID."""
    query = "DELETE FROM nasabah WHERE id = %s"
    args = (nasabah_id,)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, args)
            conn.commit()
            if cursor.rowcount > 0:
                print(f"✅ Nasabah dengan ID {nasabah_id} berhasil dihapus.")
            else:
                print(f"⚠️ Nasabah dengan ID {nasabah_id} tidak ditemukan.")
        except Error as e:
            print(f"❌ Gagal menghapus nasabah: {e}")
        finally:
            cursor.close()
            conn.close()


def buka_rekening(nasabah_id, nomor_rekening, jenis_rekening):
    """(CREATE) Membuat rekening baru untuk nasabah."""
    query = "INSERT INTO rekening (nasabah_id, nomor_rekening, jenis_rekening) VALUES (%s, %s, %s)"
    args = (nasabah_id, nomor_rekening, jenis_rekening)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, args)
            conn.commit()
            print(f"✅ Rekening baru '{nomor_rekening}' berhasil dibuka untuk nasabah_id {nasabah_id}.")
        except Error as e:
            print(f"❌ Gagal membuka rekening: {e}")
        finally:
            cursor.close()
            conn.close()

def lihat_rekening_nasabah(nasabah_id):
    """(READ) Menampilkan semua rekening milik seorang nasabah."""
    query = "SELECT id, nomor_rekening, jenis_rekening, saldo FROM rekening WHERE nasabah_id = %s"
    args = (nasabah_id,)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, args)
            results = cursor.fetchall()
            if not results:
                print(f"Tidak ditemukan rekening untuk nasabah_id {nasabah_id}.")
                return
            print(f"\n--- Daftar Rekening untuk nasabah_id: {nasabah_id} ---")
            for row in results:
                print(f"ID Rek: {row[0]}, No: {row[1]}, Jenis: {row[2]}, Saldo: Rp {row[3]:,.2f}")
            print("------------------------------------------\n")
        except Error as e:
            print(f"❌ Gagal membaca data rekening: {e}")
        finally:
            cursor.close()
            conn.close()


def lihat_saldo(rekening_id):
    """(READ) Melihat saldo spesifik dari satu rekening berdasarkan ID."""
    query = "SELECT saldo, nomor_rekening FROM rekening WHERE id = %s"
    args = (rekening_id,)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, args)
            result = cursor.fetchone() # Ambil satu baris hasil
            
            if result:
                saldo = result[0]
                nomor_rekening = result[1]
                print(f"\n✅ Saldo untuk Rekening No. {nomor_rekening} (ID: {rekening_id}) adalah: Rp {saldo:,.2f}")
            else:
                print(f"⚠️ Rekening dengan ID {rekening_id} tidak ditemukan.")
        except Error as e:
            print(f"❌ Gagal mengambil data saldo: {e}")
        finally:
            cursor.close()
            conn.close()

def tutup_rekening(rekening_id):
    """(DELETE) Menghapus/menutup rekening berdasarkan ID."""
    query = "DELETE FROM rekening WHERE id = %s"
    args = (rekening_id,)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, args)
            conn.commit()
            if cursor.rowcount > 0:
                print(f"✅ Rekening dengan ID {rekening_id} berhasil ditutup.")
            else:
                print(f"⚠️ Rekening dengan ID {rekening_id} tidak ditemukan.")
        except Error as e:
            print(f"❌ Gagal menutup rekening: {e}")
        finally:
            cursor.close()
            conn.close()

def buat_transaksi(rekening_id, tipe_transaksi, jumlah, deskripsi):
    """(CREATE) Membuat catatan transaksi dan MENGUPDATE saldo rekening."""
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()
    try:
        # Langkah 1: Ambil saldo berdasarkan ID rekening (primary key)
        cursor.execute("SELECT saldo FROM rekening WHERE id = %s FOR UPDATE", (rekening_id,))
        result = cursor.fetchone()
        
        if result is None:
            # Pesan error yang benar, mencari berdasarkan ID
            print(f"❌ Rekening dengan ID {rekening_id} tidak ditemukan.")
            return

        saldo_sekarang = result[0]
        
        # Konversi 'jumlah' dari float ke tipe Decimal
        jumlah_decimal = Decimal(str(jumlah))

        # Langkah 2: Hitung saldo baru
        if tipe_transaksi.upper() == 'KREDIT':
            saldo_baru = saldo_sekarang + jumlah_decimal
        elif tipe_transaksi.upper() == 'DEBIT':
            if saldo_sekarang < jumlah_decimal:
                print("❌ Gagal: Saldo tidak mencukupi.")
                return
            saldo_baru = saldo_sekarang - jumlah_decimal
        else:
            print("❌ Tipe transaksi tidak valid (harus 'DEBIT' atau 'KREDIT').")
            return

        # Update saldo di tabel rekening menggunakan ID
        update_rekening_query = "UPDATE rekening SET saldo = %s WHERE id = %s"
        cursor.execute(update_rekening_query, (saldo_baru, rekening_id))

        # Masukkan catatan ke tabel transaksi menggunakan ID
        insert_transaksi_query = "INSERT INTO transaksi (rekening_id, tipe_transaksi, jumlah, deskripsi) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_transaksi_query, (rekening_id, tipe_transaksi.upper(), jumlah_decimal, deskripsi))

        # Jika semua berhasil, commit transaksi
        conn.commit()
        print(f"✅ Transaksi '{deskripsi}' sebesar Rp {jumlah_decimal:,.2f} berhasil.")

    except Error as e:
        conn.rollback()
        print(f"❌ Gagal membuat transaksi: {e}")
    finally:
        cursor.close()
        conn.close()


def lihat_riwayat_transaksi(rekening_id):
    """(READ) Menampilkan riwayat transaksi dari sebuah rekening."""
    query = "SELECT tipe_transaksi, jumlah, deskripsi, waktu_transaksi FROM transaksi WHERE rekening_id = %s ORDER BY waktu_transaksi DESC"
    args = (rekening_id,)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, args)
            results = cursor.fetchall()
            if not results:
                print(f"Tidak ada riwayat transaksi untuk Rekening ID {rekening_id}.")
                return

            print(f"\n--- Riwayat Transaksi Rekening ID: {rekening_id} ---")
            for row in results:
                waktu = row[3].strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{waktu}] {row[0]:<7} | Rp {row[1]:>12,.2f} | {row[2]}")
            print("-------------------------------------------\n")
        except Error as e:
            print(f"❌ Gagal membaca riwayat transaksi: {e}")
        finally:
            cursor.close()
            conn.close()