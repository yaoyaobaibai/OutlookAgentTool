"""ZIP handler - extract and collect mergeable files from ZIP archives."""
import os
import zipfile
import logging

logger = logging.getLogger(__name__)

MERGEABLE_EXTENSIONS = {'.pdf', '.txt', '.docx', '.doc', '.xlsx', '.xls',
                         '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp', '.msg'}


def extract_from_zip(zip_path, output_dir):
    """Extract mergeable files from a ZIP archive.
    
    Returns: (success: bool, file_paths: list, error_msg: str)
    """
    try:
        if not os.path.exists(zip_path):
            return False, [], f"ZIP file not found: {zip_path}"

        zip_name = os.path.splitext(os.path.basename(zip_path))[0]
        extract_dir = os.path.join(output_dir, f"_zip_{zip_name}")
        os.makedirs(extract_dir, exist_ok=True)

        collected_files = []

        with zipfile.ZipFile(zip_path, 'r') as zf:
            file_list = zf.namelist()
            logger.info(f"ZIP contains {len(file_list)} entries: {zip_path}")

            for member in file_list:
                if member.endswith('/') or member.endswith('\\'):
                    continue

                ext = os.path.splitext(member)[1].lower()

                if ext in MERGEABLE_EXTENSIONS:
                    zf.extract(member, extract_dir)
                    extracted_path = os.path.join(extract_dir, member)

                    if os.path.isfile(extracted_path):
                        collected_files.append(extracted_path)
                        logger.info(f"Extracted from ZIP: {member}")
                elif ext == '.zip':
                    logger.info(f"Skipping nested ZIP: {member}")

        if not collected_files:
            return False, [], f"No mergeable files found in ZIP"

        return True, collected_files, ""

    except zipfile.BadZipFile:
        return False, [], f"Not a valid ZIP: {os.path.basename(zip_path)}"
    except Exception as e:
        logger.error(f"ZIP extraction failed: {e}")
        return False, [], f"ZIP extraction failed: {str(e)}"
