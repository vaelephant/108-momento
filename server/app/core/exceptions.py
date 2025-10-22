"""
自定义异常类
"""
from typing import Optional, Any


class MomentoException(Exception):
    """Momento应用基础异常类"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "MOMENTO_ERROR",
        data: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.data = data
        super().__init__(self.message)


class ValidationError(MomentoException):
    """数据验证错误"""
    
    def __init__(self, message: str = "数据验证失败", data: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            data=data
        )


class NotFoundError(MomentoException):
    """资源未找到错误"""
    
    def __init__(self, message: str = "资源未找到", data: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            data=data
        )


class UnauthorizedError(MomentoException):
    """未授权错误"""
    
    def __init__(self, message: str = "未授权访问", data: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
            data=data
        )


class ForbiddenError(MomentoException):
    """禁止访问错误"""
    
    def __init__(self, message: str = "禁止访问", data: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
            data=data
        )


class ConflictError(MomentoException):
    """冲突错误"""
    
    def __init__(self, message: str = "资源冲突", data: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            data=data
        )


class FileError(MomentoException):
    """文件处理错误"""
    
    def __init__(self, message: str = "文件处理失败", data: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="FILE_ERROR",
            data=data
        )


class AIProcessingError(MomentoException):
    """AI处理错误"""
    
    def __init__(self, message: str = "AI处理失败", data: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="AI_PROCESSING_ERROR",
            data=data
        )
