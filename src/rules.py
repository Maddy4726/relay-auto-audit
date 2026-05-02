def check_contact_balance(values):
    if len(values) != 3:
        return None
    max_v = max(values)
    min_v = min(values)
    # If contact resistance is less than 200 microohm, variation is acceptable
    if max_v < 200:
        return None
    if (max_v - min_v) / min_v > 0.25:
        return "FAIL: Contact resistance imbalance"


def check_ct_ratio(data):
    ct_spec = data.get("ct_ratio_spec", None)
    ct_measured = data.get("ct_ratio_measured", {})

    if not ct_spec or not ct_measured:
        return None

    # Check if measured ratios match the specification within 2% tolerance
    tolerance = 0.02
    for phase, measured_ratio in ct_measured.items():
        # If measured ratio is 1.0, it means secondary values are missing
        if measured_ratio == 1.0:
            return "WARNING: Please write secondary values instead of Primary in the relay column"
        if abs(measured_ratio - ct_spec) / ct_spec > tolerance:
            return f"FAIL: CT ratio mismatch in {phase} phase (expected {ct_spec}, got {measured_ratio:.2f})"

    return None


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
    avg = sum(values) / 3
    if (max(values) - min(values)) / avg > 0.03:
        return "FAIL: Winding resistance imbalance"


def check_voltage_ratio(data):
    vr = data.get("voltage_ratio", {})
    if not vr:
        return None

    hv = sum(vr["HV"]) / 3
    lv = sum(vr["LV"]) / 3

    ratio = hv / lv
    expected = 11000 / 440

    if abs(ratio - expected) / expected > 0.03:
        return "FAIL: Voltage ratio mismatch"


def check_magnetizing_current(data):
    vals = data.get("magnetizing_current", [])
    if len(vals) != 3:
        return None
    if (max(vals) - min(vals)) / min(vals) > 0.3:
        return "WARNING: Magnetizing current imbalance"


def check_short_circuit(data):
    sc = data.get("short_circuit", {})
    if not sc:
        return None

    set_current = sc.get("set_current", None)
    delay = sc.get("delay", None)
    output_delay = sc.get("output_contact_delay", 20.0)
    master_delay = sc.get("master_trip_delay", 30.0)
    measurement = sc.get("measurement")

    if set_current is None or delay is None:
        return None

    # Check if short circuit set current is within acceptable range (5-15x In)
    if set_current < 5 or set_current > 15:
        return f"WARNING: Short circuit set current {set_current}x In is outside typical range (5-15x In)"

    # Check if delay is within acceptable range (0.02-0.5 sec)
    if delay < 0.02 or delay > 0.5:
        return f"WARNING: Short circuit delay {delay}s is outside typical range (0.02-0.5 sec)"

    if measurement:
        operated_time = measurement.get("operated_time")
        if operated_time is not None:
            expected_time = delay + (output_delay / 1000.0) + (master_delay / 1000.0)
            if abs(operated_time - expected_time) / expected_time > 0.25:
                return (
                    f"FAIL: Short circuit operated time {operated_time}s does not match expected {expected_time:.3f}s "
                    f"(delay {delay}s + output {output_delay}ms + master {master_delay}ms)"
                )

    return None


def check_insulation_resistance(data):
    """Check insulation resistance test results"""
    ir = data.get("insulation_resistance", {})
    if not ir:
        return "WARNING: Insulation resistance test not found"
    
    # Check if all required tests are present
    required_tests = ["pole_pole", "phase_phase", "pole_earth"]
    for test in required_tests:
        if test not in ir:
            return f"WARNING: {test.replace('_', '-')} insulation resistance test missing"
    
    # Check resistance values (should be >500 MΩ for 5000V test)
    for test_name, test_data in ir.items():
        resistance = test_data.get("resistance", "0")
        if resistance.startswith(">"):
            resistance_val = int(resistance[1:])
        else:
            resistance_val = int(resistance)
        
        if resistance_val < 500:
            return f"FAIL: {test_name.replace('_', '-')} insulation resistance too low ({resistance} MΩ)"
    
    return None


def check_coil_resistance(data):
    """Check coil resistance test results"""
    coil = data.get("coil_resistance", {})
    if not coil:
        return "WARNING: Coil resistance test not found"
    
    # Check if all required coils are present
    required_coils = ["closing_coil", "tripping_coil", "spring_charge_motor"]
    for coil_name in required_coils:
        if coil_name not in coil:
            return f"WARNING: {coil_name.replace('_', ' ')} resistance test missing"
    
    # Check typical resistance ranges
    closing_resistance = coil.get("closing_coil", 0)
    tripping_resistance = coil.get("tripping_coil", 0)
    motor_resistance = coil.get("spring_charge_motor", 0)
    
    if closing_resistance < 50 or closing_resistance > 150:
        return f"WARNING: Closing coil resistance {closing_resistance}Ω outside typical range (50-150Ω)"
    
    if tripping_resistance < 20 or tripping_resistance > 100:
        return f"WARNING: Tripping coil resistance {tripping_resistance}Ω outside typical range (20-100Ω)"
    
    if motor_resistance < 5000 or motor_resistance > 20000:
        return f"WARNING: Spring charge motor resistance {motor_resistance}Ω outside typical range (5-20KΩ)"
    
    return None


def check_time_interval(data):
    """Check time interval test results"""
    time_data = data.get("time_interval", {})
    if not time_data:
        return "WARNING: Time interval test not found"
    
    # Check if all operations are present
    required_ops = ["close", "open", "close___open"]
    for op in required_ops:
        if op not in time_data:
            return f"WARNING: {op.replace('___', '-')} time interval test missing"
    
    # Check time balance for each operation
    for op, phases in time_data.items():
        if isinstance(phases, dict) and len(phases) == 3:
            times = list(phases.values())
            max_t = max(times)
            min_t = min(times)
            if max_t - min_t > 5:  # 5ms tolerance
                return f"WARNING: {op.replace('___', '-')} time imbalance ({max_t - min_t}ms difference)"
    
    return None


def check_cbct_ratio(data):
    """Check CBCT ratio test results"""
    cbct = data.get("cbct_ratio", {})
    if not cbct:
        return "WARNING: CBCT ratio test not found"
    
    # Check if ratio calculation is correct (150/1 = 150)
    injected = cbct.get("injected_primary", 0)
    measured = cbct.get("measured_secondary", 0)
    
    if injected > 0 and measured > 0:
        ratio = injected / measured
        expected_ratio = 150.0  # CBCT ratio 150/1
        if abs(ratio - expected_ratio) / expected_ratio > 0.05:  # 5% tolerance
            return f"FAIL: CBCT ratio mismatch (expected {expected_ratio}, got {ratio:.2f})"
    
    return None

def check_overcurrent_logic(data):
    oc = data.get("overcurrent", {})
    phases = oc.get("phases", {})
    
    if not oc or not phases:
        return "WARNING: Overcurrent test data missing"

    setting_percent = oc.get("setting_percent")
    ct_ratio = data.get("ct_ratio_spec") # 100/5 = 20.0

    if not setting_percent or not ct_ratio:
        return None

    # CT secondary is 5A; Expected = 5A * (600/100) = 30A[cite: 5]
    expected_current = 5.0 * (setting_percent / 100)
    issues = []

    for phase, info in phases.items():
        injected = info["injected_current"]
        if not info["operated"]:
            issues.append(f"FAIL: {phase} phase relay did not operate")
        
        # Check if injected current (32.6 or 29.9) is near expected 30A[cite: 5]
        if abs(injected - expected_current) / expected_current > 0.15:
            issues.append(f"FAIL: {phase} phase current mismatch")

    return "; ".join(issues) if issues else None


def check_earth_fault_cbct(data):
    """Check earth fault protection through CBCT"""
    ef_cbct = data.get("earth_fault_cbct", {})
    if not ef_cbct:
        return "WARNING: Earth fault protection through CBCT test not found"
    
    # Check if Io test was performed and operated
    io_test = ef_cbct.get("Io", {})
    if not io_test or not io_test.get("operated", False):
        return "WARNING: Io earth fault test not performed or failed"
    
    return None


def check_over_current_protection(data):
    """Check over current protection test results"""
    oc = data.get("over_current_protection", {})
    if not oc:
        return "WARNING: Over current protection test not found"
    
    # Check set current
    set_current = oc.get("set_current")
    if set_current and (set_current < 400 or set_current > 800):
        return f"WARNING: Over current set current {set_current}% outside typical range (400-800%)"
    
    # Check operated time
    operated_time = oc.get("operated_time")
    if operated_time and operated_time > 1.0:
        return f"WARNING: Over current operated time {operated_time}s too high (>1s)"
    
    return None


def check_overload_protection(data):
    """Check overload protection test results"""
    ol = data.get("overload_protection", {})
    if not ol:
        return "WARNING: Overload protection test not found"
    
    # Check setting
    setting = ol.get("setting")
    if setting and (setting < 3.0 or setting > 8.0):
        return f"WARNING: Overload setting {setting}A outside typical range (3-8A)"
    
    # Check TDR
    tdr = ol.get("tdr")
    if tdr and (tdr < 0.5 or tdr > 1.5):
        return f"WARNING: Overload TDR {tdr} outside typical range (0.5-1.5)"
    
    # Check operated times
    operated_times = ol.get("operated_times", {})
    if operated_times:
        for phase, data in operated_times.items():
            time = data.get("operated_time", 0)
            if time > 2.0:  # Typical overload time
                return f"WARNING: {phase} phase overload operated time {time}s too high"
    
    return None


def check_earth_fault_protection(data):
    """Check earth fault protection test results"""
    ef = data.get("earth_fault_protection", {})
    if not ef:
        return "WARNING: Earth fault protection test not found"
    
    # Check setting
    setting = ef.get("setting")
    if setting and (setting < 2 or setting > 10):
        return f"WARNING: Earth fault setting {setting}A outside typical range (2-10A)"
    
    # Check TMS
    tms = ef.get("tms")
    if tms and (tms < 0.05 or tms > 0.3):
        return f"WARNING: Earth fault TMS {tms} outside typical range (0.05-0.3)"
    
    return None


def check_magnetic_balance(data):
    """Check magnetic balance test results"""
    mb = data.get("magnetic_balance", {})
    if not mb:
        return "WARNING: Magnetic balance test not found"

    # Check if all three winding combinations are present
    required_windings = ["1U-1V", "1V-1W", "1W-1U"]
    for winding in required_windings:
        if winding not in mb:
            return f"WARNING: {winding} magnetic balance test missing"

    # For magnetic balance tests, imbalance is expected and normal
    # Just verify that measurements were taken (non-zero values)
    for winding, voltages in mb.items():
        if len(voltages) == 3:
            if any(v <= 0 for v in voltages):
                return f"WARNING: {winding} magnetic balance has invalid readings"

    return None


def check_lt_breaker_contact_resistance(data):
    """Check LT breaker contact resistance"""
    lt_contact = data.get("lt_breaker_contact_resistance", {})
    if not lt_contact:
        return "WARNING: LT breaker contact resistance test not found"
    
    # Check if all phases are present
    if len(lt_contact) != 3:
        return "WARNING: LT breaker contact resistance missing for some phases"
    
    # Check resistance values (should be low, <100 μΩ typical)
    for phase, resistance in lt_contact.items():
        if resistance > 100:
            return f"WARNING: {phase} phase LT breaker contact resistance too high ({resistance} μΩ)"
    
    return None


def check_final_checks(data):
    """Check final checks completion"""
    checks = data.get("final_checks", {})
    if not checks:
        return "WARNING: Final checks not found"
    
    # Check critical items that should be DONE
    critical_items = [
        "Relay Measurement Testing",
        "Relay Protection Testing", 
        "Relay Indications",
        "Cleaning of Auxiliary Relay",
        "Consolidate data & Control Scheme Checked",
        "Trip of CB through Master Checked",
        "All Protection Settings Normalized after Testing",
        "Auxiliary Relay operation check"
    ]
    
    for item in critical_items:
        status = checks.get(item, "")
        if status not in ["DONE", "OK"]:
            return f"WARNING: Critical check '{item}' not completed (status: {status})"
    
    return None
