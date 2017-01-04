"""
This module contains tests for programs-related signals and signal handlers.
"""

from django.test import TestCase
from nose.plugins.attrib import attr
import mock

from student.tests.factories import UserFactory

from openedx.core.djangoapps.credentials.tests.mixins import CredentialsApiConfigMixin
from openedx.core.djangoapps.programs.signals import handle_course_cert_awarded
from openedx.core.djangoapps.signals.signals import COURSE_CERT_AWARDED


TEST_USERNAME = 'test-user'


@attr(shard=2)
@mock.patch(
    'openedx.core.djangoapps.programs.tasks.v1.tasks.award_program_certificates.delay',
    new_callable=mock.PropertyMock,
    return_value=None,
)
@mock.patch(
    'openedx.core.djangoapps.credentials.models.CredentialsApiConfig.is_learner_issuance_enabled',
    new_callable=mock.PropertyMock,
    return_value=True,
)
class CertAwardedReceiverTest(CredentialsApiConfigMixin, TestCase):
    """
    Tests for the `handle_course_cert_awarded` signal handler function.
    """

    @property
    def signal_kwargs(self):
        """
        DRY helper.
        """
        return dict(
            sender=self.__class__,
            user=UserFactory.create(username=TEST_USERNAME),
            course_key='test-course',
            mode='test-mode',
            status='test-status',
        )

    def test_signal_received(self, mock_award_program_certificates, mock_is_certification_enabled):  # pylint: disable=unused-argument
        """
        Ensures the receiver function is invoked when COURSE_CERT_AWARDED is
        sent.

        Suboptimal: because we cannot mock the receiver function itself (due
        to the way django signals work), we mock a configuration call that is
        known to take place inside the function.
        """
        COURSE_CERT_AWARDED.send(**self.signal_kwargs)
        self.assertEqual(mock_award_program_certificates.call_count, 1)

    def test_programs_enabled(self, mock_award_program_certificates, mock_is_certification_enabled):  # pylint: disable=unused-argument
        """
        Ensures that the receiver function invokes the expected celery task
        """
        mock_award_program_certificates.return_value = True
        handle_course_cert_awarded(**self.signal_kwargs)
        self.assertEqual(mock_award_program_certificates.call_count, 1)
        self.assertEqual(mock_award_program_certificates.call_args[0], (TEST_USERNAME,))
