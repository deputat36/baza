-- Черновик структуры будущего CRM-модуля базы знаний
-- Версия: MVP draft

CREATE TABLE knowledge_categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(50) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  parent_id INT NULL,
  description TEXT NULL,
  sort_order INT DEFAULT 500,
  is_active TINYINT(1) DEFAULT 1,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE knowledge_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(50) NOT NULL UNIQUE,
  item_type VARCHAR(50) NOT NULL,
  category_id INT NULL,
  title VARCHAR(255) NOT NULL,
  short_description TEXT NULL,
  content MEDIUMTEXT NULL,
  priority TINYINT DEFAULT 3,
  status VARCHAR(50) DEFAULT 'DRAFT',
  source VARCHAR(255) NULL,
  checked_at DATE NULL,
  checked_by INT NULL,
  is_private TINYINT(1) DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_item_type (item_type),
  INDEX idx_status (status),
  INDEX idx_priority (priority),
  INDEX idx_category_id (category_id)
);

CREATE TABLE knowledge_contacts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  item_id INT NOT NULL,
  organization VARCHAR(255) NULL,
  person_name VARCHAR(255) NULL,
  position_name VARCHAR(255) NULL,
  phone VARCHAR(100) NULL,
  phone_extra VARCHAR(100) NULL,
  email VARCHAR(255) NULL,
  address VARCHAR(255) NULL,
  website VARCHAR(255) NULL,
  work_hours VARCHAR(255) NULL,
  comment TEXT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_item_id (item_id)
);

CREATE TABLE knowledge_relations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  from_item_id INT NOT NULL,
  to_item_id INT NOT NULL,
  relation_type VARCHAR(100) DEFAULT 'related',
  comment TEXT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_from_item_id (from_item_id),
  INDEX idx_to_item_id (to_item_id)
);

CREATE TABLE knowledge_keywords (
  id INT AUTO_INCREMENT PRIMARY KEY,
  item_id INT NOT NULL,
  keyword VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_item_id (item_id),
  INDEX idx_keyword (keyword)
);

CREATE TABLE knowledge_change_requests (
  id INT AUTO_INCREMENT PRIMARY KEY,
  item_id INT NULL,
  author_name VARCHAR(255) NULL,
  section_name VARCHAR(255) NULL,
  change_text TEXT NOT NULL,
  old_value TEXT NULL,
  new_value TEXT NULL,
  reason TEXT NULL,
  status VARCHAR(50) DEFAULT 'NEW',
  reviewed_by VARCHAR(255) NULL,
  reviewed_at DATETIME NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_status (status)
);

CREATE TABLE knowledge_practice_notes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  item_id INT NULL,
  author_name VARCHAR(255) NULL,
  note TEXT NOT NULL,
  usefulness TINYINT DEFAULT 3,
  status VARCHAR(50) DEFAULT 'REVIEW',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_item_id (item_id),
  INDEX idx_status (status)
);
