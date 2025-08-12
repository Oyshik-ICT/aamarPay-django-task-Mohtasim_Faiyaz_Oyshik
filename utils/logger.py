import logging

from fileprocessing.models import ActivityLog

logger = logging.getLogger(__name__)


class ActivityLogger:
    """
    Utility class for logging user activites into Activitylog Model
    """

    @staticmethod
    def log_file_upload(user, filename):
        try:
            ActivityLog.objects.create(
                user=user, action="file_uploaded", metadata={"filename": filename}
            )
        except Exception as e:
            logger.error(f"Failed to log file upload=> {e}", exc_info=True)

    @staticmethod
    def log_payment_info(user, tranasction_id, payment_status):
        try:
            ActivityLog.objects.create(
                user=user,
                action="payment",
                metadata={
                    "tranasction_id": tranasction_id,
                    "payment_status": payment_status,
                    "amount": 100.00,
                },
            )
        except Exception as e:
            logger.error(f"Failed to log payment info=> {e}", exc_info=True)

    @staticmethod
    def log_word_count(user, filename, word_count, status):
        try:
            ActivityLog.objects.create(
                user=user,
                action="word_count",
                metadata={
                    "filename": filename,
                    "word_count": word_count,
                    "status": status,
                },
            )
        except Exception as e:
            logger.error(f"Failed to log word count=> {e}", exc_info=True)
