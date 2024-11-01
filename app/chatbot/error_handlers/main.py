import openai

# Refer documentation: https://platform.openai.com/docs/guides/error-codes
def error_handler(e):
    error_message = str(e)

    # Map of exception types to error messages
    error_map = {
        openai.RateLimitError: "Error running target function: " + error_message,
        openai.APITimeoutError: "Timeout error. Retrying in several seconds...",
        openai.BadRequestError: f"Invalid request error: {e}",
        openai.AuthenticationError: f"Authentication error: {e}",
        openai.APIConnectionError: f"Failed to connect to OpenAI API: {e}"
    }

    # Handle special case for insufficient quota in RateLimitError
    if isinstance(e, openai.RateLimitError) and "insufficient_quota" in error_message:
        raise Exception("Error: Insufficient quota for OpenAI API. Please check your billing details.")
    
    # Check error map for the error type and raise the corresponding message
    for error_type, message in error_map.items():
        if isinstance(e, error_type):
            raise Exception(message)
    
    # Fallback for unexpected errors
    raise Exception(f"An error occurred: {error_message}")
