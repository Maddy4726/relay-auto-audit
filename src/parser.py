from email.mime import text
import re


def extract_contact_resistance(text):
    contact = {}

    # Find section
    section = re.search(
        r"CONTACT RESISTANCE TEST.*?(R\s+\d+\.\d+.*?B\s+\d+\.\d+)", text, re.S
    )

    if section:
        block = section.group(1)

        matches = re.findall(r"\b(R|Y|B)\s+(\d+\.\d+)", block)
        for phase, value in matches:
            contact[phase] = float(value)

    return contact


def extract_remark(text):
    match = re.search(r"REMARKS:(.*)", text, re.IGNORECASE)
    return match.group(1) if match else ""


def extract_data(text):
    data = {}

    data["contact_resistance"] = extract_contact_resistance(text)
    data["remark"] = extract_remark(text)

    data["close_time"] = extract_time(text)

    # Flags
    data["has_binary_test"] = "Binary Input" in text
    data["has_comm_test"] = "Communication" in text
    data["ct_y_present"] = not re.search(r"Y\s+-", text)
    data["winding_resistance"] = extract_winding_resistance(text)
    data["voltage_ratio"] = extract_voltage_ratio(text)
    data["magnetizing_current"] = extract_magnetizing_current(text)
    data["ct_ratio_spec"] = extract_ct_ratio(text)
    data["ct_ratio_measured"] = extract_ct_measured_ratio(text)
    data["short_circuit"] = extract_short_circuit(text)

    return data


def extract_time(text):
    match = re.search(r"Close\s+(\d+)\s+(\d+)\s+(\d+)", text)
    if match:
        return [int(match.group(1)), int(match.group(2)), int(match.group(3))]
    return []


def extract_winding_resistance(text):
    match = re.search(
        r"WINDING RESISTANCE TEST.*?NT\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)", text, re.S
    )
    if match:
        return {
            "HV": [float(match.group(1)), float(match.group(2)), float(match.group(3))]
        }
    return {}


def extract_voltage_ratio(text):
    match = re.search(
        r"N\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+).*?([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)",
        text,
        re.S,
    )
    if match:
        return {
            "HV": [float(match.group(1)), float(match.group(2)), float(match.group(3))],
            "LV": [float(match.group(4)), float(match.group(5)), float(match.group(6))],
        }
    return {}


def extract_magnetizing_current(text):
    match = re.search(
        r"Measured Current.*?([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)", text, re.S
    )
    if match:
        return [float(match.group(1)), float(match.group(2)), float(match.group(3))]
    return []


def extract_ct_ratio(text):
    # Extract CT ratio specification (e.g., 100 / 5 A)
    match = re.search(r"CT\s*\(CTR:\s*(\d+)\s*\/\s*(\d+)\s*A\)", text)
    if match:
        primary = float(match.group(1))
        secondary = float(match.group(2))
        return primary / secondary
    return None


def extract_ct_measured_ratio(text):
    # Extract measured CT ratios from ratio test
    ct_ratios = {}

    # Find the CT ratio test section
    section = re.search(r"3\.1\s+CT.*?(?=3\.2|$)", text, re.S)
    if not section:
        return ct_ratios

    block = section.group(0)

    # Extract rows: Phase | Injected Primary (A) | Measured Secondary (A)
    matches = re.findall(r"(R|Y|B)\s+(\d+)\s+([\d\-]+)", block)

    for phase, injected, measured in matches:
        injected = float(injected)
        measured_val = measured.strip()
        if measured_val != "-":
            measured = float(measured_val)
            if measured > 0:
                ct_ratios[phase] = injected / measured

    return ct_ratios


def extract_delay_value(text, label_pattern):
    match = re.search(rf"{label_pattern}.*?([\d\.]+)\s*(?:ms|msec)", text, re.I | re.S)
    if match:
        return float(match.group(1))
    return None


def extract_short_circuit(text):
    # Extract short circuit (DTOC) settings and measured values
    sc_data = {}

    # Find SHORT CIRCUIT section
    match = re.search(
        r"4\.2\s+SHORT CIRCUIT:.*?Set Current\s*=\s*([\d\.]+)\s*x\s*In.*?Delay\s*=\s*([\d\.]+)\s*m?Sec",
        text,
        re.S | re.I,
    )
    if match:
        sc_data["set_current"] = float(match.group(1))
        sc_data["delay"] = float(match.group(2))
        sc_data["output_contact_delay"] = (
            extract_delay_value(text, r"output.*contact") or 20.0
        )
        sc_data["master_trip_delay"] = (
            extract_delay_value(text, r"master.*trip") or 30.0
        )

        # Find the first measured row following the 4.2 section
        sub = text[match.end() :]
        block_match = re.search(
            r"Phase\s*\n\s*Injected Current\s*\(A\)\s*\n\s*Operated Time\s*\(Sec\)\s*(.*?)\n\s*Phase\b",
            sub,
            re.S | re.I,
        )
        if block_match:
            block = block_match.group(1)
            rows = re.findall(r"([A-Z]{1,3})\s*\n\s*([\d\.]+)\s*\n\s*([\d\.]+)", block)
            if rows:
                phase, injected, operated = rows[0]
                sc_data["measurement"] = {
                    "phase": phase.strip(),
                    "injected_current": float(injected),
                    "operated_time": float(operated),
                }

    return sc_data
