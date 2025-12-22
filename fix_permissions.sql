ALTER DATABASE tradifyerp_db OWNER TO tradifyerp_user;
REASSIGN OWNED BY postgres TO tradifyerp_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tradifyerp_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tradifyerp_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO tradifyerp_user;
