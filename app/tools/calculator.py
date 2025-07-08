"""
Basic calculator tool for mathematical operations.
Auto-discovered by the tool loader system.
"""

from agents import function_tool
import logging

logger = logging.getLogger(__name__)

@function_tool()
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression safely.
    
    This tool can handle basic arithmetic operations including:
    - Addition (+)
    - Subtraction (-)
    - Multiplication (*)
    - Division (/)
    - Exponentiation (**)
    - Parentheses for grouping
    
    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 3 * 4", "(10 - 2) / 2")
    
    Returns:
        The result of the mathematical expression as a string
    
    Examples:
        calculate("2 + 3") -> "5"
        calculate("10 * (5 + 3)") -> "80"
        calculate("15 / 3") -> "5.0"
    """
    try:
        # Lista di caratteri permessi per sicurezza
        allowed_chars = set('0123456789+-*/.() ')
        
        # Verifica che l'espressione contenga solo caratteri sicuri
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters. Only numbers, +, -, *, /, **, (, ), and spaces are allowed."
        
        # Valuta l'espressione
        result = eval(expression)
        
        logger.info(f"Calculator: {expression} = {result}")
        return str(result)
        
    except ZeroDivisionError:
        return "Error: Division by zero is not allowed."
    except SyntaxError:
        return "Error: Invalid mathematical expression syntax."
    except Exception as e:
        logger.error(f"Calculator error: {e}")
        return f"Error: Could not evaluate expression - {str(e)}"
