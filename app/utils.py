import hashlib


def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode('utf8')).hexdigest()


def format_date(date_str: str) -> str:
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M')
    except:
        return date_str
