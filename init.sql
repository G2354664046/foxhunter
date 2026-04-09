-- 1. 创建数据库（如果还没有）
CREATE DATABASE IF NOT EXISTS `foxhunter`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `foxhunter`;

-- 2. 用户表：users
DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `id`           INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username`     VARCHAR(50)  NOT NULL COMMENT '用户名',
  `email`        VARCHAR(255) NOT NULL COMMENT '邮箱',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希（经过 bcrypt 等加密）',
  `created_at`   DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_users_username` (`username`),
  UNIQUE KEY `uq_users_email`    (`email`)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='用户表';

-- 3. 样本表：samples
DROP TABLE IF EXISTS `samples`;

CREATE TABLE `samples` (
  `id`         INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id`    INT UNSIGNED NOT NULL COMMENT '所属用户ID，关联 users.id',
  `filename`   VARCHAR(255) NOT NULL COMMENT '原始文件名',
  `sample_type` VARCHAR(20) NOT NULL DEFAULT 'file' COMMENT '样本类型：file/url/hash',
  `hash`       CHAR(64)     NOT NULL COMMENT '样本 SHA-256 哈希',
  `status`     VARCHAR(50)  NOT NULL DEFAULT 'pending' COMMENT '状态：pending/processing/completed/failed',
  `result`     LONGTEXT     NULL COMMENT '检测结果（JSON 字符串，当前为伪数据占位）',
  `result_json` JSON        NULL COMMENT '检测结果（结构化 JSON，推荐读取此字段）',
  `task_id`    VARCHAR(128) NULL COMMENT 'Celery 任务ID（可选）',
  `created_at` DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
  `updated_at` DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
                              ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_samples_user_id` (`user_id`),
  KEY `idx_samples_hash`    (`hash`),
  CONSTRAINT `fk_samples_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='样本表：存储上传文件及检测状态/结果';

-- 4. CNN 检测结果表：cnn_detection_results
-- 参考测试脚本 results.csv 字段（filename/predicted/prob）并扩展业务字段
DROP TABLE IF EXISTS `cnn_detection_results`;

CREATE TABLE `cnn_detection_results` (
  `id`              INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `sample_id`       INT UNSIGNED NOT NULL COMMENT '关联样本ID，引用 samples.id',
  `image_name`      VARCHAR(255) NOT NULL COMMENT '灰度图文件名（如 sample_1.png）',
  `image_path`      VARCHAR(512) NOT NULL COMMENT '灰度图存储路径（out_data）',
  `predicted_index` INT          NOT NULL COMMENT '预测类别索引（对应 class_index.json 的值）',
  `predicted_label` VARCHAR(64)  NOT NULL COMMENT '预测类别标签（对应 class_index.json 的键）',
  `probability`     DOUBLE       NOT NULL COMMENT '预测置信度（0~1）',
  `is_malware`      TINYINT(1)   NOT NULL DEFAULT 1 COMMENT '是否恶意（1=是，0=否）',
  `weights_path`    VARCHAR(512) NULL COMMENT '推理时使用的权重文件路径',
  `created_at`      DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_cnn_result_sample_id` (`sample_id`),
  KEY `idx_cnn_result_created_at` (`created_at`),
  CONSTRAINT `fk_cnn_result_sample`
    FOREIGN KEY (`sample_id`) REFERENCES `samples` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='CNN检测结果表：存储灰度图推理结果（参考 results.csv 扩展）';