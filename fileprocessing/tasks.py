import logging
from fileprocessing.models import FileUpload
from fileprocessing.choices import StatusChoice
from docx import Document
from utils.logger import ActivityLogger
import re

from celery import shared_task


logger = logging.getLogger(__name__)

def word_count_from_txt_file(file_path):
    with open(file_path, "r") as f:
        text = f.read()
        word_list = re.findall(r"\b[a-zA-Z0-9'-]+\b", text)

        return len(word_list)
    
def word_count_from_doc_file(file_path):
    doc = Document(file_path)
    total_count = 0

    for para in doc.paragraphs:
        word_list = re.findall(r"\b[a-zA-Z0-9'’'-]+\b", para.text)
        total_count += len(word_list)

    return total_count
        


@shared_task(bind=True)
def count_words(self, file_id):
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
            ActivityLogger.log_word_count(file_upload.user, filename, None, "Failed")
            raise ValueError(f"Unsupported file type {filename}")
        
        file_upload.word_count = word_count
        file_upload.status = StatusChoice.COMPLETED
        file_upload.save(update_fields=["word_count", "status"])

        ActivityLogger.log_word_count(file_upload.user, filename, word_count, "COMPLETED")

        return "Done"
    except Exception as e:
        logger.error(f"Error in count_words: {str(e)}")
        return "Error"