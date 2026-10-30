"""
Diagnose outgoing auth email and, optionally, send a real test message.

Usage:
    python manage.py mail_check                  # show the configured transport
    python manage.py mail_check you@gmail.com    # send a real test message

Verification and password-reset emails are sent through `mailers.default`, so a
message accepted here travels exactly the same path they do.
"""

import smtplib
import socket

from django.conf import settings
from django.core.mail import EmailMessage, mailers
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

# Ordered by specificity: the first matching entry explains the failure in the
# terms of the setting that is most likely wrong.
ERROR_HINTS = (
    (
        smtplib.SMTPAuthenticationError,
        'The server rejected the login. Gmail needs an App Password (16 '
        'characters, spaces ignored) and 2-Step Verification enabled; the '
        'normal account password no longer works for SMTP.',
    ),
    (
        smtplib.SMTPSenderRefused,
        'The server refused the From address. Gmail only accepts your own '
        'address, or an alias you have verified.',
    ),
    (
        smtplib.SMTPRecipientsRefused,
        'The server refused the recipient address.',
    ),
    (
        smtplib.SMTPServerDisconnected,
        'The server hung up mid-conversation. This is what TLS on the wrong '
        'port looks like: Gmail needs port 587 with EMAIL_USE_TLS=True.',
    ),
    (
        smtplib.SMTPException,
        'The SMTP conversation failed. Check EMAIL_HOST / EMAIL_PORT and TLS.',
    ),
    (socket.gaierror, 'The SMTP host name could not be resolved.'),
    (ConnectionRefusedError, 'Nothing is listening on that host and port.'),
    (
        (socket.timeout, TimeoutError),
        'The connection timed out. Networks and VPNs that block outbound SMTP '
        'produce this; port 465 (EMAIL_USE_SSL=True) sometimes gets through.',
    ),
)


class Command(BaseCommand):
    help = 'Show the configured email transport and optionally send a test message.'

    def add_arguments(self, parser):
        parser.add_argument(
            'recipient',
            nargs='?',
            help='Address to send a test message to. Omit to print the config only.',
        )
        parser.add_argument(
            '--connect',
            action='store_true',
            help='Open and authenticate the SMTP connection without sending.',
        )

    def handle(self, *args, **options):
        backend_path, mailer_options = self.transport()
        smtp = backend_path.endswith('smtp.EmailBackend')

        self.report_config(backend_path, mailer_options)

        if options['connect']:
            if not smtp:
                raise CommandError(
                    f'--connect needs the SMTP backend; the active one is {backend_path}.'
                )
            missing = self.missing_credentials(mailer_options)
            if missing:
                self.stdout.write(
                    self.style.WARNING(
                        f'Authentication will be skipped: {", ".join(missing)} '
                        'empty in backend/.env.'
                    )
                )
            self.check_connection(authenticated=not missing)
            return

        recipient = options['recipient']
        if not recipient:
            self.stdout.write('\nPass an address to send a test message.')
            return

        if smtp:
            self.check_credentials(mailer_options)
        self.check_sender(mailer_options)

        message = EmailMessage(
            'Code Yaar email test',
            (
                'This is a test message from Code Yaar.\n\n'
                'Receiving it means verification and password-reset emails will '
                'arrive too.\n\n'
                f'Sent {timezone.now():%Y-%m-%d %H:%M:%S %Z}.'
            ),
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
        )

        try:
            accepted = mailers.default.send_messages([message])
        except Exception as error:
            raise CommandError(
                f'{type(error).__name__}: {error}\n{self.explain(error)}'
            ) from error

        if not accepted:
            raise CommandError(
                'The backend reported no messages sent. With SMTP that means the '
                'connection or login did not complete.'
            )

        self.stdout.write(
            self.style.SUCCESS(f'\nThe server accepted 1 message for {recipient}.')
        )
        self.stdout.write(f'Message-ID              : {message.message()["Message-ID"]}')
        self.stdout.write(
            'Acceptance only means the server queued it; it does not prove the '
            'message reached the inbox. Check the inbox and the spam folder, and '
            'quote the Message-ID if you have to ask the provider about it.'
        )

    def report_config(self, backend_path, mailer_options):
        self.stdout.write(f'Backend                 : {backend_path}')
        self.stdout.write(f'DEFAULT_FROM_EMAIL      : {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(
            f'Verification required   : {settings.AUTH_REQUIRE_EMAIL_VERIFICATION}'
        )
        for key, value in mailer_options.items():
            if key == 'password':
                value = '(set)' if value else '(empty)'
            self.stdout.write(f'{key:<24}: {value}')

        if backend_path.endswith('console.EmailBackend'):
            self.stdout.write(
                self.style.WARNING(
                    '\nThe console backend never delivers mail: messages are only '
                    'printed to this terminal.'
                )
            )

    def missing_credentials(self, mailer_options):
        return [
            name
            for name in ('host', 'username', 'password')
            if not mailer_options.get(name)
        ]

    def check_credentials(self, mailer_options):
        missing = self.missing_credentials(mailer_options)
        if missing:
            raise CommandError(
                'SMTP is selected but '
                f'{self.style.ERROR(", ".join(missing))} is empty in backend/.env.'
            )

    def check_connection(self, authenticated=True):
        """Open the SMTP connection: proves DNS, TCP, STARTTLS and the login."""
        backend = mailers.default
        try:
            backend.open()
        except Exception as error:
            raise CommandError(
                f'Connection or authentication failed: {type(error).__name__}: '
                f'{error}\n{self.explain(error)}'
            ) from error

        try:
            server = getattr(backend, 'connection', None)
            reply = server.noop() if server is not None else (None, b'')
            code, detail = reply
            result = (
                'connected and authenticated' if authenticated
                else 'connected (STARTTLS negotiated, no login attempted)'
            )
            if code is not None:
                result += f' (NOOP {code} {detail.decode(errors="replace").strip()})'
            self.stdout.write(self.style.SUCCESS(result))
        finally:
            backend.close()

    def transport(self):
        """Return (backend path, OPTIONS mapping) for `mailers.default`."""
        config = getattr(settings, 'MAILERS', {}).get('default', {})
        return (
            config.get('BACKEND', getattr(settings, 'EMAIL_BACKEND', '(unset)')),
            config.get('OPTIONS', {}),
        )

    def check_sender(self, mailer_options):
        """Warn when Gmail is asked to send as a different address."""
        host = str(mailer_options.get('host', '')).lower()
        username = str(mailer_options.get('username', ''))
        if 'gmail' not in host or not username:
            return
        from_email = str(settings.DEFAULT_FROM_EMAIL)
        if username.lower() not in from_email.lower():
            self.stdout.write(
                self.style.WARNING(
                    f'Heads up: DEFAULT_FROM_EMAIL ({from_email}) does not contain '
                    f'EMAIL_HOST_USER ({username}). Gmail rewrites such senders '
                    'and the message often lands in spam.'
                )
            )

    def explain(self, error):
        for kinds, hint in ERROR_HINTS:
            if isinstance(error, kinds):
                return hint
        return 'No specific hint for this failure; the traceback above is the raw error.'
