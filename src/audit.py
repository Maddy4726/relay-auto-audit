from src.rules import *


def run_audit(data):
    issues = []

    checks = [
        check_contact_balance(list(data.get("contact_resistance", {}).values())),
        check_insulation_resistance(data),
        check_coil_resistance(data),
        check_time_interval(data),
        check_cbct_ratio(data),
        check_earth_fault_cbct(data),
        check_over_current_protection(data),
        check_overload_protection(data),
        check_earth_fault_protection(data),
        check_magnetic_balance(data),
        check_lt_breaker_contact_resistance(data),
        check_final_checks(data),
        check_ct_ratio(data),
        check_binary(data),
        check_comm(data),
        check_time_balance(data.get("close_time", [])),
        check_winding_balance(data),
        check_voltage_ratio(data),
        check_magnetizing_current(data),
        check_short_circuit(data),
    ]

    for c in checks:
        if c:
            issues.append(c)

    remark_issue = check_remark(data, issues)
    if remark_issue:
        issues.append(remark_issue)

    return issues