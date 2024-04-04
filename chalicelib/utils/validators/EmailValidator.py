from email_validator import validate_email, EmailNotValidError


class EmailAddressValidator:
    @staticmethod
    def is_valid(email_address, check_deliverability=False):
        try:
            validate_email(email_address,
                           check_deliverability=check_deliverability)
        except EmailNotValidError:
            return False
        return True
