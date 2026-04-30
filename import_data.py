import os
import glob
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

load_dotenv()
CONN_STR = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(CONN_STR)

def run_etl():
    dataset_path = "./dataset" 
    files = sorted(glob.glob(os.path.join(dataset_path, "*.xls")) + glob.glob(os.path.join(dataset_path, "*.ods")))

    print(f"🚀 Found {len(files)} state files. Starting MINI-BATCH import...")

    state_cache = {} 
    dist_cache = {}
    subdist_cache = {}

    for file_path in files:
        file_name = os.path.basename(file_path)
        print(f"📖 Reading: {file_name}")
        
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            df = pd.read_excel(file_path)
            df.columns = [c.strip() for c in df.columns]
            village_batch = []

            for _, row in df.iterrows():
                st_code = str(row['MDDS STC'])
                if st_code not in state_cache:
                    cur.execute("INSERT INTO states (mdds_code, name) VALUES (%s, %s) ON CONFLICT (mdds_code) DO UPDATE SET name=EXCLUDED.name RETURNING id", (st_code, row['STATE NAME']))
                    state_cache[st_code] = cur.fetchone()[0]
                s_id = state_cache[st_code]
                
                dt_code = str(row['MDDS DTC'])
                if dt_code not in dist_cache:
                    cur.execute("INSERT INTO districts (state_id, mdds_code, name) VALUES (%s, %s, %s) ON CONFLICT (mdds_code) DO UPDATE SET name=EXCLUDED.name RETURNING id", (s_id, dt_code, row['DISTRICT NAME']))
                    dist_cache[dt_code] = cur.fetchone()[0]
                d_id = dist_cache[dt_code]

                sd_code = str(row['MDDS Sub_DT'])
                if sd_code not in subdist_cache:
                    cur.execute("INSERT INTO sub_districts (district_id, mdds_code, name) VALUES (%s, %s, %s) ON CONFLICT (mdds_code) DO UPDATE SET name=EXCLUDED.name RETURNING id", (d_id, sd_code, row['SUB-DISTRICT NAME']))
                    subdist_cache[sd_code] = cur.fetchone()[0]
                sd_id = subdist_cache[sd_code]

                village_batch.append((sd_id, str(row['MDDS PLCN']), row['Area Name']))

            # 🚀 MINI-BATCHING LOGIC FOR STABILITY
            if village_batch:
                chunk_size = 1000  # Smaller chunks to prevent SSL timeout
                print(f"   Uploading {len(village_batch)} villages in chunks...")
                for i in range(0, len(village_batch), chunk_size):
                    chunk = village_batch[i:i + chunk_size]
                    execute_values(cur, "INSERT INTO villages (sub_district_id, mdds_code, name) VALUES %s ON CONFLICT (mdds_code) DO NOTHING", chunk)
                    # Optional: Print progress for huge files like UP
                    if i % 10000 == 0 and i > 0:
                        print(f"   Progress: {i} villages uploaded...")
            
            conn.commit()
            print(f"✅ Finished {file_name} (Cache Size: {len(subdist_cache)} Sub-Districts)")

        except Exception as e:
            print(f"❌ Error processing {file_name}: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    print("✨ ALL STATES IMPORTED SUCCESSFULLY!")
    dataset_path = "./dataset" 
    files = sorted(glob.glob(os.path.join(dataset_path, "*.xls")) + glob.glob(os.path.join(dataset_path, "*.ods")))

    print(f"🚀 Found {len(files)} state files. Starting TURBO import...")

    # Global caches to remember IDs across different files
    state_cache = {} 
    dist_cache = {}
    subdist_cache = {}

    for file_path in files:
        file_name = os.path.basename(file_path)
        print(f"📖 Reading: {file_name}")
        
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            df = pd.read_excel(file_path)
            df.columns = [c.strip() for c in df.columns]
            village_batch = []

            for _, row in df.iterrows():
                # 1. Cache-Aware State Insert
                st_code = str(row['MDDS STC'])
                if st_code not in state_cache:
                    cur.execute("INSERT INTO states (mdds_code, name) VALUES (%s, %s) ON CONFLICT (mdds_code) DO UPDATE SET name=EXCLUDED.name RETURNING id", (st_code, row['STATE NAME']))
                    state_cache[st_code] = cur.fetchone()[0]
                s_id = state_cache[st_code]
                
                # 2. Cache-Aware District Insert
                dt_code = str(row['MDDS DTC'])
                if dt_code not in dist_cache:
                    cur.execute("INSERT INTO districts (state_id, mdds_code, name) VALUES (%s, %s, %s) ON CONFLICT (mdds_code) DO UPDATE SET name=EXCLUDED.name RETURNING id", (s_id, dt_code, row['DISTRICT NAME']))
                    dist_cache[dt_code] = cur.fetchone()[0]
                d_id = dist_cache[dt_code]

                # 3. Cache-Aware Sub-District Insert
                sd_code = str(row['MDDS Sub_DT'])
                if sd_code not in subdist_cache:
                    cur.execute("INSERT INTO sub_districts (district_id, mdds_code, name) VALUES (%s, %s, %s) ON CONFLICT (mdds_code) DO UPDATE SET name=EXCLUDED.name RETURNING id", (d_id, sd_code, row['SUB-DISTRICT NAME']))
                    subdist_cache[sd_code] = cur.fetchone()[0]
                sd_id = subdist_cache[sd_code]

                # 4. Village (Prepare for Batch)
                village_batch.append((sd_id, str(row['MDDS PLCN']), row['Area Name']))

            # 🚀 MASSIVE SPEEDUP: Insert all villages for this state in one go
            if village_batch:
                execute_values(cur, "INSERT INTO villages (sub_district_id, mdds_code, name) VALUES %s ON CONFLICT DO NOTHING", village_batch)
            
            conn.commit()
            print(f"✅ Finished {file_name} (Cache Size: {len(subdist_cache)} Sub-Districts)")

        except Exception as e:
            print(f"❌ Error processing {file_name}: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    print("✨ ALL STATES IMPORTED SUCCESSFULLY!")
    dataset_path = "./dataset" 
    files = sorted(glob.glob(os.path.join(dataset_path, "*.xls")) + glob.glob(os.path.join(dataset_path, "*.ods")))

    print(f"🚀 Found {len(files)} state files. Starting robust import...")

    for file_path in files:
        file_name = os.path.basename(file_path)
        print(f"📖 Reading: {file_name}")
        
        # Open a fresh connection for EVERY state file
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            df = pd.read_excel(file_path)
            df.columns = [c.strip() for c in df.columns]
            village_batch = []

            for _, row in df.iterrows():
                # 1. State
                st_code = str(row['MDDS STC'])
                cur.execute("INSERT INTO states (mdds_code, name) VALUES (%s, %s) ON CONFLICT (mdds_code) DO UPDATE SET name=EXCLUDED.name RETURNING id", (st_code, row['STATE NAME']))
                s_id = cur.fetchone()[0]
                
                # 2. District
                dt_code = str(row['MDDS DTC'])
                cur.execute("INSERT INTO districts (state_id, mdds_code, name) VALUES (%s, %s, %s) ON CONFLICT (mdds_code) DO UPDATE SET name=EXCLUDED.name RETURNING id", (s_id, dt_code, row['DISTRICT NAME']))
                d_id = cur.fetchone()[0]

                # 3. Sub-District
                sd_code = str(row['MDDS Sub_DT'])
                cur.execute("INSERT INTO sub_districts (district_id, mdds_code, name) VALUES (%s, %s, %s) ON CONFLICT (mdds_code) DO UPDATE SET name=EXCLUDED.name RETURNING id", (d_id, sd_code, row['SUB-DISTRICT NAME']))
                sd_id = cur.fetchone()[0]

                # 4. Village (Prepare for Batch)
                village_batch.append((sd_id, str(row['MDDS PLCN']), row['Area Name']))

            # Batch Insert Villages
            execute_values(cur, "INSERT INTO villages (sub_district_id, mdds_code, name) VALUES %s ON CONFLICT DO NOTHING", village_batch)
            
            conn.commit()
            print(f"✅ Finished {file_name}")

        except Exception as e:
            print(f"❌ Error processing {file_name}: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close() # Always close to free up Neon's connection pool

    print("✨ ALL STATES IMPORTED SUCCESSFULLY!")

if __name__ == "__main__":
    run_etl()