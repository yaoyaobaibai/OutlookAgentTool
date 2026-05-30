"""Auto-save crash scene - collect logs, temp files, system info into a ZIP."""
import os
import sys
import platform
import shutil
import zipfile
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def save_crash_dump(error_msg, current_log_file="", temp_dir=""):
    """Collect crash scene and save as ZIP to merged_output.
    
    Returns: zip file path, or empty string on failure.
    """
    try:
        output_base = os.path.join(os.path.expanduser("~"), "merged_output")
        crash_dir = os.path.join(output_base, "crash_dumps")
        os.makedirs(crash_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        crash_zip = os.path.join(crash_dir, f"crash_{timestamp}.zip")
        work_dir = os.path.join(crash_dir, f"_tmp_{timestamp}")
        os.makedirs(work_dir, exist_ok=True)

        try:
            # 1. Error summary
            summary_path = os.path.join(work_dir, "error_summary.txt")
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(f"Time: {datetime.now().isoformat()}\n")
                f.write(f"OS: {platform.system()} {platform.release()}\n")
                f.write(f"Error:\n{error_msg}\n")

            # 2. Current log
            if current_log_file and os.path.exists(current_log_file):
                shutil.copy(current_log_file, os.path.join(work_dir, "current_log.txt"))

            # 3. Log directory
            log_dir = os.path.join(os.path.expanduser("~"), "PDFMergeTool_logs")
            if os.path.exists(log_dir):
                log_dest = os.path.join(work_dir, "logs")
                os.makedirs(log_dest, exist_ok=True)
                for fname in os.listdir(log_dir):
                    fpath = os.path.join(log_dir, fname)
                    if os.path.isfile(fpath):
                        try:
                            shutil.copy(fpath, os.path.join(log_dest, fname))
                        except Exception:
                            pass

            # 4. Temp files
            if temp_dir and os.path.exists(temp_dir):
                temp_dest = os.path.join(work_dir, "temp_files")
                os.makedirs(temp_dest, exist_ok=True)
                for fname in os.listdir(temp_dir):
                    fpath = os.path.join(temp_dir, fname)
                    if os.path.isfile(fpath):
                        try:
                            shutil.copy(fpath, os.path.join(temp_dest, fname))
                        except Exception:
                            pass

            # 5. Package as ZIP
            with zipfile.ZipFile(crash_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(work_dir):
                    for fn in files:
                        full_path = os.path.join(root, fn)
                        arcname = os.path.relpath(full_path, work_dir)
                        zf.write(full_path, arcname)

            logger.info(f"Crash dump saved: {crash_zip}")
            return crash_zip

        finally:
            try:
                shutil.rmtree(work_dir)
            except Exception:
                pass

    except Exception as e:
        logger.error(f"Failed to save crash dump: {e}")
        return ""
