"""
测试数据库连接和初始化
"""
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .entities import Base, Configuration

# 导入路径工具函数
try:
    from utils.path_utils import get_executable_dir
except ImportError:
    # 如果导入失败，使用备用方案
    def get_executable_dir():
        if getattr(sys, 'frozen', False):
            if "__compiled__" in globals():
                return Path(sys.argv[0]).resolve().parent
            return Path(sys.executable).parent
        return Path(__file__).parent.parent.parent.resolve()

# 测试数据库路径 - 使用单独的测试数据库文件
BASE_DIR = get_executable_dir()
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
TEST_DATABASE_PATH = DATA_DIR / "test_app.db"
TEST_DATABASE_URL = f"sqlite:///{TEST_DATABASE_PATH}"

# 创建测试引擎
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# 测试会话工厂
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def get_test_db():
    """获取测试数据库会话（用于依赖注入）"""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_test_db():
    """初始化测试数据库，创建表和默认数据"""
    # 创建所有表
    Base.metadata.create_all(bind=test_engine)
    
    # 插入默认配置
    db = TestSessionLocal()
    try:
        default_configs = [
            Configuration(key='llm_provider', value='openai', category='llm', 
                         description='默认LLM提供商'),
            Configuration(key='llm_model', value='gpt-4-turbo', category='llm',
                         description='默认使用的模型'),
            Configuration(key='llm_temperature', value='0.7', category='llm',
                         description='模型温度参数'),
            Configuration(key='llm_max_tokens', value='2000', category='llm',
                         description='最大token数'),
            Configuration(key='llm_timeout', value='30', category='llm',
                         description='API请求超时时间(秒)'),
            Configuration(key='system_language', value='zh-CN', category='system',
                         description='系统语言'),
            Configuration(key='system_timezone', value='Asia/Shanghai', category='system',
                         description='系统时区'),
            Configuration(key='ui_theme', value='light', category='ui',
                         description='界面主题'),
        ]
        
        for config in default_configs:
            existing = db.query(Configuration).filter_by(key=config.key).first()
            if not existing:
                db.add(config)
        
        db.commit()
    finally:
        db.close()
    
    # 检查并添加 tasks 表的 order 列
    db = TestSessionLocal()
    try:
        from sqlalchemy import text
        # 检查 tasks 表是否有 order 列
        result = db.execute(text("PRAGMA table_info(tasks)"))
        columns = [row[1] for row in result]
        
        if 'order' not in columns:
            # 添加 order 列
            db.execute(text("ALTER TABLE tasks ADD COLUMN \"order\" INTEGER DEFAULT 0"))
            db.commit()
            # 为现有任务设置默认的 order 值
            tasks = db.execute(text("SELECT id FROM tasks ORDER BY id")).fetchall()
            for i, task in enumerate(tasks):
                db.execute(text(f"UPDATE tasks SET \"order\" = {i} WHERE id = {task[0]}"))
            db.commit()
            print("已成功添加 tasks.order 列并设置默认值")
        else:
            print("tasks.order 列已存在")
    except Exception as e:
        print(f"添加 order 列失败: {str(e)}")
        db.rollback()
    finally:
        db.close()
    
    # 检查并添加 projects 表的 assignee 列
    db = TestSessionLocal()
    try:
        from sqlalchemy import text
        # 检查 projects 表是否有 assignee 列
        result = db.execute(text("PRAGMA table_info(projects)"))
        columns = [row[1] for row in result]
        
        if 'assignee' not in columns:
            # 添加 assignee 列
            db.execute(text("ALTER TABLE projects ADD COLUMN assignee TEXT"))
            db.commit()
            print("已成功添加 projects.assignee 列")
        else:
            print("projects.assignee 列已存在")
    except Exception as e:
        print(f"添加 assignee 列失败: {str(e)}")
        db.rollback()
    finally:
        db.close()
    
    print(f"测试数据库初始化完成: {TEST_DATABASE_PATH}")
