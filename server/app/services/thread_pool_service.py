"""
线程池服务 - 简单的异步处理方案
"""
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ThreadPoolService:
    """线程池服务"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor: Optional[ThreadPoolExecutor] = None
        self._lock = threading.Lock()
    
    def get_executor(self) -> ThreadPoolExecutor:
        """获取线程池执行器"""
        if self.executor is None:
            with self._lock:
                if self.executor is None:
                    self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
                    logger.info(f"线程池初始化完成，最大工作线程: {self.max_workers}")
        return self.executor
    
    def submit_task(self, func, *args, **kwargs):
        """提交任务到线程池"""
        executor = self.get_executor()
        future = executor.submit(func, *args, **kwargs)
        logger.info(f"任务已提交到线程池: {func.__name__}")
        return future
    
    def shutdown(self):
        """关闭线程池"""
        if self.executor:
            self.executor.shutdown(wait=True)
            logger.info("线程池已关闭")

# 全局线程池实例
thread_pool = ThreadPoolService(max_workers=4)
