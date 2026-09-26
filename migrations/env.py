from alembic import context
from flask import current_app


config = context.config
migration_extension = current_app.extensions["migrate"]
target_metadata = migration_extension.db.metadata
configure_args = migration_extension.configure_args


def run_migrations_offline():
    """Genera SQL sin abrir una conexión a la base de datos."""
    database_url = migration_extension.db.engine.url
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **configure_args,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Ejecuta migraciones usando el engine configurado por Flask-SQLAlchemy."""
    with migration_extension.db.engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            **configure_args,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
