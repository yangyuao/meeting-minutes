from contextlib import contextmanager
import logging

import pymysql
from pymysql import Error

from .settings import DBConfig

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection(db_config: DBConfig):
    connection = None
    try:
        connection = pymysql.connect(
            host=db_config.host,
            port=db_config.port,
            user=db_config.user,
            password=db_config.password,
            database=db_config.database,
            charset=db_config.charset,
        )
        yield connection
    except Error as exc:
        logger.error("数据库连接错误: %s", exc)
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()


def init_database(db_config: DBConfig) -> None:
    try:
        with get_db_connection(db_config) as connection:
            with connection.cursor() as cursor:
                create_table_query = """
                CREATE TABLE IF NOT EXISTS meeting_minutes_records (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    client_ip VARCHAR(45) NOT NULL,
                    username VARCHAR(255),
                    original_text LONGTEXT,
                    final_prompt LONGTEXT,
                    generated_summary LONGTEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_client_ip (client_ip),
                    INDEX idx_username (username),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                cursor.execute(create_table_query)

                create_transcript_table_query = """
                CREATE TABLE IF NOT EXISTS meeting_minutes_transcript_files (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    client_ip VARCHAR(45) NOT NULL,
                    username VARCHAR(255),
                    audio_file_path VARCHAR(512),
                    transcript_file_path VARCHAR(512),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_client_ip (client_ip),
                    INDEX idx_username (username),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """
                cursor.execute(create_transcript_table_query)

                connection.commit()
                logger.info("数据库表初始化完成")
    except Exception as exc:
        logger.error("数据库初始化失败: %s", exc)


def save_meeting_record(
    db_config: DBConfig,
    client_ip: str,
    username: str,
    original_text: str,
    final_prompt: str,
    generated_summary: str,
) -> None:
    try:
        with get_db_connection(db_config) as connection:
            with connection.cursor() as cursor:
                insert_query = """
                INSERT INTO meeting_minutes_records
                (client_ip, username, original_text, final_prompt, generated_summary)
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(
                    insert_query,
                    (client_ip, username, original_text, final_prompt, generated_summary),
                )
                connection.commit()
                logger.info("会议记录已保存到数据库，ID: %s", cursor.lastrowid)
    except Exception as exc:
        logger.error("保存会议记录失败: %s", exc)


def save_transcript_record(
    db_config: DBConfig,
    client_ip: str,
    username: str,
    audio_file_path: str,
    transcript_file_path: str,
) -> None:
    try:
        with get_db_connection(db_config) as connection:
            with connection.cursor() as cursor:
                insert_query = """
                INSERT INTO meeting_minutes_transcript_files
                (client_ip, username, audio_file_path, transcript_file_path)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(
                    insert_query,
                    (client_ip, username, audio_file_path, transcript_file_path),
                )
                connection.commit()
                logger.info("转录文件记录已保存到数据库，ID: %s", cursor.lastrowid)
    except Exception as exc:
        logger.error("保存转录文件记录失败: %s", exc)
