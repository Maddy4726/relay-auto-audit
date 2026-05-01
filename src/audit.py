from src.rules import *

def run_audit(data):
    issues = []

    checks = [
    check_contact_balance(list(data["contact_resistance"].values())),
    check_ct_ratio(data),
    check_binary(data),
    check_comm(data),
    check_time_balance(data.get("close_time", [])),
    check_winding_balance(data),
    check_voltage_ratio(data),
    check_magnetizing_current(data),
    check_short_circuit(data)]

    for c in checks:
        if c:
            issues.append(c)

    remark_issue = check_remark(data, issues)
    if remark_issue:
        issues.append(remark_issue)

    return issues

