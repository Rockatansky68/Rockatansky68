import argparse
import imaplib
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Delete advertising and newsletter emails")
    parser.add_argument("--server", default="imap.gmail.com", help="IMAP server address")
    parser.add_argument("--user", required=True, help="Email username")
    parser.add_argument("--password", required=True, help="Email password or app password")
    parser.add_argument("--dry-run", action="store_true", help="List emails that would be deleted")
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        mail = imaplib.IMAP4_SSL(args.server)
        mail.login(args.user, args.password)
    except imaplib.IMAP4.error as e:
        print(f"Login failed: {e}")
        sys.exit(1)

    mail.select("INBOX")

    # Search for common keywords in the subject
    criteria = '(OR SUBJECT "newsletter" SUBJECT "werbung")'
    typ, data = mail.search(None, criteria)

    if typ != 'OK':
        print("No messages found!")
        mail.logout()
        return

    msg_nums = data[0].split()
    if not msg_nums:
        print("No advertising or newsletter emails detected.")
    else:
        for num in msg_nums:
            if args.dry_run:
                typ, msg_data = mail.fetch(num, '(BODY[HEADER.FIELDS (SUBJECT FROM)])')
                header = msg_data[0][1].decode('utf-8', errors='ignore')
                print(f"Would delete email #{num.decode()}:\n{header}")
            else:
                mail.store(num, '+FLAGS', '\\Deleted')
                print(f"Marked email #{num.decode()} for deletion")

    if not args.dry_run and msg_nums:
        mail.expunge()
        print("Deleted marked emails.")

    mail.logout()


if __name__ == "__main__":
    main()
