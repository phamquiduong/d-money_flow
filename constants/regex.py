# Must contain uppercase, lowercase, and special character
PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[^A-Za-z0-9]).*$'

# Letters, numbers, and underscores only
USERNAME_REGEX = r'^[A-Za-z0-9_]+$'
