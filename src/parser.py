from email.mime import text
import re

def extract_contact_resistance(text):
    contact = {}

    # Find section
    section = re.search(r'CONTACT RESISTANCE TEST.*?(R\s+\d+\.\d+.*?B\s+\d+\.\d+)', text, re.S)

    if section:
        block = section.group(1)

        matches = re.findall(r'\b(R|Y|B)\s+(\d+\.\d+)', block)
        for phase, value in matches:
            contact[phase] = float(value)

    return contact


def extract_remark(text):
    match = re.search(r'REMARKS:(.*)', text, re.IGNORECASE)
    return match.group(1) if match else ""


def extract_data(text):
    data = {}

    data["contact_resistance"] = extract_contact_resistance(text)
    data["remark"] = extract_remark(text)
    
    data["close_time"] = extract_time(text)

    # Flags
    data["has_binary_test"] = "Binary Input" in text
    data["has_comm_test"] = "Communication" in text
    data["ct_y_present"] = not re.search(r'Y\s+-', text)
    data["winding_resistance"] = extract_winding_resistance(text)
    data["voltage_ratio"] = extract_voltage_ratio(text)
    data["magnetizing_current"] = extract_magnetizing_current(text)    
    
   

    return data

def extract_time(text):
    match = re.search(r'Close\s+(\d+)\s+(\d+)\s+(\d+)', text)
    if match:
        return [int(match.group(1)), int(match.group(2)), int(match.group(3))]
    return []

def extract_winding_resistance(text):
    match = re.search(r'WINDING RESISTANCE TEST.*?NT\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)', text, re.S)
    if match:
        return {
            "HV": [float(match.group(1)), float(match.group(2)), float(match.group(3))]
        }
    return {}

def extract_voltage_ratio(text):
    match = re.search(r'N\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+).*?([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)', text, re.S)
    if match:
        return {
            "HV": [float(match.group(1)), float(match.group(2)), float(match.group(3))],
            "LV": [float(match.group(4)), float(match.group(5)), float(match.group(6))]
        }
    return {}

def extract_magnetizing_current(text):
    match = re.search(r'Measured Current.*?([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)', text, re.S)
    if match:
        return [float(match.group(1)), float(match.group(2)), float(match.group(3))]
    return []
