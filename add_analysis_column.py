#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为conversations表添加analysis字段
"""
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text

# 数据库路径
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DATABASE_PATH = os.path.join(DATA_DIR, 'app.db')
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

def add_analysis_column():
    """为conversations表添加analysis字段"""
    print(f"数据库路径: {DATABASE_PATH}")
    
    # 创建引擎
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # 检查字段是否存在
    with engine.connect() as conn:
        # 检查conversations表的所有列
        result = conn.execute(text("PRAGMA table_info(conversations)"))
        columns = [row[1] for row in result.fetchall()]
        print(f"当前conversations表的列: {columns}")
        
        if 'analysis' in columns:
            print("✓ analysis字段已存在，无需添加")
            return
        
        # 添加analysis字段
        conn.execute(text("ALTER TABLE conversations ADD COLUMN analysis TEXT"))
        conn.commit()
        print("✓ 已添加analysis字段")
        
        # 验证
        result = conn.execute(text("PRAGMA table_info(conversations)"))
        columns = [row[1] for row in result.fetchall()]
        print(f"添加后conversations表的列: {columns}")

if __name__ == '__main__':
    add_analysis_column()