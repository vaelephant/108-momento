#!/usr/bin/env python3
"""
Momento AI Photo Management System - ASCII Logo
精美的启动Logo显示
"""
from typing import List
import os


class MomentoLogo:
    """Momento Logo 显示器"""
    
    # 颜色代码
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'magenta': '\033[95m',
        'white': '\033[97m',
        'gray': '\033[90m',
    }
    
    # Logo ASCII Art
    LOGO_LINES = [
        "  ███╗   ███╗ ██████╗ ███╗   ███╗███████╗███╗   ██╗████████╗ ██████╗ ",
        "  ████╗ ████║██╔═══██╗████╗ ████║██╔════╝████╗  ██║╚══██╔══╝██╔═══██╗",
        "  ██╔████╔██║██║   ██║██╔████╔██║█████╗  ██╔██╗ ██║   ██║   ██║   ██║",
        "  ██║╚██╔╝██║██║   ██║██║╚██╔╝██║██╔══╝  ██║╚██╗██║   ██║   ██║   ██║",
        "  ██║ ╚═╝ ██║╚██████╔╝██║ ╚═╝ ██║███████╗██║ ╚████║   ██║   ╚██████╔╝",
        "  ╚═╝     ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ",
    ]
    
    SUBTITLE = "AI-Powered Photo Classification & Management System"
    SUBTITLE_CN = "AI 智能照片分类与管理系统"
    
    @classmethod
    def print_logo(cls, colored: bool = True) -> None:
        """
        打印Logo
        
        Args:
            colored: 是否使用彩色输出
        """
        # 检测是否支持彩色输出
        if not colored or os.getenv('NO_COLOR'):
            cls._print_plain_logo()
            return
        
        # 打印彩色Logo
        cls._print_colored_logo()
    
    @classmethod
    def _print_colored_logo(cls) -> None:
        """打印彩色Logo"""
        print()
        
        # 渐变颜色效果
        colors = ['cyan', 'cyan', 'blue', 'blue', 'magenta', 'magenta']
        
        for i, line in enumerate(cls.LOGO_LINES):
            color = colors[i]
            print(f"{cls.COLORS[color]}{cls.COLORS['bold']}{line}{cls.COLORS['reset']}")
        
        # 副标题
        print()
        print(f"{cls.COLORS['gray']}  {cls.SUBTITLE}{cls.COLORS['reset']}")
        print(f"{cls.COLORS['gray']}  {cls.SUBTITLE_CN}{cls.COLORS['reset']}")
        print()
    
    @classmethod
    def _print_plain_logo(cls) -> None:
        """打印纯文本Logo"""
        print()
        for line in cls.LOGO_LINES:
            print(line)
        print()
        print(f"  {cls.SUBTITLE}")
        print(f"  {cls.SUBTITLE_CN}")
        print()
    
    @classmethod
    def print_banner(cls, version: str = "1.0.0", colored: bool = True) -> None:
        """
        打印完整的启动横幅
        
        Args:
            version: 版本号
            colored: 是否使用彩色
        """
        cls.print_logo(colored)
        
        if colored and not os.getenv('NO_COLOR'):
            c = cls.COLORS
            print(f"{c['gray']}{'═' * 76}{c['reset']}")
            print(f"{c['green']}  📸 Version: {c['bold']}{version}{c['reset']}  {c['gray']}|{c['reset']}  "
                  f"{c['yellow']}🤖 Powered by YAN{c['reset']}  {c['gray']}|{c['reset']}  "
                  f"{c['blue']}✨ Smart Classification{c['reset']}")
            print(f"{c['gray']}{'═' * 76}{c['reset']}")
        else:
            print("=" * 76)
            print(f"  📸 Version: {version}  |  🤖 Powered by AI  |  ✨ Smart Classification")
            print("=" * 76)
        print()


class SimpleLogo:
    """简化版Logo - 更小巧"""
    
    LOGO = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🎯 MOMENTO - AI Photo Management System                ║
    ║   智能照片分类与管理系统                                   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    
    @classmethod
    def print_logo(cls) -> None:
        """打印简化Logo"""
        print(cls.LOGO)


class MinimalLogo:
    """极简版Logo - 单行"""
    
    @classmethod
    def print_logo(cls, version: str = "1.0.0") -> None:
        """打印极简Logo"""
        print()
        print(f"  🎯 MOMENTO v{version} - AI Photo Management System")
        print(f"  智能照片分类与管理系统")
        print()


def demo():
    """演示所有Logo样式"""
    print("\n" + "=" * 80)
    print("1️⃣  完整Logo（彩色）")
    print("=" * 80)
    MomentoLogo.print_banner(version="1.0.0", colored=True)
    
    input("\n按Enter查看下一个... ")
    
    print("\n" + "=" * 80)
    print("2️⃣  完整Logo（纯文本）")
    print("=" * 80)
    MomentoLogo.print_banner(version="1.0.0", colored=False)
    
    input("\n按Enter查看下一个... ")
    
    print("\n" + "=" * 80)
    print("3️⃣  简化Logo")
    print("=" * 80)
    SimpleLogo.print_logo()
    
    input("\n按Enter查看下一个... ")
    
    print("\n" + "=" * 80)
    print("4️⃣  极简Logo")
    print("=" * 80)
    MinimalLogo.print_logo(version="1.0.0")
    
    print("\n✅ 演示完成！")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # 演示模式
        demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "simple":
        # 简化版
        SimpleLogo.print_logo()
    elif len(sys.argv) > 1 and sys.argv[1] == "minimal":
        # 极简版
        MinimalLogo.print_logo()
    else:
        # 默认：完整版
        MomentoLogo.print_banner(version="1.0.0", colored=True)

