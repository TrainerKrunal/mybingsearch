

# Import json for serializing results
import json

def calculate(expression: str) -> str:
    """
    Evaluates a mathematical expression and returns the result.

    :param expression: The mathematical expression to evaluate.
    :return: Result of the calculation as a JSON string.
    """
    try:
        # WARNING: Using eval can be dangerous; ensure to sanitize inputs in production.
        result = eval(expression)  # Evaluate the mathematical expression
        return json.dumps({"result": result})  # Return result as JSON
    except Exception as e:
        return json.dumps({"error": str(e)})  # Return error as JSON

# Set of user-defined functions (can be extended with more functions)
user_functions = {calculate}

#
# ---
#
# Explanation for Participants:
#
# This module defines a user function for evaluating mathematical expressions.
# - The `calculate` function takes a string expression, evaluates it, and returns the result as a JSON string.
# - If evaluation fails, it returns the error as a JSON string.
# - The set `user_functions` can be extended to include more custom functions for use in Azure AI Foundry agents.
# - Note: In production, always sanitize inputs to avoid security risks with `eval`.
