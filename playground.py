from collections import defaultdict
from datetime import datetime, timedelta
from cyber import Cyber
from sample_data import AUTH_LOGS, CONNECTION_LOGS, THREAT_INTEL, LATEST_THREAT_INTEL
  
cyb = Cyber(AUTH_LOGS, CONNECTION_LOGS, THREAT_INTEL)

NOW = datetime(2024, 1, 1, 17, 0)
# window = datetime(2024, 1, 1, 16, 30) # 30 min window
# # window = datetime(2024, 1, 1, 16, 0) # 1 hour window
window = timedelta(hours=8) # 8 hour window


# failed_attempts_in_window = cyb.failed_attempts_in_window(1, NOW, window)
# print(failed_attempts_in_window)

# malicious_ip_connections = cyb.malicious_ip_connections()
# for src_host, dst_ip in malicious_ip_connections:
#     print(f"{src_host} -> {dst_ip}")

# cyb.ingest_latest_threat_intel(LATEST_THREAT_INTEL)

# new_conns, old_conns = cyb.get_latest_threat_report()
# print(new_conns)
# print("$$$$$$$$$$$$$$$$$$$$$$$")
# print(old_conns)

cyb.blast_radius("srv_db_03", 2)
# first_result = [ 
#   (10.0.0.200, 1)
#   (srv_legacy_02, 1)
#   (srv_backup_01, 1)

# second_result = 
#  srv_vault_01, 2
#  srv_web_01 , 2


# third result 
# 194.5.249.157, 3
# 194.5.249.157, 3 
# wkstn_101  , 3