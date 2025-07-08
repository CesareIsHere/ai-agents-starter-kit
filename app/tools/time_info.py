"""
Time and timezone information tool.
Auto-discovered by the tool loader system.
"""

from agents import function_tool
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

@function_tool()
def get_time(timezone_offset: int = 0) -> str:
    """
    Get current time for a specified timezone offset.
    
    This tool provides current date and time information for any timezone offset from UTC.
    
    Args:
        timezone_offset: Hours offset from UTC (e.g., -5 for EST, +1 for CET, +9 for JST)
    
    Returns:
        Current date and time information as a formatted string
    
    Examples:
        get_time(0) -> "UTC+0: 2024-01-15 14:30:25"
        get_time(-5) -> "UTC-5: 2024-01-15 09:30:25 (EST)"
        get_time(9) -> "UTC+9: 2024-01-15 23:30:25 (JST)"
    """
    try:
        # Limita l'offset a valori ragionevoli
        if timezone_offset < -12 or timezone_offset > 14:
            return "Error: Timezone offset must be between -12 and +14 hours."
        
        # Crea timezone con offset
        tz = timezone(datetime.timedelta(hours=timezone_offset))
        now = datetime.now(tz)
        
        # Formatta il risultato
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Determina il nome del timezone
        if timezone_offset == 0:
            tz_name = "UTC"
        elif timezone_offset > 0:
            tz_name = f"UTC+{timezone_offset}"
        else:
            tz_name = f"UTC{timezone_offset}"
        
        # Aggiungi alcuni timezone comuni
        common_zones = {
            -8: "PST", -7: "MST", -6: "CST", -5: "EST",
            0: "GMT", 1: "CET", 9: "JST", 10: "AEST"
        }
        
        result = f"🕐 Time in {tz_name}: {formatted_time}"
        if timezone_offset in common_zones:
            result += f" ({common_zones[timezone_offset]})"
        
        # Aggiungi informazioni aggiuntive
        result += f"\nDay of week: {now.strftime('%A')}"
        result += f"\nDate format: {now.strftime('%B %d, %Y')}"
        
        logger.info(f"Time request for UTC{'+' if timezone_offset >= 0 else ''}{timezone_offset}")
        return result
        
    except Exception as e:
        logger.error(f"Time tool error: {e}")
        return f"Error: Could not get time for offset {timezone_offset} - {str(e)}"
