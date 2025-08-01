# Vulnerable Python code example
import os
import pickle
import subprocess


# INTENTIONALLY VULNERABLE CODE FOR DEMO PURPOSES - DO NOT USE IN PRODUCTION
# This file contains security vulnerabilities for testing/training purposes
import os
import pickle
import subprocess
import shlex


def execute_command(user_input):
    # Security vulnerability: Command injection
    # VULNERABLE VERSION - DO NOT USE:
    # result = subprocess.run(user_input, shell=True, capture_output=True)
    
    # SECURE VERSION - USE THIS INSTEAD:
    try:
        # Parse command safely and run without shell
        args = shlex.split(user_input)
        result = subprocess.run(args, capture_output=True, timeout=30)
        return result.stdout
    except (ValueError, subprocess.TimeoutExpired) as e:
        return f"Error: {str(e)}".encode()


# Keep the original vulnerable version for demo purposes but mark it clearly
def execute_command_vulnerable_demo(user_input):
    """
    DEMO ONLY - VULNERABLE TO COMMAND INJECTION
    This function is intentionally vulnerable for security testing
    """
    result = subprocess.run(user_input, shell=True, capture_output=True)
    return result.stdout


def load_data(file_path):
    # Security vulnerability: Pickle deserialization
    with open(file_path, "rb") as f:
        data = pickle.load(f)  # Unsafe!
    return data


def get_secret():
    # Security vulnerability: Hardcoded credentials
    # VULNERABLE VERSION - DO NOT USE:
    # api_key = "sk-1234567890abcdef"
    
    # SECURE VERSION - USE THIS INSTEAD:
    api_key = os.getenv("API_KEY", "NOT_SET")
    if api_key == "NOT_SET":
        raise ValueError("API_KEY environment variable not set")
    return api_key


# Keep the original vulnerable version for demo purposes but mark it clearly
def get_secret_vulnerable_demo():
    """
    DEMO ONLY - CONTAINS HARDCODED CREDENTIALS
    This function is intentionally vulnerable for security testing
    """
    api_key = "sk-1234567890abcdef"
    return api_key


# Performance issue: Inefficient loop
def slow_function(data_list):
    result = []
    for i in range(len(data_list)):
        for j in range(len(data_list)):
            if data_list[i] == data_list[j] and i != j:
                result.append(data_list[i])
    return result
