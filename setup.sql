

CREATE TABLE IF NOT EXISTS h1_carry_over_performance (
    id SERIAL PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL,
    period VARCHAR(20) NOT NULL,
    units_transferred INTEGER,
    revenue DECIMAL(12,2),
    gross_profit DECIMAL(12,2),
    taxes_and_surcharges DECIMAL(12,2),
    period_expenses DECIMAL(12,2),
    net_profit DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS h1_collections_performance (
    id SERIAL PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL,
    annual_target DECIMAL(12,2),
    h1_budget DECIMAL(12,2),
    h1_actual DECIMAL(12,2),
    h1_completion_rate VARCHAR(10),
    annual_completion_rate VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO h1_carry_over_performance (project_name, period, units_transferred, revenue, gross_profit, taxes_and_surcharges, period_expenses, net_profit) VALUES
('水月周庄', '上半年实际', 42, 4953.00, 2115.00, 1309.00, 3471.00, 3666.00),
('水月源岸', '上半年实际', 264, 47466.00, 5830.00, 0.00, 0.00, 0.00),
('酒店', '上半年实际', 0, 2065.00, 935.00, 137.00, 1924.00, -1125.00),
('合计', '上半年实际', 306, 54484.00, 8880.00, 1446.00, 5395.00, 2541.00);

INSERT INTO h1_carry_over_performance (project_name, period, units_transferred, revenue, gross_profit, taxes_and_surcharges, period_expenses, net_profit) VALUES
('水月周庄', '下半年预计', 115, 12989.00, 6792.00, 2799.00, 6342.00, 1053.00),
('水月源岸', '下半年预计', 239, 36427.00, 6295.00, 0.00, 0.00, 0.00),
('酒店', '下半年预计', 0, 2321.00, 1171.00, 151.00, 2220.00, 0.00),
('合计', '下半年预计', 354, 51737.00, 14258.00, 2950.00, 8562.00, 1053.00);

INSERT INTO h1_collections_performance (project_name, annual_target, h1_budget, h1_actual, h1_completion_rate, annual_completion_rate) VALUES
('水月周庄', 19987.00, 7754.00, 1912.00, '25%', '10%'),
('水月源岸', 76813.00, 32204.00, 35852.00, '111%', '47%'),
('铂尔曼酒店', 4472.00, 1909.00, 2124.00, '111%', '47%'),
('小计', 101272.00, 41867.00, 39888.00, '95%', '39%'),
('欢乐明湖F03源庭', 153983.00, 51000.00, 22681.00, '44%', '15%'),
('合计', 255255.00, 92867.00, 62569.00, '67%', '24%');

CREATE INDEX idx_carry_over_project ON h1_carry_over_performance(project_name);
CREATE INDEX idx_carry_over_period ON h1_carry_over_performance(period);
CREATE INDEX idx_collections_project ON h1_collections_performance(project_name);

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO oct_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO oct_user;

SELECT 'h1_carry_over_performance' as table_name, COUNT(*) as record_count FROM h1_carry_over_performance
UNION ALL
SELECT 'h1_collections_performance' as table_name, COUNT(*) as record_count FROM h1_collections_performance;
