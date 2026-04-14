-- Fix table ownership for AP tables
ALTER TABLE IF EXISTS ap_vendorbilllineitem OWNER TO zubair;
ALTER TABLE IF EXISTS ap_vendorbill OWNER TO zubair;

-- Fix table ownership for Procurement tables  
ALTER TABLE IF EXISTS procurement_polineitem OWNER TO zubair;
ALTER TABLE IF EXISTS procurement_goodsreceipt OWNER TO zubair;
ALTER TABLE IF EXISTS procurement_goodsreceiptlineitem OWNER TO zubair;
ALTER TABLE IF EXISTS procurement_purchaseorder OWNER TO zubair;
ALTER TABLE IF EXISTS procurement_purchasereturn OWNER TO zubair;
ALTER TABLE IF EXISTS procurement_debitnote OWNER TO zubair;

-- Grant all privileges to zubair user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO zubair;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO zubair;
