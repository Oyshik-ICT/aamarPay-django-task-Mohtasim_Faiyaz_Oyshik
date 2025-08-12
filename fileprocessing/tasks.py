import logging
import re

from celery import shared_task
from docx import Document

from fileprocessing.choices import StatusChoice
from fileprocessing.models import FileUpload
from utils.logger import ActivityLogger

logger = logging.getLogger(__name__)


def word_count_from_txt_file(file_path):
    """
    Count words in a text file
    """
    with open(file_path, "r") as f:
        text = f.read()
        word_list = re.findall(r"\b[a-zA-Z0-9'-]+\b", text)

        return len(word_list)


def word_count_from_doc_file(file_path):
    """
    Count words in a DOCX file
    """
    doc = Document(file_path)
    total_count = 0

    for para in doc.paragraphs:
        word_list = re.findall(r"\b[a-zA-Z0-9'’'-]+\b", para.text)
        total_count += len(word_list)

    return total_count


@shared_task(bind=True)
def count_words(self, file_id):
    """
    Celery task to count the number of words in the uploaded file(Only for text and docx file)
    """
    try:
        file_upload = FileUpload.objects.get(file_id=file_id)
        file_path = file_upload.file.path
        filename = file_upload.filename.lower()

        if filename.endswith(".txt"):
            word_count = word_count_from_txt_file(file_path)
        elif filename.endswith(".docx"):
            word_count = word_count_from_doc_file(file_path)
        else:
            file_upload.status = StatusChoice.FAILED
            file_upload.save(update_fields=["status"])
            ActivityLogger.log_word_count(file_upload.user, filename, None, "FAILED")
            raise ValueError(f"Unsupported file type {filename}")

        file_upload.word_count = word_count
        file_upload.status = StatusChoice.COMPLETED
        file_upload.save(update_fields=["word_count", "status"])

        ActivityLogger.log_word_count(
            file_upload.user, filename, word_count, "COMPLETED"
        )

        return "Done"

    except FileUpload.DoesNotExist:
        logger.error(f"File object not found for file_id: {file_id}", exc_info=True)
        return "Error: File object not found"
    except Exception as e:
        logger.error(f"Error in count_words: {str(e)}")
        return "Error"
