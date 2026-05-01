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
