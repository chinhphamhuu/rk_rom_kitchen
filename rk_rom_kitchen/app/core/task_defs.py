"""
Task Definitions - Định nghĩa TaskResult và các task types
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class TaskStatus(Enum):
    """Trạng thái của một task"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TaskResult:
    """
    Kết quả của một task
    
    Attributes:
        ok: True nếu thành công
        code: Error code (0 = success)
        message: Thông báo kết quả
        artifacts: Danh sách files/outputs đã tạo
        elapsed_ms: Thời gian chạy (milliseconds)
        data: Dữ liệu bổ sung
    """
    ok: bool = True
    code: int = 0
    message: str = ""
    artifacts: List[str] = field(default_factory=list)
    elapsed_ms: int = 0
    data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success(cls, message: str = "Thành công", 
                artifacts: List[str] = None,
                elapsed_ms: int = 0,
                **data) -> 'TaskResult':
        """Tạo successful result"""
        return cls(
            ok=True,
            code=0,
            message=message,
            artifacts=artifacts or [],
            elapsed_ms=elapsed_ms,
            data=data
        )
    
    @classmethod
    def error(cls, message: str, code: int = 1,
              elapsed_ms: int = 0, **data) -> 'TaskResult':
        """Tạo error result"""
        return cls(
            ok=False,
            code=code,
            message=message,
            artifacts=[],
            elapsed_ms=elapsed_ms,
            data=data
        )
    
    @classmethod
    def cancelled(cls, message: str = "Đã hủy") -> 'TaskResult':
        """Tạo cancelled result"""
        return cls(
            ok=False,
            code=-1,
            message=message,
            artifacts=[],
            elapsed_ms=0
        )


@dataclass
class TaskInfo:
    """Thông tin về một task đang/đã chạy"""
    task_id: str
    task_type: str
    status: TaskStatus = TaskStatus.PENDING
    progress: int = 0  # 0-100
    message: str = ""
    result: Optional[TaskResult] = None


# Error codes
class ErrorCode:
    """Các error codes chuẩn"""
    SUCCESS = 0
    UNKNOWN = 1
    CANCELLED = -1
    
    # File/IO errors (100-199)
    FILE_NOT_FOUND = 100
    FILE_EXISTS = 101
    IO_ERROR = 102
    PERMISSION_ERROR = 103
    
    # Project errors (200-299)
    PROJECT_NOT_FOUND = 200
    PROJECT_EXISTS = 201
    PROJECT_INVALID = 202
    
    # Tool errors (300-399)
    TOOL_NOT_FOUND = 300
    TOOL_FAILED = 301
    TOOL_TIMEOUT = 302
    
    # Pipeline errors (400-499)
    PIPELINE_FAILED = 400
    ROM_DETECT_FAILED = 401
    EXTRACT_FAILED = 402
    PATCH_FAILED = 403
    BUILD_FAILED = 404
    
    # State errors (500-599)
    STATE_INVALID = 500
    ALREADY_RUNNING = 501
