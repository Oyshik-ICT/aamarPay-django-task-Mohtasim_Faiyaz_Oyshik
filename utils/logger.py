from fileprocessing.models import ActivityLog

class ActivityLogger:
    @staticmethod
    def log_file_upload(user, filename):
        ActivityLog.objects.create(
            user = user,
            action = "file_uploaded",
            metadata = {"filename": filename}
        )

    @staticmethod
    def log_payment_info(user, tranasction_id, payment_status):
        ActivityLog.objects.create(
            user = user,
            action = "payment",
            metadata = {"tranasction_id": tranasction_id, "payment_status": payment_status, "amount": 100.00}
        )
    
    @staticmethod
    def log_word_count(user, filename, word_count, status):
        ActivityLog.objects.create(
            user = user,
            action = "word_count",
            metadata = {"filename": filename, "word_count": word_count, "status": status}
        )

