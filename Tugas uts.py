import mysql.connector
import pandas as pd
from datetime import datetime

class ZakatManager:
    def __init__(self):
        self.db_config = {
            "host": "localhost",
            "user": "root",
            "password": "",
            "database": "zakat"
        }
    
    def create_connection(self):
        """Create a secure database connection with error handling"""
        try:
            conn = mysql.connector.connect(**self.db_config)
            return conn
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            return None
    
    def validate_date(self, date_str):
        """Validate date format (YYYY-MM-DD)"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def get_positive_float(self, prompt):
        """Get a positive float input with validation"""
        while True:
            try:
                value = float(input(prompt))
                if value <= 0:
                    print("Value must be positive. Please try again.")
                    continue
                return value
            except ValueError:
                print("Invalid input. Please enter a valid number.")
    
    def get_positive_int(self, prompt):
        """Get a positive integer input with validation"""
        while True:
            try:
                value = int(input(prompt))
                if value <= 0:
                    print("Value must be positive. Please try again.")
                    continue
                return value
            except ValueError:
                print("Invalid input. Please enter a whole number.")
    
    def get_valid_date(self, prompt):
        """Get a valid date input"""
        while True:
            date_input = input(prompt)
            if self.validate_date(date_input):
                return date_input
            print("Invalid date format. Please use YYYY-MM-DD format.")
    
    def add_zakat(self):
        """Add new zakat record with input validation"""
        print("\n--- Add New Zakat Record ---")
        nama = input("Enter donor name: ").strip()
        while not nama:
            print("Name cannot be empty.")
            nama = input("Enter donor name: ").strip()
        
        jenis_zakat = input("Enter zakat type: ").strip()
        while not jenis_zakat:
            print("Zakat type cannot be empty.")
            jenis_zakat = input("Enter zakat type: ").strip()
        
        jumlah = self.get_positive_float("Enter zakat amount: ")
        tanggal = self.get_valid_date("Enter date (YYYY-MM-DD): ")
        
        conn = self.create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = "INSERT INTO zakat_data (nama, jenis_zakat, jumlah, tanggal) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (nama, jenis_zakat, jumlah, tanggal))
                conn.commit()
                print("Zakat record added successfully!")
            except mysql.connector.Error as err:
                print(f"Failed to add zakat record: {err}")
            finally:
                cursor.close()
                conn.close()
    
    def update_zakat(self):
        """Update existing zakat record with validation"""
        print("\n--- Update Zakat Record ---")
        try:
            id_zakat = int(input("Enter ID of zakat record to update: "))
        except ValueError:
            print("Invalid ID. Please enter a number.")
            return
        
        conn = self.create_connection()
        if conn:
            try:
                # Check if record exists
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM zakat_data WHERE id = %s", (id_zakat,))
                record = cursor.fetchone()
                
                if not record:
                    print(f"No zakat record found with ID {id_zakat}")
                    return
                
                print(f"\nCurrent Record: {record}")
                
                # Get updated values
                nama = input(f"Enter new name [{record['nama']}]: ").strip() or record['nama']
                jenis_zakat = input(f"Enter new zakat type [{record['jenis_zakat']}]: ").strip() or record['jenis_zakat']
                
                while True:
                    jumlah_input = input(f"Enter new amount [{record['jumlah']}]: ").strip()
                    if not jumlah_input:
                        jumlah = record['jumlah']
                        break
                    try:
                        jumlah = float(jumlah_input)
                        if jumlah <= 0:
                            print("Amount must be positive.")
                            continue
                        break
                    except ValueError:
                        print("Invalid amount. Please enter a number.")
                
                tanggal = self.get_valid_date(f"Enter new date [{record['tanggal']}]: ") or record['tanggal']
                
                # Update record
                query = """UPDATE zakat_data 
                           SET nama = %s, jenis_zakat = %s, jumlah = %s, tanggal = %s 
                           WHERE id = %s"""
                cursor.execute(query, (nama, jenis_zakat, jumlah, tanggal, id_zakat))
                conn.commit()
                print("Zakat record updated successfully!")
            except mysql.connector.Error as err:
                print(f"Failed to update zakat record: {err}")
            finally:
                cursor.close()
                conn.close()
    
    def delete_zakat(self):
        """Delete zakat record with confirmation"""
        print("\n--- Delete Zakat Record ---")
        try:
            id_zakat = int(input("Enter ID of zakat record to delete: "))
        except ValueError:
            print("Invalid ID. Please enter a number.")
            return
        
        conn = self.create_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Check if record exists
                cursor.execute("SELECT * FROM zakat_data WHERE id = %s", (id_zakat,))
                record = cursor.fetchone()
                
                if not record:
                    print(f"No zakat record found with ID {id_zakat}")
                    return
                
                print(f"\nRecord to delete: {record}")
                confirm = input("Are you sure you want to delete this record? (y/n): ").lower()
                
                if confirm == 'y':
                    cursor.execute("DELETE FROM zakat_data WHERE id = %s", (id_zakat,))
                    conn.commit()
                    print("Zakat record deleted successfully!")
                else:
                    print("Deletion cancelled.")
            except mysql.connector.Error as err:
                print(f"Failed to delete zakat record: {err}")
            finally:
                cursor.close()
                conn.close()
    
    def add_beras(self):
        """Add new rice type with validation"""
        print("\n--- Add New Rice Type ---")
        nama_beras = input("Enter rice name: ").strip()
        while not nama_beras:
            print("Rice name cannot be empty.")
            nama_beras = input("Enter rice name: ").strip()
        
        harga_per_kg = self.get_positive_float("Enter price per kg: ")
        
        conn = self.create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = "INSERT INTO master_beras (nama_beras, harga_per_kg) VALUES (%s, %s)"
                cursor.execute(query, (nama_beras, harga_per_kg))
                conn.commit()
                print("Rice type added successfully!")
            except mysql.connector.Error as err:
                print(f"Failed to add rice type: {err}")
            finally:
                cursor.close()
                conn.close()
    
    def view_master_beras(self):
        """View all rice types with proper formatting"""
        print("\n--- Rice Master Data ---")
        conn = self.create_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM master_beras ORDER BY id")
                results = cursor.fetchall()
                
                if not results:
                    print("No rice types found in database.")
                    return
                
                print("\nID  | Rice Name          | Price per Kg")
                print("-" * 40)
                for row in results:
                    print(f"{row['id']:<3} | {row['nama_beras'][:18]:<18} | {row['harga_per_kg']:>10.2f}")
                print(f"\nTotal rice types: {len(results)}")
            except mysql.connector.Error as err:
                print(f"Failed to retrieve rice data: {err}")
            finally:
                cursor.close()
                conn.close()
    
    def add_transaksi_zakat(self):
        """Add new zakat distribution transaction with validation"""
        print("\n--- Add Zakat Distribution ---")
        
        # Get zakat record ID
        try:
            id_zakat = int(input("Enter zakat record ID: "))
        except ValueError:
            print("Invalid ID. Please enter a number.")
            return
        
        # Get rice type ID
        try:
            id_beras = int(input("Enter rice type ID: "))
        except ValueError:
            print("Invalid ID. Please enter a number.")
            return
        
        jumlah_beras = self.get_positive_float("Enter rice amount (kg): ")
        tanggal = self.get_valid_date("Enter distribution date (YYYY-MM-DD): ")
        
        conn = self.create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Verify zakat record exists
                cursor.execute("SELECT id FROM zakat_data WHERE id = %s", (id_zakat,))
                if not cursor.fetchone():
                    print(f"No zakat record found with ID {id_zakat}")
                    return
                
                # Verify rice type exists and get price
                cursor.execute("SELECT harga_per_kg FROM master_beras WHERE id = %s", (id_beras,))
                result = cursor.fetchone()
                if not result:
                    print(f"No rice type found with ID {id_beras}")
                    return
                
                harga_per_kg = result[0]
                total_harga = harga_per_kg * jumlah_beras
                
                # Insert transaction
                query = """INSERT INTO transaksi_zakat 
                          (id_zakat, id_beras, jumlah_beras, total_harga, tanggal) 
                          VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(query, (id_zakat, id_beras, jumlah_beras, total_harga, tanggal))
                conn.commit()
                print("Zakat distribution recorded successfully!")
            except mysql.connector.Error as err:
                print(f"Failed to add distribution record: {err}")
            finally:
                cursor.close()
                conn.close()
    
    def view_transaksi_zakat(self):
        """View all zakat distribution transactions"""
        print("\n--- Zakat Distribution Records ---")
        conn = self.create_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                query = """SELECT tz.id, z.nama, z.jenis_zakat, m.nama_beras, 
                          tz.jumlah_beras, tz.total_harga, tz.tanggal
                          FROM transaksi_zakat tz
                          JOIN zakat_data z ON tz.id_zakat = z.id
                          JOIN master_beras m ON tz.id_beras = m.id
                          ORDER BY tz.tanggal DESC"""
                cursor.execute(query)
                results = cursor.fetchall()
                
                if not results:
                    print("No distribution records found.")
                    return
                
                print("\nID  | Donor Name       | Zakat Type   | Rice Type       | Amount  | Total    | Date")
                print("-" * 90)
                for row in results:
                    print(f"{row['id']:<3} | {row['nama'][:15]:<15} | {row['jenis_zakat'][:12]:<12} | "
                          f"{row['nama_beras'][:15]:<15} | {row['jumlah_beras']:>6.2f}kg | "
                          f"{row['total_harga']:>8.2f} | {row['tanggal']}")
                print(f"\nTotal distributions: {len(results)}")
            except mysql.connector.Error as err:
                print(f"Failed to retrieve distribution records: {err}")
            finally:
                cursor.close()
                conn.close()
    
    def export_to_excel(self):
        """Export zakat data to Excel file"""
        print("\n--- Export Data to Excel ---")
        conn = self.create_connection()
        if conn:
            try:
                # Get zakat data
                zakat_data = pd.read_sql("SELECT * FROM zakat_data", conn)
                
                # Get distribution data
                transaksi_data = pd.read_sql("""SELECT tz.id, z.nama, z.jenis_zakat, m.nama_beras, 
                                              tz.jumlah_beras, tz.total_harga, tz.tanggal
                                              FROM transaksi_zakat tz
                                              JOIN zakat_data z ON tz.id_zakat = z.id
                                              JOIN master_beras m ON tz.id_beras = m.id""", conn)
                
                # Create Excel writer
                with pd.ExcelWriter("zakat_report.xlsx") as writer:
                    zakat_data.to_excel(writer, sheet_name="Zakat Records", index=False)
                    transaksi_data.to_excel(writer, sheet_name="Distributions", index=False)
                
                print("Data successfully exported to 'zakat_report.xlsx'")
            except Exception as e:
                print(f"Failed to export data: {e}")
            finally:
                conn.close()
    
    def main_menu(self):
        """Display main menu and handle user input"""
        while True:
            print("\n=== ZAKAT MANAGEMENT SYSTEM ===")
            print("1. Add Zakat Record")
            print("2. Update Zakat Record")
            print("3. Delete Zakat Record")
            print("4. View Rice Types")
            print("5. Add Rice Type")
            print("6. Add Distribution Record")
            print("7. View Distribution Records")
            print("8. Export Data to Excel")
            print("9. Exit")
            
            choice = input("Enter your choice (1-9): ").strip()
            
            if choice == "1":
                self.add_zakat()
            elif choice == "2":
                self.update_zakat()
            elif choice == "3":
                self.delete_zakat()
            elif choice == "4":
                self.view_master_beras()
            elif choice == "5":
                self.add_beras()
            elif choice == "6":
                self.add_transaksi_zakat()
            elif choice == "7":
                self.view_transaksi_zakat()
            elif choice == "8":
                self.export_to_excel()
            elif choice == "9":
                print("Exiting program. Thank you!")
                break
            else:
                print("Invalid choice. Please enter a number between 1-9.")

# Run the application
if __name__ == "__main__":
    manager = ZakatManager()
    manager.main_menu()