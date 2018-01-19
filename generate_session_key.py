import random
import string

SESSION_KEY_FILE = 'web/session_key.txt'
CHOICES = string.ascii_letters + string.digits + string.punctuation


def generate_session_key():
    with open(SESSION_KEY_FILE, 'w') as f:
        secret = [random.SystemRandom().choice(CHOICES) for _ in range(50)]
        f.write('%s\n' % ''.join(secret))


if __name__ == '__main__':
    generate_session_key()
