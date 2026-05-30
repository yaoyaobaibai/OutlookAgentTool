"""
合并启动器 - 调用 PDFMergeTool.exe
"""
import os
import subprocess
import sys
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

_CREATE_NO_WINDOW = 0x08000000 if sys.platform == 'win32' else 0


def _safe_decode(data: bytes) -> str:
    """安全解码 stderr/stdout 字节流，自动检测编码。
    
    在中文 Windows 上，无控制台 PyInstaller 程序可能输出 GBK 而非 UTF-8。
    依次尝试 UTF-8 → GBK → latin-1（保底）。
    """
    for encoding in ('utf-8', 'gbk', 'latin-1'):
        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode('utf-8', errors='replace')


class MergeLauncher:
    """PDF 合并启动器"""
    
    def __init__(self, tool_path: str, output_dir: str):
        """
        初始化启动器
        
        Args:
            tool_path: PDFMergeTool.exe 路径
            output_dir: 输出目录
        """
        self.tool_path = tool_path
        self.output_dir = output_dir
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"创建输出目录: {output_dir}")
    
    def is_tool_available(self) -> bool:
        """
        检查工具是否可用
        
        Returns:
            工具是否存在
        """
        exists = os.path.exists(self.tool_path)
        if not exists:
            logger.warning(f"PDFMergeTool 不存在: {self.tool_path}")
        return exists
    
    def merge_files(
        self, 
        file_paths: List[str], 
        output_filename: Optional[str] = None,
        page_size: str = 'A4'
    ) -> tuple[bool, str]:
        """
        调用 PDFMergeTool 合并文件
        
        Args:
            file_paths: 文件路径列表
            output_filename: 输出文件名（不含路径）
            page_size: 纸张大小（A3/A4/Letter）
            
        Returns:
            (是否成功, 输出路径或错误消息)
        """
        if not file_paths:
            return False, "没有文件需要合并"
        
        if not self.is_tool_available():
            return False, f"PDFMergeTool 不存在: {self.tool_path}"
        
        # 生成输出文件名
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"merged_{timestamp}.pdf"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        logger.info(f"准备合并 {len(file_paths)} 个文件")
        logger.info(f"输出路径: {output_path}")
        
        try:
            # 使用命令行参数自动合并
            cmd = [
                self.tool_path,
                '--auto',
                '--output', output_path,
                '--page-size', page_size,
                '--files'
            ]
            cmd.extend(file_paths)
            
            logger.info(f"启动命令: {' '.join(cmd)}")
            
            # 启动 PDFMergeTool 并等待完成
            # 设置 PYTHONIOENCODING=utf-8 确保子进程 stderr 输出为 UTF-8
            # 避免中文 Windows 系统下 GBK 编码导致的乱码
            env = os.environ.copy()
            env.setdefault('PYTHONIOENCODING', 'utf-8')
            
            process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(self.tool_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                creationflags=_CREATE_NO_WINDOW
            )
            
            # 等待进程完成（超时按文件数动态计算：每文件 60 秒，最少 120 秒，最多 600 秒）
            per_file_timeout = 60
            min_timeout = 120
            max_timeout = 600
            timeout = max(min_timeout, min(len(file_paths) * per_file_timeout, max_timeout))
            logger.info(f"等待合并完成（超时: {timeout}秒, {len(file_paths)}个文件）")
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                
                if process.returncode == 0:
                    logger.info(f"合并成功: {output_path}")
                    return True, f"合并成功: {output_path}"
                else:
                    # 解码 stderr：优先 UTF-8，失败时回退到 GBK (中文 Windows)
                    error_msg = _safe_decode(stderr) if stderr else "未知错误"
                    logger.error(f"合并失败: {error_msg}")
                    return False, f"合并失败: {error_msg}"
                    
            except subprocess.TimeoutExpired:
                process.kill()
                logger.error(f"合并超时（超过{timeout}秒）")
                return False, f"合并超时（{len(file_paths)}个文件处理超过{timeout}秒，请减少文件数量或分批处理）"
            
        except Exception as e:
            error_msg = f"启动 PDFMergeTool 失败: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def merge_files_silent(
        self, 
        file_paths: List[str], 
        output_filename: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        静默合并文件（直接调用 Python 模块，不启动 GUI）
        
        Args:
            file_paths: 文件路径列表
            output_filename: 输出文件名
            
        Returns:
            (是否成功, 输出路径或错误消息)
        """
        if not file_paths:
            return False, "没有文件需要合并"
        
        # 生成输出文件名
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"merged_{timestamp}.pdf"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # 直接调用 Python 合并逻辑（绕过 GUI）
            import sys
            sys.path.insert(0, os.path.dirname(os.path.dirname(self.tool_path)))
            
            from converters import merge_pdfs
            from utils import add_page_numbers
            
            # 合并文件
            success, error = merge_pdfs(file_paths, output_path)
            
            if not success:
                return False, error
            
            # 添加页码
            final_path = os.path.join(
                self.output_dir, 
                f"final_{output_filename}"
            )
            
            if add_page_numbers(output_path, final_path):
                # 删除中间文件
                try:
                    os.remove(output_path)
                except:
                    pass
                return True, final_path
            else:
                # 页码添加失败，使用原文件
                return True, output_path
                
        except ImportError as e:
            return False, f"导入合并模块失败: {e}"
        except Exception as e:
            return False, f"合并失败: {e}"
    
    def open_output_folder(self):
        """打开输出文件夹"""
        try:
            subprocess.Popen(f'explorer "{self.output_dir}"')
            logger.info(f"打开输出文件夹: {self.output_dir}")
        except Exception as e:
            logger.error(f"打开文件夹失败: {e}")
