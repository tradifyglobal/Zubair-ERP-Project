ALTER TABLE user_theme_preference ADD COLUMN IF NOT EXISTS chart_color_1 VARCHAR(20) DEFAULT 'rgba(54, 162, 235, 0.8)';
ALTER TABLE user_theme_preference ADD COLUMN IF NOT EXISTS chart_color_2 VARCHAR(20) DEFAULT 'rgba(255, 159, 64, 0.8)';
ALTER TABLE user_theme_preference ADD COLUMN IF NOT EXISTS chart_color_3 VARCHAR(20) DEFAULT 'rgba(153, 102, 255, 0.8)';
