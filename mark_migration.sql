INSERT INTO django_migrations (app, name, applied) 
VALUES ('maintenance', '0003_workorder_completion_date_workorder_is_posted_to_gl', NOW()) 
ON CONFLICT DO NOTHING;
