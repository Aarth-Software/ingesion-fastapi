RAISE NOTICE 'Creating user keycloak';
CREATE USER keycloak with password 'keycloak';
RAISE NOTICE 'Creating schema keycloak';
CREATE SCHEMA keycloak;
RAISE NOTICE 'Granting privileges to keycloak';
GRANT ALL PRIVILEGES ON SCHEMA keycloak TO keycloak;
