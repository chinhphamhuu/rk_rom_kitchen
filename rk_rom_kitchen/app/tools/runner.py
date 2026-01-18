"""
CLI Runner - Wrapper để chạy external tools qua subprocess
Tất cả CLI commands PHẢI đi qua module này
"""
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional, Callable, List, Tuple
from dataclasses import dataclass

from ..core.logbus import get_log_bus
from ..core.task_defs import TaskResult


@dataclass
class RunResult:
    """Kết quả của một command execution"""
    returncode: int
    stdout: str
    stderr: str
    elapsed_ms: int
    timed_out: bool = False
    
    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.timed_out


class ToolRunner:
    """
    Runner để execute external CLI tools
    Thread-safe với output streaming
    """
    
    def __init__(self):
        self._log = get_log_bus()
    
    def run(self,
            command: List[str],
            cwd: Optional[Path] = None,
            timeout: int = 300,
            log_output: bool = True,
            on_output: Callable[[str], None] = None) -> RunResult:
        """
        Chạy một command và capture output
        
        Args:
            command: List of command + arguments
            cwd: Working directory
            timeout: Timeout in seconds (default 5 minutes)
            log_output: Log stdout/stderr qua logbus
            on_output: Callback cho mỗi line output (realtime streaming)
            
        Returns:
            RunResult with returncode, stdout, stderr
        """
        cmd_str = ' '.join(str(c) for c in command)
        self._log.info(f"[RUNNER] Executing: {cmd_str}")
        
        if cwd:
            self._log.debug(f"[RUNNER] CWD: {cwd}")
        
        start_time = time.time()
        stdout_lines = []
        stderr_lines = []
        timed_out = False
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(cwd) if cwd else None,
                text=True,
                encoding='utf-8',
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # Thread để đọc stdout
            def read_stdout():
                for line in iter(process.stdout.readline, ''):
                    line = line.rstrip()
                    if line:
                        stdout_lines.append(line)
                        if log_output:
                            self._log.debug(f"[OUT] {line}")
                        if on_output:
                            on_output(line)
            
            # Thread để đọc stderr
            def read_stderr():
                for line in iter(process.stderr.readline, ''):
                    line = line.rstrip()
                    if line:
                        stderr_lines.append(line)
                        if log_output:
                            self._log.warning(f"[ERR] {line}")
            
            stdout_thread = threading.Thread(target=read_stdout)
            stderr_thread = threading.Thread(target=read_stderr)
            stdout_thread.start()
            stderr_thread.start()
            
            # Wait for process with timeout
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self._log.error(f"[RUNNER] Timeout after {timeout}s")
                process.kill()
                timed_out = True
            
            stdout_thread.join(timeout=2)
            stderr_thread.join(timeout=2)
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            result = RunResult(
                returncode=process.returncode if not timed_out else -1,
                stdout='\n'.join(stdout_lines),
                stderr='\n'.join(stderr_lines),
                elapsed_ms=elapsed_ms,
                timed_out=timed_out
            )
            
            if result.ok:
                self._log.info(f"[RUNNER] Success in {elapsed_ms}ms")
            else:
                self._log.error(f"[RUNNER] Failed with code {result.returncode}")
            
            return result
            
        except FileNotFoundError:
            elapsed_ms = int((time.time() - start_time) * 1000)
            self._log.error(f"[RUNNER] Command not found: {command[0]}")
            return RunResult(
                returncode=-1,
                stdout='',
                stderr=f"Command not found: {command[0]}",
                elapsed_ms=elapsed_ms
            )
        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            self._log.error(f"[RUNNER] Exception: {e}")
            return RunResult(
                returncode=-1,
                stdout='',
                stderr=str(e),
                elapsed_ms=elapsed_ms
            )
    
    def run_tool(self,
                 tool_path: Path,
                 args: List[str] = None,
                 cwd: Optional[Path] = None,
                 timeout: int = 300) -> RunResult:
        """
        Chạy một tool với path đã biết
        
        Args:
            tool_path: Đường dẫn đến tool executable
            args: Arguments
            cwd: Working directory
            timeout: Timeout in seconds
        """
        if not tool_path.exists():
            self._log.error(f"[RUNNER] Tool không tồn tại: {tool_path}")
            return RunResult(
                returncode=-1,
                stdout='',
                stderr=f"Tool không tồn tại: {tool_path}",
                elapsed_ms=0
            )
        
        command = [str(tool_path)] + (args or [])
        return self.run(command, cwd=cwd, timeout=timeout)
    
    def check_tool(self, tool_path: Path, version_arg: str = "--version") -> Tuple[bool, str]:
        """
        Kiểm tra tool có hoạt động không
        
        Returns:
            Tuple (available, version_string)
        """
        if not tool_path.exists():
            return False, "Not found"
        
        result = self.run([str(tool_path), version_arg], timeout=10, log_output=False)
        
        if result.ok:
            version = result.stdout.split('\n')[0] if result.stdout else "OK"
            return True, version
        else:
            # Some tools return non-zero for --version
            if result.stdout or result.stderr:
                version = (result.stdout or result.stderr).split('\n')[0]
                return True, version
            return False, f"Error: {result.returncode}"


# Singleton instance
_runner: Optional[ToolRunner] = None


def get_runner() -> ToolRunner:
    """Lấy singleton ToolRunner instance"""
    global _runner
    if _runner is None:
        _runner = ToolRunner()
    return _runner
