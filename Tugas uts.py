import mysql.connector
import pandas as pd
from datetime import datetime
import sys

class ZakatManager:
    def __init__(self):
        self.db_config = {
            "host": "localhost",
            "user": "root",
            "password": "",
            "database": "zakat"
        }
        self.connection = None
    
    def create_connection(self):
        """Create a secure database connection with enhanced error handling"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    **self.db_config,
                    autocommit=False,
                    connection_timeout=5,
                    pool_size=5
                )
            return self.connection
        except mysql.connector.Error as err:
            print(f"\n⚠️ Database connection error: {err}")
            print("Please check your database configuration and ensure the server is running.")
            return None
    
    def close_connection(self):
        """Properly close the database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None
    
    def validate_date(self, date_str):
        """Validate date format (YYYY-MM-DD) with additional checks"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            # Check if date is not in the future
            if date_obj.date() > datetime.now().date():
                print("⚠️ Date cannot be in the future.")
                return False
            return True
        except ValueError:
            return False
    
    def get_positive_float(self, prompt, max_value=None):
        """Get a positive float input with enhanced validation"""
        while True:
            try:
                value = float(input(prompt))
                if value <= 0:
                    print("⚠️ Value must be positive. Please try again.")
                    continue
                if max_value is not None and value > max_value:
                    print(f"⚠️ Value cannot exceed {max_value}. Please try again.")
                    continue
                return round(value, 2)  # Round to 2 decimal places for currency
            except ValueError:
                print("⚠️ Invalid input. Please enter a valid number (e.g., 100.50).")
    
    def get_positive_int(self, prompt, max_value=None):
        """Get a positive integer input with enhanced validation"""
        while True:
            try:
                value = int(input(prompt))
                if value <= 0:
                    print("⚠️ Value must be positive. Please try again.")
                    continue
                if max_value is not None and value > max_value:
                    print(f"⚠️ Value cannot exceed {max_value}. Please try again.")
                    continue
                return value
            except ValueError:
                print("⚠️ Invalid input. Please enter a whole number (e.g., 5).")
    
    def get_valid_date(self, prompt, allow_empty=False):
        """Get a valid date input with enhanced validation"""
        while True:
            date_input = input(prompt).strip()
            if allow_empty and not date_input:
                return None
            if self.validate_date(date_input):
                return date_input
            print("⚠️ Invalid date format. Please use YYYY-MM-DD format (e.g., 2023-12-31).")
    
    def get_non_empty_input(self, prompt, field_name):
        """Get non-empty input with validation"""
        while True:
            value = input(prompt).strip()
            if not value:
                print(f"⚠️ {field_name} cannot be empty. Please try again.")
                continue
            return value
    
    def confirm_action(self, prompt):
        """Get confirmation from user with validation"""
        while True:
            response = input(f"{prompt} (y/n): ").strip().lower()
            if response in ('y', 'yes'):
                return True
            elif response in ('n', 'no'):
                return False
            print("⚠️ Please enter 'y' for yes or 'n' for no.")
    
    def display_record(self, record, title="Record Details"):
        """Display record details in a formatted way"""
        print(f"\n--- {title} ---")
        for key, value in record.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print()
    
    def add_zakat(self):
        """Add new zakat record with comprehensive validation"""
        print("\n--- Add New Zakat Record ---")
        
        try:
            nama = self.get_non_empty_input("Enter donor name: ", "Donor name")
            jenis_zakat = self.get_non_empty_input("Enter zakat type: ", "Zakat type")
            jumlah = self.get_positive_float("Enter zakat amount: ")
            tanggal = self.get_valid_date("Enter date (YYYY-MM-DD): ")
            
            conn = self.create_connection()
            if not conn:
                print("⚠️ Cannot proceed without database connection.")
                return
            
            try:
                cursor = conn.cursor()
                query = """
                INSERT INTO zakat_data (nama, jenis_zakat, jumlah, tanggal) 
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (nama, jenis_zakat, jumlah, tanggal))
                conn.commit()
                print("\n✅ Zakat record added successfully!")
                print(f"Donor: {nama} | Amount: {jumlah} | Type: {jenis_zakat}")
            except mysql.connector.Error as err:
                conn.rollback()
                print(f"⚠️ Failed to add zakat record: {err}")
                if err.errno == 1644:  # Custom error code for application-specific errors
                    print("Additional info: The transaction was rejected by business rules.")
            finally:
                if 'cursor' in locals():
                    cursor.close()
        except Exception as e:
            print(f"⚠️ Unexpected error occurred: {e}")
        finally:
            self.close_connection()
    
    def update_zakat(self):
        """Update existing zakat record with comprehensive validation"""
        print("\n--- Update Zakat Record ---")
        
        try:
            id_zakat = self.get_positive_int("Enter ID of zakat record to update: ")
            
            conn = self.create_connection()
            if not conn:
                print("⚠️ Cannot proceed without database connection.")
                return
            
            try:
                # Check if record exists
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM zakat_data WHERE id = %s", (id_zakat,))
                record = cursor.fetchone()
                
                if not record:
                    print(f"⚠️ No zakat record found with ID {id_zakat}")
                    return
                
                self.display_record(record, "Current Record Details")
                
                # Get updated values with defaults
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
                            print("⚠️ Amount must be positive.")
                            continue
                        break
                    except ValueError:
                        print("⚠️ Invalid amount. Please enter a number.")
                
                tanggal = self.get_valid_date(f"Enter new date [{record['tanggal']}]: ") or record['tanggal']
                
                # Confirm changes
                print("\n--- Changes to be Made ---")
                print(f"Name: {record['nama']} → {nama}")
                print(f"Type: {record['jenis_zakat']} → {jenis_zakat}")
                print(f"Amount: {record['jumlah']} → {jumlah}")
                print(f"Date: {record['tanggal']} → {tanggal}")
                
                if not self.confirm_action("\nAre you sure you want to update this record?"):
                    print("Update cancelled.")
                    return
                
                # Update record
                query = """
                UPDATE zakat_data 
                SET nama = %s, jenis_zakat = %s, jumlah = %s, tanggal = %s 
                WHERE id = %s
                """
                cursor.execute(query, (nama, jenis_zakat, jumlah, tanggal, id_zakat))
                conn.commit()
                print("\n✅ Zakat record updated successfully!")
            except mysql.connector.Error as err:
                conn.rollback()
                print(f"⚠️ Failed to update zakat record: {err}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
        except Exception as e:
            print(f"⚠️ Unexpected error occurred: {e}")
        finally:
            self.close_connection()
    
    def delete_zakat(self):
        """Delete zakat record with multiple confirmations"""
        print("\n--- Delete Zakat Record ---")
        
        try:
            id_zakat = self.get_positive_int("Enter ID of zakat record to delete: ")
            
            conn = self.create_connection()
            if not conn:
                print("⚠️ Cannot proceed without database connection.")
                return
            
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Check if record exists
                cursor.execute("SELECT * FROM zakat_data WHERE id = %s", (id_zakat,))
                record = cursor.fetchone()
                
                if not record:
                    print(f"⚠️ No zakat record found with ID {id_zakat}")
                    return
                
                self.display_record(record, "Record to Delete")
                
                # Double confirmation for deletion
                if not self.confirm_action("Are you sure you want to delete this record?"):
                    print("Deletion cancelled.")
                    return
                
                if not self.confirm_action("⚠️ WARNING: This action cannot be undone. Confirm deletion?"):
                    print("Deletion cancelled.")
                    return
                
                # Check for dependent records
                cursor.execute("SELECT COUNT(*) FROM transaksi_zakat WHERE id_zakat = %s", (id_zakat,))
                dependent_count = cursor.fetchone()['COUNT(*)']
                
                if dependent_count > 0:
                    print(f"⚠️ Cannot delete: This record has {dependent_count} associated distribution(s).")
                    if self.confirm_action("Would you like to view these distributions?"):
                        self.view_transaksi_zakat(filter_id=id_zakat)
                    return
                
                # Proceed with deletion
                cursor.execute("DELETE FROM zakat_data WHERE id = %s", (id_zakat,))
                conn.commit()
                print("\n✅ Zakat record deleted successfully!")
            except mysql.connector.Error as err:
                conn.rollback()
                print(f"⚠️ Failed to delete zakat record: {err}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
        except Exception as e:
            print(f"⚠️ Unexpected error occurred: {e}")
        finally:
            self.close_connection()
    
    def add_beras(self):
        """Add new rice type with comprehensive validation"""
        print("\n--- Add New Rice Type ---")
        
        try:
            nama_beras = self.get_non_empty_input("Enter rice name: ", "Rice name")
            harga_per_kg = self.get_positive_float("Enter price per kg: ", max_value=1000)  # Assuming reasonable max price
            
            conn = self.create_connection()
            if not conn:
                print("⚠️ Cannot proceed without database connection.")
                return
            
            try:
                # Check for duplicate rice name
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM master_beras WHERE nama_beras = %s", (nama_beras,))
                if cursor.fetchone():
                    print(f"⚠️ Rice type '{nama_beras}' already exists.")
                    if not self.confirm_action("Do you want to update the existing record instead?"):
                        return
                    # If yes, proceed to update
                    new_price = self.get_positive_float(f"Enter new price for {nama_beras}: ", max_value=1000)
                    cursor.execute("UPDATE master_beras SET harga_per_kg = %s WHERE nama_beras = %s", 
                                 (new_price, nama_beras))
                    conn.commit()
                    print("\n✅ Rice type updated successfully!")
                    return
                
                # Add new rice type
                query = "INSERT INTO master_beras (nama_beras, harga_per_kg) VALUES (%s, %s)"
                cursor.execute(query, (nama_beras, harga_per_kg))
                conn.commit()
                print("\n✅ Rice type added successfully!")
                print(f"Name: {nama_beras} | Price: {harga_per_kg}/kg")
            except mysql.connector.Error as err:
                conn.rollback()
                print(f"⚠️ Failed to add rice type: {err}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
        except Exception as e:
            print(f"⚠️ Unexpected error occurred: {e}")
        finally:
            self.close_connection()
    
    def view_master_beras(self):
        """View all rice types with enhanced formatting and options"""
        print("\n--- Rice Master Data ---")
        
        try:
            conn = self.create_connection()
            if not conn:
                print("⚠️ Cannot proceed without database connection.")
                return
            
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM master_beras ORDER BY nama_beras")
                results = cursor.fetchall()
                
                if not results:
                    print("No rice types found in database.")
                    return
                
                # Display table with better formatting
                print("\n" + "-" * 50)
                print(f"{'ID':<5}{'Rice Name':<25}{'Price per Kg':>15}")
                print("-" * 50)
                for row in results:
                    print(f"{row['id']:<5}{row['nama_beras'][:24]:<25}{row['harga_per_kg']:>15.2f}")
                print("-" * 50)
                print(f"Total rice types: {len(results)}")
                
                # Additional options
                if self.confirm_action("\nWould you like to export this data to CSV?"):
                    self.export_data_to_csv(results, "rice_types.csv", ["id", "nama_beras", "harga_per_kg"])
            except mysql.connector.Error as err:
                print(f"⚠️ Failed to retrieve rice data: {err}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
        except Exception as e:
            print(f"⚠️ Unexpected error occurred: {e}")
        finally:
            self.close_connection()
    
    def add_transaksi_zakat(self):
        """Add new zakat distribution transaction with comprehensive validation"""
        print("\n--- Add Zakat Distribution ---")
        
        try:
            # Get and validate zakat record ID
            id_zakat = self.get_positive_int("Enter zakat record ID: ")
            
            conn = self.create_connection()
            if not conn:
                print("⚠️ Cannot proceed without database connection.")
                return
            
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Verify zakat record exists
                cursor.execute("SELECT id, nama, jumlah FROM zakat_data WHERE id = %s", (id_zakat,))
                zakat_record = cursor.fetchone()
                
                if not zakat_record:
                    print(f"⚠️ No zakat record found with ID {id_zakat}")
                    if self.confirm_action("Would you like to view available zakat records?"):
                        self.view_zakat_records()
                    return
                
                print(f"\nZakat Record Found:")
                print(f"Donor: {zakat_record['nama']} | Amount: {zakat_record['jumlah']}")
                
                # Get and validate rice type ID
                self.view_master_beras()
                id_beras = self.get_positive_int("\nEnter rice type ID: ")
                
                # Verify rice type exists
                cursor.execute("SELECT id, nama_beras, harga_per_kg FROM master_beras WHERE id = %s", (id_beras,))
                beras_record = cursor.fetchone()
                
                if not beras_record:
                    print(f"⚠️ No rice type found with ID {id_beras}")
                    return
                
                print(f"\nRice Type Selected: {beras_record['nama_beras']}")
                print(f"Price per kg: {beras_record['harga_per_kg']}")
                
                # Get rice amount with validation
                jumlah_beras = self.get_positive_float("Enter rice amount (kg): ")
                
                # Calculate total price
                total_harga = round(beras_record['harga_per_kg'] * jumlah_beras, 2)
                print(f"Total Price: {total_harga}")
                
                # Get distribution date
                tanggal = self.get_valid_date("Enter distribution date (YYYY-MM-DD): ")
                
                # Confirm transaction
                print("\n--- Transaction Summary ---")
                print(f"Donor: {zakat_record['nama']}")
                print(f"Rice: {beras_record['nama_beras']} ({jumlah_beras}kg)")
                print(f"Total: {total_harga}")
                print(f"Date: {tanggal}")
                
                if not self.confirm_action("\nConfirm this distribution?"):
                    print("Transaction cancelled.")
                    return
                
                # Insert transaction
                query = """
                INSERT INTO transaksi_zakat 
                (id_zakat, id_beras, jumlah_beras, total_harga, tanggal) 
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (id_zakat, id_beras, jumlah_beras, total_harga, tanggal))
                conn.commit()
                print("\n✅ Zakat distribution recorded successfully!")
            except mysql.connector.Error as err:
                conn.rollback()
                print(f"⚠️ Failed to add distribution record: {err}")
                if err.errno == 1644:  # Example custom error code
                    print("Additional info: The transaction violates business rules.")
            finally:
                if 'cursor' in locals():
                    cursor.close()
        except Exception as e:
            print(f"⚠️ Unexpected error occurred: {e}")
        finally:
            self.close_connection()
    
    def view_transaksi_zakat(self, filter_id=None):
        """View all zakat distribution transactions with filtering options"""
        print("\n--- Zakat Distribution Records ---")
        
        try:
            conn = self.create_connection()
            if not conn:
                print("⚠️ Cannot proceed without database connection.")
                return
            
            try:
                cursor = conn.cursor(dictionary=True)
                
                # Build query based on filter
                base_query = """
                SELECT tz.id, z.id as zakat_id, z.nama, z.jenis_zakat, 
                       m.id as beras_id, m.nama_beras, 
                       tz.jumlah_beras, tz.total_harga, tz.tanggal
                FROM transaksi_zakat tz
                JOIN zakat_data z ON tz.id_zakat = z.id
                JOIN master_beras m ON tz.id_beras = m.id
                """
                
                if filter_id:
                    base_query += " WHERE z.id = %s"
                    params = (filter_id,)
                else:
                    params = None
                
                base_query += " ORDER BY tz.tanggal DESC, tz.id DESC"
                
                cursor.execute(base_query, params)
                results = cursor.fetchall()
                
                if not results:
                    print("No distribution records found.")
                    return
                
                # Display table with better formatting
                print("\n" + "-" * 120)
                print(f"{'ID':<5}{'Zakat ID':<10}{'Donor':<20}{'Type':<15}{'Rice':<20}{'Amount':<10}{'Total':<15}{'Date':<15}")
                print("-" * 120)
                for row in results:
                    print(f"{row['id']:<5}{row['zakat_id']:<10}{row['nama'][:18]:<20}"
                          f"{row['jenis_zakat'][:14]:<15}{row['nama_beras'][:19]:<20}"
                          f"{row['jumlah_beras']:>6.2f}kg {row['total_harga']:>12.2f} "
                          f"{row['tanggal']}")
                print("-" * 120)
                print(f"Total distributions: {len(results)}")
                
                # Additional options
                if not filter_id and self.confirm_action("\nWould you like to filter by zakat record ID?"):
                    filter_id = self.get_positive_int("Enter zakat record ID to filter: ")
                    self.view_transaksi_zakat(filter_id=filter_id)
                
                if self.confirm_action("\nWould you like to export this data to CSV?"):
                    self.export_data_to_csv(
                        results, 
                        "zakat_distributions.csv", 
                        ["id", "zakat_id", "nama", "jenis_zakat", "nama_beras", "jumlah_beras", "total_harga", "tanggal"]
                    )
            except mysql.connector.Error as err:
                print(f"⚠️ Failed to retrieve distribution records: {err}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
        except Exception as e:
            print(f"⚠️ Unexpected error occurred: {e}")
        finally:
            self.close_connection()
    
    def view_zakat_records(self):
        """View all zakat records with enhanced formatting"""
        print("\n--- Zakat Records ---")
        
        try:
            conn = self.create_connection()
            if not conn:
                print("⚠️ Cannot proceed without database connection.")
                return
            
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT z.*, COUNT(t.id) as distribution_count, 
                           COALESCE(SUM(t.total_harga), 0) as total_distributed
                    FROM zakat_data z
                    LEFT JOIN transaksi_zakat t ON z.id = t.id_zakat
                    GROUP BY z.id
                    ORDER BY z.tanggal DESC
                """)
                results = cursor.fetchall()
                
                if not results:
                    print("No zakat records found.")
                    return
                
                # Display table with better formatting
                print("\n" + "-" * 100)
                print(f"{'ID':<5}{'Donor':<20}{'Type':<15}{'Amount':<15}{'Date':<15}{'Distributions':<15}{'Total Distributed':<15}")
                print("-" * 100)
                for row in results:
                    print(f"{row['id']:<5}{row['nama'][:18]:<20}{row['jenis_zakat'][:14]:<15}"
                          f"{row['jumlah']:>12.2f} {row['tanggal']} "
                          f"{row['distribution_count']:>12} {row['total_distributed']:>15.2f}")
                print("-" * 100)
                print(f"Total records: {len(results)}")
                
                # Additional options
                if self.confirm_action("\nWould you like to view distributions for a specific record?"):
                    record_id = self.get_positive_int("Enter zakat record ID: ")
                    self.view_transaksi_zakat(filter_id=record_id)
                
                if self.confirm_action("\nWould you like to export this data to CSV?"):
                    self.export_data_to_csv(
                        results, 
                        "zakat_records.csv", 
                        ["id", "nama", "jenis_zakat", "jumlah", "tanggal", "distribution_count", "total_distributed"]
                    )
            except mysql.connector.Error as err:
                print(f"⚠️ Failed to retrieve zakat records: {err}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
        except Exception as e:
            print(f"⚠️ Unexpected error occurred: {e}")
        finally:
            self.close_connection()
    
    def export_data_to_csv(self, data, filename, fields):
        """Export data to CSV file with error handling"""
        try:
            df = pd.DataFrame(data, columns=fields)
            df.to_csv(filename, index=False)
            print(f"\n✅ Data successfully exported to '{filename}'")
        except Exception as e:
            print(f"⚠️ Failed to export data: {e}")
            print("Please ensure the file is not open in another program and you have write permissions.")
    
    def export_to_excel(self):
        """Export zakat data to Excel file with comprehensive error handling"""
        print("\n--- Export Data to Excel ---")
        
        try:
            conn = self.create_connection()
            if not conn:
                print("⚠️ Cannot proceed without database connection.")
                return
            
            try:
                # Get zakat data with distribution summary
                zakat_query = """
                SELECT z.*, COUNT(t.id) as distribution_count, 
                       COALESCE(SUM(t.total_harga), 0) as total_distributed
                FROM zakat_data z
                LEFT JOIN transaksi_zakat t ON z.id = t.id_zakat
                GROUP BY z.id
                ORDER BY z.tanggal DESC
                """
                zakat_data = pd.read_sql(zakat_query, conn)
                
                # Get distribution data
                transaksi_query = """
                SELECT tz.id, z.id as zakat_id, z.nama, z.jenis_zakat, 
                       m.nama_beras, tz.jumlah_beras, tz.total_harga, tz.tanggal
                FROM transaksi_zakat tz
                JOIN zakat_data z ON tz.id_zakat = z.id
                JOIN master_beras m ON tz.id_beras = m.id
                ORDER BY tz.tanggal DESC
                """
                transaksi_data = pd.read_sql(transaksi_query, conn)
                
                # Get rice types
                beras_data = pd.read_sql("SELECT * FROM master_beras ORDER BY nama_beras", conn)
                
                # Create Excel writer
                filename = f"zakat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
                try:
                    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                        zakat_data.to_excel(writer, sheet_name="Zakat Records", index=False)
                        transaksi_data.to_excel(writer, sheet_name="Distributions", index=False)
                        beras_data.to_excel(writer, sheet_name="Rice Types", index=False)
                    
                    print(f"\n✅ Data successfully exported to '{filename}'")
                    print("Sheets included:")
                    print("- Zakat Records: All zakat donations with distribution summary")
                    print("- Distributions: Detailed distribution records")
                    print("- Rice Types: Master list of rice types and prices")
                except PermissionError:
                    print("⚠️ Failed to create Excel file. Please ensure you have write permissions and the file is not open.")
                except Exception as e:
                    print(f"⚠️ Failed to create Excel file: {e}")
            except mysql.connector.Error as err:
                print(f"⚠️ Failed to retrieve data for export: {err}")
            except Exception as e:
                print(f"⚠️ Unexpected error during export: {e}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
        except Exception as e:
            print(f"⚠️ Unexpected error occurred: {e}")
        finally:
            self.close_connection()
    
    def backup_database(self):
        """Create a database backup with error handling"""
        print("\n--- Database Backup ---")
        if not self.confirm_action("This will create a backup of all data. Continue?"):
            return
        
        try:
            conn = self.create_connection()
            if not conn:
                print("⚠️ Cannot proceed without database connection.")
                return
            
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"zakat_backup_{timestamp}.sql"
                
                # Get all tables data
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SHOW TABLES")
                tables = [table['Tables_in_zakat'] for table in cursor.fetchall()]
                
                with open(filename, 'w') as f:
                    for table in tables:
                        # Write table structure
                        cursor.execute(f"SHOW CREATE TABLE {table}")
                        create_table = cursor.fetchone()['Create Table']
                        f.write(f"\n-- Structure for table {table}\n")
                        f.write(f"{create_table};\n\n")
                        
                        # Write table data
                        cursor.execute(f"SELECT * FROM {table}")
                        rows = cursor.fetchall()
                        if rows:
                            f.write(f"-- Data for table {table}\n")
                            columns = rows[0].keys()
                            for row in rows:
                                values = []
                                for col in columns:
                                    val = row[col]
                                    if val is None:
                                        values.append("NULL")
                                    elif isinstance(val, (int, float)):
                                        values.append(str(val))
                                    else:
                                        values.append(f"'{str(val).replace("'", "''")}'")
                                f.write(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)});\n")
                            f.write("\n")
                
                print(f"\n✅ Database backup created successfully: {filename}")
                print(f"Backup includes {len(tables)} tables: {', '.join(tables)}")
            except mysql.connector.Error as err:
                print(f"⚠️ Failed to create backup: {err}")
            except IOError as e:
                print(f"⚠️ File error during backup: {e}")
            except Exception as e:
                print(f"⚠️ Unexpected error during backup: {e}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
        except Exception as e:
            print(f"⚠️ Unexpected error occurred: {e}")
        finally:
            self.close_connection()
    
    def display_help(self):
        """Display help information for users"""
        print("\n--- Zakat Management System Help ---")
        print("This system helps manage zakat donations and distributions.")
        print("\nMain Features:")
        print("1. Add Zakat Record - Record new zakat donations")
        print("2. Update Zakat Record - Modify existing donation records")
        print("3. Delete Zakat Record - Remove donation records (with caution)")
        print("4. View Rice Types - See available rice types and prices")
        print("5. Add Rice Type - Add new rice types for distribution")
        print("6. Add Distribution Record - Record zakat distributions to recipients")
        print("7. View Distribution Records - See all distribution history")
        print("8. Export Data - Export all data to Excel for reporting")
        print("9. Database Backup - Create a complete database backup")
        print("10. Help - Display this help information")
        print("11. Exit - Quit the application")
        
        print("\nTips:")
        print("- Required fields are marked and cannot be left empty")
        print("- Dates must be in YYYY-MM-DD format")
        print("- Amounts must be positive numbers")
        print("- Always confirm important actions like deletions")
        
        input("\nPress Enter to return to the main menu...")
    
    def main_menu(self):
        """Display main menu with enhanced navigation and error handling"""
        while True:
            try:
                print("\n" + "=" * 40)
                print("=== ZAKAT MANAGEMENT SYSTEM ===".center(40))
                print("=" * 40)
                print("1. Add Zakat Record")
                print("2. Update Zakat Record")
                print("3. Delete Zakat Record")
                print("4. View Zakat Records")
                print("5. View Rice Types")
                print("6. Add Rice Type")
                print("7. Add Distribution Record")
                print("8. View Distribution Records")
                print("9. Export Data to Excel")
                print("10. Database Backup")
                print("11. Help")
                print("12. Exit")
                
                choice = input("\nEnter your choice (1-12): ").strip()
                
                if choice == "1":
                    self.add_zakat()
                elif choice == "2":
                    self.update_zakat()
                elif choice == "3":
                    self.delete_zakat()
                elif choice == "4":
                    self.view_zakat_records()
                elif choice == "5":
                    self.view_master_beras()
                elif choice == "6":
                    self.add_beras()
                elif choice == "7":
                    self.add_transaksi_zakat()
                elif choice == "8":
                    self.view_transaksi_zakat()
                elif choice == "9":
                    self.export_to_excel()
                elif choice == "10":
                    self.backup_database()
                elif choice == "11":
                    self.display_help()
                elif choice == "12":
                    if self.confirm_action("Are you sure you want to exit?"):
                        print("\nThank you for using Zakat Management System. Goodbye!")
                        self.close_connection()
                        sys.exit(0)
                else:
                    print("⚠️ Invalid choice. Please enter a number between 1-12.")
                
                # Pause before returning to menu
                if choice not in ("11", "12"):
                    input("\nPress Enter to return to the main menu...")
            except KeyboardInterrupt:
                print("\n\n⚠️ Operation cancelled by user.")
                if self.confirm_action("\nDo you want to exit the program?"):
                    print("\nThank you for using Zakat Management System. Goodbye!")
                    self.close_connection()
                    sys.exit(0)
            except Exception as e:
                print(f"\n⚠️ An unexpected error occurred: {e}")
                print("The application will try to recover...")
                self.close_connection()
                input("Press Enter to continue...")

# Run the application
if __name__ == "__main__":
    try:
        manager = ZakatManager()
        manager.main_menu()
    except KeyboardInterrupt:
        print("\n\nApplication terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n⚠️ Critical error: {e}")
        print("The application must close.")
        sys.exit(1)