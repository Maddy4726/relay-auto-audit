def check_contact_balance(values):
    if len(values) != 3:
        return None
    max_v = max(values)
    min_v = min(values)
    if (max_v - min_v) / min_v > 0.25:
        return "FAIL: Contact resistance imbalance"

def check_missing_ct(data):
    if not data["ct_y_present"]:
        return "WARNING: Missing CT data (Y phase)"

def check_binary(data):
    if not data["has_binary_test"]:
        return "WARNING: Binary I/O testing not done"

def check_comm(data):
    if not data["has_comm_test"]:
        return "WARNING: Communication testing not done"

def check_remark(data, issues):
    if issues and "satisfactory" in data["remark"].lower():
        return "CRITICAL: False 'All OK' remark"
    
def check_time_balance(times):
    if len(times) != 3:
        return None
    if max(times) - min(times) > 5:
        return "WARNING: Time variation too high"
    
def check_winding_balance(data):
    values = data.get("winding_resistance", {}).get("HV", [])
    if len(values) != 3:
        return None
    avg = sum(values)/3
    if (max(values)-min(values))/avg > 0.03:
        return "FAIL: Winding resistance imbalance"
    
def check_voltage_ratio(data):
    vr = data.get("voltage_ratio", {})
    if not vr:
        return None
    
    hv = sum(vr["HV"]) / 3
    lv = sum(vr["LV"]) / 3
    
    ratio = hv / lv
    expected = 11000 / 440
    
    if abs(ratio - expected)/expected > 0.01:
        return "FAIL: Voltage ratio mismatch"
    
def check_magnetizing_current(data):
    vals = data.get("magnetizing_current", [])
    if len(vals) != 3:
        return None
    if (max(vals)-min(vals))/min(vals) > 0.3:
        return "WARNING: Magnetizing current imbalance"