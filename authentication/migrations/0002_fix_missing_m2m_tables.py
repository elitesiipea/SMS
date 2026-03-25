from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gestion_academique", "0001_initial"),
        ("authentication", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS authentication_user_gestion (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES authentication_user(id) DEFERRABLE INITIALLY DEFERRED,
                etablissement_id BIGINT NOT NULL REFERENCES gestion_academique_etablissement(id) DEFERRABLE INITIALLY DEFERRED,
                UNIQUE (user_id, etablissement_id)
            );

            CREATE INDEX IF NOT EXISTS authentication_user_gestion_user_id_idx
            ON authentication_user_gestion (user_id);

            CREATE INDEX IF NOT EXISTS authentication_user_gestion_etablissement_id_idx
            ON authentication_user_gestion (etablissement_id);

            CREATE TABLE IF NOT EXISTS authentication_user_classe (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES authentication_user(id) DEFERRABLE INITIALLY DEFERRED,
                classe_id BIGINT NOT NULL REFERENCES gestion_academique_classe(id) DEFERRABLE INITIALLY DEFERRED,
                UNIQUE (user_id, classe_id)
            );

            CREATE INDEX IF NOT EXISTS authentication_user_classe_user_id_idx
            ON authentication_user_classe (user_id);

            CREATE INDEX IF NOT EXISTS authentication_user_classe_classe_id_idx
            ON authentication_user_classe (classe_id);
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS authentication_user_classe;
            DROP TABLE IF EXISTS authentication_user_gestion;
            """,
        ),
    ]
